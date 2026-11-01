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

    def test_joint_cells_partition_complete_case_months(self):
        prices = make_prices(120)
        indicator = [{"date": row["date"], "value": str(i)}
                     for i, row in enumerate(prices) if i % 3 != 0]
        result = analyze(prices, {"credit": indicator})
        joint = result["joint_comparisons"]["credit"]
        cells = joint["cells"].values()
        self.assertEqual(sum(cell["months"] for cell in cells), joint["eligible_months"])
        self.assertEqual(sum(cell["declines"] + cell["no_decline"] for cell in cells),
                         joint["eligible_months"])
        self.assertEqual(joint["eligible_months"] + joint["missing_months"],
                         result["eligible_price_months"])

    def test_joint_no_overlap_explicit(self):
        result = analyze(make_prices(), {"credit": [{"date": "1900-01-01", "value": "5"}]})
        self.assertEqual(result["joint_comparisons"]["credit"]["status"], "NO_OVERLAP")

    def test_duplicate_indicator_dates_rejected(self):
        with self.assertRaises(ValueError):
            analyze(make_prices(), {"credit": [
                {"date": "2005-01-01", "value": "1"},
                {"date": "2005-01-01", "value": "2"}]})

    def test_three_factor_cells_partition_complete_cases(self):
        prices = make_prices(120)
        income = [{"date": row["date"], "value": str(i % 13)}
                  for i, row in enumerate(prices) if i % 4 != 0]
        credit = [{"date": row["date"], "value": str(i % 17)}
                  for i, row in enumerate(prices) if i % 5 != 0]
        result = analyze(prices, {"housing_income_divergence": income,
                                  "consumer_credit_growth": credit})
        triple = result["three_factor_comparisons"]["consumer_credit_growth"]
        self.assertEqual(len(triple["cells"]), 8)
        self.assertEqual(sum(c["months"] for c in triple["cells"].values()),
                         triple["eligible_months"])
        self.assertEqual(triple["eligible_months"] + triple["missing_months"],
                         result["eligible_price_months"])

    def test_invalid_horizon_rejected(self):
        with self.assertRaises(ValueError):
            analyze(make_prices(), {}, horizon=0)


if __name__ == "__main__":
    unittest.main()
