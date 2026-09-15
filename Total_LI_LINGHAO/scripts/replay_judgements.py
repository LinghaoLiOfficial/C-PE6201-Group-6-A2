#!/usr/bin/env python3
"""Replay archived independent judgements without calling a provider."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[json.loads(p.read_text()) for p in (ROOT/'results/judgement').glob('*.json')]
assert len(rows)==84, 'Expected 72 live and 12 scripted designated judgement records'
assert all(r['status'] in ('judged','code_failed_not_judged') for r in rows)
for r in rows:
    if r['status']=='judged':
        assert r['judge'] and r['raw'] and r['evaluated_input']
        assert r['evaluated_input']['case']['case_id']==r['case_id']
print(json.dumps({'archived_records':len(rows),'independent_judgements':sum(r['status']=='judged' for r in rows),'combined_passing':sum(r['pass'] for r in rows),'network_calls':0,'meaning':'Replay of archived measuring-instrument verdicts, not a new independent grading run'},indent=2))
