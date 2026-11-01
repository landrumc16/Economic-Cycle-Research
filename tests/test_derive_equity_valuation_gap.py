import unittest
from scripts.derive_equity_valuation_gap import derive


class EquityValuationTests(unittest.TestCase):
    def test_gap_orientation(self):
        e = [{"date": "2000-01-01", "value": "3.0"}]
        t = [{"date": "2000-01-01", "value": "6.0"}]
        self.assertEqual(derive(e, t)[0]["value"], 3.0)

    def test_missing_month_not_filled(self):
        e = [{"date": "2000-01-01", "value": "3.0"},
             {"date": "2000-02-01", "value": "4.0"}]
        t = [{"date": "2000-02-01", "value": "5.0"}]
        self.assertEqual([r["date"] for r in derive(e, t)], ["2000-02-01"])

    def test_duplicate_dates_rejected(self):
        e = [{"date": "2000-01-01", "value": "3.0"}] * 2
        with self.assertRaises(ValueError):
            derive(e, [{"date": "2000-01-01", "value": "6.0"}])


if __name__ == "__main__":
    unittest.main()
