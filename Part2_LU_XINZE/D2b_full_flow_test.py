"""Scripted end-to-end smoke test for the Part2 D2(b) integration.

The test replaces only the model response function. The actual ReAct loop parses
Actions, calls the real Part2 tool registry against fixture data, appends real
Observations, switches the v1/v2 descriptor, and returns a Final decision.
No API key or network call is used.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _steps(version: str, claim_id: str) -> list[str]:
    if claim_id == "CLM-8842":
        member_id, policy_id, code, service_date, claim_total, decision = (
            "M-2214", "POL-3310", "62480", "2026-09-02", 2480, "approve_in_principle"
        )
    elif claim_id == "CLM-8894":
        member_id, policy_id, code, service_date, claim_total, decision = (
            "M-6118", "POL-7220", "29881", "2026-09-09", 1950, "request_document"
        )
    elif claim_id == "CLM-8925":
        member_id, policy_id, code, service_date, claim_total, decision = (
            "M-2214", "POL-3310", "27447", "2026-09-12", 11400, "escalate"
        )
    else:
        raise ValueError(f"Unsupported smoke-test claim: {claim_id}")

    preauth_action = (
        f'Action: get_preauthorisation(member_id="{member_id}", procedure_code="{code}")'
        if version == "v1"
        else f'Action: get_preauthorisation(member_id="{member_id}", procedure_code="{code}", date_of_service="{service_date}")'
    )
    common_steps = [
        f"Thought: Read the claim first.\nAction: get_claim(claim_id=\"{claim_id}\")",
        f"Thought: Resolve the member policy.\nAction: lookup_member(member_id=\"{member_id}\")",
        f"Thought: Check policy date and annual-limit status.\nAction: lookup_policy(policy_id=\"{policy_id}\", date_of_service=\"{service_date}\", claim_total={claim_total})",
    ]
    if claim_id == "CLM-8925":
        return common_steps + [
            "Thought: The annual limit is exceeded.\nFinal: escalate annual_limit_exceeded"
        ]
    return common_steps + [
        f"Thought: Check whether the procedure needs pre-authorisation.\nAction: check_procedure(code=\"{code}\")",
        f"Thought: Check the relevant pre-authorisation.\n{preauth_action}",
        f"Thought: The required evidence supports the decision.\nFinal: {decision}",
    ]


def run_case(version: str, claim_id: str) -> str:
    import D2b_integrated_agent as agent

    steps = iter(_steps(version, claim_id))
    original_call_model = agent.call_model

    def scripted_call_model(_prompt: str):
        try:
            return next(steps), {"prompt_tokens": 0, "completion_tokens": 0}
        except StopIteration as exc:
            raise AssertionError("Agent requested an unexpected extra model turn") from exc

    agent.call_model = scripted_call_model
    try:
        final, turns, transcript, _, _ = agent.run_agent(
            f"Process claim {claim_id} with D2(b) {version} pre-authorisation interface.",
            max_turns=10,
            parallel=False,
        )
    finally:
        agent.call_model = original_call_model

    expected = {
        "CLM-8842": "approve_in_principle",
        "CLM-8894": "request_document",
        "CLM-8925": "escalate",
    }[claim_id]
    assert final.startswith(expected), (claim_id, version, final)
    expected_turns = 4 if claim_id == "CLM-8925" else 6
    assert turns == expected_turns, (claim_id, version, turns)
    assert "annual_limit_status=" in transcript
    if claim_id != "CLM-8925":
        assert "get_preauthorisation" in transcript
    if version == "v2":
        expected_status = "status=valid" if claim_id == "CLM-8842" else "status=expired_before_service"
        assert expected_status in transcript, (claim_id, transcript)
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, help="Directory containing Problem A data_A JSON files")
    parser.add_argument("--version", choices=("v1", "v2"), required=True)
    args = parser.parse_args()
    os.environ["A2_DATA_DIR"] = str(Path(args.data_dir).resolve())
    os.environ["PREAUTH_VERSION"] = args.version
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    for case_id in ("CLM-8842", "CLM-8894", "CLM-8925"):
        final = run_case(args.version, case_id)
        print(f"PASS {args.version} {case_id}: {final.splitlines()[0]}")
