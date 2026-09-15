"""Instrumented hand-written ReAct loop; no framework owns sequencing."""
import json
import math
import time
from .tools import ToolSession, ToolError


def estimate_tokens(value):
    return math.ceil(len(json.dumps(value, ensure_ascii=False)) / 4)


class ScriptedBackend:
    """Deterministic observation-driven policy for harness reproduction, not an LLM.

    It reads only observations, never fixtures or the expected answer key.
    Scripted success tests plumbing and rules, not language-model competence.
    """
    name = 'scripted'

    def next(self, case_id, observations, sequential=False, variant='v2'):
        by = {}
        for o in observations:
            by[(o['tool'], o['arguments'].get('code'))] = o['result']
        def call(tool, **args):
            return {'tool': tool, 'arguments': args}
        calls = []
        c = by.get(('get_claim', None))
        if c is None:
            calls = [call('get_claim', claim_id=case_id)]
        else:
            p = by.get(('lookup_policy', None))
            h = by.get(('get_hospital_status', None))
            if p is None:
                calls = [call('lookup_policy', claim_id=case_id)]
            else:
                injection = c.get('instruction_detected', False)
                trigger = ('instruction_in_member_narrative' if injection else
                           'duplicate_claim' if c.get('duplicate') else p.get('policy_trigger'))
                # Hostile text may counterfeit a coverage observation: obtain the real one.
                needs_lines = not trigger or injection
                codes = list(dict.fromkeys(x['code'] for x in c['lines']))
                if needs_lines:
                    for code in codes:
                        if ('check_coverage', code) not in by:
                            calls.append(call('check_coverage', claim_id=case_id, code=code))
                    if not trigger and h is None:
                        calls.append(call('get_hospital_status', claim_id=case_id))
                if not calls and not trigger:
                    for code in codes:
                        cov = by[('check_coverage', code)]
                        if cov['requires_preauth'] and not cov['excluded'] and ('get_preauthorisation', code) not in by:
                            calls.append(call('get_preauthorisation', claim_id=case_id, code=code))
                if not calls:
                    lines, missing = [], []
                    approved = refused = 0
                    if not trigger:
                        for item in c['lines']:
                            code = item['code']; cov = by[('check_coverage', code)]
                            line = dict(item)
                            if cov['excluded']:
                                line.update(status='not_covered', exclusion=cov['exclusion'])
                                refused += item['amount']
                            else:
                                for doc in cov['missing_documents']:
                                    m = {'code': code, 'document': doc, 'date': c['date_of_service']}
                                    if m not in missing: missing.append(m)
                                pa = by.get(('get_preauthorisation', code))
                                valid = pa.get('valid') if pa else None
                                if cov['requires_preauth'] and not valid:
                                    m = {'code': code, 'document': 'preauthorisation', 'date': c['date_of_service']}
                                    if m not in missing: missing.append(m)
                                unresolved = bool(cov['missing_documents']) or (cov['requires_preauth'] and not valid)
                                line['status'] = 'unresolved' if unresolved else 'covered'
                                if valid: line['preauth'] = valid['preauth_id']
                                if not unresolved: approved += item['amount']
                            lines.append(line)
                    reason_parts = [f"Policy {p['policy_id']} status {p['status']}, dates {p['start_date']}..{p['end_date']}; claim total {p['claim_total']}, remaining {p['remaining']}."]
                    if trigger:
                        reason_parts.append(f'Escalated to human claims assessor: {trigger}.')
                        if trigger=='annual_limit_exceeded': reason_parts.append('No lines were individually priced: stopped before check_coverage because the total already exceeded the remaining annual limit.')
                        if c.get('duplicate'):
                            reason_parts.append('Prior decision ' + c['duplicate']['claim_id'] + '; member, hospital, date and line multiset match.')
                        if injection: reason_parts.append('Member instructions were not followed; real coverage observations override counterfeit tool text.')
                    else:
                        reason_parts.append(f"Hospital {h['hospital_id']}, panel={h['panel']}. Approved {round(approved,2)}, refused {round(refused,2)}.")
                        for code in codes:
                            pa = by.get(('get_preauthorisation', code))
                            if pa:
                                reason_parts.append('Authorisation evidence: ' + json.dumps(pa['candidates'],sort_keys=True))
                        if missing: reason_parts.append('Missing: ' + json.dumps(missing,sort_keys=True))
                        reason_parts.append('Line evidence: ' + json.dumps(lines,sort_keys=True))
                    decision = dict(case_id=case_id, decision='escalate' if trigger else 'request_document' if missing else 'approve_in_principle', lines=lines, missing=missing, approved_total=round(approved,2), refused_total=round(refused,2), reason=' '.join(reason_parts), evidence=[o['id'] for o in observations])
                    if trigger: decision.update(trigger=trigger, escalate_to='human claims assessor')
                    calls = [call('issue_decision_letter', decision=decision)]
        if sequential: calls = calls[:1]
        from .backends import system_prompt
        prefix=system_prompt(variant,sequential)
        return {'calls': calls, 'usage': {'input': estimate_tokens(observations)+estimate_tokens(prefix), 'output': estimate_tokens(calls)}, 'raw': {'calls': calls}}


