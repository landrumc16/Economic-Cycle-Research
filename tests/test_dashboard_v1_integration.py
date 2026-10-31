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

    def test_financial_stress_requires_human_approval(self):
        rows = [
            {"series_id": "T10Y2Y", "observation_date": "2026-10-28", "value": -0.4,
             "unit": "pp", "workbook_usable": True, "publisher_verified": True,
             "vintage_verified": True, "human_approved": False},
            {"series_id": "BAA10Y", "observation_date": "2026-10-28", "value": 2.8,
             "unit": "pp", "workbook_usable": True, "publisher_verified": True,
             "vintage_verified": True, "human_approved": False},
        ]
        current = {"snapshot_date": "2026-10-30", "rows": rows}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        page = make_dashboard(current, history)
        self.assertIn("Not assessable", page)
        self.assertNotIn("Historical stress definition met", page)

    def test_v2_historical_conditions_render_in_dashboard(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        v2 = {"status": "DESCRIPTIVE_ONLY",
              "descriptive_comparison": {"crash_parent_clusters": 8, "monthly_observations": 444,
                                         "crashes_with_exact_prior_month_match": 8},
              "crash_parent_clusters": [{"peak_date": "2007-10-31", "prior_month": "2007-09",
                                         "gdp_yoy_pct": 1.93, "inflation_pct": 1.78,
                                         "unemployment_3m_pp": 0.2, "curve_pp": 0.62,
                                         "credit_pp": 2.0, "policy_12m_pp": -0.37,
                                         "monthly_match_status": "EXACT_PRIOR_MONTH_DESCRIPTIVE"}]}
        page = make_dashboard(current, history, v2=v2)
        self.assertIn("Version 2 historical conditions", page)
        self.assertIn("2007-10-31", page)
        self.assertIn("444", page)
        self.assertIn("not verified non-crash controls", page)
        self.assertNotIn("V2HISTORICAL", page)
    def test_v2_24_month_financial_lead_up_renders(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        samples = [{"month": "1998-01", "curve_pp": None, "credit_pp": None,
                    "financial_stress": None, "status": "MISSING_MONTHLY_OBSERVATION"}
                   for _ in range(24)]
        samples[-1] = {"month": "1999-12", "curve_pp": -0.1, "credit_pp": 2.0,
                       "financial_stress": True, "status": "REVISED_NOT_PIT"}
        trajectories = {"status": "DESCRIPTIVE_ONLY",
                        "pathway_profiles": [{"peak_date": "2000-03-10",
                                             "prior_24_months_financial": samples}]}
        page = make_dashboard(current, history, trajectories=trajectories)
        self.assertIn("Version 2: 24-month financial lead-up", page)
        self.assertIn("2000-03-10", page)
        self.assertIn("1/24", page)
        self.assertIn("Unavailable", page)
        self.assertNotIn("V2TRAJECTORIES", page)

    def test_unavailable_analogues_are_explicit(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        page = make_dashboard(current, history, analogues={"status": "INSUFFICIENT_SOURCE_DATA", "analogues": []})
        self.assertIn("Unavailable: insufficient comparable data", page)

if __name__ == "__main__":
    unittest.main()
