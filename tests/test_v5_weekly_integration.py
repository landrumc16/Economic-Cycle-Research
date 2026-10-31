import unittest
from scripts.v5_weekly_research_readout import assemble
from scripts.v5_weekly_dashboard import render


class V5IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.standardized = {"report_type": "V5_STANDARDIZED_MACRO_METRICS",
                             "as_of": "2026-10-31", "metrics": [
                                 {"series": "UNRATE", "metric": "Three-month change",
                                  "status": "DESCRIPTIVE_TRANSFORM_AVAILABLE",
                                  "value": 0.2, "observation_date": "2026-09-01"}]}
        self.mechanisms = {"report_type": "V5_MECHANISM_EVIDENCE_GATE",
                           "mechanisms": {"labor_growth": {"pit_features_verified": [],
                                                          "required_features": ["unemployment", "real_gdp"]}}}
        self.outcomes = {"event_count": 0, "coverage_status": "NO_VERIFIED_OUTCOME_INPUTS"}
        self.replay = {"report_type": "V5_PIT_REPLAY", "publisher_original_coverage": 0}

    def test_integrated_readout_preserves_block(self):
        report = assemble(self.standardized, self.mechanisms, self.outcomes, self.replay)
        self.assertEqual(report["macro_metric_count"], 1)
        self.assertEqual(report["predictive_publication"], "BLOCKED")
        self.assertEqual(report["outcome_coverage_status"], "NO_VERIFIED_OUTCOME_INPUTS")

    def test_missing_macro_is_visible_not_fabricated(self):
        self.standardized["metrics"].append({"series": "GDPC1", "status": "INSUFFICIENT_HISTORY", "value": None})
        report = assemble(self.standardized, self.mechanisms, self.outcomes, self.replay)
        self.assertEqual(report["macro_metric_count"], 1)
        self.assertEqual(report["macro_metric_total"], 2)
        self.assertIn("GDPC1", render(report))
        self.assertIn("INSUFFICIENT_HISTORY", render(report))

    def test_missing_replay_rejected(self):
        with self.assertRaises(ValueError):
            assemble(self.standardized, self.mechanisms, self.outcomes, {})

    def test_dashboard_renders_evidence_gaps(self):
        report = assemble(self.standardized, self.mechanisms, self.outcomes, self.replay)
        page = render(report)
        self.assertIn("NO_VERIFIED_OUTCOME_INPUTS", page)
        self.assertIn("Predictive publication: BLOCKED", page)

    def test_dashboard_escapes_untrusted_values(self):
        report = assemble(self.standardized, self.mechanisms, self.outcomes, self.replay)
        report["as_of"] = "<script>alert(1)</script>"
        page = render(report)
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)

if __name__ == "__main__":
    unittest.main()
