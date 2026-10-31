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
        self.assertIn("Not assessable — source eligibility incomplete",page)
        self.assertIn("Closest historical spread profiles",page)
        macro={"domains":{"growth":{"observation":2.1,"unit":"percent year over year","description":"POSITIVE_REAL_GROWTH"},"labor":{"observation":None,"unit":"percentage points over 3 months","description":"MISSING"},"inflation":{"observation":3.0,"unit":"percent year over year","description":"PRICES_RISING"}}}
        macro_page=make_dashboard(current,history,macro)
        self.assertIn("Real GDP growth",macro_page)
        self.assertIn("Unavailable",macro_page)
        self.assertIn("Consumer price inflation",macro_page)
        self.assertNotIn("CARDS</div>",page)

if __name__=="__main__":
    unittest.main()
