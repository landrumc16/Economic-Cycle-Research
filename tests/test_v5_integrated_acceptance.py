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
                "current_conditions_approved": False},
            "weekly_release_acceptance.json": {"status": "STALE_RESEARCH_ONLY"},
            "unified_research_status.json": {"github_monthly_release_status": "STALE_RESEARCH_ONLY"},
            "v5_forecast_release_gate.json": {"status": "FORECAST_RELEASE_BLOCKED",
                "numeric_forecasts_approved": False},
            "v5_dashboard.json": {"status": "V5_RESEARCH_DASHBOARD_ONLY",
                "observation_month": "2026-08"},
        }
        for name in FILES:
            (self.folder / name).write_text(json.dumps(data[name]) if name in data else
                                            "Economic Cycle Research — research-only")

    def test_accept_stale_descriptive_release(self):
        self.assertEqual(verify(self.folder)["status"], "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED")

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

    def test_reject_stale_as_current(self):
        path = self.folder / "v5_unified_portal.json"
        data = json.loads(path.read_text())
        data["current_conditions_approved"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.folder)


if __name__ == "__main__":
    unittest.main()
