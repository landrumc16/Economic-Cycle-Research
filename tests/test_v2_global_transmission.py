"""Tests for conservative international evidence inventory."""
import unittest
from scripts.v2_global_transmission import build

class GlobalTransmissionTests(unittest.TestCase):
    def sample(self):
        return {"status": "DESCRIPTIVE_ONLY", "publication": "BLOCKED",
                "source_sha256": "a" * 64,
                "pathway_profiles": [{"parent_cluster": str(i), "peak_date": "2000-03-10"}
                                     for i in range(1, 9)]}
    def test_missing_sources_do_not_create_signals(self):
        result = build(self.sample())
        self.assertEqual(result["coverage"]["channels_defined"], 8)
        self.assertEqual(result["coverage"]["channels_with_historical_data"], 0)
        self.assertEqual(len(result["crash_channel_matrix"]), 8)
        self.assertTrue(all(x["historical_observation"] is None for x in result["channels"]))
        self.assertTrue(all(v["status"] == "NOT_ASSESSED" for r in result["crash_channel_matrix"]
                            for v in r["channels"].values()))
    def test_prediction_promotion_rejected(self):
        sample = self.sample()
        sample["publication"] = "ALLOWED"
        with self.assertRaises(ValueError):
            build(sample)
if __name__ == "__main__":
    unittest.main()
