import math
import unittest
from scripts.derive_housing_income_divergence import derive


def data(growth, n=36):
    return [{"date": f"{2000+i//12:04d}-{i%12+1:02d}-01",
             "value": str(100 * math.exp(growth * i))} for i in range(n)]


class HousingIncomeTests(unittest.TestCase):
    def test_positive_price_income_divergence(self):
        rows = derive(data(0.02), data(0.01))
        self.assertEqual(len(rows), 24)
        self.assertAlmostEqual(rows[0]["value"], 12.0, places=4)

    def test_missing_income_month_not_imputed(self):
        income = data(0.01)
        income.pop(12)
        rows = derive(data(0.02), income)
        self.assertNotIn("2001-01-01", [row["date"] for row in rows])

    def test_future_change_does_not_change_past(self):
        prices = data(0.02)
        first = derive(prices, data(0.01))
        prices[-1]["value"] = "10000"
        second = derive(prices, data(0.01))
        self.assertEqual(first[:-1], second[:-1])


if __name__ == "__main__":
    unittest.main()
