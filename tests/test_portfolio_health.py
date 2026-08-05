import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "portfolio_health.py"
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


if __name__ == "__main__":
    unittest.main()
