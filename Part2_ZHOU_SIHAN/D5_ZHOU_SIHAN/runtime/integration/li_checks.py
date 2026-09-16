"""Independent code checks for LI LINGHAO's original five cases."""
import json
from pathlib import Path


def load_li_labels(root=None):
    base = Path(root or Path(__file__).resolve().parents[1])
    rows = json.loads((base / "case_request/cases_LI_LINGHAO/labels_LI_LINGHAO.json").read_text(encoding="utf-8"))
    return {row["case_id"]: row for row in rows}


def check_li_case(result, expected):
    failures = []
    def check(ok, msg):
        if not ok:
            failures.append(msg)
    check(result["status"] == "completed", f"execution status: {result['status']}")
    check(result["case_id"] == expected["case_id"], "wrong case_id")
    check(result["decision"] == expected["expected_decision"], "wrong decision")
    check(result["action_count"] == 1, "expected one actual decision write")
    record = result["action_records"][0] if result["action_records"] else {}
    for field in ("decision", "reason", "evidence", "trigger", "missing", "lines", "approved_total", "refused_total", "escalate_to"):
        check(record.get(field) == result.get(field), "log mismatch: " + field)
    successful = {row["tool"] for row in result["trace"] if row["status"] == "ok"}
    check(set(expected["must_record"]) != set(), "label must_record is empty")
    check({"get_claim", "lookup_member", "lookup_policy", "check_duplicate", "issue_decision_letter"} <= successful,
          "required core evidence calls missing")
    cid = expected["case_id"]
    if cid in {"CLM-16301", "CLM-16302"}:
        amount = expected["approved_total"]
        check(result["approved_total"] == amount and result["refused_total"] == 0, "wrong totals")
        line = (result.get("lines") or [{}])[0]
        check(line.get("code") == "99213" and line.get("amount") == amount and line.get("status") == "covered", "consultation disposition is wrong")
        check("check_procedure" in successful and "check_documents" in successful, "missing procedure/document evidence")
    elif cid == "CLM-16303":
        line = (result.get("lines") or [{}])[0]
        check(result["approved_total"] == expected["approved_total"] and result["refused_total"] == expected["refused_total"], "wrong exclusion totals")
        check(line.get("status") == "not_covered" and line.get("exclusion") == "EX-14 cosmetic dermatology", "missing EX-14 line evidence")
    elif cid == "CLM-16304":
        got = {x.get("code"): x for x in result.get("lines") or []}
        check(result["approved_total"] == expected["approved_total"] and result["refused_total"] == expected["refused_total"], "wrong mixed totals")
        check(got.get("47120", {}).get("amount") == 900 and got.get("47120", {}).get("status") == "covered", "47120 disposition missing")
        check(got.get("31255", {}).get("amount") == 250 and got.get("31255", {}).get("status") == "not_covered" and got.get("31255", {}).get("exclusion") == "EX-14 cosmetic dermatology", "31255 disposition missing")
    elif cid == "CLM-16305":
        check(result.get("trigger") == "outside_policy_dates", "wrong escalation trigger")
        check(result.get("escalate_to") == "human claims assessor", "wrong escalation recipient")
    return {"code_passed": not failures, "failures": failures,
            "check_type": "code", "judgement_status": "pending",
            "judgement_requirements": expected.get("must_record", [])}
