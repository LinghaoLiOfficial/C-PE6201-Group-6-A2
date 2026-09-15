#!/usr/bin/env python3
"""Derive all reported tables and cost assumptions from archived measurements."""
import ast,json,math,statistics,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from claim_agent.agent import estimate_tokens
from claim_agent.tools import tool_descriptors
ROOT=Path(__file__).resolve().parents[1]

def main():
    results=ROOT/'results'; summary=json.loads((results/'live/summary.json').read_text())
    catalog={x['id']:x for x in json.loads((results/'model_catalog.json').read_text())}
    costs=[]
    for s in summary:
        m=s['model']; n=s['trials']; prices=catalog[m]['pricing']
        s['code_passing']=s['passing']; s['code_pass_rate']=s['pass_rate']
        trial_rows=[(q.name,json.loads(q.read_text())) for q in (results/'live').glob(m.replace('/','__')+'_'+s['variant']+'_*.json')]
        selected={'CLM-8842','CLM-8894','CLM-8925','CLM-8952','CLM-9309','CLM-9310'}
        def assessed(name,r):
            if not r['grade']['pass']:return False
            if r['case_id'] not in selected:return True
            jp=results/'judgement'/name
            return jp.exists() and json.loads(jp.read_text()).get('pass') is True
        s['passing']=sum(assessed(name,r) for name,r in trial_rows)
        s['negative_passing']=sum(assessed(name,r) for name,r in trial_rows if r['negative'])
        s['pass_rate']=s['passing']/n; p=s['pass_rate']
        variable=(s['tokens_in']*float(prices['prompt'])+s['tokens_out']*float(prices['completion']))/n
        fallback=(1-p)*7.6;fixed=80
        z=1.96;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        raw_runs=[json.loads(q.read_text()) for q in (results/'live').glob(m.replace('/','__')+'_'+s['variant']+'_*.json')]
        incomplete=sum(any('usage' not in t for t in r['trace']) for r in raw_runs)
        costs.append({**s,'runs_with_missing_request_usage':incomplete,'variable_usd':variable,'fallback_usd':fallback,'cost_per_task_usd':variable+fallback,'fixed_monthly_usd':fixed,'monthly_usd':8000*(variable+fallback)+fixed,'pass_rate_wilson95':[max(0,mid-half),min(1,mid+half)],'sensitivity':[{'success_rate':max(0,min(1,p+d)),'cost_per_task_usd':variable+(1-max(0,min(1,p+d)))*7.6} for d in [-.1,0,.1]],'implied_step_reliability':p**(1/s['median_turns']) if s['median_turns'] else 0})
    v2=[x for x in costs if x['variant']=='v2'];recommended=min(v2,key=lambda x:x['cost_per_task_usd']);cheap=min(v2,key=lambda x:x['variable_usd']);expensive=max(v2,key=lambda x:x['variable_usd']);break_even=1-(expensive['cost_per_task_usd']-cheap['variable_usd'])/7.6
    seq=json.loads((results/'sequential.json').read_text());par=json.loads((results/'scripted.json').read_text());v1=json.loads((results/'scripted_v1.json').read_text())
    def observation_mean(runfile):
        values=[estimate_tokens(o['result']) for r in runfile['runs'] for o in r['observations'] if o['tool']=='get_preauthorisation']
        return sum(values)/len(values)
    before=estimate_tokens((ROOT/'docs/LEGACY_TOOL_PREFIX.txt').read_text())
    levers={'tool_prefix_before_estimated_tokens':before,'tool_prefix_after_estimated_tokens':estimate_tokens(tool_descriptors('v2')),'tool_prefix_measurement':'char/4 estimates of Chen original TOOL_SPEC actually inserted in prompt versus final six complete descriptors; not a controlled live ablation','sequential':seq['summary'],'parallel':par['summary'],'input_reduction_fraction':1-par['summary']['tokens_in']/seq['summary']['tokens_in'],'preauth_observation_v1_mean_estimated_tokens':observation_mean(v1),'preauth_observation_v2_mean_estimated_tokens':observation_mean(par)}
    judgment=[]
    jd=results/'judgement'
    for s in summary:
        prefix=s['model'].replace('/','__')+'_'+s['variant']+'_'
        vals=[json.loads(p.read_text()) for p in jd.glob(prefix+'*.json')]
        judgment.append({'model':s['model'],'variant':s['variant'],'designated_trials':len(vals),'judged':sum(x['status']=='judged' for x in vals),'combined_passing':sum(x['pass'] for x in vals),'pending':sum(x['status']=='invalid_judge_output' for x in vals)})
    model={'assumptions':{'volume':8000,'failure_usd':7.6,'hourly_usd':38,'minutes':12,'fixed_monthly_usd':80,'fixed_breakdown':{'storage':5,'infrastructure':10,'monitoring':10,'evaluation_refresh':5,'maintenance':50},'fixed_status':'illustrative operating assumption, not incurred course spending','production_mix':'evaluation trial-weighted mix; not asserted representative of production','baseline':'uncached list-price input/output, reasoning output included in API completion usage','success_definition':'code pass plus judgement pass on designated subset; legitimate escalation is a success','monthly_user_limit_usd':10,'monthly_user_limit_scope':'US$10 provider key lifetime cap is stricter than US$10 in any month; no top-ups; not a production deployment'},'models':costs,'recommended':recommended['model'],'cheapest_token_model':cheap['model'],'expensive_token_model':expensive['model'],'cheap_break_even_success':break_even,'cheap_actual_success':cheap['pass_rate'],'levers':levers,'judgement':judgment}
    raw=[json.loads(q.read_text()) for q in (results/'live').glob('*CLM*.json')]
    errors=collections.Counter(); previous=collections.Counter()
    for r in raw:
        if not r['grade']['pass']:
            errors[r['trace'][-1].get('error',r['stop'])]+=1
            previous[r['observations'][-1]['tool'] if r['observations'] else 'no successful observation']+=1
    (results/'failure_analysis.json').write_text(json.dumps({'errors':dict(errors),'preceding_successful_tool':dict(previous),'interpretation':'Temporal association identifies a diagnostic target, not causal fault in the preceding tool.'},indent=2))
    (results/'cost_model.json').write_text(json.dumps(model,indent=2))
    lines=['# Measured results','', 'Official v2 battery and the one-model v1 comparison. All rows use 64 trials; failures remain in the denominator. Assessed passing means code passing plus judgement passing on the six designated cases; it is the success rate used in costing. Costs below use list prices, not caching assumptions.','', '| Model | Version | Code passed | Assessed passed | Negative passed | Median / max turns | Variable/task US$ | With fallback US$ | Monthly US$ |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for x in costs:lines.append(f"| {x['model']} | {x['variant']} | {x['code_passing']}/{x['trials']} | {x['passing']}/{x['trials']} | {x['negative_passing']}/{x['negative_trials']} | {x['median_turns']} / {x['worst_turns']} | {x['variable_usd']:.5f} | {x['cost_per_task_usd']:.3f} | {x['monthly_usd']:.2f} |")
    lines+=['','## Cost levers','',f"Sequential input estimate {seq['summary']['tokens_in']:,}; parallel {par['summary']['tokens_in']:,}; reduction {levers['input_reduction_fraction']:.1%}. Both scripted configurations pass 64/64. Prefix before/after: {before}/{levers['tool_prefix_after_estimated_tokens']} estimated tokens. The final complete contracts can be larger despite fewer tools; no unsupported prefix-saving claim.",f"Preauthorisation observation mean v1/v2: {levers['preauth_observation_v1_mean_estimated_tokens']:.1f}/{levers['preauth_observation_v2_mean_estimated_tokens']:.1f} estimated tokens. The v1/v2 live comparison holds Gemini fixed.",'','## Judgement subset','','| Model | Version | Designated | Actually judged | Combined passed | Pending |','|---|---|---:|---:|---:|---:|']
    for j in judgment:lines.append(f"| {j['model']} | {j['variant']} | {j['designated_trials']} | {j['judged']} | {j['combined_passing']} | {j['pending']} |")
    lines+=['','## Assumptions','', 'US$80/month fixed allowance: storage 5, infrastructure 10, monitoring 10, evaluation refresh 5, maintenance 50. This is an illustrative budget, not measured spending. Expected error fallback uses US$38/hour × 12 minutes = US$7.60. Correct business escalations already count as successful decisions; their normal human handling is outside this prescribed error-fallback model. Confirmation labour and production case-mix uncertainty are additional deployment costs.',f"Cheap-model break-even against {expensive['model']}: {break_even:.2%}; actual {cheap['pass_rate']:.2%}. Best measured fallback-inclusive cost: {recommended['model']}. This is an experimental recommendation, not a deployment approval."]
    lines += ['', '## Sensitivity and finite-sample uncertainty', '', '| Model | Version | P minus 10pp US$/task | Measured P US$/task | P plus 10pp US$/task | Trial-level Wilson 95% |', '|---|---|---:|---:|---:|---|']
    for x in costs:
        lo,hi=x['pass_rate_wilson95'];ss=x['sensitivity']
        lines.append(f"| {x['model']} | {x['variant']} | {ss[0]['cost_per_task_usd']:.3f} | {ss[1]['cost_per_task_usd']:.3f} | {ss[2]['cost_per_task_usd']:.3f} | {lo:.1%}–{hi:.1%} |")
    lines += ['', 'Intervals treat trials as independent for illustration; repeated cases are correlated, so these are not population guarantees. A measured 100% does not imply zero future fallback. Success sensitivity clips at 0 and 1. Reprice failure handling at US$3.80/US$7.60/US$15.20 before assuming the default applies to another organisation.']
    (ROOT/'docs/RESULTS.md').write_text('\n'.join(lines)+'\n')
    failures=json.loads((results/'d7_failures.json').read_text())
    failure_doc=['# D7 controlled removals', '', 'All rows use the same final engine and fixed fault input. Scripted token counts are character-based estimates, not API charges. Each row is one trial.', '', '| Experiment | Configuration | Turns | Input | Output | Estimated US$ | Task pass | Stop |', '|---|---|---:|---:|---:|---:|---:|---|']
    for experiment in ['loop','interface']:
        for config in ['normal','ablated','restored']:
            r=failures[experiment][config]
            failure_doc.append(f"| {experiment} | {config} | {r['turns']} | {r['tokens_in']} | {r['tokens_out']} | {r['cost_usd']:.6f} | {int(r['grade']['pass'])}/1 | {r['stop']} |")
    failure_doc+=['','The loop fault always repeats get_claim, so normal/restored guards contain the loop without completing the task. Deleting dedup burns the step cap. The interface ablation removes validity projection only; its unsafe proposal is blocked by the independent writer. Restoring projection restores the correct request. No unsafe write is claimed.','','## Full-set turn distribution','','| Configuration | Trials | Median | Worst | Step-cap hits | Passed |','|---|---:|---:|---:|---:|---:|']
    for name,x in [('scripted parallel',par['summary']),('scripted sequential',seq['summary'])]+[(x['model']+' '+x['variant'],x) for x in costs]:
        failure_doc.append(f"| {name} | {x['trials']} | {x['median_turns']} | {x['worst_turns']} | {x['step_cap_hits']} | {x['passing']}/{x['trials']} |")
    (ROOT/'docs/FAILURE_EXPERIMENTS.md').write_text('\n'.join(failure_doc)+'\n')
    print(json.dumps({'recommended':model['recommended'],'models':len(costs),'official_trials':sum(x['trials'] for x in costs)},indent=2))
if __name__=='__main__':main()
