import unittest
from scripts.v5_pit_replay import replay, chronological_split

class PITTests(unittest.TestCase):
    def test_missing_original_vintage_is_excluded(self):
        rows = [{"series":"GDP","observation_date":"2020-01-01","value":100}]
        self.assertEqual(replay(rows, ["2020-03-01"])["publisher_original_coverage"], 0)

    def test_future_release_excluded(self):
        rows = [{"series":"GDP","observation_date":"2020-01-01","available_at":"2020-04-01","vintage_date":"2020-04-01","publisher_original":True,"value":100}]
        self.assertEqual(replay(rows, ["2020-03-01"])["publisher_original_coverage"], 0)

    def test_valid_replay_remains_blocked(self):
        rows = [{"series":"GDP","observation_date":"2020-01-01","available_at":"2020-02-01","vintage_date":"2020-02-01","publisher_original":True,"value":100}]
        result = replay(rows, ["2020-03-01"])
        self.assertEqual(result["publisher_original_coverage"], 1)
        self.assertEqual(result["predictive_publication"], "BLOCKED")

    def test_split_requires_embargo(self):
        with self.assertRaises(ValueError):
            chronological_split([], "2020-01-31", "2020-02-15")

    def test_split_rejects_shared_parent(self):
        rows = [{"as_of":"2020-01-01","parent_cluster":"A"},{"as_of":"2021-01-01","parent_cluster":"A"}]
        with self.assertRaises(ValueError):
            chronological_split(rows,"2020-06-01","2021-01-01")

if __name__ == "__main__":
    unittest.main()
