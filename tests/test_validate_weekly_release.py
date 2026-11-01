import json
import tempfile
import unittest
from pathlib import Path
from scripts.validate_weekly_release import validate

class WeeklyReleaseTests(unittest.TestCase):
    def fixture(self, root):
        folder=root/"audit-output"
        folder.mkdir()
        current={"status":"RESEARCH_SNAPSHOT_NOT_FORECAST",
                 "assessment_date":"2026-10-31","common_observation_month":"2026-09-01",
                 "stale":False}
        dashboard={"status":"DESCRIPTIVE_DASHBOARD",
                   "assessment_date":"2026-10-31","common_observation_month":"2026-09-01",
                   "metrics":[{"value":1} for _ in range(9)]}
        timeline={"status":"RETROSPECTIVE_DESCRIPTIVE_ONLY",
                  "months":1,"timeline":[{"month":"2020-01"}]}
        comparison={"status":"RETROSPECTIVE_DESCRIPTIVE_ONLY",
                    "observation_month":"2026-09-01"}
        dashboard["historical_comparison"]=comparison
        dashboard["stale"]=False
        for name,value in (("weekly_economic_assessment.json",current),
                           ("economic_dashboard.json",dashboard),
                           ("historical_cycle_timeline.json",timeline),
                           ("historical_condition_comparison.json",comparison)):
            (folder/name).write_text(json.dumps(value))
        (folder/"economic_dashboard.html").write_text("Economic Cycle Research 2026-10-31")
        return folder
    def test_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            self.fixture(root)
            self.assertEqual(validate(root)["status"],"PASS")
    def test_stale_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=self.fixture(root)
            path=folder/"weekly_economic_assessment.json"
            value=json.loads(path.read_text())
            value["stale"]=True
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                validate(root)
    def test_mismatched_historical_report_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=self.fixture(root)
            path=folder/"historical_condition_comparison.json"
            value=json.loads(path.read_text())
            value["match_count"]=99
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                validate(root)
    def test_unavailable_historical_comparison_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=self.fixture(root)
            path=folder/"historical_condition_comparison.json"
            value=json.loads(path.read_text())
            value["status"]="INSUFFICIENT_CURRENT_DATA"
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                validate(root)
    def test_missing_html_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=self.fixture(root)
            (folder/"economic_dashboard.html").unlink()
            with self.assertRaises(ValueError):
                validate(root)

if __name__=="__main__":
    unittest.main()
