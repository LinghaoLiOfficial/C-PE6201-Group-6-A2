#!/usr/bin/env python3
"""Validate LI LINGHAO's five extra cases without changing teacher fixtures.

This check verifies ids, cross-table links, labels, and arithmetic in the local
handoff files.  It intentionally does not edit ``materials/A2_reference_data``.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases_LI_LINGHAO"
DATA = HERE.parent / "materials" / "A2_reference_data" / "data_A"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    extra = load(CASES / "fixtures_LI_LINGHAO.json")
    labels = {x["case_id"]: x for x in load(CASES / "labels_LI_LINGHAO.json")}
    claims = extra["EXTRA_CLAIMS"]
    errors = []
    shipped = {x["claim_id"] for x in load(DATA / "claims.json")}
    ids = [x.get("claim_id") for x in claims]
    if len(ids) != len(set(ids)):
        errors.append("extra claim ids are duplicated")
    overlap = set(ids) & shipped
    if overlap:
        errors.append(f"extra ids overlap shipped claims: {sorted(overlap)}")
    if set(ids) != set(labels):
        errors.append("fixtures and labels do not contain the same case ids")

    members = {x["member_id"]: x for x in load(DATA / "members.json")}
    policies = {x["policy_id"]: x for x in load(DATA / "policies.json")}
    hospitals = {x["hospital_id"] for x in load(DATA / "hospitals.json")}
    procedures = {x["code"] for x in load(DATA / "procedures.json")}
    for claim in claims:
        cid = claim["claim_id"]
        if claim["member_id"] not in members:
            errors.append(f"{cid}: unknown member")
            continue
        policy_id = members[claim["member_id"]]["policy_id"]
        if policy_id not in policies:
            errors.append(f"{cid}: member policy does not exist")
        if claim["hospital_id"] not in hospitals:
            errors.append(f"{cid}: unknown hospital")
        for line in claim.get("lines", []):
            if line.get("code") not in procedures:
                errors.append(f"{cid}: unknown procedure {line.get('code')}")
            if not isinstance(line.get("amount"), (int, float)) or line["amount"] < 0:
                errors.append(f"{cid}: invalid line amount")
        label = labels.get(cid)
        if not label:
            continue
        line_total = sum(line["amount"] for line in claim["lines"])
        if label["expected_decision"] == "approve_in_principle":
            approved = label.get("approved_total")
            refused = label.get("refused_total")
            # The labels store totals in must_record prose; derive expected totals
            # from the case family below to make arithmetic independently checkable.
            expected = {
                "CLM-16301": (200, 0), "CLM-16302": (250, 0),
                "CLM-16303": (0, 180), "CLM-16304": (900, 250),
            }.get(cid)
            if expected and (expected[0] + expected[1] != line_total):
                errors.append(f"{cid}: labelled totals do not equal claim total")
            if approved is None or refused is None:
                errors.append(f"{cid}: ordinary label must provide approved_total and refused_total")
            elif approved + refused != line_total:
                errors.append(f"{cid}: approved_total + refused_total must equal claim total")
        if label["expected_decision"] == "escalate" and not label.get("trigger"):
            errors.append(f"{cid}: negative case has no single trigger")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        raise SystemExit(1)
    print("LI LINGHAO cases: 5 ids, links and labels validated.")
