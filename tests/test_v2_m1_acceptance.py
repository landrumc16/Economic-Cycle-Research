"""Version 2 milestone acceptance tests."""
import unittest
from scripts.v2_m1_acceptance import evaluate

class MilestoneAcceptanceTests(unittest.TestCase):
    def fixtures(self):
        comparison = {
            "schema_version": "2.0.0", "status": "DESCRIPTIVE_ONLY",
            "publication": "BLOCKED", "crash_probability": None,
            "provenance": {
                "point_in_time_certified": False, "human_approved_for_prediction": False,
                "sha256_export": "a" * 64,
                "extraction_timestamp_status": "NOT_RECORDED_IN_SOURCE_EXPORT",
                "tabs": [{"name": "CRASH PATHWAY TYPOLOGY"},
                         {"name": "WARNING NONCRASH BASELINES"}],
            },
            "descriptive_comparison": {"crash_parent_clusters": 8, "monthly_observations": 444},
            "crash_parent_clusters": [{} for _ in range(8)],
            "monthly_stress_baseline": [{} for _ in range(444)],
        }
        page = ("Version 2 historical conditions; not verified non-crash controls; "
                "Current conditions vs historical crash contexts; "
                "CURRENT_UNEMPLOYMENT_LEVEL_NOT_3M_CHANGE; "
                "Crash mechanism evidence gaps; International economic transmission")
        state = {"v2_historical_comparison": comparison, "publication": "BLOCKED",
                 "crash_probability": None,
                 "current_cycle_assessment": {"publication": "BLOCKED"},
                 "v2_global_transmission": {"publication": "BLOCKED",
                    "predictive_model": "NOT_VALIDATED", "channels": [{} for _ in range(8)],
                    "coverage": {"channels_defined": 8}}}
        return comparison, page, state

    def test_accepts_valid_descriptive_snapshot(self):
        self.assertTrue(evaluate(*self.fixtures())["checks_passed"])

    def test_blocks_missing_dashboard_panel(self):
        comparison, _, state = self.fixtures()
        self.assertIn("DASHBOARD_V2_SECTION_MISSING", evaluate(comparison, "", state)["issues"])

    def test_blocks_unapproved_prediction(self):
        comparison, page, state = self.fixtures()
        comparison["crash_probability"] = 0.8
        self.assertIn("PREDICTIVE_GATE_VIOLATION", evaluate(comparison, page, state)["issues"])

    def test_blocks_mismatched_dashboard_state(self):
        comparison, page, state = self.fixtures()
        state["v2_historical_comparison"] = {}
        self.assertIn("DASHBOARD_STATE_SOURCE_MISMATCH", evaluate(comparison, page, state)["issues"])

if __name__ == "__main__":
    unittest.main()
