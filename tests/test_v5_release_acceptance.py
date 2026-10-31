import unittest
from scripts.v5_release_acceptance import verify


class V5ReleaseAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.readout = {"report_type": "V5_WEEKLY_RESEARCH_READOUT",
                        "predictive_publication": "BLOCKED",
                        "release_status": "DESCRIPTIVE_RESEARCH",
                        "as_of": "2026-10-31", "macro_metric_count": 0,
                        "historical_event_count": 0,
                        "standardized_macro": [], "mechanism_readiness": {"monetary": {}},
                        "original_vintage_replay_coverage": 0,
                        "outcome_coverage_status": "NO_VERIFIED_OUTCOME_INPUTS",
                        "validation_requirements": ["independent audit"]}
        self.mechanisms = {"report_type": "V5_MECHANISM_EVIDENCE_GATE",
                           "mechanisms": {"monetary": {}}}
        self.replay = {"report_type": "V5_PIT_REPLAY",
                       "publisher_original_coverage": 0}
        self.outcomes = {"event_count": 0, "coverage_status": "NO_VERIFIED_OUTCOME_INPUTS"}
        self.html = "<html>2026-10-31 Predictive publication: BLOCKED</html>"

    def run_gate(self):
        return verify(self.readout, self.html, self.mechanisms,
                      self.replay, self.outcomes)

    def test_complete_descriptive_artifact_passes(self):
        result = self.run_gate()
        self.assertEqual(result["status"], "PASS_DESCRIPTIVE_ONLY")
        self.assertFalse(result["independent_validation_certified"])

    def test_unblocked_prediction_fails(self):
        self.readout["predictive_publication"] = "APPROVED"
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_mismatched_macro_count_fails(self):
        self.readout["macro_metric_count"] = 5
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_macro_coverage_total_mismatch_fails(self):
        self.readout["macro_metric_total"] = 2
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_missing_dashboard_disclosure_fails(self):
        self.html = "<html>Economic research</html>"
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_mismatched_mechanism_details_fail(self):
        self.mechanisms["mechanisms"]["monetary"] = {"required_features": ["yield_curve"]}
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_missing_pit_contract_fails(self):
        self.replay = {}
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_historical_event_count_mismatch_fails(self):
        self.readout["historical_event_count"] = 2
        self.assertEqual(self.run_gate()["status"], "FAIL")

    def test_missing_outcome_coverage_fails(self):
        self.outcomes = {}
        self.assertEqual(self.run_gate()["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
