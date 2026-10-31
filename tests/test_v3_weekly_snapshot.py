import unittest
from scripts.v3_weekly_snapshot import build_weekly_snapshot

class WeeklySnapshotTests(unittest.TestCase):
    def manifest(self):
        return {"series": {
            "UNRATE": {"status": "STAGED_REVISED_NOT_PIT", "latest_observation": "2026-09-01", "observation_count": 10},
            "CPIAUCSL": {"status": "MISSING", "latest_observation": None, "observation_count": 0},
            "GDPC1": {"status": "INVALID", "latest_observation": None, "observation_count": 0}
        }}

    def test_missing_and_revised_remain_explicit(self):
        result = build_weekly_snapshot(self.manifest(), "2026-10-31")
        self.assertEqual(result["source_coverage"], {"defined": 3, "available": 1, "missing_or_invalid": 2})
        self.assertIsNone(result["series"]["UNRATE"]["observation_value"])
        self.assertIsNone(result["series"]["CPIAUCSL"]["age_days"])
        self.assertEqual(result["publication"], "BLOCKED")

    def test_previous_snapshot_changes_are_metadata_only(self):
        prior = build_weekly_snapshot(self.manifest(), "2026-10-24")
        next_manifest = self.manifest()
        next_manifest["series"]["CPIAUCSL"]["status"] = "STAGED_REVISED_NOT_PIT"
        next_manifest["series"]["CPIAUCSL"]["latest_observation"] = "2026-09-01"
        result = build_weekly_snapshot(next_manifest, "2026-10-31", prior)
        self.assertTrue(result["week_over_week"]["CPIAUCSL"]["status_changed"])
        self.assertTrue(result["week_over_week"]["CPIAUCSL"]["new_observation_date"])
        self.assertIsNone(result["week_over_week"]["CPIAUCSL"]["numeric_change"])

    def test_new_release_delta_only_for_changed_observation_date(self):
        old = build_weekly_snapshot(self.manifest(), "2026-10-24", observations={"UNRATE": {"2026-09-01": 4.1}})
        new_manifest = self.manifest()
        new_manifest["series"]["UNRATE"]["latest_observation"] = "2026-10-01"
        new = build_weekly_snapshot(new_manifest, "2026-10-31", old,
                                    observations={"UNRATE": {"2026-10-01": 4.3}})
        self.assertEqual(new["series"]["UNRATE"]["observation_value"], 4.3)
        self.assertAlmostEqual(new["week_over_week"]["UNRATE"]["numeric_change"], 0.2)
        self.assertEqual(new["week_over_week"]["UNRATE"]["reason"], "NEW_RELEASED_OBSERVATION_REVISED_NOT_PIT")

    def test_no_delta_for_same_observation_date(self):
        old = build_weekly_snapshot(self.manifest(), "2026-10-24", observations={"UNRATE": {"2026-09-01": 4.1}})
        new = build_weekly_snapshot(self.manifest(), "2026-10-31", old,
                                    observations={"UNRATE": {"2026-09-01": 4.2}})
        self.assertIsNone(new["week_over_week"]["UNRATE"]["numeric_change"])
        self.assertTrue(new["week_over_week"]["UNRATE"]["same_observation_revision_detected"])
        self.assertAlmostEqual(new["week_over_week"]["UNRATE"]["revision_delta"], 0.1)

    def test_missing_series_not_promoted_by_stale_value(self):
        new = build_weekly_snapshot(self.manifest(), "2026-10-31",
                                    observations={"CPIAUCSL": {"2026-09-01": 100.0}})
        self.assertIsNone(new["series"]["CPIAUCSL"]["observation_value"])

    def test_future_observation_rejected(self):
        manifest = self.manifest()
        manifest["series"]["UNRATE"]["latest_observation"] = "2026-11-01"
        with self.assertRaises(ValueError):
            build_weekly_snapshot(manifest, "2026-10-31")

    def test_nonchronological_comparison_rejected(self):
        prior = build_weekly_snapshot(self.manifest(), "2026-10-31")
        with self.assertRaises(ValueError):
            build_weekly_snapshot(self.manifest(), "2026-10-31", prior)

if __name__ == "__main__":
    unittest.main()
