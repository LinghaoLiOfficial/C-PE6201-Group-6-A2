#!/usr/bin/env python3
"""Read-only account reconciliation; never print credentials or account identity."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from claim_agent.backends import credential,BASE_URL
rows=[]
for directory in (ROOT/'results').iterdir():
    if directory.is_dir() and directory.name.startswith(('live','pilot','judgement')):
        cost=sum(json.loads(p.read_text()).get('cost_usd',0) for p in directory.glob('*.json') if p.name not in ['manifest.json','summary.json'])
        rows.append({'experiment':directory.name,'returned_cost_usd':cost})
req=urllib.request.Request(BASE_URL+'/key',headers={'Authorization':'Bearer '+credential()})
x=json.load(urllib.request.urlopen(req,timeout=30))['data']
start=json.loads((ROOT/'results/account_budget.json').read_text())
account_delta=x['usage']-start['usage'];reported=sum(r['returned_cost_usd'] for r in rows)
result={'starting_usage_usd':start['usage'],'ending_usage_usd':x['usage'],'account_delta_usd':account_delta,'remaining_usd':x['limit_remaining'],'returned_usage_total_usd':reported,'unreconciled_usd':account_delta-reported,'cap_usd':min(10,start['limit_remaining']),'experiments':rows,'note':'Account delta may include delayed charges or other use of the shared key; no unsupported attribution of any discrepancy. Failed requests may omit usage. All figures are USD.'}
(ROOT/'results/spend_reconciliation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if account_delta>result['cap_usd']+.000001:raise SystemExit('Budget exceeded')
