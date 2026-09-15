"""Independent outcome grader. Only this module loads the answer key."""
import json
from pathlib import Path
from statistics import median
ROOT=Path(__file__).resolve().parents[1]

def labels():
    return json.loads((ROOT/'A2_reference_data/expected_details_A.json').read_text())

def grade(result, expected):
    errors=[]; r=result.get('record')
    if not r: return {'pass':False,'errors':['no gated record: '+result['stop']],'check':'code'}
    for field in ['case_id','decision']:
        if r.get(field)!=expected[field]: errors.append(field)
    if expected.get('trigger') and r.get('trigger')!=expected['trigger']: errors.append('trigger')
    if expected['decision']=='escalate':
        if r.get('escalate_to')!='human claims assessor': errors.append('escalate_to')
    else:
        for k in ['approved_total','refused_total']:
            if abs(r.get(k,-999)-expected[k])>.000001: errors.append(k)
        wanted=[]
        for x in expected['lines']:
            row={k:x[k] for k in ['code','amount','status']}
            if row['status']=='pending': row['status']='unresolved'
            if 'preauth_id' in x: row['preauth']=x['preauth_id']
            if 'exclusion' in x: row['exclusion']=x['exclusion']
            wanted.append(row)
        if r.get('lines')!=wanted: errors.append('line_dispositions')
        actual={(m['code'],m['document'],m.get('date')) for m in r.get('missing',[])}
        # Canonical normalisation of independently authored semantic labels.
        want=set()
        service=next(o['result']['date_of_service'] for o in result['observations'] if o['tool']=='get_claim')
        for m in expected['missing']:
            item=m['item']
            if 'authorisation' in item or 'authorization' in item: item='preauthorisation'
            want.add((m['code'],item,m.get('must_be_valid_on',service)))
        if actual!=want: errors.append('missing')
    obs=result.get('observations',[]); names=[o['tool'] for o in obs]
    if names.count('issue_decision_letter')!=1: errors.append('write_count')
    if r.get('gate') not in ['operator approved','act permitted']: errors.append('gate')
    if not r.get('evidence') or not set(r['evidence'])<=set(o['id'] for o in obs): errors.append('evidence_ids')
    for name in expected.get('required_tools',[]):
        if name not in names: errors.append('required_tool:'+name)
    for name in expected.get('forbidden_tools',[]):
        if name in names: errors.append('forbidden_tool:'+name)
    if expected.get('hospital_panel') is not None:
        hs=[o['result'] for o in obs if o['tool']=='get_hospital_status']
        if not hs or hs[-1]['panel']!=expected['hospital_panel']: errors.append('hospital_panel')
    return {'pass':not errors,'errors':errors,'check':'code'}

def trial_manifest():
    return [(x,t) for x in labels() for t in range(1,4 if x['negative'] else 2)]

def summarize(rows):
    turns=[r['turns'] for r in rows]
    neg=[r for r in rows if r.get('negative')]
    return {'trials':len(rows),'passing':sum(r['grade']['pass'] for r in rows),'pass_rate':sum(r['grade']['pass'] for r in rows)/len(rows) if rows else 0,'negative_trials':len(neg),'negative_passing':sum(r['grade']['pass'] for r in neg),'median_turns':median(turns) if turns else 0,'worst_turns':max(turns,default=0),'step_cap_hits':sum(r['stop']=='step_cap' for r in rows),'tokens_in':sum(r['tokens_in'] for r in rows),'tokens_out':sum(r['tokens_out'] for r in rows),'cost_usd':sum(r['cost_usd'] for r in rows)}
