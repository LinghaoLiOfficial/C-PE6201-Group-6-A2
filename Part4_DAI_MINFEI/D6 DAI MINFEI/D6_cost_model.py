#!/usr/bin/env python3
"""Reproducible D6 cost-to-serve calculator for Problem A.

Success results are taken from D5_FINAL_REPORT.md / D5_EVIDENCE_MANIFEST.json.
Token and turn totals are measured D5 values; model prices are the frozen
MODEL_ASSIGNMENT.csv values checked on 2026-09-16.
"""

from __future__ import annotations

import csv
from pathlib import Path


# Write alongside the delivered calculator so the folder is self-contained.
OUT = Path(__file__).resolve().parent
VOLUME = 8_000
FAILURE_COST = 7.60
LAYER3_BASE = 200.00
LAYER3_SCENARIOS = (0, 100, 200, 500, 1_000)

MODELS = [
    dict(member="LI_LINGHAO", model="deepseek/deepseek-v3.2", prompt_version="v2", tier="cheap", price_in=0.269, price_out=0.4, trials=75, turns=383, tokens_in=959130, tokens_out=62138, agent_spend=0.28286117, preflight_spend=0.026086838, judge_spend=0.0820508, ordinary_trials=30, ordinary_code_passed=28, negative_trials=45, negative_code_passed=44, code_passed=72, execution_errors=3, reviewable=72, judge_pass=71, judge_fail=0, judge_uncertain=1, overall_passed=71),
    dict(member="ZHOU_SIHAN", model="deepseek/deepseek-v3.2", prompt_version="v1", tier="cheap", price_in=0.269, price_out=0.4, trials=75, turns=398, tokens_in=983574, tokens_out=67043, agent_spend=0.291398606, preflight_spend=0.02622079, judge_spend=0.0722228, ordinary_trials=30, ordinary_code_passed=25, negative_trials=45, negative_code_passed=39, code_passed=64, execution_errors=11, reviewable=64, judge_pass=64, judge_fail=0, judge_uncertain=0, overall_passed=64),
    dict(member="CHEN_MINGSONG", model="google/gemini-2.5-flash-lite", prompt_version="v2", tier="cheap", price_in=0.1, price_out=0.4, trials=75, turns=460, tokens_in=1231861, tokens_out=59791, agent_spend=0.1471025, preflight_spend=0.0133753, judge_spend=0.0047568, ordinary_trials=30, ordinary_code_passed=0, negative_trials=45, negative_code_passed=3, code_passed=3, execution_errors=70, reviewable=5, judge_pass=5, judge_fail=0, judge_uncertain=0, overall_passed=3),
    dict(member="LU_XINZE", model="qwen/qwen3-235b-a22b-2507", prompt_version="v2", tier="cheap", price_in=0.0875, price_out=0.35, trials=75, turns=260, tokens_in=613991, tokens_out=54714, agent_spend=0.0728741125, preflight_spend=0.0058051, judge_spend=0.014962, ordinary_trials=30, ordinary_code_passed=6, negative_trials=45, negative_code_passed=5, code_passed=11, execution_errors=61, reviewable=14, judge_pass=14, judge_fail=0, judge_uncertain=0, overall_passed=11),
    dict(member="WANG_YI", model="mistralai/mistral-small-3.2-24b-instruct", prompt_version="v2", tier="cheap", price_in=0.09375, price_out=0.25, trials=75, turns=320, tokens_in=800977, tokens_out=46126, agent_spend=0.08662309375, preflight_spend=0.007353875, judge_spend=0.0305852, ordinary_trials=30, ordinary_code_passed=17, negative_trials=45, negative_code_passed=8, code_passed=25, execution_errors=48, reviewable=27, judge_pass=24, judge_fail=3, judge_uncertain=0, overall_passed=23),
    dict(member="DAI_MINFEI", model="anthropic/claude-haiku-4.5", prompt_version="v2", tier="mid", price_in=1.0, price_out=5.0, trials=75, turns=342, tokens_in=949938, tokens_out=81259, agent_spend=1.356233, preflight_spend=0.103667, judge_spend=0.0386664, ordinary_trials=30, ordinary_code_passed=16, negative_trials=45, negative_code_passed=12, code_passed=28, execution_errors=44, reviewable=31, judge_pass=31, judge_fail=0, judge_uncertain=0, overall_passed=28),
]


