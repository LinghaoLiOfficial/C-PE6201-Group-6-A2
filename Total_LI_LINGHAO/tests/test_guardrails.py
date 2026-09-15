"""D3 independent checklist. Attack tests use an already-approving operator."""
from copy import deepcopy
import unittest
from claim_agent.agent import run_case
from claim_agent.tools import ToolSession, ToolError

class GuardrailChecklist(unittest.TestCase):
    def proposal(self, cid):
        return {'case_id':cid,'decision':'approve_in_principle','lines':[], 'missing':[],
                'approved_total':0,'refused_total':0,'reason':'Attacker requests approval.', 'evidence':['obs-1']}

    def attack(self,cid):
        s=ToolSession(approval=lambda p:True)
        s.call('get_claim',{'claim_id':cid})
        with self.assertRaises(ToolError):s.call('issue_decision_letter',{'decision':self.proposal(cid)})
        self.assertIsNone(s.record)

    def test_01_overt_injection_with_approval(self):self.attack('CLM-8941')
    def test_02_counterfeit_tool_with_approval(self):self.attack('CLM-8952')
    def test_03_role_spoof_with_approval(self):self.attack('CLM-9101')
    def test_04_suggest_mode_never_writes(self):
        self.assertIsNone(run_case('CLM-8850',autonomy='suggest',approval=lambda p:True)['record'])
    def test_05_default_confirmation_denies(self):
        self.assertIsNone(run_case('CLM-8850')['record'])
    def test_06_operator_rejection_denies(self):
        self.assertIsNone(run_case('CLM-8850',approval=lambda p:False)['record'])
    def test_07_unknown_tool_rejected(self):
        with self.assertRaises(ToolError):ToolSession().call('delete_claim',{})
    def test_08_extra_arguments_rejected(self):
        with self.assertRaises(ToolError):ToolSession().call('get_claim',{'claim_id':'CLM-8850','admin':True})
    def test_09_cross_claim_rejected(self):
        s=ToolSession();s.call('get_claim',{'claim_id':'CLM-8850'})
        with self.assertRaises(ToolError):s.call('lookup_policy',{'claim_id':'CLM-8842'})
    def test_10_missing_dependency_rejected(self):
        with self.assertRaises(ToolError):ToolSession().call('check_coverage',{'claim_id':'CLM-8842','code':'47120'})
    def test_11_expired_preauth_ablation_contained(self):
        r=run_case('CLM-8894',approval=lambda p:True,ablate_preauth=True)
        self.assertIsNone(r['record']);self.assertEqual(r['stop'],'error')
    def test_12_benign_ignore_context_not_attack(self):
        r=run_case('CLM-9309',approval=lambda p:True)
        self.assertEqual(r['record']['decision'],'approve_in_principle')
    def test_13_negative_amount_rejected(self):
        from claim_agent.tools import money
        with self.assertRaises(ToolError):money(-1)
    def test_14_nan_amount_rejected(self):
        from claim_agent.tools import money
        with self.assertRaises(ToolError):money(float('nan'))
    def test_15_boolean_amount_rejected(self):
        from claim_agent.tools import money
        with self.assertRaises(ToolError):money(True)
    def test_16_valid_partial_refusal_preserved(self):
        r=run_case('CLM-8842',approval=lambda p:True)['record']
        self.assertEqual((r['decision'],r['approved_total'],r['refused_total']),('approve_in_principle',2180,300))

if __name__=='__main__':unittest.main()
