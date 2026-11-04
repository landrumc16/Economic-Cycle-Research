import unittest
from scripts.v6_historical_validation import validate_episodes


class HistoricalValidationTests(unittest.TestCase):
    def test_empty_evidence_cannot_certify(self):
        report = validate_episodes([])
        self.assertEqual(report["independent_events"], 0)
        self.assertFalse(report["ready_for_holdout"])
        self.assertFalse(report["predictive_skill_certified"])

    def test_rejects_future_data_and_unverified_history(self):
        item = {"id": "case-1", "outcome": "contraction",
                "signal_date": "2007-01-01", "data_available_date": "2007-02-01",
                "outcome_date": "2008-01-01", "point_in_time_verified": True}
        with self.assertRaises(ValueError):
            validate_episodes([item])
        item["data_available_date"] = "2006-12-01"
        item["point_in_time_verified"] = False
        with self.assertRaises(ValueError):
            validate_episodes([item])

    def test_negative_controls_do_not_count_as_downturns(self):
        rows = []
        for i in range(6):
            outcome = "contraction" if i % 2 == 0 else "non_downturn"
            year = 1990 + 2 * i
            rows.append({"id": f"{outcome}-{i}", "outcome": outcome,
                         "signal_date": f"{year}-01-01",
                         "data_available_date": f"{year-1}-12-01",
                         "outcome_date": f"{year}-12-01",
                         "point_in_time_verified": True})
        report = validate_episodes(rows)
        self.assertEqual(report["independent_events"], 3)
        self.assertEqual(report["negative_controls"], 3)
        self.assertTrue(report["ready_for_holdout"])
        self.assertFalse(report["predictive_skill_certified"])

    def test_overlapping_episodes_and_future_outcomes_rejected(self):
        first = {"id": "a", "outcome": "contraction",
                 "signal_date": "2007-01-01", "data_available_date": "2006-12-01",
                 "outcome_date": "2008-01-01", "point_in_time_verified": True}
        second = dict(first, id="b", signal_date="2007-06-01",
                      data_available_date="2007-05-01", outcome_date="2009-01-01")
        with self.assertRaises(ValueError):
            validate_episodes([first, second])
        with self.assertRaises(ValueError):
            validate_episodes([first], as_of=__import__("datetime").date(2007, 6, 1))

    def test_duplicate_episode_rejected(self):
        item = {"id": "same", "outcome": "non_downturn",
                "signal_date": "2001-01-01", "data_available_date": "2000-12-01",
                "outcome_date": "2002-01-01", "point_in_time_verified": True}
        with self.assertRaises(ValueError):
            validate_episodes([item, item])


if __name__ == "__main__":
    unittest.main()
