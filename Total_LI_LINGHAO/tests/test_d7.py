"""Controlled single-component removals on the actual integrated engine."""
import unittest
from claim_agent.agent import run_case, estimate_tokens
from claim_agent.backends import system_prompt

class RepeatingBackend:
    name='scripted'
    def next(self,case_id,observations,sequential=False,variant='v2'):
        return {'calls':[{'tool':'get_claim','arguments':{'claim_id':case_id}}],
                'usage':{'input':estimate_tokens(observations)+estimate_tokens(system_prompt(variant,sequential)),'output':estimate_tokens([{'tool':'get_claim','arguments':{'claim_id':case_id}}])},'raw':'Injected repeated-action fault'}

class D7Tests(unittest.TestCase):
    def test_remove_dedup_exhausts_step_budget(self):
        normal=run_case('CLM-8850',backend=RepeatingBackend(),max_turns=5)
        ablated=run_case('CLM-8850',backend=RepeatingBackend(),max_turns=5,disable_dedup=True)
        self.assertEqual(normal['stop'],'duplicate_action')
        self.assertEqual(normal['turns'],2)
        self.assertEqual(ablated['turns'],5)
        self.assertIsNone(ablated['record'])
        self.assertGreater(ablated['tokens_in'],normal['tokens_in'])

    def test_remove_validity_projection_causes_blocked_proposal(self):
        normal=run_case('CLM-8894',approval=lambda p:True)
        ablated=run_case('CLM-8894',approval=lambda p:True,ablate_preauth=True)
        self.assertEqual(normal['record']['decision'],'request_document')
        self.assertEqual(ablated['stop'],'error')
        self.assertIsNone(ablated['record'])
        calls=ablated['trace'][-1]['calls']
        self.assertEqual(calls[0]['arguments']['decision']['decision'],'approve_in_principle')
        restored=run_case('CLM-8894',approval=lambda p:True)
        self.assertEqual(restored['record']['decision'],'request_document')

if __name__=='__main__':unittest.main()
