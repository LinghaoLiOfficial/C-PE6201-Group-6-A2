#!/usr/bin/env python3
"""Rebuild offline measurements and controlled failure evidence."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from claim_agent.agent import run_case
from claim_agent.harness import summarize,grade,labels
from test_d7 import RepeatingBackend
for args in [[],['--sequential','--output','results/sequential.json'],['--variant','v1','--output','results/scripted_v1.json']]:
    subprocess.run([sys.executable,'run_eval.py',*args],cwd=ROOT,check=True)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)
expected={x['case_id']:x for x in labels()}
loop={}; interface={}
for name,disabled in [('normal',False),('ablated',True),('restored',False)]:
    r=run_case('CLM-8850',backend=RepeatingBackend(),max_turns=10,disable_dedup=disabled)
    r['grade']=grade(r,expected[r['case_id']]);loop[name]=r
    r=run_case('CLM-8894',approval=lambda p:True,ablate_preauth=disabled)
    r['grade']=grade(r,expected[r['case_id']]);interface[name]=r
out={'design':'Same injected observation/call policy; normal minus one component; restoration. Loop test measures containment, not successful task completion. All tokens are instrumented character-based estimates, not API charges.','loop':loop,'interface':interface}
(ROOT/'results/d7_failures.json').write_text(json.dumps(out,indent=2))
subprocess.run([sys.executable,'scripts/check_guardrail_variants.py'],cwd=ROOT,check=True)
print('Offline evidence rebuilt.')
