import unittest
from scripts.historical_usability_scorecard import scorecard

class ScorecardTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "noncrash": {"rows": [
                ["Month", "cutoff", "Curve", "Credit"],
                ["2000-01", "", "-0.2", "1.5"],
                ["2000-02", "", "0.2", "1.2"],
                ["2000-03", "", "0.4", "3.0"],
                ["2000-04", "", "0.3", "1.0"]]},
            "pathways": {"rows": [
                ["parent", "peak"], ["1", "2000-03-10"]]}
        }
        self.leads = {"rows": [["id"], ["1"]]}

    def test_prior_month_and_unmatured_tail(self):
        result = scorecard(self.snapshot, self.leads, 1)
        self.assertEqual(result["monthly_observations"], 4)
        self.assertEqual(result["flagged_months"], 2)
        self.assertEqual(result["flagged_followed_by_listed_peak"], 0)
        self.assertEqual(result["unflagged_followed_by_listed_peak"], 1)
        self.assertEqual(result["monthly_assessments"][-1]["retrospective_listed_peak_outcome"], "UNMATURED")
        self.assertFalse(result["point_in_time_certified"])

    def test_duplicate_months_rejected(self):
        self.snapshot["noncrash"]["rows"].append(["2000-01", "", "0", "0"])
        with self.assertRaises(ValueError):
            scorecard(self.snapshot, self.leads, 1)

if __name__ == "__main__":
    unittest.main()
