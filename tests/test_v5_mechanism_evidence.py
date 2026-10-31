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

    def test_standardized_macro_adapter(self):
        document = {"report_type": "V5_STANDARDIZED_MACRO_METRICS", "metrics": [
            {"series": "UNRATE", "status": "DESCRIPTIVE_TRANSFORM_AVAILABLE",
             "value": 0.3, "publisher_original_pit_certified": False}]}
        mapped = adapt_standardized_metrics(document)
        self.assertEqual(mapped["unemployment"]["value"], 0.3)
        self.assertEqual(assess(mapped)["mechanisms"]["labor_growth"]["pit_features_verified"], [])

    def test_cpi_and_claims_are_mapped_to_relevant_pathways(self):
        document = {"report_type": "V5_STANDARDIZED_MACRO_METRICS", "metrics": [
            {"series": "CPIAUCSL", "status": "DESCRIPTIVE_TRANSFORM_AVAILABLE", "value": 3.0},
            {"series": "ICSA", "status": "DESCRIPTIVE_TRANSFORM_AVAILABLE", "value": 4.0}]}
        mapped = adapt_standardized_metrics(document)
        result = assess(mapped)
        self.assertIn("inflation", result["mechanisms"]["monetary"]["missing_or_unverified"])
        self.assertIn("initial_claims", result["mechanisms"]["labor_growth"]["missing_or_unverified"])
        self.assertEqual(result["prediction_status"], "BLOCKED")

    def test_no_fabricated_validation_from_labels(self):
        result = assess({}, [{"label": "POSITIVE_RESEARCH_LABEL"}])
        self.assertFalse(result["independent_outcome_validation"])
        self.assertEqual(result["research_outcomes_provided"], 1)

if __name__ == "__main__":
    unittest.main()
