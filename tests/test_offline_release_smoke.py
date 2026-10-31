"""End-to-end offline release-candidate smoke test, independent of API credentials.

This verifies actual rendering -> JSON state -> acceptance, not live source freshness.
"""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_dashboard import make_dashboard
from scripts.v1_acceptance import evaluate

class OfflineReleaseSmokeTests(unittest.TestCase):
    def test_complete_research_dashboard_passes_acceptance(self):
        current = {"snapshot_date": "2026-10-30", "rows": [
            {"series_id": key, "observation_date": "2026-10-28", "value": value,
             "unit": "pp", "publisher_verified": True, "vintage_verified": True,
             "workbook_usable": True, "human_approved": False}
            for key, value in (("T10Y2Y", 0.4), ("BAA10Y", 1.4))
        ]}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        macro = {"domains": {name: {"observation": 1.0, "unit": "percent",
                                   "description": "RESEARCH_ONLY", "latest_date": "2026-09-01"}
                             for name in ("growth", "labor", "inflation")}}
        assessment = {
            "publication": "BLOCKED", "crash_probability": None,
            "observed_domains": {name: {"interpretation": "Research only"}
                                 for name in ("growth", "labor", "inflation")},
            "mechanism_lenses": {name: {"status": "CONTEXT_ONLY"}
                                 for name in ("inflation_supply_shock", "monetary_tightening",
                                              "valuation_speculation", "credit_housing", "external_shock")},
            "financial_context": {},
        }
        analogues = {
            "status": "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE",
            "crash_probability": None,
            "analogues": [{"episode": name, "status": "EXPLORATORY_ANALOGUE",
                           "normalized_distance": 1.0} for name in
                          ("1973", "1980", "2000", "2007", "2020")],
        }
        page = make_dashboard(current, history, macro=macro, assessment=assessment,
                              analogues=analogues)
        state = {
            "publication": "BLOCKED", "point_in_time_certified": False,
            "crash_probability": None, "validated_cycle_stage": None,
            "macro_domains": macro["domains"], "financial_observations": current["rows"],
            "current_cycle_assessment": assessment,
            "historical_macro_analogues": analogues,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(page, encoding="utf-8")
            (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
            report = evaluate((root / "index.html").read_text(),
                              json.loads((root / "state.json").read_text()))
        self.assertEqual(report["issues"], [])
        self.assertEqual(report["status"], "RESEARCH_DASHBOARD_CANDIDATE")
        self.assertIn("Not assessable", page)
        self.assertIn("2020", page)

    def test_empty_historical_analogue_does_not_pass(self):
        html = "\n".join((
            "Economic Cycle Research", "Current research observations",
            "Growth, labor and inflation", "Integrated economic-cycle assessment",
            "Financial and housing conditions", "Historical macro similarities",
            "Source readiness", "Crash pathway comparison",
        ))
        state = {"publication": "BLOCKED", "point_in_time_certified": False,
                 "crash_probability": None, "validated_cycle_stage": None,
                 "macro_domains": {name: {"observation": 1} for name in ("growth", "labor", "inflation")},
                 "financial_observations": [{"series_id": "BAA10Y"}],
                 "current_cycle_assessment": {"publication": "BLOCKED", "crash_probability": None,
                                              "mechanism_lenses": {str(i): {} for i in range(5)}},
                 "historical_macro_analogues": {"status": "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE",
                                                "analogues": []}}
        self.assertIn("HISTORICAL_EPISODES_INCOMPLETE", evaluate(html, state)["issues"])

if __name__ == "__main__":
    unittest.main()
