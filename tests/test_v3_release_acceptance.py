import unittest
from scripts.v3_release_acceptance import validate

class V3ReleaseAcceptanceTests(unittest.TestCase):
    def report(self):
        return {"report_type": "V3_WEEKLY_DESCRIPTIVE_ASSESSMENT",
                "predictive_publication": "BLOCKED", "crash_probability": None,
                "validated_cycle_stage": None, "as_of": "2026-10-31",
                "change_summary": {}, "macro_narrative": {}, "indicators": [],
                "pathway_evidence": {}}

    def page(self):
        return "<html>Weekly Economic Intelligence What changed Economic conditions by domain Latest economic indicators Distinct crash-pathway evidence Predictions blocked</html>"

    def test_descriptive_release_passes(self):
        self.assertEqual(validate(self.report(), self.page())["status"], "PASS_DESCRIPTIVE_RELEASE")

    def test_prediction_unblocks_release_failure(self):
        report = self.report()
        report["crash_probability"] = 0.8
        self.assertEqual(validate(report, self.page())["status"], "FAIL")

    def test_missing_dashboard_section_fails(self):
        self.assertEqual(validate(self.report(), "<html></html>")["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
