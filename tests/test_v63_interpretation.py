import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.v63_interpretation import derive_metrics, interpret, _shift
from scripts.v6_public_site import build

AS_OF = date(2026, 11, 5)


def assessment(growth=2.0, labor=0.0, inflation=2.2, month="2026-09", **extra):
    data = {"stale": False, "assessment_date": "2026-11-01",
            "industrial_production_growth_12m_log_pct": growth,
            "unemployment_change_3m_pp": labor, "unemployment_rate_pct": 4.1,
            "cpi_inflation_12m_log_pct": inflation,
            "industrial_production_momentum_3m_pp": 0.0,
            "cpi_inflation_change_3m_pp": 0.0,
            "unemployment_3m_avg_rise_from_12m_low_pp": 0.1,
            "sources": {s: {"latest_used_month": month,
                            "source_url": "https://fred.stlouisfed.org/series/" + s}
                        for s in ("INDPRO", "UNRATE", "CPIAUCSL", "BUSLOANS")}}
    data.update(extra)
    return data


class RubricFixtureTests(unittest.TestCase):
    def test_current_expansion_is_high_coverage_with_reversal_triggers(self):
        result = interpret(assessment(), "PASS", AS_OF)
        self.assertEqual(result["condition"], "Expanding")
        self.assertEqual(result["direction"], "Steady")
        self.assertEqual(result["evidence_confidence"], "High")
        self.assertFalse(result["is_forecast"])
        self.assertFalse(result["probabilities_published"])
        self.assertTrue(any("-0.5%" in r for r in result["reversal_conditions"]))
        self.assertTrue(any("0.3 percentage points" in r for r in result["reversal_conditions"]))
        self.assertEqual(len(result["drivers"]), 3)

    def test_stale_gate_and_stale_pillar_withhold_judgment(self):
        self.assertEqual(interpret(assessment(), "STALE_RESEARCH_ONLY", AS_OF)["condition"],
                         "Insufficient evidence")
        self.assertEqual(interpret(assessment(stale=True), "PASS", AS_OF)["condition"],
                         "Insufficient evidence")
        old = assessment()
        old["sources"]["INDPRO"]["latest_used_month"] = "2026-06"
        result = interpret(old, "PASS", AS_OF)
        self.assertEqual(result["condition"], "Insufficient evidence")
        self.assertEqual(result["pillars"]["growth"]["status"], "stale")
        self.assertIn("growth (stale)", result["withheld_reason"])
        self.assertEqual(result["reversal_conditions"], [])

    def test_missing_value_or_unverified_source_withholds(self):
        missing = assessment()
        del missing["cpi_inflation_12m_log_pct"]
        self.assertEqual(interpret(missing, "PASS", AS_OF)["pillars"]["inflation"]["status"], "missing")
        self.assertEqual(interpret(missing, "PASS", AS_OF)["condition"], "Insufficient evidence")
        fake = assessment()
        fake["sources"]["UNRATE"]["source_url"] = "https://example.org/UNRATE"
        self.assertEqual(interpret(fake, "PASS", AS_OF)["condition"], "Insufficient evidence")
        nan = assessment(growth=float("nan"))
        self.assertEqual(interpret(nan, "PASS", AS_OF)["condition"], "Insufficient evidence")

    def test_future_observation_is_not_used(self):
        future = assessment(month="2026-12")
        result = interpret(future, "PASS", AS_OF)
        self.assertEqual(result["condition"], "Insufficient evidence")
        self.assertEqual(result["pillars"]["growth"]["status"], "missing")

    def test_contradictory_signals_are_mixed_and_disclosed(self):
        result = interpret(assessment(growth=-1.5, labor=-0.3), "PASS", AS_OF)
        self.assertEqual(result["condition"], "Mixed")
        self.assertIn("Growth and employment point in different directions", result["counterevidence"])
        self.assertNotEqual(result["evidence_confidence"], "High")
        result = interpret(assessment(growth=2.0, labor=0.4), "PASS", AS_OF)
        self.assertEqual(result["condition"], "Mixed")
        self.assertEqual(result["direction"], "Weakening")

    def test_deterioration_and_sahm_style_labor_rule(self):
        result = interpret(assessment(growth=-1.0, labor=0.4, inflation=4.5), "PASS", AS_OF)
        self.assertEqual(result["condition"], "Deteriorating")
        self.assertTrue(any("limits room for policy support" in c for c in result["counterevidence"]))
        rule = interpret(assessment(growth=0.2, labor=0.1,
                                    unemployment_3m_avg_rise_from_12m_low_pp=0.6), "PASS", AS_OF)
        self.assertEqual(rule["condition"], "Deteriorating")
        self.assertTrue(rule["classification"]["labor_rule_triggered"])
        self.assertTrue(any("false alarms" in d for d in rule["drivers"]))

    def test_flat_growth_with_stable_jobs_is_slowing_and_deadband_avoids_false_certainty(self):
        self.assertEqual(interpret(assessment(growth=0.3), "PASS", AS_OF)["condition"], "Slowing")
        self.assertEqual(interpret(assessment(growth=-0.3), "PASS", AS_OF)["condition"], "Slowing")

    def test_missing_momentum_does_not_invent_a_trend(self):
        result = interpret(assessment(industrial_production_momentum_3m_pp=None), "PASS", AS_OF)
        self.assertEqual(result["direction"], "Unconfirmed")
        self.assertEqual(result["evidence_confidence"], "Moderate")

    def test_momentum_and_inflation_trend(self):
        result = interpret(assessment(industrial_production_momentum_3m_pp=-0.8,
                                      inflation=3.2, cpi_inflation_change_3m_pp=0.5), "PASS", AS_OF)
        self.assertEqual(result["direction"], "Softening")
        self.assertEqual(result["classification"]["inflation"], "elevated")
        self.assertEqual(result["classification"]["inflation_trend"], "firming")
        self.assertIn("Inflation remains a risk", result["headline"])

    def test_revision_and_change_since_previous(self):
        previous = assessment(growth=-1.0, labor=0.4)
        previous["assessment_date"] = "2026-10-20"
        current = assessment(growth=1.5, labor=0.0)
        result = interpret(current, "PASS", AS_OF, previous)
        self.assertEqual(result["previous_assessment_date"], "2026-10-20")
        self.assertTrue(any("from Deteriorating to Expanding" in c for c in result["changes_since_previous"]))
        self.assertTrue(any("INDPRO 2026-09 reading revised" in r for r in result["revisions"]))
        self.assertNotEqual(result["evidence_confidence"], "High")

    def test_previous_must_precede_and_be_qualified(self):
        later = assessment()
        later["assessment_date"] = "2026-12-01"
        self.assertEqual(interpret(assessment(), "PASS", AS_OF, later)["changes_since_previous"], [])
        stale = assessment()
        stale.update(assessment_date="2026-10-01", stale=True)
        self.assertIsNone(interpret(assessment(), "PASS", AS_OF, stale)["previous_assessment_date"])


