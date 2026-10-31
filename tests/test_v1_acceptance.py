"""Acceptance gate tests: no unsupported release or predictive claims."""
import unittest
from scripts.v1_acceptance import evaluate, REQUIRED_SECTIONS

class AcceptanceTests(unittest.TestCase):
    def valid(self):
        html = "\n".join(REQUIRED_SECTIONS)
        state = {
            "publication": "BLOCKED", "point_in_time_certified": False,
            "crash_probability": None, "validated_cycle_stage": None,
            "macro_domains": {}, "financial_observations": [],
            "current_cycle_assessment": {"status": "DESCRIPTIVE_CURRENT_REVISED_NOT_PIT"},
            "historical_macro_analogues": {"status": "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE"},
        }
        return html, state

    def test_complete_descriptive_dashboard_is_candidate(self):
        html, state = self.valid()
        result = evaluate(html, state)
        self.assertTrue(result["checks_passed"])
        self.assertEqual(result["status"], "RESEARCH_DASHBOARD_CANDIDATE")
        self.assertEqual(result["predictive_model_status"], "NOT_VALIDATED")

    def test_missing_historical_comparison_blocks_candidate(self):
        html, state = self.valid()
        state["historical_macro_analogues"] = {"status": "INSUFFICIENT_SOURCE_DATA"}
        self.assertEqual(evaluate(html, state)["status"], "INCOMPLETE")

    def test_predictive_promotion_blocks_candidate(self):
        html, state = self.valid()
        state["crash_probability"] = 0.25
        self.assertEqual(evaluate(html, state)["status"], "INCOMPLETE")

    def test_missing_dashboard_section_blocks_candidate(self):
        html, state = self.valid()
        self.assertEqual(evaluate(html.replace("Financial and housing conditions", ""), state)["status"], "INCOMPLETE")

if __name__ == "__main__":
    unittest.main()
