import unittest
from scripts.historical_research_bridge import attach

class HistoricalResearchBridgeTests(unittest.TestCase):
    def test_preserves_nonindependent_denominators(self):
        result = attach({"publication": "BLOCKED", "financial_housing": {"domains": {}}})
        self.assertEqual(result["historical_research"]["pathways"]["denominator"]["parent_clusters"], 8)
        self.assertEqual(result["historical_research"]["noncrash_baselines"]["denominator"]["monthly_observations"], 444)
        self.assertEqual(result["historical_research"]["holdout"]["validation"], "NOT_UNTOUCHED_OUT_OF_SAMPLE")
        self.assertIsNone(result["crash_probability"])
    def test_cannot_promote_published_input(self):
        with self.assertRaises(ValueError):
            attach({"publication": "APPROVED"})

if __name__ == "__main__":
    unittest.main()
