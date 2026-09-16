"""Zhou's gate/check/append design, extended to preserve the grading fields."""
import json
from datetime import datetime, timezone
from .protocol import validate_decision


def make_issue_decision_tool(state, path, case_id, trace):
    def issue_decision_letter(claim_id, decision, reason, evidence, trigger=None,
                              missing=None, lines=None, approved_total=None,
                              refused_total=None, escalate_to=None):
        if claim_id != case_id:
            return "BLOCKED: claim_id does not match this run"
        if state.autonomy == "suggest":
            return "BLOCKED: autonomy=suggest"
        if state.autonomy == "confirm" and not state.is_approved(claim_id):
            return "BLOCKED: awaiting operator confirmation"
        if state.check_budget():
            return "BLOCKED: budget ceiling"
        if path.exists() and path.read_text(encoding="utf-8").strip():
            return "BLOCKED: duplicate decision in this run"
        record = validate_decision(dict(decision=decision, reason=reason,
            evidence=evidence, trigger=trigger, missing=missing, lines=lines,
            approved_total=approved_total, refused_total=refused_total,
            escalate_to=escalate_to))
        observed = {row["tool"] for row in trace if row["status"] == "ok"}
        if any(name not in observed for name in evidence):
            return "BLOCKED: evidence cites a tool without a successful observation"
        record.update(case_id=case_id, ts=datetime.now(timezone.utc).isoformat(),
            autonomy=state.autonomy,
            gate="operator approved" if state.autonomy == "confirm" else "autonomy=act",
            turns=state.turn, tokens_in=state.tokens_in, tokens_out=state.tokens_out,
            cost_usd=state.cost_usd)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        state.record_call("issue_decision_letter", {"claim_id": claim_id})
        return f"recorded: {decision} on {claim_id}"
    return issue_decision_letter
