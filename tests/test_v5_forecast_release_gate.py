import unittest

from scripts.v5_forecast_release_gate import assess


class ForecastReleaseGateTests(unittest.TestCase):
    def test_even_good_retrospective_scores_do_not_approve_live_forecasts(self):
        report = {"status": "RETROSPECTIVE_OUT_OF_SAMPLE_DIAGNOSTIC_ONLY",
                  "results": {h: {"evaluation_months": 150,
                                  "baseline_brier": 0.2,
                                  "phase_frequency_brier": 0.1} for h in ("3", "6", "12")}}
        result = assess(report)
        self.assertEqual(result["status"], "FORECAST_RELEASE_BLOCKED")
        self.assertFalse(result["numeric_forecasts_approved"])
        self.assertTrue(result["horizons"]["3"]["retrospective_benchmark_pass"])
        self.assertFalse(result["horizons"]["3"]["numeric_forecast_approved"])

    def test_insufficient_history_fails_benchmark(self):
        report = {"status": "RETROSPECTIVE_OUT_OF_SAMPLE_DIAGNOSTIC_ONLY",
                  "results": {h: {"evaluation_months": 5,
                                  "baseline_brier": 0.2,
                                  "phase_frequency_brier": 0.1} for h in ("3", "6", "12")}}
        self.assertFalse(assess(report)["horizons"]["12"]["retrospective_benchmark_pass"])

    def test_rejects_unapproved_status(self):
        with self.assertRaises(ValueError):
            assess({"status": "PASS"})


if __name__ == "__main__":
    unittest.main()
