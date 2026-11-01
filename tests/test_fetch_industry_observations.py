import unittest
from scripts.fetch_industry_observations import normalize_csv, api_observations_to_csv


class FetchIndustryObservationsTests(unittest.TestCase):
    def test_official_api_json_adapter(self):
        data = {"observations": [
            {"date": "2000-01-03", "value": "100"},
            {"date": "2000-01-31", "value": "110"},
            {"date": "2000-02-01", "value": "."},
        ]}
        rows = normalize_csv(api_observations_to_csv(data, "NASDAQCOM"), "NASDAQCOM")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["value"], 110.0)

    def test_official_api_malformed_response_rejected(self):
        with self.assertRaises(ValueError):
            api_observations_to_csv({"error_message": "Invalid API key"}, "UNRATE")
        with self.assertRaises(ValueError):
            api_observations_to_csv({"observations": [{"date": "2000-01-01"}]}, "UNRATE")

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
            normalize_csv("observation_date,NOT_APPROVED\n2000-01-01,4\n", "NOT_APPROVED")

    def test_empty(self):
        with self.assertRaises(ValueError):
            normalize_csv("observation_date,CSUSHPINSA\n2000-01-01,.\n", "CSUSHPINSA")

    def test_fred_date_header_accepted(self):
        payload = "DATE,NASDAQCOM\n2000-01-03,100\n2000-01-31,110\n"
        self.assertEqual(normalize_csv(payload, "NASDAQCOM")[0]["value"], 110.0)

    def test_missing_date_header_rejected(self):
        with self.assertRaises(ValueError):
            normalize_csv("wrong,NASDAQCOM\n2000-01-03,100\n", "NASDAQCOM")


if __name__ == "__main__":
    unittest.main()
