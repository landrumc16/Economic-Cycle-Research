import unittest
from scripts.v4_economic_signals import build_signals

class V4SignalsTests(unittest.TestCase):
    def snapshot(self, series="UNRATE", value=4.5, delta=0.3, revised=False):
        return {"report_type": "V3_WEEKLY_ECONOMIC_EVIDENCE", "as_of": "2026-10-31",
                "series": {series: {"observation_value": value, "latest_observation": "2026-09-01",
                                    "status": "STAGED_REVISED_NOT_PIT"}},
                "week_over_week": {series: {"new_observation_date": True, "numeric_change": delta,
                                            "same_observation_revision_detected": revised}}}

    def test_unemployment_increase_is_adverse_directional_evidence(self):
        report = build_signals(self.snapshot())
        labor = next(x for x in report["signals"] if x["series"] == "UNRATE")
        self.assertEqual(labor["risk_evidence"], "ADVERSE_DIRECTIONAL_EVIDENCE")
        self.assertIsNone(report["crash_probability"])

    def test_cpi_change_is_not_inflation_acceleration(self):
        report = build_signals(self.snapshot("CPIAUCSL", 320, 1))
        cpi = next(x for x in report["signals"] if x["series"] == "CPIAUCSL")
        self.assertEqual(cpi["risk_evidence"], "NOT_ASSESSED")
        self.assertIn("cannot be inferred", cpi["interpretation"])

    def test_revision_does_not_become_new_signal(self):
        report = build_signals(self.snapshot(revised=True))
        labor = next(x for x in report["signals"] if x["series"] == "UNRATE")
        self.assertEqual(labor["direction"], "REVISED")
        self.assertEqual(labor["risk_evidence"], "NOT_ASSESSED")

    def test_missing_value_never_becomes_zero(self):
        report = build_signals(self.snapshot(value=None))
        labor = next(x for x in report["signals"] if x["series"] == "UNRATE")
        self.assertEqual(labor["direction"], "UNAVAILABLE")
        self.assertIsNone(labor["observation_value"])

if __name__ == "__main__":
    unittest.main()
