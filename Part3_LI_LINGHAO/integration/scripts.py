"""One interface smoke fixture, not the completed D5(a) script library.
No answer-key file is read. The moves are explicitly authored for CLM-8925.
"""
import json

LIMIT_DECISION = {
    "decision": "escalate",
    "trigger": "annual_limit_exceeded",
    "escalate_to": "human claims assessor",
    "reason": "Claim total SGD 11400 exceeds SGD 9200 remaining on POL-3310.",
    "evidence": ["get_claim", "check_duplicate", "lookup_member", "lookup_policy"],
}


def action(name, **kwargs):
    return "Action: " + name + "(" + ", ".join(f"{k}={v!r}" for k, v in kwargs.items()) + ")"


def script_for(case_id):
    if case_id != "CLM-8925":
        raise ValueError(f"No Step 1 script for {case_id}; only CLM-8925 is bundled")
    return [
        action("get_claim", claim_id=case_id),
        action("check_duplicate", claim_id=case_id) + "\n" + action("lookup_member", member_id="M-2214"),
        action("lookup_policy", policy_id="POL-3310", date_of_service="2026-09-12", claim_total=11400),
        action("issue_decision_letter", claim_id=case_id, **LIMIT_DECISION),
        "Final: " + json.dumps(LIMIT_DECISION),
    ]