def calculate(row: dict) -> dict:
    row = row.copy()
    row["success_rate"] = row["overall_passed"] / row["trials"]
    row["avg_turns"] = row["turns"] / row["trials"]
    row["avg_input_tokens"] = row["tokens_in"] / row["trials"]
    row["avg_output_tokens"] = row["tokens_out"] / row["trials"]
    row["layer1_variable_cost_per_task"] = (
        row["avg_input_tokens"] * row["price_in"]
        + row["avg_output_tokens"] * row["price_out"]
    ) / 1_000_000
    row["layer2_expected_fallback_per_task"] = (1 - row["success_rate"]) * FAILURE_COST
    row["all_in_per_task_before_layer3"] = row["layer1_variable_cost_per_task"] + row["layer2_expected_fallback_per_task"]
    row["monthly_cost_before_layer3"] = row["all_in_per_task_before_layer3"] * VOLUME
    row["layer3_base_monthly_usd"] = LAYER3_BASE
    row["layer3_base_per_task"] = LAYER3_BASE / VOLUME
    row["all_in_per_task_with_layer3_base"] = row["all_in_per_task_before_layer3"] + row["layer3_base_per_task"]
    row["monthly_total_with_layer3_base"] = row["monthly_cost_before_layer3"] + LAYER3_BASE
    row["evaluation_spend_total"] = row["preflight_spend"] + row["agent_spend"] + row["judge_spend"]
    row["layer1_crosscheck_difference"] = row["layer1_variable_cost_per_task"] * row["trials"] - row["agent_spend"]
    return row


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [calculate(x) for x in MODELS]

    input_fields = [
        "member", "model", "prompt_version", "tier", "price_in", "price_out",
        "trials", "turns", "tokens_in", "tokens_out", "agent_spend",
        "preflight_spend", "judge_spend", "ordinary_trials", "ordinary_code_passed",
        "negative_trials", "negative_code_passed", "code_passed", "execution_errors",
        "reviewable", "judge_pass", "judge_fail", "judge_uncertain", "overall_passed",
    ]
    write_csv(OUT / "D6_AUTHORITATIVE_INPUTS.csv", rows, input_fields)

    ledger_fields = input_fields + [
        "success_rate", "avg_turns", "avg_input_tokens", "avg_output_tokens",
        "layer1_variable_cost_per_task", "layer2_expected_fallback_per_task",
        "all_in_per_task_before_layer3", "monthly_cost_before_layer3",
        "layer3_base_monthly_usd", "layer3_base_per_task",
        "all_in_per_task_with_layer3_base", "monthly_total_with_layer3_base",
        "evaluation_spend_total", "layer1_crosscheck_difference",
    ]
    write_csv(OUT / "D6_COST_LEDGER.csv", rows, ledger_fields)

    sensitivity = []
    for row in rows:
        for delta_pp in (-10, -5, 0, 5, 10):
            rate = min(1.0, max(0.0, row["success_rate"] + delta_pp / 100))
            fallback = (1 - rate) * FAILURE_COST
            per_task = row["layer1_variable_cost_per_task"] + fallback
            sensitivity.append({
                "sensitivity_type": "success_rate",
                "member": row["member"],
                "model": row["model"],
                "prompt_version": row["prompt_version"],
                "scenario": f"{delta_pp:+d} pp",
                "success_rate": rate,
                "failure_cost_usd": FAILURE_COST,
                "volume_per_month": VOLUME,
                "layer3_fixed_monthly_usd": LAYER3_BASE,
                "all_in_per_task_usd": per_task + LAYER3_BASE / VOLUME,
                "monthly_total_usd": per_task * VOLUME + LAYER3_BASE,
                "note": "Success rate clipped to [0%, 100%]. Includes owner-approved $200/month Layer 3 scenario assumption.",
            })

    best = rows[0]
    for row in rows:
        for fixed in LAYER3_SCENARIOS:
            sensitivity.append({
                "sensitivity_type": "layer3_scenario",
                "member": row["member"], "model": row["model"], "prompt_version": row["prompt_version"],
                "scenario": f"Layer 3 = ${fixed}/month", "success_rate": row["success_rate"],
                "failure_cost_usd": FAILURE_COST, "volume_per_month": VOLUME,
                "layer3_fixed_monthly_usd": fixed,
                "all_in_per_task_usd": row["all_in_per_task_before_layer3"] + fixed / VOLUME,
                "monthly_total_usd": row["monthly_cost_before_layer3"] + fixed,
                "note": "Planning scenario, not measured production spend. $200/month is the owner-approved base.",
            })
    for volume in (4_000, 8_000, 16_000):
        sensitivity.append({
            "sensitivity_type": "volume_scenario",
            "member": best["member"], "model": best["model"], "prompt_version": best["prompt_version"],
            "scenario": f"{volume:,} claims/month", "success_rate": best["success_rate"],
            "failure_cost_usd": FAILURE_COST, "volume_per_month": volume,
            "layer3_fixed_monthly_usd": LAYER3_BASE,
            "all_in_per_task_usd": best["all_in_per_task_before_layer3"] + LAYER3_BASE / volume,
            "monthly_total_usd": best["all_in_per_task_before_layer3"] * volume + LAYER3_BASE,
            "note": "Variable/fallback cost scales with volume; includes fixed $200/month Layer 3 base scenario.",
        })

    fields = ["sensitivity_type", "member", "model", "prompt_version", "scenario", "success_rate", "failure_cost_usd", "volume_per_month", "layer3_fixed_monthly_usd", "all_in_per_task_usd", "monthly_total_usd", "note"]
    write_csv(OUT / "D6_SENSITIVITY.csv", sensitivity, fields)

    expensive = rows[-1]
    cheapest_token = next(r for r in rows if r["member"] == "LU_XINZE")
    break_even = 1 - (expensive["all_in_per_task_before_layer3"] - cheapest_token["layer1_variable_cost_per_task"]) / FAILURE_COST
    print(f"Recommendation: {best['model']} {best['prompt_version']}")
    print(f"Cost/task before Layer 3: ${best['all_in_per_task_before_layer3']:.9f}")
    print(f"Monthly before Layer 3: ${best['monthly_cost_before_layer3']:.2f}")
    print(f"Monthly with Layer 3 base: ${best['monthly_total_with_layer3_base']:.2f}")
    print(f"Qwen cheap-model break-even success vs Claude: {break_even:.6%}")


if __name__ == "__main__":
    main()
