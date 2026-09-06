"""
A2 Problem A — D3(a) guardrail layer (code, not prompt).

Four controls the brief requires before any prompt tuning:
  1. step cap
  2. budget ceiling
  3. action de-duplication
  4. autonomy setting with the gate in front of the irreversible step

This module is deliberately free of network / API calls so D3(b) and D7 can
run on a scripted backend at zero cost.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Autonomy = Literal["suggest", "confirm", "act"]


def _call_key(name: str, kwargs: dict[str, Any]) -> tuple:
    """Stable identity for one tool call: name + sorted kwargs."""
    items = tuple(sorted((str(k), repr(v)) for k, v in kwargs.items()))
    return (name, items)


@dataclass
class GuardrailState:
    """Per-run guardrail state. Create one instance at the start of each case."""

    # Defaults calibrated to Group 6 Part1/Part2 measurements:
    #   parallel CLM-8842 ≈ 4 turns; Part2 scripted flows ≈ 4–6 turns → cap 8
    #   Part1 parallel cost ≈ US$0.0017 → ceiling 0.05 is a tripwire
    autonomy: Autonomy = "confirm"
    step_cap: int = 8
    budget_ceiling_usd: float = 0.05
    enable_dedup: bool = True
    enable_step_cap: bool = True
    enable_budget: bool = True

    turn: int = 0
    cost_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    call_history: list[tuple] = field(default_factory=list)
    operator_approved: set[str] = field(default_factory=set)
    stop_reason: str | None = None

    # ---- instrumentation helpers ----
    def note_tokens(self, tokens_in: int = 0, tokens_out: int = 0,
                    price_in_per_m: float = 0.10,
                    price_out_per_m: float = 0.40) -> None:
        """Accumulate tokens and estimated USD cost (cheap-tier defaults)."""
        self.tokens_in += tokens_in
        self.tokens_out += tokens_out
        self.cost_usd += (
            tokens_in * price_in_per_m / 1_000_000
            + tokens_out * price_out_per_m / 1_000_000
        )

    def begin_turn(self) -> str | None:
        """Call at the start of each loop turn. Returns a stop message if capped."""
        self.turn += 1
        if self.enable_step_cap and self.turn > self.step_cap:
            self.stop_reason = (
                f"STEP_CAP: run stopped after {self.step_cap} turns "
                f"(attempted turn {self.turn})"
            )
            return self.stop_reason
        return None

    def check_budget(self) -> str | None:
        """Call after adding tokens for a turn. Returns a stop message if over budget."""
        if self.enable_budget and self.cost_usd > self.budget_ceiling_usd:
            self.stop_reason = (
                f"BUDGET_CEILING: run stopped at ${self.cost_usd:.4f} "
                f"(ceiling ${self.budget_ceiling_usd:.4f})"
            )
            return self.stop_reason
        return None

    def check_dedup(self, name: str, kwargs: dict[str, Any]) -> str | None:
        """
        Return a BLOCKED observation if this exact call already ran this run.
        Does not record the call — caller should record only successful attempts
        via record_call(), or use wrap_tool().
        """
        if not self.enable_dedup:
            return None
        key = _call_key(name, kwargs)
        if key in self.call_history:
            return (
                f"BLOCKED: action de-duplication — {name}{kwargs} "
                f"already executed this run"
            )
        return None

    def record_call(self, name: str, kwargs: dict[str, Any]) -> None:
        """Record a tool call that was actually executed."""
        self.call_history.append(_call_key(name, kwargs))

    def approve(self, claim_id: str) -> None:
        """Operator confirmation for autonomy='confirm'."""
        self.operator_approved.add(claim_id)

    def is_approved(self, claim_id: str) -> bool:
        return claim_id in self.operator_approved

    def snapshot(self) -> dict[str, Any]:
        return {
            "turns": self.turn,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_usd": round(self.cost_usd, 6),
            "stop_reason": self.stop_reason,
            "autonomy": self.autonomy,
            "step_cap": self.step_cap,
            "budget_ceiling_usd": self.budget_ceiling_usd,
            "calls": len(self.call_history),
        }


def wrap_tools(tools: dict, state: GuardrailState) -> dict:
    """
    Return a TOOLS dict where every call is checked for de-duplication first.
    Use this from Part1's run_agent instead of calling TOOLS raw.
    """
    wrapped = {}

    def _make(name, fn):
        def _wrapped(**kwargs):
            blocked = state.check_dedup(name, kwargs)
            if blocked:
                return blocked
            result = fn(**kwargs)
            state.record_call(name, kwargs)
            return result
        _wrapped.__name__ = name
        _wrapped.__doc__ = getattr(fn, "__doc__", None)
        return _wrapped

    for name, fn in tools.items():
        wrapped[name] = _make(name, fn)
    return wrapped
