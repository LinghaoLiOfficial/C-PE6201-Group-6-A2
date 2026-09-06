"""
A2 Problem A — gated action: issue_decision_letter.

Per the brief: this is ONE function, three steps —
  (1) check the gate (autonomy / operator / duplicate)
  (2) append one structured record to a local JSONL file
  (3) return a confirmation string

It does NOT compose a letter, send email, or build a UI.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from guardrails import GuardrailState

# Decisions land here (local file only — never a live system).
DECISIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decisions.jsonl")

VALID_DECISIONS = {
    "approve_in_principle",
    "request_document",
    "escalate",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def already_decided(claim_id: str, path: str = DECISIONS_PATH) -> bool:
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("case_id") == claim_id:
                return True
    return False


def append_decision(record: dict[str, Any], path: str = DECISIONS_PATH) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def clear_decisions(path: str = DECISIONS_PATH) -> None:
    """Test helper — wipe the log between checklist / D7 runs."""
    if os.path.exists(path):
        os.remove(path)


def issue_decision_letter(
    claim_id: str,
    decision: str,
    reason: str,
    evidence: list[str] | None = None,
    *,
    state: GuardrailState,
    escalate_to: str | None = None,
    trigger: str | None = None,
    path: str = DECISIONS_PATH,
) -> str:
    """
    WHAT  Records the first-response decision on a claim (the irreversible write).
    INPUT claim_id str;
          decision Literal["approve_in_principle","request_document","escalate"];
          reason str; evidence list[str]
    RETURNS confirmation str, <= 40 tokens
    FAILS WHEN the gate is not satisfied, decision is invalid, or claim already decided
    IRREVERSIBLE? YES — covered by the autonomy gate on GuardrailState
    """
    evidence = evidence or []

    if decision not in VALID_DECISIONS:
        return (
            f"BLOCKED: invalid decision {decision!r}; "
            f"must be one of {sorted(VALID_DECISIONS)}"
        )

    # --- gate: autonomy ---
    if state.autonomy == "suggest":
        return (
            "BLOCKED: autonomy=suggest — agent may only propose; "
            "a human must issue the decision"
        )
    if state.autonomy == "confirm" and not state.is_approved(claim_id):
        return "BLOCKED: awaiting operator confirmation"

    # --- gate: no double-write ---
    if already_decided(claim_id, path=path):
        return "BLOCKED: duplicate — a decision already exists for this claim"

    record = {
        "ts": _now(),
        "case_id": claim_id,
        "decision": decision,
        "reason": reason,
        "evidence": evidence,
        "autonomy": state.autonomy,
        "gate": (
            "operator approved"
            if state.autonomy == "confirm"
            else f"autonomy={state.autonomy}"
        ),
        "turns": state.turn,
        "tokens_in": state.tokens_in,
        "tokens_out": state.tokens_out,
        "cost_usd": round(state.cost_usd, 6),
    }
    if decision == "escalate":
        record["escalate_to"] = escalate_to or "human claims assessor"
        if trigger:
            record["trigger"] = trigger

    append_decision(record, path=path)
    return f"recorded: {decision} on {claim_id}"


def make_issue_decision_tool(state: GuardrailState, path: str = DECISIONS_PATH):
    """
    Bind a GuardrailState into a plain tool callable for TOOLS registries.

    evidence may be passed as a list or as a JSON/list-looking string from the
    model's Action line.
    """
    def issue_decision_letter_tool(
        claim_id: str,
        decision: str,
        reason: str,
        evidence: Any = None,
        escalate_to: str = "",
        trigger: str = "",
    ) -> str:
        if isinstance(evidence, str):
            try:
                evidence = json.loads(evidence)
            except json.JSONDecodeError:
                evidence = [evidence] if evidence else []
        elif evidence is None:
            evidence = []

        # Dedup applies to the gated action too.
        kwargs = {
            "claim_id": claim_id,
            "decision": decision,
            "reason": reason,
        }
        blocked = state.check_dedup("issue_decision_letter", kwargs)
        if blocked:
            return blocked

        result = issue_decision_letter(
            claim_id=claim_id,
            decision=decision,
            reason=reason,
            evidence=evidence,
            state=state,
            escalate_to=escalate_to or None,
            trigger=trigger or None,
            path=path,
        )
        if not result.startswith("BLOCKED"):
            state.record_call("issue_decision_letter", kwargs)
        return result

    issue_decision_letter_tool.__name__ = "issue_decision_letter"
    return issue_decision_letter_tool
