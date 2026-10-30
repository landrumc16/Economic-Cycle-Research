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

if __name__ == "__main__":
    unittest.main()
