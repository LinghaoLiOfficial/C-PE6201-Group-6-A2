#!/usr/bin/env python3
"""Execute the same independent guardrail checklist against both contract variants."""
import functools,io,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import test_guardrails as checks
from claim_agent.agent import run_case
from claim_agent.tools import ToolSession
class Capture(unittest.TextTestResult):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.rows=[]
    def addSuccess(self,t):super().addSuccess(t);self.rows.append({'test':t.id(),'pass':True})
    def addFailure(self,t,e):super().addFailure(t,e);self.rows.append({'test':t.id(),'pass':False,'kind':'failure'})
    def addError(self,t,e):super().addError(t,e);self.rows.append({'test':t.id(),'pass':False,'kind':'error'})
outputs=[]
for variant in ['v1','v2']:
    class VariantSession(ToolSession):
        def __init__(self,*a,**kw):kw.setdefault('variant',variant);super().__init__(*a,**kw)
    checks.ToolSession=VariantSession
    checks.run_case=functools.partial(run_case,variant=variant)
    result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Capture).run(unittest.defaultTestLoader.loadTestsFromTestCase(checks.GuardrailChecklist))
    outputs.append({'variant':variant,'tests':result.rows,'passed':result.wasSuccessful()})
(ROOT/'results/guardrail_variants.json').write_text(json.dumps(outputs,indent=2))
print([(x['variant'],len(x['tests']),x['passed']) for x in outputs])
raise SystemExit(not all(x['passed'] for x in outputs))
