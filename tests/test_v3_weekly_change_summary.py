import unittest
from scripts.v3_weekly_change_summary import summarize

class WeeklyChangeSummaryTests(unittest.TestCase):
    def test_each_indicator_has_one_primary_bucket(self):
        rows = [
            {"series": "UNRATE", "value": 4.3, "new_observation_date": True, "delta_new_release": 0.2},
            {"series": "CPIAUCSL", "value": 330, "same_observation_revision_detected": True},
            {"series": "DGS10", "value": 4.2},
            {"series": "ICSA", "value": None, "source_availability_changed": True},
        ]
        x = summarize(rows)
        self.assertEqual(x["counts"]["new_observations"], 1)
        self.assertEqual(x["counts"]["revisions"], 1)
        self.assertEqual(x["counts"]["carried_forward"], 1)
        self.assertEqual(x["counts"]["unavailable"], 1)
        self.assertEqual(x["counts"]["source_transitions"], 1)
        self.assertIsNone(x["economic_direction"])
        self.assertIsNone(x["crash_probability"])

if __name__ == "__main__":
    unittest.main()
