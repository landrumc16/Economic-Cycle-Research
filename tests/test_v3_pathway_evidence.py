import unittest
from scripts.v3_pathway_evidence import pathway_evidence

class PathwayEvidenceTests(unittest.TestCase):
    def test_missing_pathways_not_marked_confirmed(self):
        report = pathway_evidence([])
        self.assertEqual(len(report["pathways"]), 5)
        self.assertTrue(all(not p["mechanism_confirmed"] for p in report["pathways"]))
        self.assertIsNone(report["composite_risk_score"])
        self.assertEqual(report["predictive_publication"], "BLOCKED")

    def test_available_credit_observation_is_not_crash_classification(self):
        report = pathway_evidence([{"series": "BAMLH0A0HYM2", "value": 4.2,
                                    "latest_observation": "2026-10-30", "delta_new_release": 0.2}])
        credit = next(p for p in report["pathways"] if p["pathway"] == "banking_credit_liquidity")
        self.assertEqual(credit["observed"], 1)
        self.assertFalse(credit["mechanism_confirmed"])
        self.assertIsNone(credit["validated_probability"])

if __name__ == "__main__":
    unittest.main()
