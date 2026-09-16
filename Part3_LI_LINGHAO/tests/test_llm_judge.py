"""Offline judge contract checks. No mock result is reported as a real judgement."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration.llm_judge import validate_verdict, run_judge
from integration.d4_harness import write, read


class JudgeTests(unittest.TestCase):
    def test_invalid_and_missing_criteria_fail_closed(self):
        criteria = [{'review_id': 'C/1/1'}, {'review_id': 'C/1/2'}]
        result = {'case_id': 'C', 'trial': 1, 'criteria': [
            {'review_id': 'C/1/1', 'verdict': 'pass', 'rationale': 'ok', 'evidence_refs': ['reason']}]}
        with self.assertRaises(ValueError):
            validate_verdict(json.dumps(result), 'C', 1, criteria)
        result['criteria'] *= 2
        with self.assertRaises(ValueError):
            validate_verdict(json.dumps(result), 'C', 1, criteria)

    def make_suite(self, path):
        write(path / 'metadata.json', {'model': 'scripted', 'backend': 'scripted'})
        rows = [{'case_id': 'C', 'trial': 1, 'negative': False, 'code_passed': True,
                 'failures': [], 'judgement': 'pending', 'record': {'model': 'scripted',
                 'status': 'completed', 'decision': 'approve_in_principle', 'reason': 'test'}}]
        write(path / 'results.json', rows)
        write(path / 'review_template.json', [{'review_id': 'C/1/1', 'case_id': 'C',
              'trial': 1, 'criterion': 'Explain', 'verdict': '', 'graded_by': '',
              'comments': '', 'record_path': 'C.json'}])

    def test_resume_and_uncertain_do_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            self.make_suite(p)
            calls = []
            def caller(*args, **kwargs):
                calls.append(1)
                content = {'case_id': 'C', 'trial': 1, 'criteria': [{'review_id': 'C/1/1',
                           'verdict': 'uncertain', 'rationale': 'Missing evidence', 'evidence_refs': []}]}
                return {'model': 'judge/test', 'usage': {'prompt_tokens': 10, 'completion_tokens': 20},
                        'choices': [{'message': {'content': json.dumps(content)}}]}
            s = run_judge(p, model='judge/test', caller=caller)
            self.assertEqual(s['overall_passed'], 0)
            self.assertEqual(s['judgement_pending'], 1)
            run_judge(p, model='judge/test', caller=caller)
            self.assertEqual(len(calls), 1)
            self.assertEqual(read(p / 'results.json')[0]['judgement'], 'pending')

    def test_same_model_and_zero_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            self.make_suite(p)
            with self.assertRaises(ValueError):
                run_judge(p, model='scripted', caller=lambda *a, **k: self.fail('no network'))
            s = run_judge(p, budget=0, caller=lambda *a, **k: self.fail('no network'))
            self.assertEqual(s['judge_calls_pending'], 1)
