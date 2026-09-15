#!/usr/bin/env python3
"""Read-only evidence consistency checks for the assembled submission."""
import hashlib,json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from claim_agent.harness import trial_manifest,grade,summarize
from scripts.run_live import fingerprint
errors=[]
manifest=json.loads((ROOT/'results/live/manifest.json').read_text())
if fingerprint()!=manifest['code_data_sha256']:errors.append('source/data fingerprint differs from live experiment')
rows=[json.loads(p.read_text()) for p in (ROOT/'results/live').glob('*CLM*.json')]
if len(rows)!=384:errors.append(f'expected 384 official trials; got {len(rows)}')
key={e['case_id']:e for e,t in trial_manifest()}
for r in rows:
 if grade(r,key[r['case_id']])!=r['grade']:errors.append('stale grade '+r['case_id'])
 if r.get('source_hash')!=manifest['code_data_sha256']:errors.append('mixed source hash')
 if r['backend']!='live' or r['token_measurement']!='api_usage':errors.append('mislabelled backend')
 actual_i=sum(t.get('usage',{}).get('input',0) for t in r['trace']);actual_o=sum(t.get('usage',{}).get('output',0) for t in r['trace'])
 if (actual_i,actual_o)!=(r['tokens_in'],r['tokens_out']):errors.append('token mismatch')
for model in manifest['models']:
 for variant in (['v1','v2'] if model==manifest['models'][0] else ['v2']):
  subset=[r for r in rows if r['model']==model and r['variant']==variant]
  if {(r['case_id'],r['trial']) for r in subset}!={(e['case_id'],t) for e,t in trial_manifest()}:errors.append('manifest trials mismatch '+model+variant)
judged=list((ROOT/'results/judgement').glob('*.json'))
if len(judged)!=84:errors.append(f'expected 84 designated judgement records (72 live + 12 scripted); got {len(judged)}')
for p in judged:
    j=json.loads(p.read_text())
    if j['status'] not in ['judged','code_failed_not_judged']:errors.append('pending judgement '+p.name)
for p in ROOT.rglob('*'):
 if p.is_file() and p.suffix in ['.py','.json','.md','.txt'] and '.git' not in p.parts:
  b=p.read_bytes()
  if re.search(rb'sk-or-' + rb'v1-[0-9a-f]{64}', b): errors.append('credential-like content in '+str(p.relative_to(ROOT)))
print(json.dumps({'verified_trials':len(rows),'errors':errors},indent=2))
raise SystemExit(bool(errors))
