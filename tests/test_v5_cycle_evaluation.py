import unittest

from scripts.v5_cycle_evaluation import evaluate, reference_recession


class CycleEvaluationTests(unittest.TestCase):
    def test_reference_boundaries(self):
        self.assertFalse(reference_recession("2007-12"))
        self.assertTrue(reference_recession("2008-01"))
        self.assertTrue(reference_recession("2009-06"))
        self.assertFalse(reference_recession("2009-07"))

    def test_counts(self):
        rows = [
            {"month": "2007-12", "phase": "EXPANSION"},
            {"month": "2008-01", "phase": "CONTRACTION"},
            {"month": "2008-02", "phase": "EXPANSION"},
            {"month": "2008-03", "phase": "UNCERTAIN"},
            {"month": "2009-07", "phase": "CONTRACTION"},
        ]
        result = evaluate({"status": "HISTORICAL_RESEARCH_ONLY", "timeline": rows})
        self.assertEqual(result["counts"], {
            "true_positive": 1, "false_positive": 1,
            "true_negative": 1, "false_negative": 1, "uncertain": 1})
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 0.5)
        self.assertFalse(result["point_in_time_certified"])

    def test_rejects_wrong_status(self):
        with self.assertRaises(ValueError):
            evaluate({"status": "PASS", "timeline": []})


if __name__ == "__main__":
    unittest.main()
