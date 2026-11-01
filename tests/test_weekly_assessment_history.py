import unittest
from scripts.weekly_assessment_history import update, previous

class HistoryTests(unittest.TestCase):
    def test_previous_date(self):
        history=[{"assessment_date":"2026-10-17"},{"assessment_date":"2026-10-24"}]
        self.assertEqual(previous(history,"2026-10-31")["assessment_date"],"2026-10-24")
    def test_same_day_replaces(self):
        history=[{"assessment_date":"2026-10-24","value":1}]
        result=update(history,{"assessment_date":"2026-10-24","value":2,"status":"RESEARCH_SNAPSHOT_NOT_FORECAST"})
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]["value"],2)
    def test_no_future_comparison(self):
        self.assertIsNone(previous([{"assessment_date":"2026-11-07"}],"2026-10-31"))

if __name__=="__main__":
    unittest.main()
