import unittest
from scripts.v5_objective_outcomes import label_windows


class ObjectiveOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.events = [{"parent_cluster": "A", "onset_date": "2020-03-01",
                        "end_date": "2020-04-01", "objective_rule": "documented threshold",
                        "outcome_source": "source-id"}]
        self.cutoff = "2026-10-31"

    def window(self, origin, covered=True):
        return {"as_of": origin, "complete_outcome_coverage": covered,
                "outcome_source": "complete-index" if covered else None}

    def test_positive(self):
        x = label_windows(self.events, [self.window("2019-12-01")], self.cutoff)
        self.assertEqual(x["windows"][0]["label"], "POSITIVE_RESEARCH_LABEL")

    def test_negative(self):
        x = label_windows(self.events, [self.window("2021-01-01")], self.cutoff)
        self.assertEqual(x["windows"][0]["label"], "NEGATIVE_RESEARCH_LABEL")
        self.assertEqual(x["predictive_publication"], "BLOCKED")

    def test_missing_coverage(self):
        x = label_windows(self.events, [self.window("2021-01-01", False)], self.cutoff)
        self.assertEqual(x["windows"][0]["label"], "UNVERIFIED_OUTCOME_COVERAGE")

    def test_future_horizon(self):
        x = label_windows(self.events, [self.window("2026-10-01")], self.cutoff)
        self.assertEqual(x["windows"][0]["label"], "CENSORED_FUTURE_HORIZON")

    def test_embargo(self):
        x = label_windows(self.events, [self.window("2020-04-02")], self.cutoff)
        self.assertEqual(x["windows"][0]["label"], "EMBARGOED")

    def test_duplicate_parent(self):
        with self.assertRaises(ValueError):
            label_windows(self.events * 2, [], self.cutoff)

    def test_invalid_chronology(self):
        bad = [dict(self.events[0], end_date="2020-02-01")]
        with self.assertRaises(ValueError):
            label_windows(bad, [], self.cutoff)

    def test_missing_provenance(self):
        bad = [dict(self.events[0], outcome_source="")]
        with self.assertRaises(ValueError):
            label_windows(bad, [], self.cutoff)

    def test_future_origin(self):
        with self.assertRaises(ValueError):
            label_windows(self.events, [self.window("2027-01-01")], self.cutoff)


if __name__ == "__main__":
    unittest.main()
