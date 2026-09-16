"""Offline trajectories used by the deterministic scripted backend.

All 45 fixed trajectories are committed in scripted_library.json. The constants
below remain for older contract tests and the three-case smoke runner. Runtime
loads only canned replies; it never loads labels, case audits or fixture tables.
"""
import json
from copy import deepcopy

LIMIT_DECISION = {
    "decision": "escalate", "trigger": "annual_limit_exceeded",
    "escalate_to": "human claims assessor",
    "reason": "Claim total SGD 11400 exceeds SGD 9200 remaining on POL-3310.",
    "evidence": ["get_claim", "check_duplicate", "lookup_member", "lookup_policy"],
}
APPROVAL_DECISION = {
    "decision": "approve_in_principle",
    "reason": "POL-3310 active and service date 2026-09-02 covered; H-114 on panel. "
              "Of 3 lines, 47120 and 62480 are payable; PA-5521 covers 2026-09-02. "
              "31255 is excluded by EX-14 cosmetic dermatology. Documents present, "
              "no duplicate; claim total 2480 is within 9200 remaining. "
              "Approved total 2180; refused total 300.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate",
                 "get_hospital_status", "check_procedure", "check_documents", "get_preauthorisation"],
    "lines": [
        {"code": "47120", "amount": 1400, "status": "covered"},
        {"code": "62480", "amount": 780, "status": "covered", "preauth": "PA-5521"},
        {"code": "31255", "amount": 300, "status": "not_covered", "exclusion": "EX-14 cosmetic dermatology"},
    ],
    "approved_total": 2180, "refused_total": 300,
}
REQUEST_DECISION = {
    "decision": "request_document",
    "reason": "POL-7220 active; service date covered, total 1950 within 6800 remaining; "
              "no duplicate, H-207 on panel and required documents attached. "
              "Line 29881 needs pre-authorisation. PA-5640 was found but its validity "
              "ended 2026-05-31, before service on 2026-09-09. "
              "An existing expired reference cannot authorise this claim.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate",
                 "get_hospital_status", "check_procedure", "check_documents", "get_preauthorisation"],
    "missing": {"item": "pre-authorisation reference", "for_line": "29881",
                "must_be_valid_on": "2026-09-09"},
    "lines": [{"code": "29881", "amount": 1950, "status": "pending_preauthorisation"}],
}
SCRIPTED_CASE_IDS = ("CLM-8842", "CLM-8894", "CLM-8925")
LI_CASE_IDS = ("CLM-16301", "CLM-16302", "CLM-16303", "CLM-16304", "CLM-16305")

LI_APPROVAL_START = {
    "decision": "approve_in_principle",
    "reason": "POL-6001 is active from 2026-06-01 through 2027-05-31 inclusive. "
              "The 99213 consultation is covered and the claim is within the "
              "remaining annual limit. Approved total 200; refused total 0.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate",
                 "get_hospital_status", "check_procedure", "check_documents"],
    "lines": [{"code": "99213", "amount": 200, "status": "covered"}],
    "approved_total": 200, "refused_total": 0,
}

LI_APPROVAL_END = {
    "decision": "approve_in_principle",
    "reason": "POL-6001 is active through 2027-05-31 inclusive. The service date "
              "equals that end date, 99213 is covered, and the claim is within "
              "the remaining annual limit. Approved total 250; refused total 0.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate",
                 "get_hospital_status", "check_procedure", "check_documents"],
    "lines": [{"code": "99213", "amount": 250, "status": "covered"}],
    "approved_total": 250, "refused_total": 0,
}

LI_APPROVAL_EXCLUDED = {
    "decision": "approve_in_principle",
    "reason": "POL-4102 is active and the service date is covered. Procedure 15823 "
              "is refused under the policy exclusion EX-14 cosmetic dermatology; "
              "the line is fully resolved rather than escalated. Approved total 0; "
              "refused total 180.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate",
                 "get_hospital_status", "check_procedure", "check_documents"],
    "lines": [{"code": "15823", "amount": 180, "status": "not_covered",
               "exclusion": "EX-14 cosmetic dermatology"}],
    "approved_total": 0, "refused_total": 180,
}

LI_APPROVAL_MIXED = {
    "decision": "approve_in_principle",
    "reason": "POL-3310 is active and the claim is within the remaining annual limit. "
              "Procedure 47120 is covered for 900. Procedure 31255 is refused under "
              "EX-14 cosmetic dermatology for 250. Both lines are resolved. Approved "
              "total 900; refused total 250.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate",
                 "get_hospital_status", "check_procedure", "check_documents"],
    "lines": [
        {"code": "47120", "amount": 900, "status": "covered"},
        {"code": "31255", "amount": 250, "status": "not_covered",
         "exclusion": "EX-14 cosmetic dermatology"},
    ],
    "approved_total": 900, "refused_total": 250,
}

LI_ESCALATION_DATE = {
    "decision": "escalate", "trigger": "outside_policy_dates",
    "escalate_to": "human claims assessor",
    "reason": "POL-6001 starts on 2026-06-01, but the service date is 2026-05-31, "
              "which is outside the inclusive policy dates.",
    "evidence": ["get_claim", "lookup_member", "lookup_policy", "check_duplicate"],
}


def action(name, **kwargs):
    return "Action: " + name + "(" + ", ".join(f"{k}={v!r}" for k, v in kwargs.items()) + ")"


def batch(*calls):
    return "\n".join(calls)


def finish(case_id, decision):
    return [action("issue_decision_letter", claim_id=case_id, **decision),
            "Final: " + json.dumps(decision)]


def script_for(case_id, version="v2"):
    """Replay committed canned replies only; never read fixtures or labels here."""
    from pathlib import Path
    if version not in {"v1", "v2"}:
        raise ValueError("version must be v1 or v2")
    library = json.loads(Path(__file__).with_name("scripted_library.json").read_text(encoding="utf-8"))
    try:
        return deepcopy(library["scripts"][version][case_id])
    except KeyError:
        raise ValueError(f"No scripted trajectory for {case_id}") from None
