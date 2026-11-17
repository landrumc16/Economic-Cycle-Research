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
            "weekly_economic_assessment.json": {"status": "RESEARCH_SNAPSHOT_NOT_FORECAST",
                "assessment_date": "2026-11-17", "common_observation_month": "2026-08-01",
                "sources": {name: {"latest_used_month": "2026-08-01"} for name in
                            ("NASDAQCOM", "CSUSHPINSA", "TOTALSL", "BUSLOANS", "PI",
                             "UNRATE", "CPIAUCSL", "INDPRO")}},
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


    # --- Observation-month contract: each module against its own sources ---
    def _edit(self, name, change):
        path = self.folder / name
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def _lagging_housing_and_income(self, data):
        # Real November 2026 pattern: labor, prices, production and credit reach
        # September while Case-Shiller and personal income stop at August.
        for name in ("TOTALSL", "BUSLOANS", "UNRATE", "CPIAUCSL", "INDPRO", "NASDAQCOM"):
            data["sources"][name]["latest_used_month"] = "2026-09-01"

    def test_accept_legitimate_publication_lag_between_modules(self):
        self._edit("weekly_economic_assessment.json", self._lagging_housing_and_income)
        for name in ("v5_dashboard.json", "v5_unified_portal.json"):
            self._edit(name, lambda d: d.update(observation_month="2026-09"))
        result = verify(self.folder)
        self.assertEqual(result["monthly_observation_month"], "2026-08")
        self.assertEqual(result["v5_observation_month"], "2026-09")

    def test_reject_v5_month_not_supported_by_timeline_sources(self):
        # Sources end in August, so a September V5 month would be invented.
        for name in ("v5_dashboard.json", "v5_unified_portal.json"):
            self._edit(name, lambda d: d.update(observation_month="2026-09"))
        with self.assertRaisesRegex(ValueError, "timeline sources"):
            verify(self.folder)

    def test_reject_v5_month_older_than_its_sources(self):
        self._edit("weekly_economic_assessment.json", self._lagging_housing_and_income)
        with self.assertRaisesRegex(ValueError, "timeline sources"):
            verify(self.folder)

    def test_reject_portal_disagreeing_with_v5_dashboard(self):
        self._edit("weekly_economic_assessment.json", self._lagging_housing_and_income)
        self._edit("v5_dashboard.json", lambda d: d.update(observation_month="2026-09"))
        with self.assertRaisesRegex(ValueError, "Historical research mismatch"):
            verify(self.folder)

    def test_reject_monthly_gate_not_matching_assessment(self):
        self._edit("weekly_economic_assessment.json",
                   lambda d: d.update(common_observation_month="2026-07-01"))
        with self.assertRaisesRegex(ValueError, "observation date mismatch"):
            verify(self.folder)

    def test_reject_future_dated_source(self):
        self._edit("weekly_economic_assessment.json",
                   lambda d: d["sources"]["UNRATE"].update(latest_used_month="2026-12-01"))
        with self.assertRaisesRegex(ValueError, "Future-dated"):
            verify(self.folder)

    def test_reject_missing_timeline_series_and_bad_months(self):
        self._edit("weekly_economic_assessment.json", lambda d: d["sources"].pop("BUSLOANS"))
        with self.assertRaisesRegex(ValueError, "lacks V5 timeline series"):
            verify(self.folder)
        self.setUp()
        self._edit("weekly_economic_assessment.json",
                   lambda d: d["sources"]["INDPRO"].update(latest_used_month="2026-13"))
        with self.assertRaisesRegex(ValueError, "Invalid observation month"):
            verify(self.folder)
        self.setUp()
        for name in ("v5_dashboard.json", "v5_unified_portal.json"):
            self._edit(name, lambda d: d.update(observation_month=None))
        with self.assertRaisesRegex(ValueError, "Invalid observation month"):
            verify(self.folder)

    def test_reject_unapproved_or_misdated_assessment(self):
        self._edit("weekly_release_acceptance.json", lambda d: d.update(assessment_date="2026-11-16"))
        with self.assertRaisesRegex(ValueError, "assessment date mismatch"):
            verify(self.folder)
        self.setUp()
        self._edit("weekly_economic_assessment.json", lambda d: d.update(status="FORECAST"))
        with self.assertRaisesRegex(ValueError, "Unapproved monthly assessment"):
            verify(self.folder)


if __name__ == "__main__":
    unittest.main()
