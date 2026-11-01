import unittest
from scripts.industry_multifactor_research import analyze


def make_prices(n=110):
    return [{"date": f"{2000+i//12:04d}-{i%12+1:02d}-01",
             "value": str(100 + i * 2)} for i in range(n)]


class MultifactorTests(unittest.TestCase):
    def test_missing_indicator_not_imputed(self):
        prices = make_prices()
        indicator = [{"date": prices[55]["date"], "value": "4.0"}]
        result = analyze(prices, {"credit": indicator})
        group = result["groups"]["credit"]
        self.assertEqual(group["above"]["months"] + group["other"]["months"], 1)
        self.assertEqual(group["missing_months"], result["eligible_price_months"] - 1)

    def test_no_indicators_still_reports_acceleration(self):
        result = analyze(make_prices(), {})
        self.assertIn("acceleration", result["groups"])
        self.assertEqual(result["groups"]["acceleration"]["missing_months"], 0)

    def test_future_value_does_not_change_past_acceleration(self):
        prices = make_prices()
        first = analyze(prices, {})["observations"]
        prices[-1]["value"] = "1"
        second = analyze(prices, {})["observations"]
        self.assertEqual([(r["date"], r["acceleration"]) for r in first],
                         [(r["date"], r["acceleration"]) for r in second])

    def test_invalid_horizon_rejected(self):
        with self.assertRaises(ValueError):
            analyze(make_prices(), {}, horizon=0)


if __name__ == "__main__":
    unittest.main()
