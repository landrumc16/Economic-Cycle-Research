import unittest

from scripts.v5_forward_outcomes import evaluate, shift


class ForwardOutcomeTests(unittest.TestCase):
    def test_month_shift_across_year(self):
        self.assertEqual(shift("2007-12", 1), "2008-01")
        self.assertEqual(shift("2008-01", 12), "2009-01")

    def test_future_outcome_excludes_current_month(self):
        months = ["2007-11", "2007-12", "2008-01", "2008-02",
                  "2008-03", "2008-04", "2008-05", "2008-06",
                  "2008-07", "2008-08", "2008-09", "2008-10",
                  "2008-11", "2008-12", "2009-01"]
        report = evaluate({"status": "HISTORICAL_RESEARCH_ONLY",
                           "timeline": [{"month": m, "phase": "EXPANSION"} for m in months]})
        horizon = report["results"]["3"]
        self.assertGreater(horizon["event_months"], 0)
        self.assertEqual(horizon["eligible_months"], len(months) - 3)
        self.assertFalse(report["probabilities_approved"])

    def test_missing_future_month_excludes_row(self):
        report = evaluate({"status": "HISTORICAL_RESEARCH_ONLY",
                           "timeline": [{"month": "2007-12", "phase": "EXPANSION"},
                                        {"month": "2008-02", "phase": "EXPANSION"}]})
        self.assertEqual(report["results"]["3"]["eligible_months"], 0)

    def test_reject_wrong_status(self):
        with self.assertRaises(ValueError):
            evaluate({"status": "PASS", "timeline": []})


if __name__ == "__main__":
    unittest.main()
