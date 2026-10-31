"""Regression tests for research-only historical comparisons and source gating."""
import unittest
from scripts.current_cycle_assessment import assess
from scripts.historical_macro_analogues import compare, features_at

class CurrentCycleAssessmentTests(unittest.TestCase):
    def test_missing_financial_values_do_not_promote_mechanism(self):
        report = {"economic_cycle": {"domains": {}}, "financial_housing": {"domains": {
            "credit": {"value": None, "quality": "MISSING"},
            "yield_curve": {"value": None, "quality": "MISSING"},
        }}}
        result = assess(report)
        self.assertEqual(result["mechanism_lenses"]["credit_housing"]["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["mechanism_lenses"]["monetary_tightening"]["status"], "INSUFFICIENT_EVIDENCE")
        self.assertIsNone(result["crash_probability"])

    def test_unapproved_financial_values_do_not_promote_mechanism(self):
        report = {"economic_cycle": {"domains": {}}, "financial_housing": {"domains": {
            "credit": {"value": 4.5, "quality": "STAGED_NOT_APPROVED"},
        }}}
        result = assess(report)
        self.assertEqual(result["mechanism_lenses"]["credit_housing"]["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["financial_context"]["credit"]["value"], 4.5)

    def test_macro_context_is_not_forecast(self):
        report = {"economic_cycle": {"domains": {
            "growth": {"observation": 2.0}, "labor": {"observation": 0.0},
            "inflation": {"observation": 3.0},
        }}, "financial_housing": {"domains": {}}}
        result = assess(report)
        self.assertEqual(result["mechanism_lenses"]["inflation_supply_shock"]["status"], "CONTEXT_ONLY_NOT_CLASSIFIED")
        self.assertIsNone(result["validated_cycle_stage"])
        self.assertEqual(result["publication"], "BLOCKED")

class HistoricalAnalogueTests(unittest.TestCase):
    def test_missing_current_data_fails_closed(self):
        result = compare({"UNRATE": {}, "CPIAUCSL": {}, "GDPC1": {}}, {"metrics": {}})
        self.assertEqual(result["status"], "INSUFFICIENT_CURRENT_DATA")
        self.assertEqual(result["analogues"], [])
        self.assertEqual(result["publication"], "BLOCKED")

    def test_uses_same_quarter_gdp_and_yoy_cpi(self):
        data = {
            "UNRATE": {"2000-03-01": 4.0, "1999-12-01": 4.2},
            "CPIAUCSL": {"2000-03-01": 110, "1999-03-01": 100},
            "GDPC1": {"2000-01-01": 220, "1999-01-01": 200},
        }
        result = features_at(data, "2000-03-01")
        self.assertAlmostEqual(result["real_gdp_yoy_pct"], 10)
        self.assertAlmostEqual(result["cpi_yoy_pct"], 10)
        self.assertAlmostEqual(result["unemployment_3m_change_pp"], -0.2)

if __name__ == "__main__":
    unittest.main()
