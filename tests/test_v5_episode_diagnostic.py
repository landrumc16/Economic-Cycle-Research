import unittest
from scripts.v5_episode_diagnostic import analyze, shift


class EpisodeDiagnosticTests(unittest.TestCase):
    def test_shift(self):
        self.assertEqual(shift("2008-01", -1), "2007-12")

    def test_warning_and_detection(self):
        rows = [{"month": "2007-12", "phase": "LATE_CYCLE"},
                {"month": "2008-01", "phase": "CONTRACTION"}]
        result = analyze({"status": "HISTORICAL_RESEARCH_ONLY", "timeline": rows})
        episode = next(e for e in result["episodes"] if e["reference_start"] == "2008-01")
        self.assertTrue(episode["pre_recession_12m_warning"])
        self.assertEqual(episode["first_warning_month"], "2007-12")
        self.assertTrue(episode["contraction_detected_during_episode"])

    def test_rejects_wrong_status(self):
        with self.assertRaises(ValueError):
            analyze({"status": "PASS"})


if __name__ == "__main__":
    unittest.main()
