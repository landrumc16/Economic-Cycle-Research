import unittest
from scripts.v3_historical_cohort_audit import audit

class HistoricalCohortAuditTests(unittest.TestCase):
    def fixture(self):
        return {"status": "DESCRIPTIVE_ONLY", "publication": "BLOCKED",
                "crash_parent_clusters": [{"parent_cluster": str(i), "prior_month": f"{1980+i}-01",
                                            "peak_date": f"{1980+i}-02-01"} for i in range(8)],
                "monthly_stress_baseline": [{"month": "1970-01"}, {"month": "1980-01"}, {"month": "2000-01"}]}

    def test_screening_does_not_certify_negative_controls(self):
        result = audit(self.fixture())
        self.assertEqual(result["canonical_parent_clusters"], 8)
        self.assertEqual(result["candidate_months_outside_conservative_event_windows"], 2)
        self.assertFalse(result["candidate_months_are_verified_noncrash_controls"])
        self.assertFalse(result["no_lookahead_certified"])
        self.assertEqual(result["predictive_validation"], "BLOCKED")

    def test_duplicate_month_rejected(self):
        data = self.fixture()
        data["monthly_stress_baseline"].append({"month": "1980-01"})
        with self.assertRaises(ValueError):
            audit(data)

if __name__ == "__main__":
    unittest.main()
