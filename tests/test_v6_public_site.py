import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from scripts.v6_public_site import build, observation_summary

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
        self.assertIn("Historical research only",(self.root/"overview.html").read_text())
        self.assertIn("Insufficient Evidence",(self.root/"sectors.html").read_text())
        self.assertIn('name="viewport"',(self.root/"monthly-research.html").read_text())
        self.assertEqual((self.root/"v5_dashboard.html").read_text(),"Existing research")

    def test_rejected_candidate_preserves_last_good(self):
        (self.root/"overview.html").write_text("last good")
        (self.root/"weekly_release_acceptance.json").write_text('{"status":"FAIL"}')
        with self.assertRaises(ValueError):
            build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"overview.html").read_text(),"last good")

    def test_missing_link_preserves_last_good(self):
        (self.root/"index.html").write_text("last good")
        (self.root/"v5_dashboard.html").unlink()
        with self.assertRaises(ValueError):
            build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"index.html").read_text(),"last good")

    def test_observation_values_and_source_dates(self):
        result=observation_summary({
            "industrial_production_growth_12m_log_pct":1.234,
            "sources":{"INDPRO":{"latest_used_month":"2026-09","source_url":"https://fred.stlouisfed.org/series/INDPRO"}}
        })
        self.assertEqual(result[0]["value"],"1.23%")
        self.assertEqual(result[0]["date"],"2026-09")
        self.assertEqual(result[1]["value"],"Unavailable")
        build(self.root,date(2026,11,4))
        self.assertTrue((self.root/"overview.html").exists())

    def test_nonfinite_and_missing_provenance_never_become_current_values(self):
        metrics=observation_summary({
            "industrial_production_growth_12m_log_pct":float("nan"),
            "unemployment_rate_pct":float("inf"),
            "sources":{"INDPRO":None,"UNRATE":"invalid"}
        })
        self.assertEqual(metrics[0]["value"],"Unavailable")
        self.assertEqual(metrics[1]["value"],"Unavailable")
        self.assertEqual(metrics[0]["date"],"unavailable")
        self.assertEqual(metrics[1]["date"],"unavailable")

    def test_monthly_page_uses_dated_prior_comparison_when_available(self):
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD",
            "previous_assessment_date":"2026-09-20",
            "metrics":[{"title":"Unemployment rate","units":"percentage points","delta":0.2},
                       {"title":"Unqualified metric","units":"percent","delta":None}]
        }))
        build(self.root,date(2026,11,4))
        markup=(self.root/"monthly-research.html").read_text()
        self.assertIn("+0.20 percentage points since 2026-09-20",markup)
        self.assertNotIn("Unqualified metric",markup)

    def test_monthly_page_discloses_missing_prior_assessment(self):
        build(self.root,date(2026,11,4))
        self.assertIn("Previous comparable assessment unavailable",
                      (self.root/"monthly-research.html").read_text())

    def test_stale_comparison_is_not_presented_as_current(self):
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD", "stale":True,
            "previous_assessment_date":"2026-09-20",
            "metrics":[{"title":"Unemployment","units":"points","delta":0.3}]
        }))
        build(self.root,date(2026,11,4))
        markup=(self.root/"monthly-research.html").read_text()
        self.assertNotIn("+0.30 points",markup)
        self.assertIn("Previous comparable assessment unavailable",markup)

    def test_page_generation_date_not_mislabeled_as_assessment(self):
        (self.root/"weekly_release_acceptance.json").write_text(json.dumps({
            "status":"STALE_RESEARCH_ONLY","assessment_date":"2026-10-20"
        }))
        build(self.root,date(2026,11,4))
        markup=(self.root/"overview.html").read_text()
        self.assertIn("Page generated: 2026-11-04",markup)
        self.assertIn("Official assessment: 2026-10-20",markup)

    def test_overview_does_not_mislabel_credit_growth_as_stress(self):
        build(self.root,date(2026,11,4))
        overview=(self.root/"overview.html").read_text()
        self.assertIn("Business credit",overview)
        self.assertIn("not a direct financial-stress measure",overview)
        self.assertIn("What changed?",overview)
        self.assertIn("What is uncertain?",overview)

    def test_eleven_sector_detail_pages_link_from_sector_index(self):
        build(self.root,date(2026,11,4))
        listing=(self.root/"sectors.html").read_text()
        for i in range(1,12):
            name=f"sector-{i:02d}.html"
            self.assertIn(f'href="{name}"',listing)
            detail=(self.root/name).read_text()
            self.assertIn('name="viewport"',detail)
            self.assertIn('href="sectors.html"',detail)
            self.assertIn("Insufficient Evidence",detail)

    def test_v6_preserves_accepted_v5_index(self):
        (self.root/"index.html").write_text("V5 accepted landing")
        build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"index.html").read_text(),"V5 accepted landing")

    def test_v6_does_not_replace_accepted_monthly_html(self):
        (self.root/"monthly.html").write_text("previous accepted report")
        build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"monthly.html").read_text(),"previous accepted report")

    def test_rejects_contradictory_freshness(self):
        (self.root/"weekly_release_acceptance.json").write_text('{"status":"PASS"}')
        (self.root/"v5_unified_portal.json").write_text('{"monthly_release":"PASS","numeric_forecasts_approved":false}')
        (self.root/"weekly_economic_assessment.json").write_text('{"stale":true}')
        with self.assertRaises(ValueError):
            build(self.root,date(2026,11,4))

    def test_sector_report_is_parseable_json_and_navigation_resolves(self):
        build(self.root,date(2026,11,4))
        report=json.loads((self.root/"v6_sector_report.json").read_text())
        self.assertEqual(len(report["sectors"]),11)
        overview=(self.root/"overview.html").read_text()
        self.assertIn('href="monthly-research.html"',overview)
        self.assertIn('href="sectors.html"',overview)
        self.assertTrue((self.root/"monthly-research.html").exists())
