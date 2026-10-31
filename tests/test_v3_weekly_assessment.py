import unittest
from scripts.v3_weekly_assessment import assess, render_markdown

class WeeklyAssessmentTests(unittest.TestCase):
    def test_unavailable_indicators_do_not_create_cycle_claims(self):
        result = assess({"report_type": "V3_WEEKLY_ECONOMIC_EVIDENCE", "as_of": "2026-10-31",
                         "series": {"UNRATE": {"status": "MISSING", "observation_value": None}},
                         "week_over_week": {}})
        self.assertEqual(result["predictive_publication"], "BLOCKED")
        self.assertIsNone(result["validated_cycle_stage"])
        self.assertIn("No usable numeric", result["indicators"][0]["headline"])
        self.assertIn("Not validated", render_markdown(result))

    def test_new_release_change_keeps_original_units(self):
        result = assess({"report_type": "V3_WEEKLY_ECONOMIC_EVIDENCE", "as_of": "2026-10-31",
                         "series": {"UNRATE": {"status": "STAGED_REVISED_NOT_PIT",
                                              "observation_value": 4.3,
                                              "latest_observation": "2026-10-01", "age_days": 30}},
                         "week_over_week": {"UNRATE": {"numeric_change": 0.2, "new_observation_date": True}}})
        self.assertIn("percentage points", result["indicators"][0]["headline"])
        self.assertEqual(result["indicators"][0]["delta_new_release"], 0.2)
        self.assertNotIn("recession", result["summary"].lower())

    def test_wrong_input_rejected(self):
        with self.assertRaises(ValueError):
            assess({"report_type": "V2"})

if __name__ == "__main__":
    unittest.main()
