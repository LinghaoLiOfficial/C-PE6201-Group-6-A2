"""
A2 Problem A — D7 Failure 1: loop-control failure (required).

Build as a DELETION from the working agent, not a separately written bad agent:
  working run  = GuardrailState(enable_dedup=True)
  broken run   = GuardrailState(enable_dedup=False)   # delete the dedup guard
  restore run  = GuardrailState(enable_dedup=True)    # putting X back recovers behaviour

Scripted: a fake model that keeps re-calling get_claim. No API key.

Run:
  python D7_loop_failure_demo.py
"""
from __future__ import annotations

import json
import os

from guardrails import GuardrailState, wrap_tools

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_JSON = os.path.join(HERE, "D7_loop_failure_results.json")


def _stub_get_claim(claim_id: str) -> str:
    return f"claim_id={claim_id} member_id=M-2214 hospital_id=H-114 lines=[3]"


STUB = {"get_claim": _stub_get_claim}


def simulate_loop(enable_dedup: bool, step_cap: int = 8) -> dict:
    """
    Scripted agent that stubbornly re-issues get_claim every turn.
    With dedup ON, turn 2 is blocked and we can stop early once we see it.
    With dedup OFF, it burns turns until the step cap.
    """
    state = GuardrailState(
        autonomy="confirm",
        step_cap=step_cap,
        enable_dedup=enable_dedup,
        enable_budget=False,  # isolate the loop-control question
    )
    tools = wrap_tools(STUB, state)
    observations = []
    stopped_by = None

    for _ in range(step_cap + 2):
        cap_msg = state.begin_turn()
        if cap_msg:
            stopped_by = "step_cap"
            observations.append(cap_msg)
            break

        # Fake model: always asks for the same claim again.
        obs = tools["get_claim"](claim_id="CLM-8842")
        observations.append(obs)

        if obs.startswith("BLOCKED: action de-duplication"):
            stopped_by = "dedup"
            # A well-instrumented agent would Final/escalate here; we stop the demo.
            break

        # Cheap-tier token estimate per turn (illustrative, for the before/after table).
        state.note_tokens(tokens_in=1200 + 400 * (state.turn - 1), tokens_out=80)

    else:
        stopped_by = "ran_out"

    return {
        "enable_dedup": enable_dedup,
        "stopped_by": stopped_by,
        "turns": state.turn,
        "tokens_in": state.tokens_in,
        "tokens_out": state.tokens_out,
        "cost_usd": round(state.cost_usd, 6),
        "unique_calls": len(state.call_history),
        "observations_tail": observations[-3:],
        "snapshot": state.snapshot(),
    }


def main() -> None:
    broken = simulate_loop(enable_dedup=False, step_cap=8)
    working = simulate_loop(enable_dedup=True, step_cap=8)
    restored = simulate_loop(enable_dedup=True, step_cap=8)

    payload = {
        "failure": "loop-control: repeated get_claim",
        "deletion": "enable_dedup=False",
        "broken": broken,
        "working": working,
        "restored": restored,
        "restore_matches_working": restored["stopped_by"] == working["stopped_by"],
    }
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print("=" * 64)
    print("D7 Failure 1 — loop-control (dedup deleted)")
    print("=" * 64)
    print(f"BROKEN  (dedup OFF): turns={broken['turns']}  "
          f"stopped_by={broken['stopped_by']}  cost=${broken['cost_usd']}")
    print(f"WORKING (dedup ON):  turns={working['turns']}  "
          f"stopped_by={working['stopped_by']}  cost=${working['cost_usd']}")
    print(f"RESTORED:            turns={restored['turns']}  "
          f"stopped_by={restored['stopped_by']}  "
          f"matches_working={payload['restore_matches_working']}")
    print(f"Wrote {REPORT_JSON}")


if __name__ == "__main__":
    main()
