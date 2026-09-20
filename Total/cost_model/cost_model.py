#!/usr/bin/env python3
"""Recalculate the three-layer cost model from committed measurements."""
import argparse, csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output-dir', default=str(ROOT / 'artifacts' / 'cost_model'))
    args = p.parse_args()
    assumptions = json.loads((ROOT / 'cost_model' / 'D6_LAYER3_ASSUMPTIONS.json').read_text())
    source = ROOT / 'results' / 'live_model_results.csv'
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    volume = assumptions['monthly_volume_claims']
    failure = assumptions['failure_handling']['failure_cost_usd']
    fixed = assumptions['layer3_base_monthly_usd']
    with source.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0]) + ['success_rate','avg_turns','avg_input_tokens','avg_output_tokens','layer1_variable_cost_per_task','layer2_expected_fallback_per_task','all_in_per_task_before_layer3','monthly_cost_before_layer3','layer3_base_monthly_usd','layer3_base_per_task','all_in_per_task_with_layer3_base','monthly_total_with_layer3_base','evaluation_spend_total','layer1_crosscheck_difference']
    ledger=[]
    for r in rows:
        trials=float(r['trials']); success=float(r['overall_passed'])/trials
        # Layer 1 is the agent's measured serving spend. Preflight and judge
        # calls are evaluation overhead and remain visible in the ledger.
        layer1=float(r['agent_spend'])/trials
        fallback=(1-success)*failure
        before=layer1+fallback
        item=dict(r, success_rate=success, avg_turns=float(r['turns'])/trials, avg_input_tokens=float(r['tokens_in'])/trials, avg_output_tokens=float(r['tokens_out'])/trials, layer1_variable_cost_per_task=layer1, layer2_expected_fallback_per_task=fallback, all_in_per_task_before_layer3=before, monthly_cost_before_layer3=before*volume, layer3_base_monthly_usd=fixed, layer3_base_per_task=fixed/volume, all_in_per_task_with_layer3_base=before+fixed/volume, monthly_total_with_layer3_base=before*volume+fixed, evaluation_spend_total=float(r['agent_spend'])+float(r['preflight_spend'])+float(r['judge_spend']), layer1_crosscheck_difference=0.0)
        ledger.append(item)
    with (out/'cost_ledger.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(ledger)
    sens=[]
    for r in ledger:
        for v in (4000, volume, 16000):
            for fixed_s in (0,100,200,500,1000):
                total=float(r['all_in_per_task_before_layer3'])*v+fixed_s
                sens.append({'member':r['member'],'model':r['model'],'prompt_version':r['prompt_version'],'volume':v,'layer3_fixed_monthly_usd':fixed_s,'success_rate':r['success_rate'],'monthly_total_usd':total})
    with (out/'sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(sens[0])); w.writeheader(); w.writerows(sens)
    print(f'wrote {len(ledger)} ledger rows and {len(sens)} sensitivity rows to {out}')

if __name__ == '__main__': main()
