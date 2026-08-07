import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "portfolio_health.py"
WORKFLOW = ROOT / ".github" / "workflows" / "portfolio-health.yml"
SPEC = importlib.util.spec_from_file_location("portfolio_health", SCRIPT)
portfolio_health = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portfolio_health)


class PortfolioHealthTests(unittest.TestCase):
    def test_repository_passes_four_local_audit_layers(self):
        result = portfolio_health.run(check_live=False, fix=False)
        self.assertEqual(result["status"], "passed", result["issues"])

    def test_auto_fixer_is_idempotent(self):
        self.assertEqual(portfolio_health.apply_safe_fixes(), [])

    def test_twice_daily_schedule_is_central_time_dst_safe(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('cron: "15 0,1,12,13 * * *"', source)
        self.assertIn("TZ=America/Chicago", source)
        self.assertIn('== "07"', source)
        self.assertIn('== "19"', source)
        self.assertIn("needs: schedule-gate", source)

    def test_privacy_contract_uses_generic_license_detection(self):
        contract_path = ROOT / "portfolio_contract.json"
        source = contract_path.read_text(encoding="utf-8")
        self.assertNotIn("14790", source)

        contract = json.loads(source)
        self.assertTrue(any(
            re.search(pattern, "Minnesota license #12345")
            for pattern in contract["forbidden_patterns"]
        ))


if __name__ == "__main__":
    unittest.main()