class DerivedMetricTests(unittest.TestCase):
    def test_shift_crosses_years(self):
        self.assertEqual(_shift("2026-02", 3), "2025-11")
        self.assertEqual(_shift("2026-02", 14), "2024-12")

    def test_derive_metrics_and_short_history(self):
        months = [_shift("2026-09", k) for k in range(30)]
        indpro = {m: 100.0 for m in months}
        cpi = {m: 100.0 for m in months}
        unrate = {m: 4.0 for m in months}
        for m in months[:3]:
            unrate[m] = 4.6
        out = derive_metrics(indpro, unrate, cpi)
        self.assertEqual(out["industrial_production_momentum_3m_pp"], 0.0)
        self.assertEqual(out["cpi_inflation_change_3m_pp"], 0.0)
        self.assertAlmostEqual(out["unemployment_3m_avg_rise_from_12m_low_pp"], 0.6)
        short = derive_metrics({"2026-09": 1.0}, {"2026-09": 4.0}, {"2026-09": 1.0})
        self.assertIsNone(short["industrial_production_momentum_3m_pp"])
        self.assertIsNone(short["unemployment_3m_avg_rise_from_12m_low_pp"])


class HomepageIntegrationTests(unittest.TestCase):
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

    def test_homepage_explains_drivers_counterevidence_reversal_and_changes(self):
        previous = assessment(growth=2.0, labor=0.0, month="2026-08")
        previous["assessment_date"] = "2026-10-01"
        (self.root / "previous_weekly_assessment.json").write_text(json.dumps(previous))
        build(self.root, AS_OF)
        page = (self.root / "overview.html").read_text()
        for text in ("Why we think this", "What argues against it", "What would change our view",
                     "What changed since the last accepted assessment",
                     "Condition changed from Expanding to Deteriorating",
                     "Confidence in evidence coverage", "not the odds of any event",
                     "Direction: weakening"):
            self.assertIn(text, page)
        self.assertLess(page.index("1. Where is the economy right now?"),
                        page.index("2. Where do we think it is going?"))
        report = json.loads((self.root / "v6_1_economic_outlook.json").read_text())
        self.assertEqual(report["observed_outlook"]["interpretation"]["condition"], "Deteriorating")
        self.assertFalse(report["observed_outlook"]["interpretation"]["probabilities_published"])

    def test_stale_release_shows_no_rubric_sections(self):
        (self.root / "weekly_release_acceptance.json").write_text(json.dumps({"status": "STALE_RESEARCH_ONLY"}))
        (self.root / "v5_unified_portal.json").write_text(json.dumps(
            {"monthly_release": "STALE_RESEARCH_ONLY", "numeric_forecasts_approved": False}))
        build(self.root, AS_OF)
        page = (self.root / "overview.html").read_text()
        self.assertIn("Insufficient current evidence for a defensible economic call", page)
        self.assertNotIn("What would change our view", page)


if __name__ == "__main__":
    unittest.main()
