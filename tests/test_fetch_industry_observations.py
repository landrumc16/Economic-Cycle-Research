import unittest
from scripts.fetch_industry_observations import normalize_csv


class FetchIndustryObservationsTests(unittest.TestCase):
    def test_daily_month_end_uses_last_available(self):
        payload = "observation_date,NASDAQCOM\n2000-01-03,100\n2000-01-31,110\n2000-02-01,120\n"
        rows = normalize_csv(payload, "NASDAQCOM")
        self.assertEqual([r["value"] for r in rows], [110.0, 120.0])
        self.assertEqual(rows[0]["last_observed_date"], "2000-01-31")

    def test_missing_daily_observation(self):
        payload = "observation_date,NASDAQCOM\n2000-01-03,.\n2000-01-31,110\n"
        self.assertEqual(len(normalize_csv(payload, "NASDAQCOM")), 1)

    def test_unapproved_series(self):
        with self.assertRaises(ValueError):
            normalize_csv("observation_date,UNRATE\n2000-01-01,4\n", "UNRATE")

    def test_empty(self):
        with self.assertRaises(ValueError):
            normalize_csv("observation_date,CSUSHPINSA\n2000-01-01,.\n", "CSUSHPINSA")

    def test_fred_date_header_accepted(self):
        payload = "DATE,NASDAQCOM\\n2000-01-03,100\\n2000-01-31,110\\n"
        self.assertEqual(normalize_csv(payload, "NASDAQCOM")[0]["value"], 110.0)

    def test_missing_date_header_rejected(self):
        with self.assertRaises(ValueError):
            normalize_csv("wrong,NASDAQCOM\\n2000-01-03,100\\n", "NASDAQCOM")


if __name__ == "__main__":
    unittest.main()
