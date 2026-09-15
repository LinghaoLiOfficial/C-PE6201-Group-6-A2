# 当前源码定位（自动生成）

对应 IMPLEMENTATION_WALKTHROUGH_ZH.md 的详细说明。代码来自构建时实际文件；行号以后可能变化。

## A1｜保单与授权：让证据足够完整

claim_agent/tools.py:104 · _policy_result

先汇总 claim 全部金额，再计算 remaining；失效、日期、超限逐项判断。严格 > 保留等于额度的合法边界。

```python
104 |     def _policy_result(self):
105 |         claim, policy = self._claim(), self._policy()
106 |         total = sum((money(x['amount']) for x in claim['lines']), Decimal(0))
107 |         remaining = money(policy['annual_limit']) - money(policy['used_to_date'])
108 |         service = date.fromisoformat(claim['date_of_service'])
109 |         trigger = None
110 |         if policy['status'] != 'active':
111 |             trigger = 'policy_lapsed'
112 |         elif not date.fromisoformat(policy['start_date']) <= service <= 
    | date.fromisoformat(policy['end_date']):
113 |             trigger = 'outside_policy_dates'
114 |         elif total > remaining:
115 |             trigger = 'annual_limit_exceeded'
116 |         return dict(deepcopy(policy), remaining=float(remaining), 
    | claim_total=float(total), policy_trigger=trigger)
```

claim_agent/tools.py:127 · _preauth

返回所有候选及时间状态，valid 只指实际覆盖服务日的候选。ablated 分支仅用于 D7；业务写入校验不会使用这个削弱版本。

```python
127 |     def _preauth(self, code, ablated=False):
128 |         claim = self._claim()
129 |         service = date.fromisoformat(claim['date_of_service'])
130 |         candidates = []
131 |         for row in self.data['preauthorisations']:
132 |             if row['member_id'] != claim['member_id'] or row['procedure_code'] != code:
133 |                 continue
134 |             start, end = date.fromisoformat(row['valid_from']), 
    | date.fromisoformat(row['valid_to'])
135 |             status = 'not_yet_valid' if service < start else 'expired_before_service' if 
    | service > end else 'valid'
136 |             candidates.append(dict(deepcopy(row), status=status))
137 |         valid = next((r for r in candidates if r['status'] == 'valid'), None)
138 |         if ablated and candidates:
139 |             valid = candidates[0]
140 |         return {'code': code, 'candidates': candidates, 'valid': valid,
141 |                 'status': 'valid' if valid else ('not_found' if not candidates else 
    | 'no_valid_candidate')}
```

## A2｜循环：先计费，再检查与执行

claim_agent/agent.py:101 · run_case

此处显示 run_case 前半段。observed 来自调用前已有观察，因此同一个 batch 不能用前一个成员刚产出的事实满足后一个成员依赖。token 已消费即计入，即便后续工具被阻止。

