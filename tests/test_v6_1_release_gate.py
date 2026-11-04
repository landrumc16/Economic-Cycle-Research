import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.v6_public_site import build
from scripts.v6_1_release_gate import validate


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        fixtures = {
            "v5_integrated_acceptance.json": {"status": "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED"},
            "v5_unified_portal.json": {"monthly_release": "STALE_RESEARCH_ONLY",
                                       "observation_month": "2026-08", "numeric_forecasts_approved": False},
            "weekly_release_acceptance.json": {"status": "STALE_RESEARCH_ONLY"},
            "weekly_economic_assessment.json": {"sources": {}},
        }
        for name, payload in fixtures.items():
            (self.root / name).write_text(json.dumps(payload))
        for name in ("economic_dashboard.html", "v5_dashboard.html", "v5_executive_brief.md"):
            (self.root / name).write_text("accepted research")
        build(self.root, date(2026, 11, 4))

    def test_full_bundle_passes(self):
        report = validate(self.root)
        self.assertEqual(report["status"], "V6_1_ARTIFACTS_VALIDATED")
        self.assertEqual(report["pages_checked"], 16)

    def test_missing_sector_page_fails(self):
        (self.root / "sector-11.html").unlink()
        with self.assertRaisesRegex(ValueError, "Missing V6.1 artifacts"):
            validate(self.root)

    def test_uncertified_forecast_required(self):
        path = self.root / "v6_1_economic_outlook.json"
        payload = json.loads(path.read_text())
        payload["numeric_forecasts_approved"] = True
        path.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "Unverified numeric forecast"):
            validate(self.root)

    def test_sector_count_mismatch_fails(self):
        path = self.root / "v6_1_economic_outlook.json"
        payload = json.loads(path.read_text())
        payload["sector_outlooks_qualified"] = 3
        path.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "Sector counts disagree"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
