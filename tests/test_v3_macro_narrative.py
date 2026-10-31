import unittest
from scripts.v3_macro_narrative import narrative

class MacroNarrativeTests(unittest.TestCase):
    def test_missing_data_does_not_infer_cycle(self):
        x = narrative([])
        self.assertEqual(len(x["domains"]), 5)
        self.assertIsNone(x["overall_cycle_stage"])
        self.assertTrue(all(y["economic_direction"] == "NOT_CLASSIFIED" for y in x["domains"]))

    def test_new_and_revised_are_distinguished(self):
        x = narrative([
            {"series": "UNRATE", "value": 4.3, "delta_new_release": 0.2},
            {"series": "ICSA", "value": 230000, "same_observation_revision_detected": True},
        ])
        labor = next(y for y in x["domains"] if y["domain"] == "labor")
        self.assertEqual(labor["new_dated_series"], ["UNRATE"])
        self.assertEqual(labor["revised_series"], ["ICSA"])
        self.assertIsNone(x["crash_probability"])

if __name__ == "__main__":
    unittest.main()
