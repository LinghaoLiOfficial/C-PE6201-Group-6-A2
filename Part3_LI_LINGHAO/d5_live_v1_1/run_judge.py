#!/usr/bin/env python3
"""Judge only revision 1.1 suites; never apply new rubric to historical suites."""
import argparse,getpass,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'runtime'))
from integration.d4_harness import read
from integration.llm_judge import run_judge
from integration.output_contract import REVISION

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--suite',required=True,type=Path)
    p.add_argument('--max-calls',type=int,default=75)
    p.add_argument('--budget',type=float,default=0.50)
    p.add_argument('--price-in',type=float,default=0.40)
    p.add_argument('--price-out',type=float,default=1.60)
    a=p.parse_args()
    if read(a.suite/'metadata.json').get('contract_revision')!=REVISION:
        p.error('Requires a new d5-live-1.1 suite; historical runs cannot be regraded here')
    if a.max_calls and not os.environ.get('OPENROUTER_API_KEY'):
        os.environ['OPENROUTER_API_KEY']=getpass.getpass('OpenRouter key (hidden): ')
    s=run_judge(a.suite,model='openai/gpt-4.1-mini',price_in=a.price_in,price_out=a.price_out,budget=a.budget,max_calls=a.max_calls)
    print({k:s[k] for k in ['trials','code_passed','judgement_passed','judgement_failed','judgement_pending','judgement_not_reviewable','overall_passed','judge_calls_completed','judge_calls_error','judge_calls_pending','judge_cost_usd','suite']})
