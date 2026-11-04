import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from scripts.v6_public_site import build, observation_summary, economic_outlook

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

    def test_v61_inconclusive_when_stale_or_missing(self):
        self.assertEqual(economic_outlook({}, "STALE_RESEARCH_ONLY", date(2026,11,4))["direction"], "Not established")
        self.assertEqual(economic_outlook({"stale": False}, "PASS", date(2026,11,4))["direction"], "Not established")

    def test_v61_observed_direction_does_not_infer_cycle_phase(self):
        base = {"stale": False, "industrial_production_growth_12m_log_pct": 2.0,
                "cpi_inflation_12m_log_pct": 2.5, "unemployment_rate_pct": 4.0,
                "unemployment_change_3m_pp": -0.2,
                "sources": {name: {"latest_used_month": "2026-09",
                                     "source_url": "https://fred.stlouisfed.org/series/" + name}
                            for name in ("INDPRO", "CPIAUCSL", "UNRATE")}}
        result = economic_outlook(base, "PASS", date(2026,11,4))
        self.assertEqual(result["direction"], "Growth and employment improving")
        self.assertEqual(result["phase"], "Not established")
        base["industrial_production_growth_12m_log_pct"] = -2.0
        base["unemployment_change_3m_pp"] = 0.4
        self.assertEqual(economic_outlook(base, "PASS", date(2026,11,4))["direction"],
                         "Growth and employment weakening")
        base["sources"]["UNRATE"]["latest_used_month"] = "2026-05"
        self.assertEqual(economic_outlook(base, "PASS", date(2026,11,4))["direction"],
                         "Not established")
        base["sources"]["UNRATE"]["latest_used_month"] = "2026-09"
        base["sources"]["INDPRO"]["latest_used_month"] = "2026-05"
        self.assertEqual(economic_outlook(base, "PASS", date(2026,11,4))["direction"],
                         "Not established")
        base["sources"]["INDPRO"]["latest_used_month"] = "2026-09"
        base["sources"]["CPIAUCSL"]["latest_used_month"] = "2026-05"
        self.assertEqual(economic_outlook(base, "PASS", date(2026,11,4))["direction"],
                         "Not established")
        base["sources"]["CPIAUCSL"]["latest_used_month"] = "2026-09"

        base["sources"]["INDPRO"]["latest_used_month"] = "2027-01"
        self.assertEqual(economic_outlook(base, "PASS", date(2026,11,4))["direction"], "Not established")

    def test_v61_homepage_leads_with_three_plain_english_questions(self):
        build(self.root, date(2026,11,4))
        content = (self.root/"overview.html").read_text()
        self.assertLess(content.index("Where We Are"), content.index("Where is the economy now?"))
        self.assertIn("Where We Are Heading", content)
        self.assertIn("Where Investors Should Look", content)
        self.assertIn("Insufficient Evidence", content)

    def test_v61_sector_shortlist_discloses_coverage_not_fake_recommendations(self):
        build(self.root, date(2026,11,4))
        overview = (self.root/"overview.html").read_text()
        self.assertIn("0 of 11 sectors currently have evidence-qualified", overview)
        self.assertIn("An unqualified sector is not automatically unattractive", overview)
        self.assertIn("No sector currently qualifies for a buy-oriented ranking", overview)
        self.assertNotIn('<ol><li><a href="sector-01.html"', overview)

    def test_v61_research_library_has_collapsible_evidence_sections(self):
        build(self.root, date(2026,11,4))
        library = (self.root/"research.html").read_text()
        self.assertIn("Research Library", library)
        self.assertGreaterEqual(library.count("<details>"), 5)
        self.assertIn('href="historical.html"', library)
        self.assertIn('href="sectors.html"', library)

    def test_v61_structured_outlook_is_evidence_gated(self):
        build(self.root, date(2026,11,4))
        report = json.loads((self.root/"v6_1_economic_outlook.json").read_text())
        self.assertEqual(report["monthly_gate"], "STALE_RESEARCH_ONLY")
        self.assertEqual(report["observed_outlook"]["direction"], "Not established")
        self.assertFalse(report["historical_phase_certified"])
        self.assertFalse(report["numeric_forecasts_approved"])
        self.assertEqual(report["sector_outlooks_qualified"], 0)
        self.assertEqual(len(report["observed_outlook"]["evidence"]), 4)

    def test_v61_publication_promotes_and_verifies_structured_outlook(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/milestone1.yml").read_text()
        self.assertIn('outlook_path = root / "v6_1_economic_outlook.json"', workflow)
        self.assertIn('outlook.get("numeric_forecasts_approved") is not False', workflow)
        self.assertIn('required += ["v6_1_economic_outlook.json"]', workflow)

    def test_sector_detail_discloses_conditional_rating(self):
        build(self.root,date(2026,11,4))
        detail=(self.root/"sector-01.html").read_text()
        self.assertIn("published only when dated earnings",detail)
        self.assertIn("Insufficient Evidence",detail)
        self.assertNotIn("prevent an investment rating",detail)

    def test_overview_distinguishes_evidence_qualified_sector_outlooks(self):
        build(self.root,date(2026,11,4))
        overview=(self.root/"overview.html").read_text()
        self.assertIn("Evidence-qualified outlooks appear only",overview)
        self.assertIn("Insufficient Evidence",overview)
        self.assertNotIn("Outlooks remain withheld until",overview)

    def test_daily_publication_can_recover_stale_research_with_explicit_warning(self):
        workflow=(Path(__file__).resolve().parents[1]/
                  ".github/workflows/milestone1.yml").read_text()
        self.assertIn('status not in ("PASS", "STALE_RESEARCH_ONLY")',workflow)
        self.assertIn('"Historical research only" not in overview.read_text()',workflow)
        self.assertIn('if status != "PASS" or assessment.get("stale") is not False',workflow)
        self.assertIn('Preserve last accepted monthly report',workflow)

    def test_daily_acquisition_and_monthly_assessment_have_distinct_schedules(self):
        repository=Path(__file__).resolve().parents[1]
        daily=(repository/".github/workflows/milestone1.yml").read_text()
        monthly=(repository/".github/workflows/industry-deviation-descriptive.yml").read_text()
        self.assertIn("    - cron: '15 12 * * *'",daily)
        self.assertIn("    - cron: '20 13 20 * *'",monthly)
        self.assertIn("workflows: ['Monthly Economic Cycle Assessment']",daily)
        self.assertIn("actions/deploy-pages@v4",daily)
        self.assertNotIn("actions/deploy-pages@v4",monthly)

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

    def test_stale_gate_suppresses_otherwise_valid_monthly_deltas(self):
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD","stale":False,
            "previous_assessment_date":"2026-09-20",
            "metrics":[{"title":"Unemployment","units":"points","delta":0.3}]
        }))
        build(self.root,date(2026,11,4))
        for name in ("overview.html","monthly-research.html"):
            content=(self.root/name).read_text()
            self.assertNotIn("+0.30 points",content)
            self.assertIn("monthly data are stale",content)

    def test_future_dated_indicator_is_withheld_on_both_public_pages(self):
        self.root.joinpath("weekly_economic_assessment.json").write_text(json.dumps({
            "industrial_production_growth_12m_log_pct":9.5,
            "sources":{"INDPRO":{"latest_used_month":"2027-01",
                                 "source_url":"https://fred.stlouisfed.org/series/INDPRO"}}
        }))
        result=observation_summary(json.loads(
            (self.root/"weekly_economic_assessment.json").read_text()),
            as_of=date(2026,11,4))
        self.assertEqual(result[0]["value"],"Unavailable")
        self.assertEqual(result[0]["date"],"unavailable")
        build(self.root,date(2026,11,4))
        for page_name in ("overview.html","monthly-research.html"):
            markup=(self.root/page_name).read_text()
            self.assertNotIn("9.50%",markup)
            self.assertIn("Unavailable",markup)

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

    def test_indicator_value_without_valid_observation_month_is_withheld(self):
        assessment = {"unemployment_rate_pct": 4.2,
                      "sources": {"UNRATE": {"source_url": "https://fred.stlouisfed.org/series/UNRATE"}}}
        self.assertEqual(observation_summary(assessment)[1]["value"], "Unavailable")
        assessment["sources"]["UNRATE"]["latest_used_month"] = "2026-99"
        self.assertEqual(observation_summary(assessment)[1]["date"], "unavailable")
        assessment["sources"]["UNRATE"]["latest_used_month"] = "2026-09"
        self.assertEqual(observation_summary(assessment)[1]["value"], "4.20%")

    def test_monthly_assessment_native_full_date_is_accepted(self):
        assessment={"unemployment_rate_pct":4.2,
                    "sources":{"UNRATE":{"latest_used_month":"2026-09-01",
                                         "source_url":"https://fred.stlouisfed.org/series/UNRATE"}}}
        metric=observation_summary(assessment,as_of=date(2026,11,4))[1]
        self.assertEqual(metric["value"],"4.20%")
        self.assertEqual(metric["date"],"2026-09-01")
        assessment["sources"]["UNRATE"]["latest_used_month"]="2026-12-01"
        self.assertEqual(observation_summary(assessment,as_of=date(2026,11,4))[1]["value"],"Unavailable")
        assessment["sources"]["UNRATE"]["latest_used_month"]="2026-09-99"
        self.assertEqual(observation_summary(assessment,as_of=date(2026,11,4))[1]["value"],"Unavailable")

    def test_numeric_observations_require_source_qualified_https_provenance(self):
        assessment={"unemployment_rate_pct":4.2,
                    "sources":{"UNRATE":{"latest_used_month":"2026-09"}}}
        for source_url in (None,"http://fred.stlouisfed.org/series/UNRATE",
                           "https://example.com/UNRATE","https://"):
            assessment["sources"]["UNRATE"]["source_url"]=source_url
            with self.subTest(source_url=source_url):
                metric=observation_summary(assessment)[1]
                self.assertEqual(metric["value"],"Unavailable")
                self.assertEqual(metric["source_url"],"")
        assessment["sources"]["UNRATE"]["source_url"]="https://fred.stlouisfed.org/series/UNRATE"
        metric=observation_summary(assessment)[1]
        self.assertEqual(metric["value"],"4.20%")
        self.assertEqual(metric["source_url"],"https://fred.stlouisfed.org/series/UNRATE")

    def test_register_additional_dated_indicator_without_changing_pipeline(self):
        definitions=(("Housing", "HOUST", "housing_starts_growth_pct",
                      "Housing starts annual growth"),)
        result=observation_summary({
            "housing_starts_growth_pct":2.5,
            "sources":{"HOUST":{"latest_used_month":"2026-09",
                                "source_url":"https://fred.stlouisfed.org/series/HOUST"}}
        },definitions)
        self.assertEqual(result[0]["label"],"Housing")
        self.assertEqual(result[0]["value"],"2.50%")
        self.assertEqual(result[0]["date"],"2026-09")
        self.assertEqual(len(result),1)

    def test_monthly_page_uses_dated_prior_comparison_when_available(self):
        (self.root/"weekly_release_acceptance.json").write_text(json.dumps({"status":"PASS","assessment_date":"2026-10-20"}))
        (self.root/"v5_unified_portal.json").write_text(json.dumps({"monthly_release":"PASS","numeric_forecasts_approved":False}))
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD","stale":False,
            "assessment_date":"2026-10-20",
            "previous_assessment_date":"2026-09-20",
            "metrics":[{"title":"Unemployment rate","units":"percentage points","delta":0.2},
                       {"title":"Unqualified metric","units":"percent","delta":None}]
        }))
        build(self.root,date(2026,11,4))
        markup=(self.root/"monthly-research.html").read_text()
        self.assertIn("+0.20 percentage points since 2026-09-20",markup)
        self.assertNotIn("Unqualified metric",markup)

    def test_comparison_date_must_match_accepted_release(self):
        (self.root/"weekly_release_acceptance.json").write_text(json.dumps({
            "status":"PASS","assessment_date":"2026-10-20"
        }))
        (self.root/"v5_unified_portal.json").write_text(json.dumps({
            "monthly_release":"PASS","numeric_forecasts_approved":False
        }))
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD","stale":False,
            "assessment_date":"2026-10-19","previous_assessment_date":"2026-09-20",
            "metrics":[{"title":"Unemployment","units":"points","delta":0.3}]
        }))
        build(self.root,date(2026,11,4))
        for page_name in ("overview.html","monthly-research.html"):
            markup=(self.root/page_name).read_text()
            self.assertNotIn("+0.30 points",markup)
            self.assertIn("chronology is invalid",markup)

    def test_invalid_comparison_chronology_is_withheld(self):
        gate={"status":"PASS","assessment_date":"2026-10-20"}
        (self.root/"weekly_release_acceptance.json").write_text(json.dumps(gate))
        (self.root/"v5_unified_portal.json").write_text(json.dumps({"monthly_release":"PASS","numeric_forecasts_approved":False}))
        for previous,current in (("2026-10-20","2026-10-20"),("2026-11-01","2026-10-20"),("2026-09-20","2027-01-20")):
            (self.root/"economic_dashboard.json").write_text(json.dumps({
                "status":"DESCRIPTIVE_DASHBOARD","stale":False,
                "assessment_date":current,"previous_assessment_date":previous,
                "metrics":[{"title":"Unemployment","units":"points","delta":0.3}]
            }))
            with self.subTest(previous=previous,current=current):
                build(self.root,date(2026,11,4))
                markup=(self.root/"monthly-research.html").read_text()
                self.assertNotIn("+0.30 points",markup)
                self.assertIn("chronology is invalid",markup)

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

    def test_stale_release_cannot_publish_sector_evidence(self):
        from unittest.mock import patch
        from scripts.v6_sector_intelligence import build_sector_report
        submitted={"Energy":{"outlook":"Favorable"}}
        with patch("scripts.v6_public_site.build_sector_report",
                   side_effect=build_sector_report) as sector_builder:
            build(self.root,date(2026,11,4),submitted)
            self.assertEqual(sector_builder.call_args.args[0],{})
        self.assertIn("Insufficient Evidence",(self.root/"sectors.html").read_text())
        self.assertNotIn("Favorable",(self.root/"sectors.html").read_text())

    def test_historical_comparisons_are_qualified_and_navigable(self):
        build(self.root,date(2026,11,4))
        overview=(self.root/"overview.html").read_text()
        self.assertIn('href="historical.html"',overview)
        historical=(self.root/"historical.html").read_text()
        self.assertIn("unavailable or unqualified",historical)
        self.assertIn('href="v5_dashboard.html"',historical)
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD",
            "historical_comparison":{"status":"RETROSPECTIVE_DESCRIPTIVE_ONLY",
                                     "match_count":8,"historical_months_examined":140}
        }))
        build(self.root,date(2026,11,4))
        historical=(self.root/"historical.html").read_text()
        self.assertIn("8 matching historical months out of 140",historical)
        self.assertIn("not a crash probability",historical)
        (self.root/"economic_dashboard.json").write_text(json.dumps({
            "status":"DESCRIPTIVE_DASHBOARD",
            "historical_comparison":{"status":"RETROSPECTIVE_DESCRIPTIVE_ONLY",
                                     "match_count":141,"historical_months_examined":140}
        }))
        build(self.root,date(2026,11,4))
        self.assertIn("unavailable or unqualified",(self.root/"historical.html").read_text())

    def test_v6_preserves_accepted_v5_index(self):
        (self.root/"index.html").write_text("V5 accepted landing")
        build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"index.html").read_text(),"V5 accepted landing")

    def test_v6_does_not_replace_accepted_monthly_html(self):
        (self.root/"monthly.html").write_text("previous accepted report")
        build(self.root,date(2026,11,4))
        self.assertEqual((self.root/"monthly.html").read_text(),"previous accepted report")

    def test_pass_monthly_release_rejects_future_or_missing_assessment_date(self):
        (self.root/"v5_unified_portal.json").write_text(json.dumps({
            "monthly_release":"PASS","numeric_forecasts_approved":False
        }))
        (self.root/"weekly_economic_assessment.json").write_text(json.dumps({"stale":False}))
        gate=self.root/"weekly_release_acceptance.json"
        for assessment_date in ("2026-12-01", "not-a-date", None):
            gate.write_text(json.dumps({"status":"PASS","assessment_date":assessment_date}))
            with self.subTest(assessment_date=assessment_date):
                with self.assertRaises(ValueError):
                    build(self.root,date(2026,11,4))
        gate.write_text(json.dumps({"status":"PASS","assessment_date":"2026-11-04"}))
        report=build(self.root,date(2026,11,4))
        self.assertEqual(report["monthly_status"],"PASS")

    def test_rejects_contradictory_freshness(self):
        (self.root/"weekly_release_acceptance.json").write_text('{"status":"PASS","assessment_date":"2026-11-04"}')
        (self.root/"v5_unified_portal.json").write_text('{"monthly_release":"PASS","numeric_forecasts_approved":false}')
        (self.root/"weekly_economic_assessment.json").write_text('{"stale":true}')
        with self.assertRaisesRegex(ValueError,"contradicts stale assessment"):
            build(self.root,date(2026,11,4))

    def test_sector_report_is_parseable_json_and_navigation_resolves(self):
        build(self.root,date(2026,11,4))
        report=json.loads((self.root/"v6_sector_report.json").read_text())
        self.assertEqual(len(report["sectors"]),11)
        overview=(self.root/"overview.html").read_text()
        self.assertIn('href="monthly-research.html"',overview)
        self.assertIn('href="sectors.html"',overview)
        self.assertTrue((self.root/"monthly-research.html").exists())
