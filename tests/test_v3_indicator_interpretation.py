import unittest
from scripts.v3_indicator_interpretation import interpret

class IndicatorInterpretationTests(unittest.TestCase):
    def test_rising_credit_spread_is_descriptive_not_prediction(self):
        x = interpret([{"series": "BAMLH0A0HYM2", "delta_new_release": 0.5}])
        self.assertEqual(x["findings"][0]["direction"], "INCREASED")
        self.assertIn("Widening", x["findings"][0]["interpretation"])
        self.assertIsNone(x["crash_probability"])
        self.assertIsNone(x["composite_score"])

    def test_missing_observation_does_not_imply_direction(self):
        x = interpret([{"series": "ICSA", "delta_new_release": None}])
        self.assertEqual(x["findings"][0]["direction"], "NO_COMPARABLE_NEW_OBSERVATION")

    def test_cpi_level_not_inflation_acceleration(self):
        x = interpret([{"series": "CPIAUCSL", "delta_new_release": 0.4}])
        self.assertIn("does not establish inflation acceleration", x["findings"][0]["interpretation"])

if __name__ == "__main__":
    unittest.main()