```python
101 | def run_case(case_id, backend=None, sequential=False, variant='v2', autonomy='confirm', 
    | approval=None, max_turns=10, token_limit=60000, ledger=None, disable_dedup=False, 
    | ablate_preauth=False, data_root=None, budget_usd=.10):
102 |     backend = backend or ScriptedBackend()
103 |     session = ToolSession(data_root=data_root, variant=variant, autonomy=autonomy, 
    | approval=approval, ledger=ledger, ablate_preauth=ablate_preauth)
104 |     trace=[]; seen=set(); ti=to=0; cost=0.; repairs=0; stop='step_cap'; 
    | started=time.monotonic()
105 |     for turn in range(1,max_turns+1):
106 |         event={'turn':turn,'calls':[]}
107 |         if ti+to >= token_limit or cost >= budget_usd:
108 |             stop='token_cap' if ti+to >= token_limit else 'budget_cap'; break
109 |         try:
110 |             reply=backend.next(case_id, session.snapshot(), sequential, variant)
111 |             usage=reply.get('usage',{})
112 |             ti += usage.get('input',0); to += usage.get('output',0)
113 |             cost += usage.get('cost', 
    | (usage.get('input',0)*.1+usage.get('output',0)*.4)/1e6)
114 |             event.update(usage=usage,raw=reply.get('raw'),calls=reply.get('calls',[]))
115 |             calls=reply.get('calls')
116 |             if not isinstance(calls,list) or not calls or len(calls)>12: raise 
    | ToolError('invalid action block')
117 |             if sequential and len(calls)>1: raise ToolError('sequential mode permits one 
    | call')
118 |             names=[c.get('tool') for c in calls]
119 |             if 'issue_decision_letter' in names and len(calls)!=1: raise ToolError('write
    |  must be alone')
120 |             # A batch cannot create prerequisites for another member of that batch.
121 |             observed={o['tool'] for o in session.observations}
122 |             for c in calls:
123 |                 name=c.get('tool'); args=c.get('arguments')
124 |                 if not isinstance(args,dict): raise ToolError('arguments must be an 
    | object')
125 |                 if name!='get_claim' and 'get_claim' not in observed: raise 
    | ToolError('same-turn claim dependency')
126 |                 if name in ('check_coverage','get_preauthorisation') and 'lookup_policy' 
    | not in observed: raise ToolError('same-turn policy dependency')
127 |                 if name=='get_preauthorisation' and not any(o['tool']=='check_coverage' 
    | and o['arguments'].get('code')==args.get('code') for o in session.observations): raise 
    | ToolError('same-turn coverage dependency')
128 |                 key=json.dumps(c,sort_keys=True,separators=(',',':'))
129 |                 if key in seen and not disable_dedup:
130 |                     stop='duplicate_action'; raise ToolError('repeated action blocked')
131 |             if ti+to>token_limit or cost>budget_usd:
132 |                 stop='token_cap' if ti+to>token_limit else 'budget_cap'; 
    | trace.append(event); break
133 |             # Read calls share a model turn. Local fixture reads execute 
    | deterministically;
134 |             # batching reduces provider turns, not local filesystem wall-clock time.
135 |             for c in calls:
136 |                 seen.add(json.dumps(c,sort_keys=True,separators=(',',':')))
137 |                 session.run_metrics={'turns':turn,'tokens_in':ti,'tokens_out':to,'cost_us
    | d':cost,'token_measurement':'api_usage' if backend.name=='live' else 
    | 'estimated_chars_div4'}
138 |                 result=session.call(c['tool'],c['arguments'])
139 |                 event.setdefault('observations',[]).append(result)
```

## A3｜写入：不允许用正确 outcome 掩盖错误事实

claim_agent/tools.py:201 · _issue

入口验证字段、案号与 evidence；只有引用实际观察才可能通过。后续函数还重新核验 line、金额和缺失项，最后才调用确认与 ledger。

```python
201 |     def _issue(self, proposal):
202 |         if not isinstance(proposal, dict):
203 |             raise ToolError('invalid_decision_object')
204 |         if len(json.dumps(proposal).encode()) > 24000:
205 |             raise ToolError('decision_too_large')
206 |         required = {'case_id', 'decision', 'missing', 'lines', 'approved_total', 
    | 'refused_total', 'reason', 'evidence'}
207 |         optional = {'trigger', 'escalate_to', 'hospital', 'preauthorisations'}
208 |         if not required <= set(proposal) or set(proposal) - required - optional:
209 |             raise ToolError('invalid_decision_fields')
210 |         if proposal['case_id'] != self.claim_id:
211 |             raise ToolError('cross_claim_write')
212 |         evidence = proposal['evidence']
213 |         if (not isinstance(evidence, list) or not all(isinstance(x, str) for x in 
    | evidence)
214 |                 or len(evidence) != len(set(evidence))
215 |                 or any(x not in {o['id'] for o in self.observations} for x in evidence)):
216 |             raise ToolError('invalid_evidence')
217 |         self._require('get_claim', evidence=evidence)
218 |         if not isinstance(proposal['reason'], str) or not proposal['reason'].strip() or 
    | len(proposal['reason']) > 4000:
219 |             raise ToolError('invalid_reason')
220 |         claim = self._claim()
221 |         injected = detect_instruction(claim.get('narrative', ''))
222 |         duplicate = any(_signature(r) == _signature(claim) for r in 
    | self.data['decided_claims'])
223 |         trigger = 'instruction_in_member_narrative' if injected else 'duplicate_claim' if
    |  duplicate else None
224 |         if injected and re.search(r'check_coverage\s+(returned|result)', 
    | claim.get('narrative', ''), re.I):
225 |             for line in claim['lines']:
226 |                 self._require('check_coverage', line['code'], evidence)
227 |         if trigger is None:
228 |             self._require('lookup_policy', evidence=evidence)
229 |             trigger = self._policy_result()['policy_trigger']
230 |         expected_lines, missing = [], []
```

