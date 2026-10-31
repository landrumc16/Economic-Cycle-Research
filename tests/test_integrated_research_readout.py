import unittest
from scripts.integrated_research_readout import combine

class IntegratedResearchReadoutTests(unittest.TestCase):
    def test_preserves_quality_and_blocks_prediction(self):
        macro = {"domains": {"growth": {"observation": 1.0}}, "cross_domain": "DESCRIPTIVE_ONLY"}
        financial = {"domains": {"yield_curve": {"quality": "STAGED_NOT_APPROVED", "published_model_eligible": False}}, "snapshot_date": "2026-10-30"}
        report = combine(macro, financial)
        self.assertEqual(report["publication"], "BLOCKED")
        self.assertIsNone(report["crash_probability"])
        self.assertIsNone(report["validated_cycle_stage"])
        self.assertEqual(report["financial_housing"]["domains"]["yield_curve"]["quality"], "STAGED_NOT_APPROVED")
        self.assertIn("false_alarm_controls", report["research_layers"])

    def test_missing_domains_fail_closed(self):
        with self.assertRaises(ValueError):
            combine({}, {"domains": {}})

if __name__ == "__main__":
    unittest.main()
