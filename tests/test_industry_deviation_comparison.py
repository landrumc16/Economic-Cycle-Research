import unittest
from scripts.industry_deviation_comparison import compare


class ComparisonTests(unittest.TestCase):
    def test_short_series_has_no_eligible_windows(self):
        rows = [{"date": f"2000-{i:02d}-01", "value": str(100+i)} for i in range(1, 13)]
        self.assertEqual(compare(rows)["groups"]["high_deviation"]["eligible"], 0)

    def test_constant_series_has_no_drawdowns(self):
        rows = [{"date": f"{2000 + i//12:04d}-{i%12+1:02d}-01", "value": "100"}
                for i in range(100)]
        groups = compare(rows)["groups"]
        self.assertEqual(sum(v["drawdown"] for v in groups.values()), 0)

    def test_future_change_does_not_affect_earlier_group_assignment(self):
        rows = [{"date": f"{2000 + i//12:04d}-{i%12+1:02d}-01", "value": str(100+i)}
                for i in range(100)]
        a = compare(rows)["observations"]
        rows[-1]["value"] = "1"
        b = compare(rows)["observations"]
        self.assertEqual([v["group"] for v in a], [v["group"] for v in b])


if __name__ == "__main__":
    unittest.main()
