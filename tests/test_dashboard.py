import json
import unittest
from pathlib import Path
from scripts.build_dashboard import make_dashboard

ROOT = Path(__file__).resolve().parents[1]

class DashboardTests(unittest.TestCase):
    def test_snapshot_build(self):
        current=json.loads((ROOT/"data/workbook_current_risk_snapshot_2026-10-30.json").read_text())
        history=json.loads((ROOT/"data/workbook_historical_research_snapshot_2026-10-30.json").read_text())
        page=make_dashboard(current,history)
        self.assertIn("Economic Cycle Research",page)
        self.assertIn("444",page)
        self.assertIn("Nasdaq parent crash clusters",page)
        self.assertIn("not a forecast",page)
        self.assertIn("Not eligible for model",page)
        self.assertNotIn("CARDS</div>",page)

if __name__=="__main__":
    unittest.main()
