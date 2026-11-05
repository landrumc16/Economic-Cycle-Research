"""Plain-language indicator guidance must remain descriptive and fail closed."""
import unittest
from datetime import date

from scripts.v6_public_site import indicator_guidance


class IndicatorGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.assessment = {
            "stale": False,
            "industrial_production_growth_12m_log_pct": -1.2,
            "unemployment_rate_pct": 4.8,
            "unemployment_change_3m_pp": 0.3,
            "cpi_inflation_12m_log_pct": 2.7,
            "business_credit_growth_12m_log_pct": 1.1,
            "sources": {key: {"latest_used_month": "2026-10",
                              "source_url": "https://fred.stlouisfed.org/series/" + key}
                        for key in ("INDPRO", "UNRATE", "CPIAUCSL", "BUSLOANS")},
        }

    def test_weak_growth_and_rising_unemployment_are_cautions(self):
        result = indicator_guidance(self.assessment, "PASS", date(2026, 11, 5))
        self.assertIn("decreased", result["Growth"][0])
        self.assertIn("caution", result["Jobs"][1])
        self.assertIn("not proof of recession", result["Jobs"][1])

    def test_inflation_does_not_imply_acceleration(self):
        result = indicator_guidance(self.assessment, "PASS", date(2026, 11, 5))
        self.assertIn("not whether inflation is accelerating", result["Inflation"][1])

    def test_lending_is_not_stress_proxy(self):
        result = indicator_guidance(self.assessment, "PASS", date(2026, 11, 5))
        self.assertIn("not a standalone measure", result["Business credit"][1])

    def test_stale_and_missing_data_fail_closed(self):
        for status in ("STALE_RESEARCH_ONLY", "PASS"):
            assessment = dict(self.assessment)
            if status == "PASS":
                assessment["stale"] = True
            result = indicator_guidance(assessment, status, date(2026, 11, 5))
            self.assertTrue(all("Insufficient current evidence" in row[0] for row in result.values()))
        assessment = dict(self.assessment)
        assessment["sources"] = {}
        result = indicator_guidance(assessment, "PASS", date(2026, 11, 5))
        self.assertTrue(all("Insufficient current evidence" in row[0] for row in result.values()))

    def test_unemployment_level_alone_does_not_establish_trend(self):
        assessment = dict(self.assessment)
        assessment["unemployment_change_3m_pp"] = None
        result = indicator_guidance(assessment, "PASS", date(2026, 11, 5))
        self.assertIn("trend is not", result["Jobs"][0])


if __name__ == "__main__":
    unittest.main()
