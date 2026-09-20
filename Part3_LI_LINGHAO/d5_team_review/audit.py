"""Read-only submission audit; no API calls or modification of member evidence."""
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

PART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART / 'd5_live_v1_1/runtime'))
from integration.d4_harness import load_contract, code_check, summarize

def decode(b): return json.loads(b.decode('utf-8-sig'))
def digest(b): return hashlib.sha256(b).hexdigest()
labels, expected = load_contract()
wanted = {(x['case_id'], t) for x in labels for t in range(1, 2 if x['expected_decision'] == 'approve_in_principle' else 4)}
report = {'commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), 'members': {}}
runtime = PART / 'd5_live_v1_1/runtime/integration'
for member in ['LI_LINGHAO','CHEN_MINGSONG','ZHOU_SIHAN','LU_XINZE','WANG_YI','DAI_MINFEI']:
    folder = PART / f'd5_live_submissions/{member}/r1.1'
    if member == 'DAI_MINFEI': folder = PART.parent / f'Part4_DAI_MINFEI/d5_live_submissions/{member}/r1.1'
    findings = []
    d = {'path':str(folder.relative_to(PART.parent)), 'findings':findings}
    with ZipFile(PART / f'd5_live_v1_1/packets/D5_{member}.zip') as z:
        prefix = f'D5_{member}/'
        assignment = decode(z.read(prefix+'assignment.json'))
        manifest = decode(z.read(prefix+'package_manifest.json'))
        manifest_bytes = z.read(prefix+'package_manifest.json')
    def check(ok, message):
        if not ok: findings.append(message)
    check(decode((folder/'assignment.json').read_bytes()) == assignment, 'assignment differs from released package')
    check(decode((folder/'package_manifest.json').read_bytes()) == manifest, 'package manifest contents differ')
    d['manifest_byte_identical'] = (folder/'package_manifest.json').read_bytes() == manifest_bytes
    prepath = folder/'preflight/preflight.json'
    if prepath.exists():
        pre = decode(prepath.read_bytes())
        records = pre['records']
        d['preflight'] = {'trials':len(records), 'code_passed':sum(not code_check(r,expected[r['case_id']]) for r in records), 'statuses':dict(collections.Counter(r['status'] for r in records)), 'transport_ok':pre['transport_ok'], 'cost':pre['observed_cost_usd'], 'projected':pre['projected_agent_total_usd']}
        check(pre['package_sha256'] == digest(manifest_bytes), 'preflight package digest differs')
        check(pre['assignment'] == assignment, 'preflight assignment differs')
        check({r['case_id'] for r in records} == {'CLM-8842','CLM-8888','CLM-8910','CLM-8925','CLM-8952','CLM-16404'} and len(records)==6, 'preflight case set incomplete')
        for r in records:
            runpath = folder/'preflight'/r['run_id']/'result.json'
            check(runpath.exists() and decode(runpath.read_bytes()) == r, 'preflight raw record missing/different: '+r['run_id'])
    else:
        d['partial_preflight_results'] = len(list((folder/'preflight').glob('*/result.json')))
    zip_path = folder/f'D5_RETURN_{member}.zip'
    d['full_present'] = zip_path.exists()
    if zip_path.exists():
        with ZipFile(zip_path) as z:
            names = z.namelist()
            get = lambda n: decode(z.read('suite/'+n))
            rows, meta, summary = get('results.json'), get('metadata.json'), get('summary.json')
            check(len(rows)==75 and {(r['case_id'],r['trial']) for r in rows}==wanted,'incorrect trial denominator')
            check(get('assignment.json')==assignment, 'suite assignment differs')
            check(decode(z.read('package_manifest.json'))==manifest,'ZIP manifest differs')
            check(meta['contract_revision']=='d5-live-1.1' and meta['model']==assignment['model'] and meta['prompt_version']==assignment['version'] and meta['backend']=='live','suite configuration differs')
            check(meta['implementation_sha256']=={f.name:digest(f.read_bytes()) for f in sorted(runtime.glob('*.py'))},'runtime hash metadata differs')
            check({k.replace('\\','/'):v for k,v in meta['dataset_sha256'].items()}=={str(f.relative_to(runtime/'merged_A')):digest(f.read_bytes()) for f in sorted((runtime/'merged_A').rglob('*.json'))},'dataset hash metadata differs')
            check(meta['rubric_sha256']==digest((runtime/'rubric_clarifications.json').read_bytes()),'rubric hash differs')
            check(get('grading_contract.json')=={'labels':labels,'audit':expected,'clarifications':decode((runtime/'rubric_clarifications.json').read_bytes())},'grading contract differs')
            rel=get('release.json')
            check(rel['package_sha256']==digest(manifest_bytes),'release package digest differs')
            check(rel['preflight_sha256']==digest(z.read('suite/preflight.json')),'release preflight digest differs')
            d['release_note']=rel['note']
            for row in rows:
                r=row['record']; ident=f"{row['case_id']}/{row['trial']}"
                check(row['failures']==code_check(r,expected[row['case_id']]) and row['code_passed']==(not code_check(r,expected[row['case_id']])),'regraded result differs: '+ident)
                check(get(f"{row['case_id']}-trial-{row['trial']}.json")==r,'trial raw record differs: '+ident)
                check(get(r['run_id']+'/result.json')==r,'run raw record differs: '+ident)
                check('suite/'+r['run_id']+'/transcript.txt' in names,'missing transcript: '+ident)
                check(r['backend']=='live' and r['model']==assignment['model'] and r['prompt_version']==assignment['version'],'trial assignment differs: '+ident)
                check(r['limits']=={'step_cap':8,'budget_usd':0.05},'trial limits differ: '+ident)
                cost=(r['tokens_in']*assignment['price_in']+r['tokens_out']*assignment['price_out'])/1e6
                check(abs(cost-r['cost_usd'])<1e-9,'trial cost mismatch: '+ident)
            for k,v in summarize(rows).items():
                if k == 'cost_usd':
                    check(all(abs(summary[k][field]-value)<1e-9 for field,value in v.items()),'summary mismatch: '+k)
                else: check(summary[k]==v,'summary mismatch: '+k)
            d['full']={k:summary[k] for k in ['trials','cases','code_passed','execution_errors','judgement_pending','judgement_not_reviewable','ordinary','negative','step_cap_hits','cost_usd','turns']}
            d['statuses']=dict(collections.Counter(r['record']['status'] for r in rows))
            d['errors']=dict(collections.Counter(r['record'].get('error') for r in rows if r['record'].get('error')))
            d['provider_cost']=sum(a['usage'].get('cost',0) for r in rows for a in r['record']['responses'])
            d['responses']=sum(len(r['record']['responses']) for r in rows)
            d['unique_run_ids']=len({r['record']['run_id'] for r in rows})
            receipt=get('dispatch_receipt.json')
            check(abs(receipt['observed_agent_spend_usd']-summary['cost_usd']['total']-get('preflight.json')['observed_cost_usd'])<1e-8,'dispatch cost mismatch')
            for n in names:
                check(not re.search(rb'sk-or-v1-[A-Za-z0-9]{20,}',z.read(n)), 'possible API key: '+n)
    report['members'][member]=d
out=Path(__file__).with_name('audit_results.json')
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
for name,d in report['members'].items():
    print(name, 'full',d['full_present'], 'preflight',d.get('preflight',d.get('partial_preflight_results')), 'findings',d['findings'])
