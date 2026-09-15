#!/usr/bin/env python3
"""Budgeted, resumable official battery. All outputs are actual model responses."""
import concurrent.futures
import hashlib,json,sys,tempfile,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from claim_agent.agent import run_case
from claim_agent.backends import LiveBackend
from claim_agent.harness import trial_manifest,grade,summarize
ROOT=Path(__file__).resolve().parents[1]
MODELS=['google/gemini-2.5-flash-lite','openai/gpt-4o-mini','meta-llama/llama-3.3-70b-instruct','qwen/qwen3-30b-a3b-instruct-2507','anthropic/claude-haiku-4.5']

def fingerprint():
    paths=sorted(list((ROOT/'claim_agent').glob('*.py'))+list((ROOT/'A2_reference_data/data_A').glob('*.json'))+list((ROOT/'A2_reference_data').glob('expected*.json')))
    return hashlib.sha256(b''.join(p.relative_to(ROOT).as_posix().encode()+p.read_bytes() for p in paths)).hexdigest()

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--workers',type=int,default=4); args=parser.parse_args()
    catalog={m['id']:m for m in json.loads((ROOT/'results/model_catalog.json').read_text())}
    balance=json.loads((ROOT/'results/account_budget.json').read_text())['limit_remaining']
    cap=min(10,balance); outdir=ROOT/'results'/('pilot' if args.pilot else 'live');outdir.mkdir(parents=True,exist_ok=True)
    manifest={'code_data_sha256':fingerprint(),'models':MODELS,'trials_per_configuration':64,'configurations':6,'shared_key':True,'cap_usd':cap,'date':time.strftime('%Y-%m-%d'),'operator':'simulated evaluation approval; not a human decision','prices':{m:catalog[m]['pricing'] for m in MODELS},'temperature':0,'max_output_tokens':2200}
    manifest_path=outdir/'manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text())['code_data_sha256']!=manifest['code_data_sha256']:
        raise SystemExit('Frozen source changed; archive prior experiment before starting a new version.')
    manifest_path.write_text(json.dumps(manifest,indent=2))
    configs=[(m,'v2') for m in MODELS]+[(MODELS[0],'v1')]
    jobs=[]
    for model,variant in configs:
        for expected,trial in trial_manifest():
            if args.pilot and (expected['case_id'] not in ['CLM-8842','CLM-8894','CLM-8952'] or trial!=1):continue
            name=model.replace('/','__')+'_'+variant+'_'+expected['case_id']+'_'+str(trial)+'.json'
            if not (outdir/name).exists():jobs.append((model,variant,expected,trial,outdir/name))
    lock=threading.Lock()
    # Include already written pilot and official API charges, never reset when resuming.
    def spent():
        return sum(json.loads(p.read_text()).get('cost_usd',0) for folder in [ROOT/'results/live',ROOT/'results/pilot',ROOT/'results/pilot_initial'] if folder.exists() for p in folder.glob('*.json') if p.name not in ['manifest.json','summary.json'])
    current=spent(); reserved=0.
    def run(job):
        nonlocal current,reserved
        model,variant,expected,trial,path=job
        allowance=.18
        with lock:
            if current+reserved+allowance>cap: return 'budget exhausted'
            reserved+=allowance
        prices=catalog[model]['pricing']
        backend=LiveBackend(model,float(prices['prompt']),float(prices['completion']))
        with tempfile.TemporaryDirectory() as temp:
            r=run_case(expected['case_id'],backend=backend,variant=variant,approval=lambda payload:True,ledger=Path(temp)/'ledger.jsonl',budget_usd=.14,max_turns=10)
        r.update(model=model,trial=trial,negative=expected['negative'],grade=grade(r,expected),source_hash=manifest['code_data_sha256'],operator='simulated')
        path.write_text(json.dumps(r,indent=2))
        with lock:current+=r['cost_usd'];reserved-=allowance
        return f"{model} {variant} {expected['case_id']} #{trial}: {'PASS' if r['grade']['pass'] else r['stop']+' '+str(r['grade']['errors'])} ${r['cost_usd']:.5f}"
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for s in pool.map(run,jobs):print(s,flush=True)
    summaries=[]
    for model,variant in configs:
        rows=[json.loads(p.read_text()) for p in outdir.glob(model.replace('/','__')+'_'+variant+'_*.json')]
        summaries.append({'model':model,'variant':variant,**summarize(rows)})
    (outdir/'summary.json').write_text(json.dumps(summaries,indent=2));print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