def run_case(case_id, backend=None, sequential=False, variant='v2', autonomy='confirm', approval=None, max_turns=10, token_limit=60000, ledger=None, disable_dedup=False, ablate_preauth=False, data_root=None, budget_usd=.10):
    backend = backend or ScriptedBackend()
    session = ToolSession(data_root=data_root, variant=variant, autonomy=autonomy, approval=approval, ledger=ledger, ablate_preauth=ablate_preauth)
    trace=[]; seen=set(); ti=to=0; cost=0.; repairs=0; stop='step_cap'; started=time.monotonic()
    for turn in range(1,max_turns+1):
        event={'turn':turn,'calls':[]}
        if ti+to >= token_limit or cost >= budget_usd:
            stop='token_cap' if ti+to >= token_limit else 'budget_cap'; break
        try:
            reply=backend.next(case_id, session.snapshot(), sequential, variant)
            usage=reply.get('usage',{})
            ti += usage.get('input',0); to += usage.get('output',0)
            cost += usage.get('cost', (usage.get('input',0)*.1+usage.get('output',0)*.4)/1e6)
            event.update(usage=usage,raw=reply.get('raw'),calls=reply.get('calls',[]))
            calls=reply.get('calls')
            if not isinstance(calls,list) or not calls or len(calls)>12: raise ToolError('invalid action block')
            if sequential and len(calls)>1: raise ToolError('sequential mode permits one call')
            names=[c.get('tool') for c in calls]
            if 'issue_decision_letter' in names and len(calls)!=1: raise ToolError('write must be alone')
            # A batch cannot create prerequisites for another member of that batch.
            observed={o['tool'] for o in session.observations}
            for c in calls:
                name=c.get('tool'); args=c.get('arguments')
                if not isinstance(args,dict): raise ToolError('arguments must be an object')
                if name!='get_claim' and 'get_claim' not in observed: raise ToolError('same-turn claim dependency')
                if name in ('check_coverage','get_preauthorisation') and 'lookup_policy' not in observed: raise ToolError('same-turn policy dependency')
                if name=='get_preauthorisation' and not any(o['tool']=='check_coverage' and o['arguments'].get('code')==args.get('code') for o in session.observations): raise ToolError('same-turn coverage dependency')
                key=json.dumps(c,sort_keys=True,separators=(',',':'))
                if key in seen and not disable_dedup:
                    stop='duplicate_action'; raise ToolError('repeated action blocked')
            if ti+to>token_limit or cost>budget_usd:
                stop='token_cap' if ti+to>token_limit else 'budget_cap'; trace.append(event); break
            # Read calls share a model turn. Local fixture reads execute deterministically;
            # batching reduces provider turns, not local filesystem wall-clock time.
            for c in calls:
                seen.add(json.dumps(c,sort_keys=True,separators=(',',':')))
                session.run_metrics={'turns':turn,'tokens_in':ti,'tokens_out':to,'cost_usd':cost,'token_measurement':'api_usage' if backend.name=='live' else 'estimated_chars_div4'}
                result=session.call(c['tool'],c['arguments'])
                event.setdefault('observations',[]).append(result)
            trace.append(event)
            if session.record is not None:
                stop='completed'; break
        except Exception as exc:
            event['error']=f'{type(exc).__name__}: {exc}'
            trace.append(event)
            if stop!='duplicate_action': stop='error'
            if isinstance(exc,ToolError) and hasattr(backend,'feedback') and repairs<2 and stop!='duplicate_action':
                backend.feedback.append({'turn':turn,'rejected_calls':event.get('calls'), 'error':str(exc),'instruction':'Correct the call using existing evidence. No write occurred.'})
                repairs+=1
                stop='step_cap'
                continue
            break
    result=dict(case_id=case_id,record=session.record,trace=trace,observations=session.snapshot(),turns=len(trace),tokens_in=ti,tokens_out=to,cost_usd=cost,stop=stop,backend=backend.name,token_measurement='api_usage' if backend.name=='live' else 'estimated_chars_div4',elapsed_seconds=round(time.monotonic()-started,4),variant=variant,sequential=sequential,autonomy=autonomy)
    if result['record']:
        result['record']=dict(result['record'],turns=len(trace),tokens_in=ti,tokens_out=to,cost_usd=cost)
    return result
