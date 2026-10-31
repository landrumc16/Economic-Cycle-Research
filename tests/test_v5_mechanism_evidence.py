import unittest
from scripts.v5_mechanism_evidence import assess, MECHANISMS, adapt_standardized_metrics

class MechanismEvidenceTests(unittest.TestCase):
    def test_all_six_mechanisms_present(self):
        result = assess({})
        self.assertEqual(set(result["mechanisms"]), set(MECHANISMS))
        self.assertEqual(result["prediction_status"], "BLOCKED")

    def test_unverified_features_not_counted(self):
        result = assess({"yield_curve": {"value": 1.2}})
        self.assertEqual(result["mechanisms"]["monetary"]["pit_features_verified"], [])

    def test_verified_features_counted_without_model_claim(self):
        result = assess({"yield_curve": {"value": 1.2, "publisher_original_pit_certified": True}})
        self.assertEqual(result["mechanisms"]["monetary"]["pit_features_verified"], ["yield_curve"])
        self.assertEqual(result["mechanisms"]["monetary"]["ablation"], "NOT_RUN")

    def test_standardized_macro_adapter(self):\n        document = {"report_type": "V5_STANDARDIZED_MACRO_METRICS", "metrics": [\n            {"series": "UNRATE", "status": "DESCRIPTIVE_TRANSFORM_AVAILABLE",\n             "value": 0.3, "publisher_original_pit_certified": False}]}\n        mapped = adapt_standardized_metrics(document)\n        self.assertEqual(mapped["unemployment"]["value"], 0.3)\n        self.assertEqual(assess(mapped)["mechanisms"]["labor_growth"]["pit_features_verified"], [])\n\n    def test_no_fabricated_validation_from_labels(self):
        result = assess({}, [{"label": "POSITIVE_RESEARCH_LABEL"}])
        self.assertFalse(result["independent_outcome_validation"])
        self.assertEqual(result["research_outcomes_provided"], 1)

if __name__ == "__main__":
    unittest.main()
