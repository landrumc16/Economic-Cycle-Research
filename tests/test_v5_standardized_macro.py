import unittest
from scripts.v5_standardized_macro import transform, build

class V5MacroTests(unittest.TestCase):
    def test_cpi_twelve_month_inflation(self):
        result = transform("CPIAUCSL", [{"date": "2025-09-01", "value": 300},
                                          {"date": "2026-09-01", "value": 309}], "2026-10-31")
        self.assertEqual(result["value"], 3.0)

    def test_gdp_quarterly_annualized(self):
        result = transform("GDPC1", [{"date": "2026-04-01", "value": 100},
                                       {"date": "2026-07-01", "value": 101}], "2026-10-31")
        self.assertAlmostEqual(result["value"], 4.060401, places=5)

    def test_unemployment_percentage_point_change(self):
        result = transform("UNRATE", [{"date": "2026-06-01", "value": 4.0},
                                        {"date": "2026-09-01", "value": 4.4}], "2026-10-31")
        self.assertAlmostEqual(result["value"], 0.4)

    def test_missing_history_not_invented(self):
        result = build({"schema_version": 1, "as_of": "2026-10-31", "series": {}})
        self.assertEqual(result["available"], 0)

    def test_future_release_rejected(self):
        with self.assertRaises(ValueError):
            transform("CPIAUCSL", [{"date": "2026-09-01", "value": 300,
                                     "release_date": "2026-11-01"}], "2026-10-31")

    def test_weekly_claims_are_monthly_averaged(self):
        result = transform("ICSA", [
            {"date": "2026-08-01", "value": 200},
            {"date": "2026-08-08", "value": 220},
            {"date": "2026-09-05", "value": 231},
            {"date": "2026-09-12", "value": 231},
        ], "2026-10-31")
        self.assertEqual(result["status"], "DESCRIPTIVE_TRANSFORM_AVAILABLE")
        self.assertEqual(result["value"], 10.0)
        self.assertFalse(result["predictive_use_approved"])

    def test_duplicate_vintages_rejected(self):
        with self.assertRaises(ValueError):
            transform("UNRATE", [{"date": "2026-09-01", "value": 4.0},
                                   {"date": "2026-09-01", "value": 4.1}], "2026-10-31")

if __name__ == "__main__":
    unittest.main()
