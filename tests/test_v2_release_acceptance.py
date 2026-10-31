"""Regression tests for scoped descriptive release and inherited data gaps."""
import unittest
from scripts.v2_release_acceptance import evaluate

class ReleaseTests(unittest.TestCase):
    def fixtures(self):
        v2 = {"checks_passed": True, "status": "M1_ACCEPTANCE_CANDIDATE",
              "publication": "BLOCKED", "predictive_model": "NOT_VALIDATED"}
        v1 = {"checks_passed": False, "status": "INCOMPLETE", "publication": "BLOCKED",
              "predictive_model_status": "NOT_VALIDATED",
              "issues": ["CURRENT_MACRO_VALUES_MISSING", "HISTORICAL_COMPARISON_NOT_POPULATED"]}
        state = {"publication": "BLOCKED", "crash_probability": None, "validated_cycle_stage": None,
                 "v2_historical_comparison": {}, "v2_global_transmission": {},
                 "current_cycle_assessment": {}}
        page = ("Version 2 historical conditions Current conditions vs historical crash contexts "
                "Crash mechanism evidence gaps International economic transmission "
                "CURRENT_UNEMPLOYMENT_LEVEL_NOT_3M_CHANGE")
        return v2, v1, state, page

    def test_accepts_scoped_release_and_discloses_missing_sources(self):
        result = evaluate(*self.fixtures())
        self.assertTrue(result["checks_passed"])
        self.assertFalse(result["current_macro_complete"])
        self.assertEqual(len(result["disclosed_source_gaps"]), 2)
        self.assertEqual(result["status"], "V2_DESCRIPTIVE_RELEASE_ACCEPTED")

    def test_blocks_other_v1_failures(self):
        v2, v1, state, page = self.fixtures()
        v1["issues"].append("UNAUTHORIZED_PREDICTIVE_OUTPUT")
        self.assertFalse(evaluate(v2, v1, state, page)["checks_passed"])

    def test_blocks_predictive_output(self):
        v2, v1, state, page = self.fixtures()
        state["crash_probability"] = 0.5
        self.assertFalse(evaluate(v2, v1, state, page)["checks_passed"])

    def test_blocks_missing_panel(self):
        v2, v1, state, page = self.fixtures()
        self.assertFalse(evaluate(v2, v1, state, "")["checks_passed"])

if __name__ == "__main__":
    unittest.main()
