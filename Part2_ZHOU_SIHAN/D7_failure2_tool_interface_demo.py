"""
A2 Problem A — D7 Failure 2: tool-interface failure (not loop-control).

Aligned with Part2 (Lu Xinze) v1→v2 pre-authorisation rewrite:
  v1 returns raw valid_from / valid_to — model must compare dates
  v2 returns status=valid|expired_before_service|not_found

Build as a DELETION from the working interface:
  working = v2 status contract
  broken  = delete the status field (fall back to v1 raw dates only)
  restore = put status back

A tiny scripted "agent policy" then shows the wrong behaviour v1 allows:
  "if a preauth_id exists, treat as valid" — which wrongly accepts an expired PA.

No API key.

Run:
  python D7_failure2_tool_interface_demo.py
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "D7_failure2_results.json")

# Fixture fragment matching Part2 smoke tests (CLM-8894 / M-6118 / 29881).
PA = {
    "preauth_id": "PA-5640",
    "member_id": "M-6118",
    "procedure_code": "29881",
    "valid_from": "2026-01-01",
    "valid_to": "2026-08-31",  # expired before service 2026-09-14
}
SERVICE_DATE = "2026-09-14"


def preauth_v1(member_id: str, procedure_code: str) -> str:
    """Broken interface (deletion of v2): raw dates only."""
    if (member_id, procedure_code) != (PA["member_id"], PA["procedure_code"]):
        return f"ERROR: no preauthorisation for {member_id} / {procedure_code}"
    return (
        f"preauth_id={PA['preauth_id']} "
        f"member_id={PA['member_id']} "
        f"procedure_code={PA['procedure_code']} "
        f"valid_from={PA['valid_from']} "
        f"valid_to={PA['valid_to']}"
    )


def preauth_v2(member_id: str, procedure_code: str, date_of_service: str) -> str:
    """Working interface: code decides validity."""
    if (member_id, procedure_code) != (PA["member_id"], PA["procedure_code"]):
        return "status=not_found valid_on_service_date=False"
    if PA["valid_from"] <= date_of_service <= PA["valid_to"]:
        return (
            f"status=valid valid_on_service_date=True "
            f"preauth_id={PA['preauth_id']}"
        )
    return "status=expired_before_service valid_on_service_date=False"


def naive_policy(observation: str) -> str:
    """
    Deliberately weak decision rule — stands in for a model that skims the
    observation. If a preauth_id appears, it assumes the auth applies.
    """
    if "status=expired_before_service" in observation or "status=not_found" in observation:
        return "request_document"
    if "status=valid" in observation:
        return "approve_in_principle"
    if "preauth_id=" in observation:
        return "approve_in_principle"  # THE BUG v1 permits
    return "request_document"


def run(version: str) -> dict:
    if version == "v1":
        obs = preauth_v1("M-6118", "29881")
    else:
        obs = preauth_v2("M-6118", "29881", SERVICE_DATE)
    decision = naive_policy(obs)
    correct = "request_document"  # expired before service
    return {
        "version": version,
        "observation": obs,
        "decision": decision,
        "correct": correct,
        "pass": decision == correct,
    }


def main() -> None:
    broken = run("v1")       # deletion of status contract
    working = run("v2")
    restored = run("v2")
    payload = {
        "failure": "tool-interface: expired pre-auth treated as valid",
        "deletion": "remove v2 status field / date_of_service check (fall back to v1)",
        "why_not_loop_or_prompt": (
            "A prompt saying 'check the dates carefully' still leaves the error "
            "possible; a loop cap does not change a wrong observation shape. "
            "Putting validity in the tool return makes the bad class impossible."
        ),
        "aligned_with": "Part2_LU_XINZE D2b v1/v2 get_preauthorisation",
        "broken": broken,
        "working": working,
        "restored": restored,
        "restore_matches_working": restored == working,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print("=" * 64)
    print("D7 Failure 2 — tool interface (preauth v1 deleted status)")
    print("=" * 64)
    print(f"BROKEN  v1: decision={broken['decision']}  pass={broken['pass']}")
    print(f"         obs={broken['observation']}")
    print(f"WORKING v2: decision={working['decision']}  pass={working['pass']}")
    print(f"         obs={working['observation']}")
    print(f"RESTORED matches working: {payload['restore_matches_working']}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
