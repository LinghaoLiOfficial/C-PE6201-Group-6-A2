"""Three-outcome regression tests with all HTTP calls forbidden."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_minimal import run_minimal
from integration import run_case
from integration.tools import ClaimTools
from integration import config
from integration.minimal_checks import check_minimal, load_key


class MinimalFlowTests(unittest.TestCase):
    def test_both_versions_complete_real_tool_flows(self):
        with tempfile.TemporaryDirectory() as folder, patch('urllib.request.urlopen',side_effect=AssertionError('offline')) as net:
            for version in ['v1','v2']:
                summary, results=run_minimal(version,folder)
                self.assertEqual((summary['trials'],summary['code_passed'],summary['negative_trials']), (7,7,6))
                self.assertEqual(len({r['record']['decision_log'] for r in results}),7)
                for r in results:
                    logged=json.loads(Path(r['record']['decision_log']).read_text())
                    self.assertEqual(logged['decision'],r['record']['decision'])
                    self.assertEqual(r['record']['turns'],5 if r['case_id']=='CLM-8925' else 7)
                    for row in r['record']['trace']:
                        if row['tool']=='get_preauthorisation':
                            self.assertEqual('date_of_service' in row['args'],version=='v2')
                request=next(r['record'] for r in results if r['case_id']=='CLM-8894')
                observation=next(row['observation'] for row in request['trace'] if row['tool']=='get_preauthorisation')
                self.assertIn('PA-5640',observation)
                self.assertIn('2026-05-31',observation)
            net.assert_not_called()

    def test_all_three_gates_stay_closed_without_confirmation(self):
        with tempfile.TemporaryDirectory() as folder:
            for cid in ['CLM-8842','CLM-8894','CLM-8925']:
                result=run_case(cid,output_dir=folder)
                self.assertEqual((result['status'],result['action_count']),('not_recorded',0))

    def test_wrong_amount_or_missing_item_fails_even_if_decision_is_right(self):
        with tempfile.TemporaryDirectory() as folder:
            key=load_key()
            approved=run_case('CLM-8842',output_dir=folder,operator_approved=True)
            approved['approved_total']=2480
            approved['action_records'][0]['approved_total']=2480
            self.assertFalse(check_minimal(approved,key['CLM-8842'])['code_passed'])
            request=run_case('CLM-8894',output_dir=folder,operator_approved=True)
            request['missing']['for_line']='62480'
            request['action_records'][0]['missing']['for_line']='62480'
            self.assertFalse(check_minimal(request,key['CLM-8894'])['code_passed'])

    def test_v2_expired_evidence_is_available_without_raw_date_reasoning(self):
        tool=ClaimTools(config.DATA_DIR,'v2')
        text=tool.get_preauthorisation('M-6118','29881','2026-09-09')
        self.assertIn('status=expired_before_service',text)
        self.assertIn('preauth_id=PA-5640',text)
        self.assertIn('valid_to=2026-05-31',text)


if __name__=='__main__':
    unittest.main()
