import unittest
from datetime import date, timedelta
from scripts.v5_historical_episode_research import evaluate


class HistoricalEpisodeResearchTests(unittest.TestCase):
    def setUp(self):
        self.registry = {"episodes": [{"parent_cluster": "event-a", "peak_date": "2020-03-20"}]}
        self.today = "2026-10-31"

    def test_unverified_control_is_not_negative(self):
        report = evaluate(self.registry, [{"as_of": "2019-01-01", "no_event_observed": True}], as_of=self.today)
        self.assertEqual(report["negative_controls_verified"], 0)

    def test_embargo_rejects_event_neighborhood(self):
        item = {"as_of": "2019-09-01", "no_event_observed": True,
                "complete_outcome_coverage": True, "outcome_source": "independent-audit"}
        report = evaluate(self.registry, [item], as_of=self.today)
        self.assertEqual(report["negative_controls_verified"], 0)
        self.assertEqual(report["candidate_controls"][0]["parent_overlap"], ["event-a"])

    def test_future_horizon_not_labeled(self):
        item = {"as_of": "2026-10-01", "no_event_observed": True,
                "complete_outcome_coverage": True, "outcome_source": "independent-audit"}
        self.assertEqual(evaluate(self.registry, [item], as_of=self.today)["negative_controls_verified"], 0)

    def test_future_candidate_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(self.registry, [{"as_of": "2027-01-01"}], as_of=self.today)

    def test_duplicate_parent_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"episodes": self.registry["episodes"] * 2}, as_of=self.today)

    def test_qualified_control_remains_research_only(self):
        item = {"as_of": "2021-01-01", "no_event_observed": True,
                "complete_outcome_coverage": True, "outcome_source": "independent-audit"}
        result = evaluate(self.registry, [item], as_of=self.today)
        self.assertEqual(result["negative_controls_verified"], 1)
        self.assertEqual(result["predictive_publication"], "BLOCKED")
        self.assertFalse(result["point_in_time_replay_certified"])


if __name__ == "__main__":
    unittest.main()
