"""Version 2 pathway coverage regression checks."""
import json
import unittest
from pathlib import Path
from scripts.v2_canonical_comparison import build
from scripts.v2_pathway_coverage import assemble

class PathwayCoverageTests(unittest.TestCase):
    def comparison(self):
        raw = Path("data/workbook_historical_research_snapshot_2026-10-30.json").read_bytes()
        return build(json.loads(raw), raw)

    def test_canonical_features_and_missingness(self):
        result = assemble(self.comparison())
        self.assertEqual(len(result["pathway_profiles"]), 8)
        self.assertEqual(result["coverage"]["growth"]["observed_parent_clusters"], 8)
        self.assertEqual(result["coverage"]["housing"]["observed_parent_clusters"], 0)
        self.assertEqual(result["control_status"], "NOT_VERIFIED")
        self.assertTrue(all(p["pathway_mechanism"] is None for p in result["pathway_profiles"]))
        self.assertTrue(all(p["features"]["valuation"]["value"] is None for p in result["pathway_profiles"]))

    def test_rejects_predictive_promotion(self):
        comparison = self.comparison()
        comparison["publication"] = "ALLOWED"
        with self.assertRaises(ValueError):
            assemble(comparison)

    def test_missing_individual_feature_is_explicit(self):
        comparison = self.comparison()
        comparison["crash_parent_clusters"][0]["credit_pp"] = None
        result = assemble(comparison)
        self.assertEqual(result["coverage"]["credit"]["observed_parent_clusters"], 7)
        self.assertEqual(result["pathway_profiles"][0]["features"]["credit"]["status"], "MISSING")

if __name__ == "__main__":
    unittest.main()
