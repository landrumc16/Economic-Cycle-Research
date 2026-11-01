import unittest

from scripts.v5_baseline_validation import brier, evaluate


class BaselineValidationTests(unittest.TestCase):
    def test_brier(self):
        self.assertEqual(brier([(0.0, 0), (1.0, 1)]), 0.0)
        self.assertEqual(brier([(1.0, 0), (0.0, 1)]), 1.0)
        self.assertIsNone(brier([]))

    def test_insufficient_history_does_not_approve(self):
        rows = [{"month": f"2019-{m:02d}", "phase": "EXPANSION"} for m in range(1, 13)]
        result = evaluate({"status": "HISTORICAL_RESEARCH_ONLY", "timeline": rows})
        self.assertFalse(result["probabilities_approved"])
        self.assertEqual(result["results"]["3"]["evaluation_months"], 0)
        self.assertIsNone(result["results"]["3"]["baseline_brier"])

    def test_rejects_unapproved_input(self):
        with self.assertRaises(ValueError):
            evaluate({"status": "PASS", "timeline": []})


if __name__ == "__main__":
    unittest.main()
