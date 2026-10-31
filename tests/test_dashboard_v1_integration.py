"""Dashboard integration smoke tests for Version 1.0."""
import unittest
from scripts.build_dashboard import make_dashboard

class DashboardIntegrationTests(unittest.TestCase):
    def test_cycle_and_historical_analogue_sections_both_render(self):
        current = {"snapshot_date": "2026-10-30", "rows": [
            {"series_id": "T10Y2Y", "observation_date": "2026-10-01", "value": 0.5,
             "unit": "pp", "workbook_usable": False, "vintage_verified": False},
            {"series_id": "BAA10Y", "observation_date": "2026-10-01", "value": 1.8,
             "unit": "pp", "workbook_usable": False, "vintage_verified": False},
        ]}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        assessment = {"observed_domains": {"growth": {"interpretation": "Positive real output growth"}},
                      "mechanism_lenses": {"credit_housing": {"status": "INSUFFICIENT_EVIDENCE"}}}
        analogues = {"status": "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE",
                     "analogues": [{"episode": "2007 credit / housing", "normalized_distance": 1.4,
                                    "status": "EXPLORATORY_ANALOGUE"}]}
        page = make_dashboard(current, history, assessment=assessment, analogues=analogues)
        self.assertIn("Integrated economic-cycle assessment", page)
        self.assertIn("Credit Housing", page)
        self.assertIn("INSUFFICIENT_EVIDENCE", page)
        self.assertIn("Historical macro similarities", page)
        self.assertIn("2007 credit / housing", page)
        self.assertIn("Not assessable", page)
        self.assertNotIn("CYCLEANALOGUES", page)

    def test_financial_context_shows_quality_and_missing_data(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        assessment = {"financial_context": {
            "credit": {"value": 1.43, "observation_date": "2026-10-28",
                       "quality": "STAGED_NOT_APPROVED"},
            "yield_curve": {"value": None, "observation_date": None, "quality": "MISSING"},
        }}
        page = make_dashboard(current, history, assessment=assessment)
        self.assertIn("Financial and housing conditions", page)
        self.assertIn("Corporate credit spread", page)
        self.assertIn("1.43", page)
        self.assertIn("STAGED NOT APPROVED", page)
        self.assertIn("Unavailable", page)
        self.assertIn("No observation", page)

    def test_unavailable_analogues_are_explicit(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        page = make_dashboard(current, history, analogues={"status": "INSUFFICIENT_SOURCE_DATA", "analogues": []})
        self.assertIn("Unavailable: insufficient comparable data", page)

if __name__ == "__main__":
    unittest.main()
