"""Resource, protocol and accounting boundaries at the actual engine."""
import json,tempfile,unittest
from pathlib import Path
from claim_agent.agent import run_case

class FixedBackend:
    name='scripted'
    def __init__(self,calls,usage=None):self.calls=calls;self.usage=usage or {'input':10,'output':10}
    def next(self,*args):return {'calls':self.calls,'usage':self.usage,'raw':self.calls}

class LoopTests(unittest.TestCase):
    def test_dependent_batch_has_no_partial_reads(self):
        b=FixedBackend([{'tool':'get_claim','arguments':{'claim_id':'CLM-8850'}},{'tool':'lookup_policy','arguments':{'claim_id':'CLM-8850'}}])
        r=run_case('CLM-8850',backend=b)
        self.assertEqual(r['observations'],[])
        self.assertIn('same-turn',r['trace'][0]['error'])
    def test_token_cap_blocks_action_after_billed_response(self):
        b=FixedBackend([{'tool':'get_claim','arguments':{'claim_id':'CLM-8850'}}],{'input':90,'output':20})
        r=run_case('CLM-8850',backend=b,token_limit=100)
        self.assertEqual(r['stop'],'token_cap');self.assertEqual(r['observations'],[])
        self.assertEqual(r['tokens_in']+r['tokens_out'],110)
    def test_dollar_cap_blocks_action(self):
        b=FixedBackend([{'tool':'get_claim','arguments':{'claim_id':'CLM-8850'}}],{'input':1,'output':1,'cost':.02})
        r=run_case('CLM-8850',backend=b,budget_usd=.01)
        self.assertEqual(r['stop'],'budget_cap');self.assertIsNone(r['record'])
    def test_malformed_block_is_loud(self):
        r=run_case('CLM-8850',backend=FixedBackend(None))
        self.assertEqual(r['stop'],'error');self.assertIn('invalid action block',r['trace'][0]['error'])
    def test_written_record_contains_instrumentation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'decisions.jsonl';r=run_case('CLM-8850',approval=lambda x:True,ledger=p)
            row=json.loads(p.read_text())
            for name in ['turns','tokens_in','tokens_out','cost_usd']:
                self.assertEqual(row[name],r[name])
    def test_unknown_case_is_loud(self):
        r=run_case('CLM-UNKNOWN')
        self.assertEqual(r['stop'],'error');self.assertIsNone(r['record'])
if __name__=='__main__':unittest.main()
