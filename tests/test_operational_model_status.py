"""Safety tests for operational status: no fabricated risk score or implicit approval."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from operational_model_status import build_status

FIELDS = ("publisher_source_acquired", "independent_source_acquired",
          "numeric_reconciliation_pass", "publisher_vintage_authenticated",
          "release_timing_verified", "point_in_time_no_lookahead_pass",
          "coverage_pass")
SERIES = ("UNRATE", "CPIAUCSL", "GDPC1")

class OperationalStatusTests(unittest.TestCase):
    def test_missing_evidence_blocks_all_scores(self):
        result = build_status({})
        self.assertEqual(result["publication"], "BLOCKED")
        self.assertFalse(result["scores_generated"])
        self.assertTrue(all(x["score"] is None for x in result["domains"].values()))

    def test_approved_sources_still_do_not_imply_predictive_validation(self):
        gate = {"all_evidence_pass": True,
                "series": {name: {field: True for field in FIELDS} for name in SERIES}}
        result = build_status(gate, {name: "APPROVED" for name in SERIES})
        self.assertTrue(result["canonical_inputs_approved"])
        self.assertEqual(result["publication"], "BLOCKED")
        self.assertEqual(result["historical_predictive_validation"], "NOT_VERIFIED")

    def test_one_unverified_vintage_blocks_input_approval(self):
        gate = {"all_evidence_pass": True,
                "series": {name: {field: True for field in FIELDS} for name in SERIES}}
        gate["series"]["GDPC1"]["release_timing_verified"] = False
        result = build_status(gate, {name: "APPROVED" for name in SERIES})
        self.assertFalse(result["canonical_inputs_approved"])

if __name__ == "__main__":
    unittest.main()
