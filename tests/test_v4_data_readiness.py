import unittest
from scripts.v4_data_readiness import audit

class V4DataReadinessTests(unittest.TestCase):
    def snapshot(self):
        return {"report_type": "V3_WEEKLY_ECONOMIC_EVIDENCE", "as_of": "2026-10-31",
                "series": {"UNRATE": {"status": "STAGED_REVISED_NOT_PIT", "latest_observation": "2026-09-01",
                                      "observation_value": 4.2, "age_days": 60, "release_date": None}},
                "week_over_week": {"UNRATE": {"previous_snapshot_available": True,
                                               "new_observation_date": True, "numeric_change": None}}}

    def test_new_observation_without_numeric_baseline_is_not_carried_forward(self):
        result = audit(self.snapshot())
        self.assertEqual(result["details"][0]["comparison_status"], "NEW_DATED_OBSERVATION_NO_NUMERIC_BASELINE")
        self.assertEqual(result["numeric_sources"], 1)
        self.assertTrue(result["weekly_comparison_verified"])
        self.assertEqual(result["predictive_publication"], "BLOCKED")

    def test_staged_without_value_is_not_numeric(self):
        snap = self.snapshot()
        snap["series"]["UNRATE"]["observation_value"] = None
        result = audit(snap)
        self.assertEqual(result["numeric_sources"], 0)
        self.assertEqual(result["details"][0]["comparison_status"], "NO_NUMERIC_EVIDENCE")

    def test_future_dated_observation_rejected(self):
        snap = self.snapshot()
        snap["series"]["UNRATE"]["latest_observation"] = "2026-11-01"
        with self.assertRaises(ValueError):
            audit(snap)

if __name__ == "__main__":
    unittest.main()
