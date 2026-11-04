import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from scripts.v6_public_site import build

class PublicSiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for name, data in {
            "v5_integrated_acceptance.json":{"status":"V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED"},
            "v5_unified_portal.json":{"monthly_release":"STALE_RESEARCH_ONLY","observation_month":"2026-08","numeric_forecasts_approved":False},
            "weekly_release_acceptance.json":{"status":"STALE_RESEARCH_ONLY"},
            "weekly_economic_assessment.json":{"sources":{"UNRATE":{"latest_used_month":"2026-08"}}}
        }.items():
            (self.root/name).write_text(json.dumps(data))
        for name in ("economic_dashboard.html","v5_dashboard.html","v5_executive_brief.md"):
            (self.root/name).write_text("Existing research")

    def test_build_preserves_stale_warning_and_research(self):
        report=build(self.root,date(2026,11,4))
        self.assertEqual(report["sector_count"],11)
        self.assertIn("Historical research only",(self.root/"index.html").read_text())
        self.assertIn("Insufficient Evidence",(self.root/"sectors.html").read_text())
        self.assertIn('name="viewport"',(self.root/"monthly.html").read_text())
        self.assertEqual((self.root/"v5_dashboard.html").read_text(),"Existing research")

    def test_rejected_candidate_preserves_last_good(self):
        (self.root/"index.html").write_text("last good")
        (self.root/"weekly_release_acceptance.json").write_text('{"status":"FAIL"}')
        with self.assertRaises(ValueError):
            build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"index.html").read_text(),"last good")

    def test_missing_link_preserves_last_good(self):
        (self.root/"index.html").write_text("last good")
        (self.root/"v5_dashboard.html").unlink()
        with self.assertRaises(ValueError):
            build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"index.html").read_text(),"last good")