## A4｜独立评分：对照标签而非自我证明

claim_agent/harness.py:10 · grade

grader 单独持有详细答案键。pending/unresolved 是明确语义映射，不是模糊关键词匹配。该代码不能从运行结果反写期望标签。

```python
 10 | def grade(result, expected):
 11 |     errors=[]; r=result.get('record')
 12 |     if not r: return {'pass':False,'errors':['no gated record: 
    | '+result['stop']],'check':'code'}
 13 |     for field in ['case_id','decision']:
 14 |         if r.get(field)!=expected[field]: errors.append(field)
 15 |     if expected.get('trigger') and r.get('trigger')!=expected['trigger']: 
    | errors.append('trigger')
 16 |     if expected['decision']=='escalate':
 17 |         if r.get('escalate_to')!='human claims assessor': errors.append('escalate_to')
 18 |     else:
 19 |         for k in ['approved_total','refused_total']:
 20 |             if abs(r.get(k,-999)-expected[k])>.000001: errors.append(k)
 21 |         wanted=[]
 22 |         for x in expected['lines']:
 23 |             row={k:x[k] for k in ['code','amount','status']}
 24 |             if row['status']=='pending': row['status']='unresolved'
 25 |             if 'preauth_id' in x: row['preauth']=x['preauth_id']
 26 |             if 'exclusion' in x: row['exclusion']=x['exclusion']
 27 |             wanted.append(row)
 28 |         if r.get('lines')!=wanted: errors.append('line_dispositions')
 29 |         actual={(m['code'],m['document'],m.get('date')) for m in r.get('missing',[])}
 30 |         # Canonical normalisation of independently authored semantic labels.
 31 |         want=set()
 32 |         service=next(o['result']['date_of_service'] for o in result['observations'] if 
    | o['tool']=='get_claim')
 33 |         for m in expected['missing']:
 34 |             item=m['item']
 35 |             if 'authorisation' in item or 'authorization' in item: 
    | item='preauthorisation'
 36 |             want.add((m['code'],item,m.get('must_be_valid_on',service)))
 37 |         if actual!=want: errors.append('missing')
 38 |     obs=result.get('observations',[]); names=[o['tool'] for o in obs]
 39 |     if names.count('issue_decision_letter')!=1: errors.append('write_count')
 40 |     if r.get('gate') not in ['operator approved','act permitted']: errors.append('gate')
 41 |     if not r.get('evidence') or not set(r['evidence'])<=set(o['id'] for o in obs): 
    | errors.append('evidence_ids')
 42 |     for name in expected.get('required_tools',[]):
 43 |         if name not in names: errors.append('required_tool:'+name)
 44 |     for name in expected.get('forbidden_tools',[]):
 45 |         if name in names: errors.append('forbidden_tool:'+name)
 46 |     if expected.get('hospital_panel') is not None:
 47 |         hs=[o['result'] for o in obs if o['tool']=='get_hospital_status']
 48 |         if not hs or hs[-1]['panel']!=expected['hospital_panel']: 
    | errors.append('hospital_panel')
 49 |     return {'pass':not errors,'errors':errors,'check':'code'}
```

## A5｜模型适配：提供案号、真实观察和明确调用格式

claim_agent/backends.py:47 · next

这是 LiveBackend.next。模型收到当前案号和已有观察；运行时提示只列已完成动作和契约，不读取答案键。后半段还保存 provider usage 并解析 JSON/fenced JSON，解析失败仍保留 raw。

