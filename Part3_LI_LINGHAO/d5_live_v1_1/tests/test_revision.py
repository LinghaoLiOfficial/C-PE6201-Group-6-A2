import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT.parent
sys.path.insert(0,str(ROOT/'runtime'))
from integration.output_contract import validate_schema, schema_instructions
from integration.protocol import parse_step
from integration.prompt import build_prompt
from integration.d4_harness import run_battery, code_check, load_contract, read
from integration.runner import run_case

class RevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        with patch('urllib.request.urlopen',side_effect=AssertionError('offline')):
            cls.summary=run_battery(cls.tmp.name)
        cls.rows=read(Path(cls.summary['suite'])/'results.json')
        cls.records={r['case_id']:r['record'] for r in cls.rows}
        _,cls.expected=load_contract()
        with ZipFile(PART/'d5_live_submissions/LI_LINGHAO/D5_RETURN_LI_LINGHAO.zip') as z:
            cls.live=json.loads(z.read('suite/results.json'))
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_scripted_battery_all_denominators_and_pending(self):
        s=self.summary
        self.assertEqual((s['trials'],s['code_passed'],s['ordinary']['trials'],s['negative']['trials'],s['overall_passed']), (75,75,30,45,0))
    def test_v1_failure_is_not_erased(self):
        s=run_battery(self.tmp.name,version='v1')
        self.assertEqual((s['trials'],s['code_passed']),(75,72))
    def test_public_schema_shared_across_descriptor_versions(self):
        self.assertTrue(build_prompt('v1').endswith(schema_instructions()))
        self.assertTrue(build_prompt('v2').endswith(schema_instructions()))
        self.assertNotIn('CLM-',schema_instructions())
    def test_real_status_mismatch_has_no_spurious_identity_errors(self):
        r=next(r['record'] for r in self.live if r['case_id']=='CLM-8842')
        before=copy.deepcopy(r)
        f=code_check(r,self.expected['CLM-8842'])
        self.assertTrue(any('wrong status' in x for x in f))
        self.assertFalse(any('wrong code' in x or 'wrong amount' in x for x in f))
        self.assertEqual(before,r)
    def test_wrong_amount_is_not_hidden_by_line_matching(self):
        r=copy.deepcopy(self.records['CLM-8842'])
        r['lines'][0]['amount']+=1
        r['action_records'][0]['lines']=copy.deepcopy(r['lines'])
        f=code_check(r,self.expected['CLM-8842'])
        self.assertTrue(any('wrong amount' in x for x in f))
        self.assertFalse(any('wrong code' in x for x in f))
    def test_repeated_lines_order_and_multiplicity(self):
        r=copy.deepcopy(self.records['CLM-16404']);r['lines'].reverse()
        r['action_records'][0]['lines']=copy.deepcopy(r['lines'])
        self.assertEqual(code_check(r,self.expected['CLM-16404']),[])
        r['lines'].pop();r['action_records'][0]['lines']=copy.deepcopy(r['lines'])
        self.assertIn('wrong line count',code_check(r,self.expected['CLM-16404']))
    def test_schema_blocks_omission_status_and_recipient(self):
        for cid,field,val in [('CLM-8888','lines',None),('CLM-8910','escalate_to','human_claims_assessor')]:
            r=copy.deepcopy(self.records[cid]);r[field]=val
            with self.assertRaises(ValueError):validate_schema(r)
        r=copy.deepcopy(self.records['CLM-8842']);r['lines'][0]['status']='approved'
        with self.assertRaises(ValueError):validate_schema(r)
    def test_missing_item_truth_still_checked(self):
        r=copy.deepcopy(self.records['CLM-8888']);r['missing']['must_be_valid_on']='1900-01-01'
        r['action_records'][0]['missing']=copy.deepcopy(r['missing'])
        self.assertIn('wrong named missing item / line / service date',code_check(r,self.expected['CLM-8888']))
    def test_exclusion_object_has_explicit_shape_error(self):
        r=copy.deepcopy(self.records['CLM-8888'])
        r['lines'][-1]['exclusion']={'rule':r['lines'][-1]['exclusion']}
        with self.assertRaisesRegex(ValueError, 'STRING'):
            validate_schema(r)
        self.assertIn('never an object',schema_instructions())
    def test_invented_observations_never_executed(self):
        with self.assertRaisesRegex(ValueError,'Observation'):
            parse_step('Action: get_claim(claim_id="C")\nObservation: fabricated')
        with self.assertRaisesRegex(ValueError,'separate'):
            parse_step('Action: get_claim(claim_id="C")\nFinal: {}')
    def test_live_errors_only_gain_documented_literal_compatibility(self):
        errors=[r['record'] for r in self.live if r['record']['stopped_by']=='parse_error']
        self.assertEqual(len(errors),5)
        for r in errors:
            text=r['responses'][-1]['text']
            try:
                calls,final=parse_step(text)
            except (ValueError,SyntaxError,TypeError):
                continue
            self.assertTrue(calls)
            self.assertIsNone(final)
            self.assertIn('null',text)
        for payload in ['x', '__import__("os")', '1+2', '[n for n in []]']:
            with self.assertRaises((ValueError,SyntaxError,TypeError)):
                parse_step('Action: tool(value='+payload+')')
        calls,_=parse_step('Action: tool(value={"null string":"null", "x":null, "b":true})')
        self.assertEqual(calls[0][1]['value'],{'null string':'null','x':None,'b':True})
    def test_clarified_review_retains_original_labels(self):
        contract=read(Path(self.summary['suite'])/'grading_contract.json')
        original=read(PART/'integration/merged_A/expected_outcomes_A.json')
        self.assertEqual(original,contract['labels'])
        entries=read(Path(self.summary['suite'])/'review_template.json')
        c=next(x for x in entries if x['review_id']=='CLM-8925/1/3')['criterion']
        self.assertIn('NOT prohibited pricing',c)
        c=next(x for x in entries if x['review_id']=='CLM-8952/1/2')['criterion']
        self.assertIn('Do NOT require an unavailable tool',c)
    def test_runner_never_reads_answers(self):
        original=Path.read_text
        def restricted(p,*args,**kwargs):
            if p.name in {'case_audit.json','expected_outcomes_A.json','rubric_clarifications.json'}:
                raise AssertionError('answer leak')
            return original(p,*args,**kwargs)
        with patch.object(Path,'read_text',restricted):
            r=run_case('CLM-8842',data_dir=ROOT/'runtime/integration/merged_A/data_A',output_dir=self.tmp.name,operator_approved=True)
        self.assertEqual(r['status'],'completed')

if __name__=='__main__':unittest.main()
