import unittest
from scripts.v5_temporal_provenance import audit

class V5TemporalTests(unittest.TestCase):
    def sample(self):
        return {"report_type": "V3_WEEKLY_ECONOMIC_EVIDENCE", "as_of": "2026-10-31",
                "series": {"UNRATE": {"latest_observation": "2026-09-01", "observation_value": 4.2,
                                     "release_date": None, "vintage_date": None}},
                "week_over_week": {"UNRATE": {"previous_snapshot_available": True,
                                             "new_observation_date": False, "numeric_change": None}}}

    def test_carry_forward_is_not_weekly_change(self):
        result = audit(self.sample())
        self.assertEqual(result["valid_dated_comparisons"], 0)
        self.assertEqual(result["series"][0]["reporting_warning"], "CARRIED_FORWARD")

    def test_new_dated_comparison_is_counted(self):
        snapshot = self.sample()
        snapshot["week_over_week"]["UNRATE"].update(new_observation_date=True, numeric_change=0.2)
        self.assertEqual(audit(snapshot)["valid_dated_comparisons"], 1)

    def test_future_release_fails(self):
        snapshot = self.sample()
        snapshot["series"]["UNRATE"]["release_date"] = "2026-11-01"
        with self.assertRaises(ValueError):
            audit(snapshot)

    def test_future_observation_fails(self):
        snapshot = self.sample()
        snapshot["series"]["UNRATE"]["latest_observation"] = "2026-11-01"
        with self.assertRaises(ValueError):
            audit(snapshot)

if __name__ == "__main__":
    unittest.main()
