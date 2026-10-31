"""V5 release evidence manifest regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.v5_release_evidence_manifest import REQUIRED, summarize


class V5ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.documents = {
            "v5_weekly_research_readout.json": {"as_of": "2026-10-31",
                "macro_metric_count": 0, "macro_metric_total": 4,
                "predictive_publication": "BLOCKED"},
            "v5_standardized_macro_metrics.json": {"as_of": "2026-10-31",
                "predictive_publication": "BLOCKED"},
            "v5_mechanism_evidence_gate.json": {"prediction_status": "BLOCKED"},
            "v5_objective_outcomes.json": {"predictive_publication": "BLOCKED"},
            "v5_pit_replay.json": {"predictive_publication": "BLOCKED"},
            "v5_release_acceptance.json": {"status": "PASS_DESCRIPTIVE_ONLY",
                "predictive_publication": "BLOCKED"},
        }
        for name, document in self.documents.items():
            (self.root / name).write_text(json.dumps(document))
        dashboard = self.root / "dashboard" / "weekly-v5.html"
        dashboard.parent.mkdir(parents=True)
        dashboard.write_text("<html>Descriptive only</html>")

    def test_complete_manifest_passes_without_predictive_claim(self):
        report = summarize(self.root)
        self.assertEqual(report["status"], "DESCRIPTIVE_ARTIFACTS_VERIFIED")
        self.assertEqual(report["artifact_paths"], list(REQUIRED))
        self.assertFalse(report["source_freshness_certified"])
        self.assertFalse(report["independent_predictive_validation_certified"])

    def test_missing_dashboard_fails(self):
        (self.root / "dashboard" / "weekly-v5.html").unlink()
        report = summarize(self.root)
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertIn("dashboard/weekly-v5.html", report["missing"])

    def test_failed_acceptance_fails(self):
        self.documents["v5_release_acceptance.json"]["status"] = "FAIL"
        (self.root / "v5_release_acceptance.json").write_text(
            json.dumps(self.documents["v5_release_acceptance.json"]))
        self.assertEqual(summarize(self.root)["status"], "INCOMPLETE")

    def test_mismatched_dates_fail(self):
        self.documents["v5_standardized_macro_metrics.json"]["as_of"] = "2026-10-30"
        (self.root / "v5_standardized_macro_metrics.json").write_text(
            json.dumps(self.documents["v5_standardized_macro_metrics.json"]))
        self.assertEqual(summarize(self.root)["status"], "INCOMPLETE")

    def test_predictive_unblock_fails(self):
        self.documents["v5_pit_replay.json"]["predictive_publication"] = "APPROVED"
        (self.root / "v5_pit_replay.json").write_text(
            json.dumps(self.documents["v5_pit_replay.json"]))
        self.assertEqual(summarize(self.root)["status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
