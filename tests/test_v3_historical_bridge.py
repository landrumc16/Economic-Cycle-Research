import unittest
from scripts.v3_historical_bridge import bridge

class HistoricalBridgeTests(unittest.TestCase):
    def historical(self):
        return {"status": "DESCRIPTIVE_ONLY", "publication": "BLOCKED",
                "control_status": "NOT_VERIFIED", "source_sha256": "fixture",
                "pathway_profiles": [{}, {}],
                "coverage": {"credit": {"status": "REVISED_NOT_PIT", "observed_parent_clusters": 2}}}

    def test_credit_coverage_not_numeric_analogue(self):
        x = bridge({"indicators": [{"series": "BAMLH0A0HYM2", "value": 4.2,
                                    "latest_observation": "2026-10-30"}]}, self.historical())
        credit = next(d for d in x["domains"] if d["domain"] == "credit")
        self.assertTrue(credit["current_observation_available"])
        self.assertEqual(credit["historical_parent_clusters_with_domain"], 2)
        self.assertTrue(credit["direct_numeric_comparison"].startswith("BLOCKED"))
        self.assertIsNone(x["historical_analogue_rankings"])

    def test_reject_changed_historical_contract(self):
        h = self.historical()
        h["publication"] = "APPROVED"
        with self.assertRaises(ValueError):
            bridge({"indicators": []}, h)

if __name__ == "__main__":
    unittest.main()
