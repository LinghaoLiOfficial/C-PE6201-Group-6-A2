"""Offline contract tests, not D4 accuracy trials or the D3 checklist."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_system import run_case
from agent_system import config
from agent_system.tools import ClaimTools
from agent_system.prompt import build_prompt
from agent_system.protocol import parse_step
from agent_system.scripts import action, script_for, LIMIT_DECISION


class IntegrationContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.network = patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden"))
        self.network_mock = self.network.start()
        self.addCleanup(self.network.stop)

    def run_claim(self, **kwargs):
        return run_case("CLM-8925", output_dir=self.tmp.name, **kwargs)

    def test_approved_run_and_real_log(self):
        r = self.run_claim(operator_approved=True)
        self.assertEqual((r['status'], r['decision'], r['trigger']),
                         ('completed', 'escalate', 'annual_limit_exceeded'))
        self.assertEqual(r['action_count'], 1)
        self.assertEqual(r['turns'], 5)
        self.assertIn('remaining_annual_limit=9200', r['trace'][3]['observation'])
        self.assertEqual(json.loads(Path(r['decision_log']).read_text())['trigger'], r['trigger'])
        self.assertEqual(r['token_source'], 'synthetic')
        self.assertEqual(r['api_cost_usd'], 0)
        self.network_mock.assert_not_called()

    def test_confirmation_is_not_granted_by_default(self):
        r = self.run_claim()
        self.assertEqual(r['status'], 'not_recorded')
        self.assertEqual(r['action_count'], 0)
        self.assertEqual(r['trace'][-1]['status'], 'blocked')

    def test_suggest_blocks_even_with_approval(self):
        r = self.run_claim(autonomy='suggest', operator_approved=True)
        self.assertEqual(r['action_count'], 0)

    def test_act_records_without_confirmation(self):
        r = self.run_claim(autonomy='act')
        self.assertEqual(r['status'], 'completed')

    def test_run_isolation(self):
        first = self.run_claim(operator_approved=True)
        second = self.run_claim(operator_approved=True)
        third = self.run_claim()
        self.assertNotEqual(first['decision_log'], second['decision_log'])
        self.assertEqual((first['action_count'], second['action_count'], third['action_count']), (1, 1, 0))
        self.assertTrue(Path(first['decision_log']).exists())
        self.assertEqual(first['trace'], second['trace'])

    def test_versions_are_run_local(self):
        v1, v2 = ClaimTools(config.DATA_DIR, 'v1'), ClaimTools(config.DATA_DIR, 'v2')
        args = ('M-6118', '29881', '2026-09-14')
        before = v1.get_preauthorisation(*args)
        self.assertIn('valid_to=', before)
        self.assertIn('status=expired_before_service', v2.get_preauthorisation(*args))
        self.assertEqual(v1.get_preauthorisation(*args), before)
        self.assertIn('never infer validity from dates', build_prompt('v2'))
        self.assertNotIn('never infer validity from dates', build_prompt('v1'))
        self.assertEqual(self.run_claim(prompt_version='v1', operator_approved=True)['status'], 'completed')

    def test_cap_counts_actual_responses(self):
        r = self.run_claim(operator_approved=True, step_cap=2)
        self.assertEqual((r['stopped_by'], r['turns'], r['action_count']), ('step_cap', 2, 0))

    def test_budget_stops_before_tool_execution(self):
        r = self.run_claim(operator_approved=True, budget_usd=0)
        self.assertEqual(r['stopped_by'], 'budget_ceiling')
        self.assertEqual(r['trace'], [])

    def test_duplicate_write_is_blocked(self):
        steps = script_for('CLM-8925')
        steps.insert(-1, steps[-2])
        r = self.run_claim(operator_approved=True, scripted_steps=steps)
        self.assertEqual(r['action_count'], 1)
        self.assertEqual(r['trace'][-1]['status'], 'blocked')
        self.assertEqual(r['status'], 'completed_with_tool_issues')

    def test_final_record_disagreement(self):
        steps = script_for('CLM-8925')
        steps[-1] = 'Final: ' + json.dumps(dict(LIMIT_DECISION, trigger='duplicate_claim'))
        r = self.run_claim(operator_approved=True, scripted_steps=steps)
        self.assertEqual(r['status'], 'record_mismatch')

    def test_structured_request_survives_write(self):
        decision = dict(decision='request_document', reason='Contract fixture only',
                        evidence=[], missing={'item':'pre-authorisation reference',
                        'for_line':'29881', 'must_be_valid_on':'2026-09-14'})
        steps = [action('issue_decision_letter', claim_id='CLM-8894', **decision),
                 'Final: ' + json.dumps(decision)]
        r = run_case('CLM-8894', output_dir=self.tmp.name, scripted_steps=steps,
                     operator_approved=True)
        self.assertEqual(r['missing'], r['action_records'][0]['missing'])
        self.assertEqual(r['status'], 'completed')

    def test_structured_approval_survives_write(self):
        decision = dict(decision='approve_in_principle', reason='Schema test only', evidence=[],
                        lines=[{'code':'99213', 'amount':180, 'status':'covered'}],
                        approved_total=180, refused_total=0)
        r = run_case('CLM-8850', output_dir=self.tmp.name, operator_approved=True,
                     scripted_steps=[action('issue_decision_letter', claim_id='CLM-8850', **decision),
                                     'Final: ' + json.dumps(decision)])
        self.assertEqual(r['action_records'][0]['lines'], decision['lines'])
        self.assertEqual(r['approved_total'], 180)

    def test_literal_parser_cannot_execute_code(self):
        with self.assertRaises(ValueError):
            parse_step('Action: get_claim(claim_id=__import__("os").getcwd())')
        with self.assertRaises(ValueError):
            parse_step('Final: escalate because the limit is exceeded')

    def test_write_must_be_alone(self):
        steps = [action('get_claim', claim_id='CLM-8925') + '\n' +
                 action('issue_decision_letter', claim_id='CLM-8925', **LIMIT_DECISION)]
        r = self.run_claim(operator_approved=True, scripted_steps=steps)
        self.assertEqual(r['stopped_by'], 'invalid_write_batch')
        self.assertEqual(r['action_count'], 0)

    def test_wrong_case_cannot_be_written(self):
        steps = [action('issue_decision_letter', claim_id='CLM-8842', **LIMIT_DECISION),
                 'Final: ' + json.dumps(LIMIT_DECISION)]
        r = self.run_claim(operator_approved=True, scripted_steps=steps)
        self.assertEqual(r['action_count'], 0)
        self.assertIn('claim_id does not match', r['trace'][0]['observation'])

    def test_missing_script_and_live_prices_fail_explicitly(self):
        with self.assertRaisesRegex(ValueError, 'Unknown claim'):
            run_case('CLM-9999', output_dir=self.tmp.name)
        with self.assertRaisesRegex(ValueError, 'explicit model'):
            self.run_claim(backend='live')

    def test_synthetic_usage_not_used_by_live_adapter(self):
        self.network.stop()
        self.addCleanup(lambda: None)
        payload = {'choices':[{'message':{'content':'Final: '+json.dumps(LIMIT_DECISION)}}],
                   'usage':{'prompt_tokens':123,'completion_tokens':45}}
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(payload)
        with patch.dict('os.environ', {'OPENROUTER_API_KEY':'test-only'}), patch(
                'urllib.request.urlopen', return_value=response) as request:
            r = self.run_claim(backend='live', price_in_per_m=1, price_out_per_m=2)
        self.assertEqual((r['tokens_in'],r['tokens_out']), (123,45))
        self.assertEqual(r['token_source'], 'api_usage')
        self.assertAlmostEqual(r['cost_usd'], 0.000213)
        self.assertEqual(r['status'], 'not_recorded')
        self.assertEqual(request.call_count, 1)


if __name__ == '__main__':
    unittest.main()
