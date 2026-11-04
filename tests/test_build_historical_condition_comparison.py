import unittest
from scripts.build_historical_condition_comparison import compare

class HistoricalComparisonTests(unittest.TestCase):
    def setUp(self):
        self.timeline={"status":"RETROSPECTIVE_DESCRIPTIVE_ONLY",
                       "timeline":[{"month":"2020-01","condition_tags":["POSITIVE_INFLATION"],
                                    "unemployment_change_3m_pp":0,
                                    "industrial_production_growth_12m_log_pct":1,
                                    "cpi_inflation_12m_log_pct":2},
                                   {"month":"2027-01","condition_tags":["POSITIVE_INFLATION"],
                                    "unemployment_change_3m_pp":0,
                                    "industrial_production_growth_12m_log_pct":1,
                                    "cpi_inflation_12m_log_pct":2}]}
        self.current={"status":"RESEARCH_SNAPSHOT_NOT_FORECAST",
                      "assessment_date":"2026-10-31","common_observation_month":"2026-09-01",
                      "stale":False,"unemployment_change_3m_pp":0,
                      "industrial_production_growth_12m_log_pct":1,
                      "cpi_inflation_12m_log_pct":2,
                      "consumer_credit_growth_12m_log_pct":-1,
                      "business_credit_growth_12m_log_pct":-1,
                      "equity_acceleration":{"high_acceleration":False},
                      "housing_acceleration":{"high_acceleration":False}}
    def test_excludes_future_months(self):
        report=compare(self.timeline,self.current)
        self.assertEqual(report["historical_months_examined"],1)
        self.assertEqual(report["match_count"],1)
    def test_mixed_observation_dates_do_not_create_false_historical_match(self):
        self.current["sources"] = {
            "UNRATE": {"latest_used_month": "2026-09-01"},
            "CSUSHPINSA": {"latest_used_month": "2026-07-01"},
        }
        report = compare(self.timeline, self.current)
        self.assertEqual(report["status"], "STALE_HISTORICAL_DATA")
        self.assertEqual(report["matches"], [])

    def test_stale_does_not_match(self):
        self.current["stale"]=True
        self.assertEqual(compare(self.timeline,self.current)["status"],"STALE_CURRENT_DATA")

if __name__=="__main__":
    unittest.main()