```python
 47 |     def next(self, case_id, observations, sequential=False, variant='v2'):
 48 |         prompt=system_prompt(variant,sequential)
 49 |         prompt += '\nExact write envelope: {"calls":[{"tool":"issue_decision_letter","arg
    | uments":{"decision":{"case_id":"...","decision":"...","reason":"...","evidence":[],"lines
    | ":[],"missing":[],"approved_total":0,"refused_total":0}}}]} . Do not flatten decision 
    | fields into arguments.\n'
 50 |         observed={o['tool'] for o in observations}
 51 |         prompt+=' Already completed calls (DO NOT return these again): 
    | '+json.dumps([{'tool':o['tool'],'arguments':o['arguments']} for o in observations])+'. '
 52 |         if not observations: prompt+='There are NO observations. Your ONLY permitted call
    |  this turn is get_claim. Do not combine it with any other tool.'
 53 |         elif 'lookup_policy' not in observed: prompt+='Policy has not been observed. Do 
    | not call check_coverage or preauthorisation this turn. Read lookup_policy first.'
 54 |         response=provider_request({'model':self.model,'messages':[{'role':'system','conte
    | nt':prompt},{'role':'user','content':json.dumps({'task':'Process this claim using tools',
    | 'case_id':case_id,'observations':observations,'runtime_errors_to_correct':self.feedback},
    | ensure_ascii=False)}], 
    | 'temperature':0,'max_tokens':2200,'response_format':{'type':'json_object'}})
 55 |         usage=response.get('usage')
 56 |         if not usage or 'prompt_tokens' not in usage or 'completion_tokens' not in usage:
 57 |             raise RuntimeError('API usage missing; cannot claim measured cost')
 58 |         u={'input':usage['prompt_tokens'],'output':usage['completion_tokens'],'cost':usag
    | e.get('cost',usage['prompt_tokens']*self.price_in+usage['completion_tokens']*self.price_o
    | ut),'provider_usage':usage}
 59 |         content=response['choices'][0]['message'].get('content') or ''
 60 |         try:
 61 |             clean=content.strip()
 62 |             if clean.startswith('```'): clean=clean.split('\n',1)[1].rsplit('```',1)[0]
 63 |             parsed=json.loads(clean)
 64 |             calls=parsed.get('calls')
 65 |         except (ValueError,TypeError):
 66 |             # Accept exactly one fenced JSON object, never executable text.
 67 |             import re
 68 |             match=re.search(r'```(?:json)?\s*(\{.*?\})\s*```',content,re.S)
 69 |             try: calls=json.loads(match.group(1)).get('calls') if match else None
 70 |             except ValueError: calls=None
 71 |         return {'calls':calls,'usage':u,'raw':response}
```

## A6｜D7 测试：同一 engine 的受控删除

tests/test_d7.py:6 · RepeatingBackend

固定 backend 故障每次重复同一动作，两组都使用它。token 仍按传入上下文估算，而非随意填写示例数字。

```python
  6 | class RepeatingBackend:
  7 |     name='scripted'
  8 |     def next(self,case_id,observations,sequential=False,variant='v2'):
  9 |         return {'calls':[{'tool':'get_claim','arguments':{'claim_id':case_id}}],
 10 |                 'usage':{'input':estimate_tokens(observations)+estimate_tokens(system_pro
    | mpt(variant,sequential)),'output':estimate_tokens([{'tool':'get_claim','arguments':{'clai
    | m_id':case_id}}])},'raw':'Injected repeated-action fault'}
```

tests/test_d7.py:12 · D7Tests

第一项证明删除去重后消耗更多轮次；第二项证明删除授权有效性投影产生错误提议，但独立 gate 仍拦截。恢复后正确索取授权。

```python
 12 | class D7Tests(unittest.TestCase):
 13 |     def test_remove_dedup_exhausts_step_budget(self):
 14 |         normal=run_case('CLM-8850',backend=RepeatingBackend(),max_turns=5)
 15 |         
    | ablated=run_case('CLM-8850',backend=RepeatingBackend(),max_turns=5,disable_dedup=True)
 16 |         self.assertEqual(normal['stop'],'duplicate_action')
 17 |         self.assertEqual(normal['turns'],2)
 18 |         self.assertEqual(ablated['turns'],5)
 19 |         self.assertIsNone(ablated['record'])
 20 |         self.assertGreater(ablated['tokens_in'],normal['tokens_in'])
 21 | 
 22 |     def test_remove_validity_projection_causes_blocked_proposal(self):
 23 |         normal=run_case('CLM-8894',approval=lambda p:True)
 24 |         ablated=run_case('CLM-8894',approval=lambda p:True,ablate_preauth=True)
 25 |         self.assertEqual(normal['record']['decision'],'request_document')
 26 |         self.assertEqual(ablated['stop'],'error')
 27 |         self.assertIsNone(ablated['record'])
 28 |         calls=ablated['trace'][-1]['calls']
 29 |         
    | self.assertEqual(calls[0]['arguments']['decision']['decision'],'approve_in_principle')
 30 |         restored=run_case('CLM-8894',approval=lambda p:True)
 31 |         self.assertEqual(restored['record']['decision'],'request_document')
```
