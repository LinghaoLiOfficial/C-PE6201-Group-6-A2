"""Regression tests for scoring errors, real runs and human-review import."""
import copy
import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration.d4_harness import run_battery, read, code_check, import_reviews


class D4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        with patch('urllib.request.urlopen', side_effect=AssertionError('network forbidden')) as network:
            cls.summary = run_battery(cls.temp.name)
            network.assert_not_called()
        cls.suite = Path(cls.summary['suite'])
        cls.rows = read(cls.suite / 'results.json')
        cls.audit = read(cls.suite / 'grading_contract.json')['audit']

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_trials_remain_in_denominator(self):
        self.assertEqual(self.summary['trials'], 75)
        self.assertEqual(self.summary['negative']['trials'], 45)
        self.assertEqual(self.summary['ordinary']['trials'], 30)
        self.assertEqual(self.summary['code_passed'], 75)
        self.assertEqual(self.summary['execution_errors'], 0)
        self.assertEqual(self.summary['turns']['measured_trials'], 75)

    def test_wrong_fields_fail_even_if_log_matches(self):
        for cid, field, value in [('CLM-8842', 'approved_total', 1),
                                  ('CLM-8925', 'trigger', 'duplicate_claim'),
                                  ('CLM-8894', 'missing', {'item': 'itemised bill', 'for_line': '29881', 'must_be_valid_on': '2026-09-09'})]:
            record = copy.deepcopy(next(x['record'] for x in self.rows if x['case_id'] == cid))
            record[field] = value
            record['action_records'][0][field] = value
            self.assertTrue(code_check(record, self.audit[cid]))

    def test_duplicate_billed_lines_and_reordering(self):
        cid = 'CLM-16404'
        r = copy.deepcopy(next(x['record'] for x in self.rows if x['case_id'] == cid))
        self.assertEqual(len(r['lines']), 4)
        r['lines'].reverse()
        r['action_records'][0]['lines'] = r['lines']
        self.assertEqual(code_check(r, self.audit[cid]), [])
        r['lines'].pop()
        self.assertTrue(code_check(r, self.audit[cid]))

    def test_early_exit_isolation_and_limits(self):
        self.assertEqual(len({x['record']['decision_log'] for x in self.rows}), 75)
        for row in self.rows:
            record = row['record']
            self.assertLessEqual(record['turns'], 8)
            self.assertEqual(record['action_count'], 1)
            self.assertEqual(record['api_cost_usd'], 0)
            if record.get('trigger') in ('policy_lapsed', 'outside_policy_dates', 'annual_limit_exceeded', 'duplicate_claim'):
                self.assertFalse({'check_procedure', 'check_documents', 'get_preauthorisation'} & {x['tool'] for x in record['trace']})

    def test_injected_failure_stays_in_denominator(self):
        from integration.runner import run_case
        def fail_one(cid, **kwargs):
            if cid == 'CLM-8850':
                raise ValueError('test missing trajectory')
            return run_case(cid, **kwargs)
        summary = run_battery(self.temp.name, executor=fail_one)
        self.assertEqual((summary['trials'], summary['code_passed'], summary['execution_errors']), (75, 74, 1))

    def test_runner_does_not_read_grading_files(self):
        from integration.runner import run_case
        from integration.d4_harness import DATASET
        original = Path.read_text
        def restricted(path, *args, **kwargs):
            if path.name in {'case_audit.json', 'expected_outcomes_A.json', 'missing_normalization.json'}:
                raise AssertionError('Runner tried to read answer material')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', restricted), patch('urllib.request.urlopen', side_effect=AssertionError('offline')):
            record = run_case('CLM-16104', data_dir=DATASET / 'data_A', output_dir=self.temp.name, operator_approved=True)
        self.assertEqual(record['status'], 'completed')
        self.assertEqual(record['approved_total'], 8785)

    def test_empty_review_stays_pending_and_bad_import_is_rejected(self):
        result = import_reviews(self.suite, self.suite / 'human_review.csv')
        self.assertEqual(result['overall_passed'], 0)
        self.assertEqual(result['judgement_pending'], 75)
        entries = read(self.suite / 'review_template.json')
        entries[0]['verdict'] = 'pass'
        path = self.suite / 'invalid.csv'
        with path.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(entries[0]))
            w.writeheader()
            w.writerows(entries)
        with self.assertRaisesRegex(ValueError, 'graded_by'):
            import_reviews(self.suite, path)

    def test_one_trial_review_does_not_propagate_to_repeats(self):
        entries = read(self.suite / 'review_template.json')
        for x in entries:
            if x['case_id'] == 'CLM-8925' and x['trial'] == 1:
                x.update(verdict='pass', graded_by='test-only')
        path = self.suite / 'test_review.csv'
        with path.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(entries[0]))
            w.writeheader()
            w.writerows(entries)
        summary = import_reviews(self.suite, path)
        self.assertEqual(summary['judgement_passed'], 1)
        self.assertEqual(summary['judgement_pending'], 74)
        import_reviews(self.suite, self.suite / 'human_review.csv')
