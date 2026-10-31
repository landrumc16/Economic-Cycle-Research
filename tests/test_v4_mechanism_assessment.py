import unittest
from scripts.v4_mechanism_assessment import assess_mechanisms

class V4MechanismTests(unittest.TestCase):
    def test_mixed_evidence_preserved_and_no_probability(self):
        signals = {"report_type": "V4_EXPLAINABLE_ECONOMIC_SIGNALS", "as_of": "2026-10-31",
                   "signals": [
                       {"series": "UNRATE", "observation_value": 4.5, "observation_date": "2026-09-01",
                        "direction": "INCREASED", "risk_evidence": "ADVERSE_DIRECTIONAL_EVIDENCE", "interpretation": "Labor softening"},
                       {"series": "ICSA", "observation_value": 200000, "observation_date": "2026-10-24",
                        "direction": "DECREASED", "risk_evidence": "FAVORABLE_DIRECTIONAL_EVIDENCE", "interpretation": "Claims falling"},
                   ]}
        report = assess_mechanisms(signals)
        labor = next(x for x in report["pathways"] if x["pathway"] == "growth_labor_recession")
        self.assertTrue(labor["mixed_directional_evidence"])
        self.assertFalse(labor["mechanism_confirmed"])
        self.assertIsNone(report["crash_probability"])

    def test_unmapped_pathway_is_unknown_not_safe(self):
        report = assess_mechanisms({"report_type": "V4_EXPLAINABLE_ECONOMIC_SIGNALS",
                                    "as_of": "2026-10-31", "signals": []})
        housing = next(x for x in report["pathways"] if x["pathway"] == "housing_leverage")
        self.assertEqual(housing["available_indicators"], 0)
        self.assertIn("cannot be assessed", housing["interpretation"])
        self.assertIsNone(housing["validated_risk_probability"])

if __name__ == "__main__":
    unittest.main()
