#!/usr/bin/env python3
"""Reproduce the complete offline battery; live is an explicit separate command."""
import argparse,json,tempfile
from pathlib import Path
from claim_agent.agent import run_case
from claim_agent.harness import trial_manifest,grade,summarize

def main():
    p=argparse.ArgumentParser(); p.add_argument('case_id',nargs='?');p.add_argument('--sequential',action='store_true');p.add_argument('--variant',choices=['v1','v2'],default='v2');p.add_argument('--output',default='results/scripted.json');p.add_argument('--demo',action='store_true')
    args=p.parse_args(); rows=[]
    with tempfile.TemporaryDirectory() as d:
        for expected,trial in trial_manifest():
            if args.case_id and expected['case_id']!=args.case_id: continue
            r=run_case(expected['case_id'],sequential=args.sequential,variant=args.variant,approval=lambda payload:True,ledger=Path(d)/f"{expected['case_id']}-{trial}.jsonl")
            r.update(trial=trial,negative=expected['negative'],grade=grade(r,expected),operator='simulated evaluation operator')
            rows.append(r)
    out={'configuration':{'backend':'scripted','variant':args.variant,'sequential':args.sequential,'approval':'simulated'},'summary':summarize(rows),'runs':rows}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2))
    print(json.dumps(out['summary'],indent=2))
    for r in rows:
        if not r['grade']['pass']: print(r['case_id'],r['grade']['errors'],r['trace'][-1].get('error'))
    if args.demo:
        for r in rows[:1]: print(json.dumps(r,indent=2))
    return 0 if rows and all(r['grade']['pass'] for r in rows) else 1
if __name__=='__main__': raise SystemExit(main())
