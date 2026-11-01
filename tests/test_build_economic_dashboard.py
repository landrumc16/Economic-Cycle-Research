import unittest
from scripts.build_economic_dashboard import compare, render

def sample(day="2026-10-31", stale=False):
    return dict(status="RESEARCH_SNAPSHOT_NOT_FORECAST", assessment_date=day,
                common_observation_month="2026-09-01", stale=stale,
                months_since_common_observation=1,
                equity_acceleration={"historical_percentile":92,"high_acceleration":True},
                housing_acceleration={"historical_percentile":70,"high_acceleration":False},
                consumer_credit_growth_12m_log_pct=3.5,
                business_credit_growth_12m_log_pct=2.0,
                housing_price_income_growth_gap_12m_log_pp=1.2,
                limitations=["Research only"])

class DashboardTests(unittest.TestCase):
    def test_render(self):
        self.assertIn("Economic Cycle Research",render(compare(sample())))
    def test_delta(self):
        previous=sample("2026-10-24")
        previous["consumer_credit_growth_12m_log_pct"]=2.5
        self.assertEqual(compare(sample(),previous)["metrics"][0]["delta"],1.0)
    def test_stale(self):
        self.assertIn("too stale",compare(sample(stale=True))["interpretation"])
    def test_bad_date_order(self):
        with self.assertRaises(ValueError):
            compare(sample("2026-10-24"),sample("2026-10-31"))

if __name__=="__main__":
    unittest.main()
