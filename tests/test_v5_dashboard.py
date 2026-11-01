import unittest
from scripts.v5_dashboard import assemble, render


def fixtures():
    estimates = {"status": "HISTORICAL_RESEARCH_ONLY", "as_of_month": "2026-08",
                 "latest": {"phase": "EXPANSION"}}
    evaluation = {"status": "RETROSPECTIVE_DIAGNOSTIC_ONLY",
                  "counts": {"true_positive": 28, "false_negative": 7,
                             "false_positive": 28, "uncertain": 39}}
    baseline = {"status": "RETROSPECTIVE_OUT_OF_SAMPLE_DIAGNOSTIC_ONLY"}
    gate = {"status": "FORECAST_RELEASE_BLOCKED", "numeric_forecasts_approved": False,
            "horizons": {h: {"evaluation_months": 100, "baseline_brier": 0.2,
                            "phase_frequency_brier": 0.1,
                            "retrospective_benchmark_pass": True}
                         for h in ("3", "6", "12")}}
    episodes = {"status": "RETROSPECTIVE_EPISODE_DIAGNOSTIC_ONLY",
                "episode_count": 4, "pre_recession_warning_episodes": 3}
    return estimates, evaluation, baseline, gate, episodes


class V5DashboardTests(unittest.TestCase):
    def test_research_dashboard_contains_all_horizons(self):
        report = assemble(*fixtures())
        self.assertFalse(report["forecast_probabilities_approved"])
        self.assertIn("12 months", render(report))
        self.assertIn("BLOCKED", render(report))
        self.assertIn("2026-08", render(report))
        self.assertIn("Classification coverage", render(report))
        self.assertGreater(report["classification_coverage"], 0)

    def test_refuses_approved_probabilities(self):
        inputs = list(fixtures())
        inputs[3]["numeric_forecasts_approved"] = True
        with self.assertRaises(ValueError):
            assemble(*inputs)

    def test_refuses_individual_horizon_approval(self):
        inputs = list(fixtures())
        inputs[3]["horizons"]["6"]["numeric_forecast_approved"] = True
        with self.assertRaises(ValueError):
            assemble(*inputs)

    def test_refuses_wrong_status(self):
        inputs = list(fixtures())
        inputs[0]["status"] = "UNAPPROVED"
        with self.assertRaises(ValueError):
            assemble(*inputs)


if __name__ == "__main__":
    unittest.main()
