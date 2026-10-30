import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from milestone1_gate import evaluate, SERIES

FIELDS = ("publisher_source_acquired", "independent_source_acquired",
          "numeric_reconciliation_pass", "publisher_vintage_authenticated",
          "release_timing_verified", "point_in_time_no_lookahead_pass",
          "coverage_pass")

def complete():
    return {"series": {series: {field: True for field in FIELDS} for series in SERIES}}

class MilestoneGateTests(unittest.TestCase):
    def test_empty_is_blocked(self):
        self.assertEqual(evaluate({})["promotion"], "BLOCKED")
    def test_missing_series_is_blocked(self):
        evidence = complete()
        del evidence["series"]["GDPC1"]
        self.assertFalse(evaluate(evidence)["all_evidence_pass"])
    def test_missing_vintage_is_blocked(self):
        evidence = complete()
        evidence["series"]["UNRATE"]["publisher_vintage_authenticated"] = False
        self.assertFalse(evaluate(evidence)["all_evidence_pass"])
    def test_string_true_does_not_pass(self):
        evidence = complete()
        evidence["series"]["CPIAUCSL"]["release_timing_verified"] = "true"
        self.assertFalse(evaluate(evidence)["all_evidence_pass"])
    def test_all_checks_eligible_only_for_human_review(self):
        result = evaluate(complete())
        self.assertTrue(result["all_evidence_pass"])
        self.assertEqual(result["promotion"], "ELIGIBLE FOR HUMAN REVIEW")
        self.assertFalse(result["automatic_promotion"])

if __name__ == "__main__":
    unittest.main()
