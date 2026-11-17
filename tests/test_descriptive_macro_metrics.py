"""Regression tests for calendar-aligned macro transformations."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from descriptive_macro_metrics import describe

class DescriptiveMacroTests(unittest.TestCase):
    def test_cpi_yoy_and_unemployment_pp(self):
        data = {
            "CPIAUCSL": {"2025-09-01": 300, "2026-09-01": 312},
            "UNRATE": {"2026-06-01": 4.0, "2026-09-01": 4.5,
                       "2025-09-01": 3.8},
            "GDPC1": {"2025-07-01": 20000, "2026-07-01": 20500}}
        result = describe(data)["metrics"]
        self.assertEqual(result["cpi_yoy_pct"]["value"], 4.0)
        self.assertEqual(result["unemployment_3m_change_pp"]["value"], 0.5)
        self.assertEqual(result["unemployment_12m_change_pp"]["value"], 0.7)
        self.assertEqual(result["real_gdp_yoy_pct"]["value"], 2.5)

    def test_gap_is_not_replaced_by_previous_available_month(self):
        result = describe({"CPIAUCSL": {
            "2025-08-01": 300, "2026-09-01": 320}})["metrics"]["cpi_yoy_pct"]
        self.assertIsNone(result["value"])
        self.assertEqual(result["baseline_date"], "2025-09-01")

    def test_zero_baseline_not_accepted(self):
        result = describe({"CPIAUCSL": {
            "2025-09-01": 0, "2026-09-01": 320}})["metrics"]["cpi_yoy_pct"]
        self.assertIsNone(result["value"])

    def test_unpublished_baseline_uses_previous_month_with_its_own_baseline(self):
        # October 2025 CPI was never published: October 2026 has no baseline.
        result = describe({"CPIAUCSL": {
            "2025-09-01": 300, "2026-09-01": 312, "2026-10-01": 313}})["metrics"]["cpi_yoy_pct"]
        self.assertEqual(result["value"], 4.0)
        self.assertEqual(result["latest_date"], "2026-09-01")
        self.assertEqual(result["latest_available_date"], "2026-10-01")
        self.assertEqual(result["baseline_date"], "2025-09-01")
        self.assertIn("baseline unpublished", result["note"])

    def test_no_deeper_fallback_and_no_baseline_substitution(self):
        result = describe({"CPIAUCSL": {
            "2025-08-01": 300, "2026-09-01": 312, "2026-10-01": 313}})["metrics"]["cpi_yoy_pct"]
        self.assertIsNone(result["value"])
        self.assertIsNone(result["note"])
        self.assertEqual(result["latest_date"], "2026-10-01")

    def test_quarterly_gdp_has_no_monthly_fallback(self):
        result = describe({"GDPC1": {"2025-04-01": 100, "2026-07-01": 103}})["metrics"]["real_gdp_yoy_pct"]
        self.assertIsNone(result["value"])


if __name__ == "__main__":
    unittest.main()
