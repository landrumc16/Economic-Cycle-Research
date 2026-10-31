"""Acceptance gate tests: no unsupported release or predictive claims."""
import unittest
from scripts.v1_acceptance import evaluate, REQUIRED_SECTIONS

class AcceptanceTests(unittest.TestCase):
    def valid(self):
        html = "\n".join(REQUIRED_SECTIONS)
        state = {
            "publication": "BLOCKED", "point_in_time_certified": False,
            "crash_probability": None, "validated_cycle_stage": None,
            "macro_domains": {name: {"observation": 1.0} for name in ("growth", "labor", "inflation")},
            "financial_observations": [{"series_id": "BAA10Y", "value": 1.4}],
            "current_cycle_assessment": {"status": "DESCRIPTIVE_CURRENT_REVISED_NOT_PIT",
                                         "publication": "BLOCKED", "crash_probability": None,
                                         "mechanism_lenses": {str(i): {} for i in range(5)}},
            "historical_macro_analogues": {"status": "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE",
                                           "crash_probability": None,
                                           "analogues": [{"status": "EXPLORATORY_ANALOGUE"} for _ in range(5)]},
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

    def test_empty_macro_observations_block_candidate(self):
        html, state = self.valid()
        state["macro_domains"]["growth"]["observation"] = None
        self.assertIn("CURRENT_MACRO_VALUES_MISSING", evaluate(html, state)["issues"])

    def test_fewer_than_five_historical_episodes_block_candidate(self):
        html, state = self.valid()
        state["historical_macro_analogues"]["analogues"] = [{"status": "EXPLORATORY_ANALOGUE"}]
        self.assertIn("HISTORICAL_EPISODES_INCOMPLETE", evaluate(html, state)["issues"])

    def test_missing_dashboard_section_blocks_candidate(self):
        html, state = self.valid()
        self.assertEqual(evaluate(html.replace("Financial and housing conditions", ""), state)["status"], "INCOMPLETE")

if __name__ == "__main__":
    unittest.main()
