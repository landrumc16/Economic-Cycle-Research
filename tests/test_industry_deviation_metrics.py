import unittest
from datetime import date
from scripts.industry_deviation_metrics import calculate


def sample(n=90):
    return [{"date": f"{(2000 + i // 12):04d}-{(i % 12 + 1):02d}-01",
             "value": str(100 + i)} for i in range(n)]


class IndustryDeviationMetricsTests(unittest.TestCase):
    def test_baseline_is_strictly_prior(self):
        rows = calculate(sample(), lookback=12, history=60, minimum_history=36)
        self.assertEqual(rows[0]["prior_observations"], 0)
        self.assertEqual(rows[36]["prior_observations"], 36)
        self.assertEqual(rows[36]["status"], "DESCRIPTIVE_ONLY")

    def test_future_values_do_not_change_past_metrics(self):
        original = sample()
        extended = original + [{"date": "2007-07-01", "value": "100000"}]
        self.assertEqual(calculate(original), calculate(extended)[:-1])

    def test_gap_rejected(self):
        rows = sample()
        rows.pop(5)
        with self.assertRaises(ValueError):
            calculate(rows)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            calculate(sample() + [sample()[0]])


if __name__ == "__main__":
    unittest.main()
