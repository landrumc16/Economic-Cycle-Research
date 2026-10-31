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
