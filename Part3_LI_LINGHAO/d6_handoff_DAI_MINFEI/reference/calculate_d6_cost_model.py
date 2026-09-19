#!/usr/bin/env python3
"""Recompute the D6 three-layer cost tables from the frozen handoff inputs.

This script uses no network and no API key. It deliberately keeps execution
failures in the 75-trial denominator and treats Layer 3 as an owner-approved
scenario assumption rather than measured production spend.
"""
from pathlib import Path
import csv, json

HERE = Path(__file__).resolve().parent
inputs = json.loads((HERE / "D5_COST_INPUTS.json").read_text())
prices = {r["member"]: r for r in csv.DictReader((HERE / "MODEL_ASSIGNMENT.csv").open(encoding="utf-8-sig"))}
volume = inputs["volume_per_month"]
failure_usd = inputs["failure_handling"]["failure_cost_usd"]
layer3_base = 200.0
layer3_scenarios = (0.0, 100.0, 200.0, 500.0, 1000.0)

rows = []
for m in inputs["models"]:
    p = prices[m["member"]]
    l1 = ((m["tokens_in"]["total"] / m["trials"]) * float(p["price_in"])
          + (m["tokens_out"]["total"] / m["trials"]) * float(p["price_out"])) / 1_000_000
    success = m["overall_passed"] / m["trials"]
    l2 = (1 - success) * failure_usd
    rows.append({"member": m["member"], "model": m["model"], "prompt_version": m["prompt_version"],
                 "trials": m["trials"], "tokens_in_total": m["tokens_in"]["total"],
                 "tokens_out_total": m["tokens_out"]["total"],
                 "avg_input_tokens": m["tokens_in"]["total"] / m["trials"],
                 "avg_output_tokens": m["tokens_out"]["total"] / m["trials"],
                 "price_in_usd_per_1m": float(p["price_in"]), "price_out_usd_per_1m": float(p["price_out"]),
                 "layer1_variable_usd_per_task": l1, "overall_passes": m["overall_passed"],
                 "success_rate": success, "execution_errors": m["execution_errors"],
                 "layer2_fallback_usd_per_task": l2,
                 "variable_plus_fallback_usd_per_task": l1 + l2,
                 "layer3_base_usd_per_month": layer3_base,
                 "layer3_allocation_usd_per_task": layer3_base / volume,
                 "monthly_total_base_usd": (l1 + l2) * volume + layer3_base,
                 "agent_measured_cost_usd": m["agent_cost_usd"]["total"],
                 "judge_measured_cost_usd": m["judge_cost_usd"],
                 "measured_d5_api_cost_usd": m["agent_cost_usd"]["total"] + m["judge_cost_usd"]})

q = next(r for r in rows if r["member"] == "LU_XINZE")
d = next(r for r in rows if r["member"] == "DAI_MINFEI")
break_even = max(0.0, min(1.0, 1 - (d["variable_plus_fallback_usd_per_task"] - q["layer1_variable_usd_per_task"]) / failure_usd))
print(f"Layer 3 base: ${layer3_base:.2f}/month; allocation: ${layer3_base/volume:.5f}/claim")
for r in rows:
    print(f"{r['member']}: success={r['success_rate']:.1%}, L1=${r['layer1_variable_usd_per_task']:.6f}, "
          f"L2=${r['layer2_fallback_usd_per_task']:.6f}, monthly=${r['monthly_total_base_usd']:,.2f}")
print(f"Qwen-versus-Claude break-even success rate: {break_even:.1%}")
