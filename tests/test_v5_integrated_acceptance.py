import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.v5_integrated_acceptance import verify, FILES


class IntegratedAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        data = {
            "v5_unified_portal.json": {"status": "V5_UNIFIED_RESEARCH_PORTAL",
                "monthly_release": "STALE_RESEARCH_ONLY", "observation_month": "2026-08",
                "research_only": True, "numeric_forecasts_approved": False,
                "current_conditions_approved": False,
                "workbook_reconciliation": "NOT_RECONCILED",
                "macro_promotion": {"UNRATE": "BLOCKED"},
                "daily_refresh_status": "NOT_RECONCILED", "weekly_outlook_status": "DESCRIPTIVE_ONLY",
                "monthly_cycle_status": "RESEARCH_ONLY",
                "workbook_snapshot_review_status": "UNREVIEWED_AUTOMATED_SNAPSHOT",},
            "weekly_release_acceptance.json": {"status": "STALE_RESEARCH_ONLY", "observation_month": "2026-08-01", "current_assessment_approved": False},
            "unified_research_status.json": {"github_monthly_release_status": "STALE_RESEARCH_ONLY",
                "workbook_reconciliation": "NOT_RECONCILED",
                "macro_promotion": {"UNRATE": "BLOCKED"},
                "numeric_forecasts_approved": False,
                "canonical_macro_approved": False,
                "daily_refresh_status": "NOT_RECONCILED", "weekly_outlook_status": "DESCRIPTIVE_ONLY",
                "monthly_cycle_status": "RESEARCH_ONLY",
                "workbook_snapshot_review_status": "UNREVIEWED_AUTOMATED_SNAPSHOT",},
            "v5_forecast_release_gate.json": {"status": "FORECAST_RELEASE_BLOCKED",
                "numeric_forecasts_approved": False},
            "v5_dashboard.json": {"status": "V5_RESEARCH_DASHBOARD_ONLY",
                "observation_month": "2026-08"},
        }
        for name in FILES:
            (self.folder / name).write_text(json.dumps(data[name]) if name in data else
                                            '<meta name="viewport" content="width=device-width">Economic Cycle Research — research-only')

    def test_accept_stale_descriptive_release(self):
        self.assertEqual(verify(self.folder)["status"], "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED")

    def test_reject_broken_portal_link(self):
        (self.folder / "index.html").write_text(
            '<meta name="viewport" content="width=device-width"><a href="missing.html">Report</a> research-only')
        with self.assertRaisesRegex(ValueError, "Broken"):
            verify(self.folder)

    def test_reject_unsafe_portal_link(self):
        (self.folder / "index.html").write_text(
            '<meta name="viewport" content="width=device-width"><a href="../outside.html">Report</a> research-only')
        with self.assertRaisesRegex(ValueError, "unsafe"):
            verify(self.folder)

    def test_reject_missing_mobile_viewport(self):
        (self.folder / "v5_dashboard.html").write_text("<html>research-only</html>")
        with self.assertRaisesRegex(ValueError, "viewport"):
            verify(self.folder)

    def test_reject_missing_artifact(self):
        (self.folder / "index.html").unlink()
        with self.assertRaises(ValueError):
            verify(self.folder)

    def test_reject_forecast_approval(self):
        path = self.folder / "v5_forecast_release_gate.json"
        data = json.loads(path.read_text())
        data["numeric_forecasts_approved"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.folder)

    def test_reject_mismatched_workbook_status(self):
        path = self.folder / "v5_unified_portal.json"
        data = json.loads(path.read_text())
        data["workbook_reconciliation"] = "RECONCILED"
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.folder)

    def test_reject_unified_numeric_forecast_claim(self):
        path = self.folder / "unified_research_status.json"
        data = json.loads(path.read_text())
        data["numeric_forecasts_approved"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.folder)

    def test_reject_stale_as_current(self):
        path = self.folder / "v5_unified_portal.json"
        data = json.loads(path.read_text())
        data["current_conditions_approved"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.folder)


    def test_reject_monthly_observation_mismatch(self):
        path = self.folder / "weekly_release_acceptance.json"
        data = json.loads(path.read_text())
        data["observation_month"] = "2026-07-01"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "observation date mismatch"):
            verify(self.folder)

    def test_reject_stale_monthly_current_claim(self):
        path = self.folder / "weekly_release_acceptance.json"
        data = json.loads(path.read_text())
        data["current_assessment_approved"] = True
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Stale monthly"):
            verify(self.folder)

    def test_reject_cadence_status_mismatch(self):
        path = self.folder / "v5_unified_portal.json"
        data = json.loads(path.read_text())
        data["daily_refresh_status"] = "VERIFIED"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "daily_refresh_status"):
            verify(self.folder)

    def test_reject_unreconciled_macro_promotion(self):
        path = self.folder / "unified_research_status.json"
        data = json.loads(path.read_text())
        data["macro_promotion"]["UNRATE"] = "APPROVED"
        path.write_text(json.dumps(data))
        portal = self.folder / "v5_unified_portal.json"
        p = json.loads(portal.read_text())
        p["macro_promotion"]["UNRATE"] = "APPROVED"
        portal.write_text(json.dumps(p))
        with self.assertRaisesRegex(ValueError, "cannot promote"):
            verify(self.folder)


if __name__ == "__main__":
    unittest.main()
