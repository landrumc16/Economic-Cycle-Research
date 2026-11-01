import math
import unittest
from scripts.derive_credit_growth import growth


def sample(n=30):
    return [{"date": f"{2000 + i // 12:04d}-{i % 12 + 1:02d}-01",
             "value": str(100 * math.exp(0.01 * i))} for i in range(n)]


class CreditGrowthTests(unittest.TestCase):
    def test_trailing_growth_uses_prior_twelve_months(self):
        output = growth(sample())
        self.assertEqual(len(output), 18)
        self.assertAlmostEqual(output[0]["value"], 12.0, places=4)

    def test_future_changes_do_not_change_earlier_growth(self):
        rows = sample()
        earlier = growth(rows)
        rows[-1]["value"] = "1"
        later = growth(rows)
        self.assertEqual(earlier[:-1], later[:-1])

    def test_gap_rejected(self):
        rows = sample()
        rows.pop(6)
        with self.assertRaises(ValueError):
            growth(rows)


if __name__ == "__main__":
    unittest.main()
