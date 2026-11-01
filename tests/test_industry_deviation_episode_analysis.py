import unittest
from scripts.industry_deviation_episode_analysis import episodes


def series(values):
    return [{"date": f"{2000 + i // 12:04d}-{i % 12 + 1:02d}-01",
             "value": str(value)} for i, value in enumerate(values)]


class EpisodeAnalysisTests(unittest.TestCase):
    def test_flat_series_has_no_alerts(self):
        result = episodes(series([100] * 120))
        self.assertEqual(result["alert_clusters"], 0)
        self.assertIsNone(result["observed_hit_fraction"])

    def test_short_history_has_no_alerts(self):
        result = episodes(series([100 + i for i in range(24)]))
        self.assertEqual(result["alert_clusters"], 0)

    def test_accounting_is_complete(self):
        values = [100 + i * 0.1 for i in range(75)]
        values += [values[-1] * (1.09 ** i) for i in range(1, 13)]
        values += [values[-1] * (0.91 ** i) for i in range(1, 13)]
        values += [values[-1]] * 24
        result = episodes(series(values))
        self.assertEqual(result["alert_clusters"], len(result["episodes"]))
        self.assertEqual(result["eligible_clusters"], result["clusters_with_decline"] +
                         result["clusters_without_decline"])
        self.assertEqual(result["alert_clusters"], result["eligible_clusters"] +
                         result["clusters_without_full_followup"])
        self.assertTrue(all(item["first_alert"] <= item["last_alert"]
                            for item in result["episodes"]))

    def test_parameter_validation(self):
        with self.assertRaises(ValueError):
            episodes(series([100] * 80), horizon=0)


if __name__ == "__main__":
    unittest.main()
