import unittest
from scripts.v5_executive_brief import build


class ExecutiveBriefTests(unittest.TestCase):
    def test_research_brief_discloses_limits(self):
        estimates = {"status": "HISTORICAL_RESEARCH_ONLY", "as_of_month": "2020-01",
                     "latest": {"phase": "LATE_CYCLE",
                                "supporting_signals": ["labor_softening"],
                                "conflicting_signals": ["production_contracting"]}}
        outcomes = {"status": "RETROSPECTIVE_FORWARD_OUTCOMES_ONLY",
                    "results": {str(h): {"event_months": 1, "eligible_months": 10}
                                for h in (3, 6, 12)}}
        brief = build(estimates, outcomes)
        self.assertIn("2020-01", brief)
        self.assertIn("Late Cycle", brief)
        self.assertIn("not forecasts", brief)
        self.assertIn("12 months", brief)

    def test_rejects_unapproved_inputs(self):
        with self.assertRaises(ValueError):
            build({"status": "PASS"}, {"status": "PASS"})


if __name__ == "__main__":
    unittest.main()
