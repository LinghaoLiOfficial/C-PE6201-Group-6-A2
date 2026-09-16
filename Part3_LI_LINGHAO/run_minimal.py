#!/usr/bin/env python3
"""Run three outcomes offline: 1 ACT trial + 3 ASK trials + 3 ESCALATE trials.
Operator confirmation is explicitly simulated by this demo runner. No live mode.
"""
import argparse
import csv
import json
import tempfile
from pathlib import Path
from integration import run_case
from integration import config
from integration.scripts import SCRIPTED_CASE_IDS
from integration.minimal_checks import load_key, check_minimal


def run_minimal(version='v2', output_dir=None):
    parent = Path(output_dir or config.ROOT / 'output' / 'minimal').resolve()
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='suite-', dir=parent))
    key = load_key()
    results = []
    for cid in SCRIPTED_CASE_IDS:
        expected = key[cid]
        negative = expected['expected_decision'] != 'approve_in_principle'
        for trial in range(1, (3 if negative else 1) + 1):
            record = run_case(cid, backend='scripted', prompt_version=version,
                              output_dir=folder, operator_approved=True)
            results.append({'case_id':cid, 'trial':trial, 'negative':negative,
                            **check_minimal(record, expected), 'record':record})
    summary = {
        'scope':'minimal_three_outcome_code_checks_only', 'backend':'scripted',
        'prompt_version':version, 'operator_confirmation':'simulated_by_demo_runner',
        'case_count':3, 'negative_case_count':2, 'trials':len(results),
        'code_passed':sum(r['code_passed'] for r in results),
        'negative_trials':sum(r['negative'] for r in results),
        'negative_code_passed':sum(r['negative'] and r['code_passed'] for r in results),
        'judgement_status':'pending; no prose-quality pass claimed',
        'api_cost_usd':0, 'token_source':'synthetic', 'output_dir':str(folder),
    }
    (folder/'results.json').write_text(json.dumps({'summary':summary,'results':results}, indent=2,
                                                ensure_ascii=False)+'\n',encoding='utf-8')
    with (folder/'results.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['case_id','trial','negative','decision','status','code_passed',
                                          'turns','action_count','judgement_status','failures'])
        writer.writeheader()
        for r in results:
            writer.writerow({**{k:r[k] for k in ['case_id','trial','negative','code_passed','judgement_status']},
                             **{k:r['record'][k] for k in ['decision','status','turns','action_count']},
                             'failures':'; '.join(r['failures'])})
    return summary, results


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', choices=['v1','v2'], default='v2')
    p.add_argument('--output-dir')
    args=p.parse_args()
    summary,_=run_minimal(args.version,args.output_dir)
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    raise SystemExit(0 if summary['code_passed']==summary['trials'] else 1)
