import unittest

from scripts.v5_cycle_estimator import build, classify


def row(**changes):
    value = {"unemployment_change_3m_pp": -0.1,
             "industrial_production_growth_12m_log_pct": 2.0,
             "consumer_credit_growth_12m_log_pct": 3.0,
             "business_credit_growth_12m_log_pct": 2.0}
    value.update(changes)
    return value


class CycleEstimatorTests(unittest.TestCase):
    def test_expansion(self):
        self.assertEqual(classify(row())["phase"], "EXPANSION")

    def test_contraction(self):
        self.assertEqual(classify(row(unemployment_change_3m_pp=0.2,
                                      industrial_production_growth_12m_log_pct=-2))["phase"], "CONTRACTION")

    def test_late_cycle(self):
        self.assertEqual(classify(row(unemployment_change_3m_pp=0.1))["phase"], "LATE_CYCLE")

    def test_recovery(self):
        self.assertEqual(classify(row(consumer_credit_growth_12m_log_pct=-1))["phase"], "RECOVERY")

    def test_missing(self):
        self.assertEqual(classify(row(consumer_credit_growth_12m_log_pct=None))["phase"], "UNCERTAIN")

    def test_historical_cutoff(self):
        timeline = {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
                    "timeline": [{"month": "2020-01", **row()},
                                 {"month": "2020-02", **row(unemployment_change_3m_pp=0.2,
                                                           industrial_production_growth_12m_log_pct=-1)}]}
        report = build(timeline, "2020-01-15")
        self.assertEqual(report["as_of_month"], "2020-01")
        self.assertEqual(report["months"], 1)
        self.assertFalse(report["point_in_time_certified"])
        self.assertEqual(report["status"], "HISTORICAL_RESEARCH_ONLY")

    def test_no_data_before_cutoff(self):
        with self.assertRaises(ValueError):
            build({"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
                   "timeline": [{"month": "2020-01", **row()}]}, "2019-01-01")


if __name__ == "__main__":
    unittest.main()
