import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.v6_sector_intelligence import SECTORS, SENSITIVITY, build_sector_report, economic_backdrop
from scripts.v63_interpretation import interpret
from scripts.v6_public_site import build
from test_v63_interpretation import assessment, AS_OF


class SectorBackdropTests(unittest.TestCase):
    def test_every_sector_has_profile_contrary_case_and_watch_list(self):
        self.assertEqual(set(SENSITIVITY), set(SECTORS))
        for name in SECTORS:
            profile = SENSITIVITY[name]
            self.assertIn(profile["growth"], {"high", "moderate", "low"})
            self.assertTrue(profile["contrary"] and profile["watch"])

    def test_backdrop_follows_condition_and_is_never_an_investment_rating(self):
        expanding = interpret(assessment(), "PASS", AS_OF)
        weak = interpret(assessment(growth=-1.0, labor=0.4, inflation=4.5), "PASS", AS_OF)
        self.assertEqual(economic_backdrop("Industrials", expanding)["backdrop"], "Supportive")
        self.assertEqual(economic_backdrop("Utilities", expanding)["backdrop"], "Neutral")
        self.assertEqual(economic_backdrop("Industrials", weak)["backdrop"], "Headwind")
        self.assertEqual(economic_backdrop("Consumer Staples", weak)["backdrop"], "Relatively resilient")
        self.assertIn("purchasing power", economic_backdrop("Consumer Staples", weak)["inflation_note"])
        self.assertIn("commodities", economic_backdrop("Energy", weak)["inflation_note"])
        self.assertFalse(economic_backdrop("Energy", weak)["is_investment_rating"])
        report = build_sector_report({}, AS_OF, expanding)
        self.assertTrue(all(s["outlook"] == "Insufficient Evidence" for s in report["sectors"]))
        self.assertEqual(len(report["sectors"]), 11)

    def test_unqualified_reading_is_not_assessed(self):
        stale = interpret(assessment(), "STALE_RESEARCH_ONLY", AS_OF)
        for name in SECTORS:
            self.assertEqual(economic_backdrop(name, stale)["backdrop"], "Not assessed")
            self.assertEqual(economic_backdrop(name, None)["backdrop"], "Not assessed")


class SectorPageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        files = {
            "v5_integrated_acceptance.json": {"status": "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED"},
            "v5_unified_portal.json": {"monthly_release": "PASS", "observation_month": "2026-09",
                                       "numeric_forecasts_approved": False},
            "weekly_release_acceptance.json": {"status": "PASS", "assessment_date": "2026-11-01"},
            "weekly_economic_assessment.json": assessment(growth=-1.0, labor=0.4),
        }
        for name, data in files.items():
            (self.root / name).write_text(json.dumps(data))
        for name in ("economic_dashboard.html", "v5_dashboard.html", "v5_executive_brief.md"):
            (self.root / name).write_text("Existing research")

    def test_deteriorating_homepage_lists_resilient_sectors_with_risks(self):
        build(self.root, AS_OF)
        page = (self.root / "overview.html").read_text()
        self.assertIn("Sectors worth investigating", page)
        self.assertIn("Consumer Staples</a> — <strong>Relatively resilient backdrop.", page)
        self.assertIn("Key risk: ", page)
        self.assertIn("What would change this:", page)
        self.assertIn("Facing an economic headwind", page)
        self.assertIn("does not make a sector a good investment", page)
        self.assertIn("No sector has enough verified valuation", page)

    def test_all_eleven_sector_pages_separate_backdrop_from_investment_evidence(self):
        build(self.root, AS_OF)
        for i in range(1, 12):
            detail = (self.root / f"sector-{i:02d}.html").read_text()
            for text in ("Economic backdrop now", "Economic sensitivity", "When the usual pattern failed",
                         "Investment evidence", "Insufficient Evidence", "not an investment rating",
                         "https://fred.stlouisfed.org/series/INDPRO"):
                self.assertIn(text, detail)
            self.assertNotIn('"economic_fit"', detail)  # no raw JSON dump

    def test_mixed_conditions_do_not_produce_shortlist(self):
        (self.root / "weekly_economic_assessment.json").write_text(
            json.dumps(assessment(growth=-1.5, labor=-0.3)))
        build(self.root, AS_OF)
        page = (self.root / "overview.html").read_text()
        self.assertIn("No cycle-based sector shortlist is justified while indicators conflict", page)
        self.assertNotIn("Sectors worth investigating", page)


if __name__ == "__main__":
    unittest.main()
