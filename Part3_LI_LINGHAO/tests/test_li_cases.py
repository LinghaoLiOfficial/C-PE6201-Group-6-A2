"""Tests for LI LINGHAO's five original case fixtures and scripted runs."""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from case_request.validate_cases import validate
from integration import run_case
from integration.li_checks import check_li_case, load_li_labels
from integration.scripts import LI_CASE_IDS

class LICaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "data_A"
        import shutil
        from integration import config
        shutil.copytree(config.DATA_DIR, self.data)
        fixture = json.loads(Path("Part3_LI_LINGHAO/case_request/cases_LI_LINGHAO/fixtures_LI_LINGHAO.json").read_text())
        claims_path = self.data / "claims.json"
        claims = json.loads(claims_path.read_text()); claims.extend(fixture["EXTRA_CLAIMS"])
        claims_path.write_text(json.dumps(claims))
        self.labels = load_li_labels()

    def test_fixture_validation(self):
        self.assertEqual(validate(), [])

    def test_all_five_scripted_cases_pass_code_checks(self):
        for cid in LI_CASE_IDS:
            result = run_case(cid, data_dir=self.data, output_dir=self.tmp.name, operator_approved=True)
            check = check_li_case(result, self.labels[cid])
            self.assertTrue(check["code_passed"], f"{cid}: {check['failures']}")

    def test_negative_case_repeats_three_times(self):
        for _ in range(3):
            result = run_case("CLM-16305", data_dir=self.data, output_dir=self.tmp.name, operator_approved=True)
            self.assertEqual((result["decision"], result["trigger"]), ("escalate", "outside_policy_dates"))

if __name__ == "__main__":
    unittest.main()
