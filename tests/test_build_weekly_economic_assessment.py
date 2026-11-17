import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from scripts.build_weekly_economic_assessment import snapshot, markdown


class WeeklyAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        folder = self.root / "data/industry_observations"
        folder.mkdir(parents=True)
        for series in ("NASDAQCOM", "CSUSHPINSA", "TOTALSL", "BUSLOANS", "PI", "UNRATE", "CPIAUCSL", "INDPRO"):
            rows = []
            for i in range(110):
                year, month = 2010 + i // 12, i % 12 + 1
                rows.append({"date": f"{year:04d}-{month:02d}-01",
                             "value": round(100 * math.exp(i * 0.01), 6)})
            with (folder / (series + "_monthly.csv")).open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["date", "value"])
                writer.writeheader()
                writer.writerows(rows)
            (folder / (series + "_metadata.json")).write_text(json.dumps({
                "series": series, "point_in_time_certified": False,
                "source_url": "https://example.org/" + series}))

    def test_latest_shared_month_and_lag(self):
        result = snapshot(self.root, "2019-06-15")
        self.assertEqual(result["common_observation_month"], "2019-02-01")
        self.assertEqual(result["months_since_common_observation"], 4)
        self.assertTrue(result["stale"])
        self.assertIn("Housing price", markdown(result) or "")

    def test_lagging_housing_does_not_stale_current_macro(self):
        housing = self.root / "data/industry_observations/CSUSHPINSA_monthly.csv"
        with housing.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["date", "value"])
            writer.writeheader()
            for i in range(90):
                writer.writerow({"date": f"{2010 + i // 12:04d}-{i % 12 + 1:02d}-01",
                                 "value": round(100 * math.exp(i * 0.01), 6)})
        result = snapshot(self.root, "2019-02-15")
        self.assertFalse(result["stale"])
        self.assertTrue(result["historical_comparison_stale"])
        self.assertEqual(result["sources"]["UNRATE"]["latest_used_month"], "2019-02-01")
        self.assertEqual(result["sources"]["CSUSHPINSA"]["latest_used_month"], "2017-06-01")
        self.assertEqual(result["common_observation_month"], "2017-06-01")

    def test_consumer_credit_release_lag_is_disclosed_and_bounded(self):
        folder = self.root / "data/industry_observations"
        for name in ("NASDAQCOM", "CSUSHPINSA", "TOTALSL", "BUSLOANS",
                     "PI", "UNRATE", "CPIAUCSL", "INDPRO"):
            path = folder / (name + "_monthly.csv")
            with path.open("a") as handle:
                for month in range(3, 11):
                    if name == "TOTALSL" and month > 8:
                        continue
                    if name == "CSUSHPINSA" and month > 8:
                        continue
                    handle.write(f"2019-{month:02d}-01,150\n")
        result = snapshot(self.root, "2019-11-04")
        self.assertFalse(result["stale"])
        self.assertEqual(result["sources"]["TOTALSL"]["observation_lag_months"], 3)
        self.assertTrue(result["historical_comparison_stale"])
        result = snapshot(self.root, "2019-12-04")
        self.assertTrue(result["stale"])

    def test_future_data_not_used(self):
        first = snapshot(self.root, "2018-01-15")
        path = self.root / "data/industry_observations/PI_monthly.csv"
        with path.open("a") as handle:
            handle.write("2025-01-01,999999\n")
        second = snapshot(self.root, "2018-01-15")
        self.assertEqual(first["housing_price_income_growth_gap_12m_log_pp"],
                         second["housing_price_income_growth_gap_12m_log_pp"])

    def test_source_metadata_must_block_pit_claim(self):
        path = self.root / "data/industry_observations/PI_metadata.json"
        metadata = json.loads(path.read_text())
        metadata["point_in_time_certified"] = True
        path.write_text(json.dumps(metadata))
        with self.assertRaises(ValueError):
            snapshot(self.root, "2018-01-15")


if __name__ == "__main__":
    unittest.main()


class V63DerivedFieldTests(unittest.TestCase):
    setUp = WeeklyAssessmentTests.setUp

    def test_v63_momentum_fields_use_only_dated_history(self):
        result = snapshot(self.root, "2018-01-15")
        # Constant 1% monthly log growth: 12m growth is flat, so momentum is zero.
        self.assertAlmostEqual(result["industrial_production_momentum_3m_pp"], 0.0, places=3)
        self.assertAlmostEqual(result["cpi_inflation_change_3m_pp"], 0.0, places=3)
        self.assertIsNotNone(result["unemployment_3m_avg_rise_from_12m_low_pp"])
        path = self.root / "data/industry_observations/INDPRO_monthly.csv"
        with path.open("a") as handle:
            handle.write("2025-01-01,999999\n")
        self.assertEqual(snapshot(self.root, "2018-01-15")["industrial_production_momentum_3m_pp"],
                         result["industrial_production_momentum_3m_pp"])


class UnpublishedYearAgoMonthTests(unittest.TestCase):
    setUp = WeeklyAssessmentTests.setUp

    def _drop(self, series, month):
        path = self.root / f"data/industry_observations/{series}_monthly.csv"
        rows = [r for r in csv.DictReader(path.open()) if not r["date"].startswith(month)]
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["date", "value"])
            writer.writeheader()
            writer.writerows(rows)

    def test_latest_computable_month_is_used_and_dated(self):
        # Latest month 2019-02; its year-earlier month 2018-02 was never published.
        self._drop("CPIAUCSL", "2018-02")
        result = snapshot(self.root, "2019-03-10")
        self.assertIsNotNone(result["cpi_inflation_12m_log_pct"])
        self.assertEqual(result["sources"]["CPIAUCSL"]["latest_used_month"], "2019-01-01")
        self.assertEqual(result["sources"]["CPIAUCSL"]["latest_available_month"], "2019-02-01")
        self.assertEqual(result["sources"]["CPIAUCSL"]["observation_lag_months"], 2)
        self.assertIn("not published", result["observation_notes"]["CPIAUCSL"])
        self.assertIn("Note (CPIAUCSL)", markdown(result))
        # Other series are untouched.
        self.assertEqual(result["sources"]["INDPRO"]["latest_used_month"], "2019-02-01")

    def test_no_deeper_fallback_and_no_imputation(self):
        self._drop("CPIAUCSL", "2018-02")
        self._drop("CPIAUCSL", "2018-01")
        result = snapshot(self.root, "2019-03-10")
        self.assertIsNone(result["cpi_inflation_12m_log_pct"])
        self.assertEqual(result["sources"]["CPIAUCSL"]["latest_used_month"], "2019-02-01")
        self.assertEqual(result["observation_notes"], {})
