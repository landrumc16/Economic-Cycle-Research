"""Regression checks for integrated V2 dashboard evidence panels."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.build_dashboard import make_dashboard


class V2DashboardIntegrationTests(unittest.TestCase):
    def test_global_and_mechanism_panels_fail_closed(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        assessment = {"mechanism_lenses": {
            "credit_housing": {"status": "INSUFFICIENT_EVIDENCE",
                               "missing": ["bank funding stress"]}}}
        global_context = {"channels": [{
            "channel": "global_usd_funding",
            "status": "SOURCE_NOT_ACQUIRED",
            "candidate_primary_source": "BIS"}]}
        page = make_dashboard(current, history, assessment=assessment,
                              global_context=global_context)
        self.assertIn("International economic transmission", page)
        self.assertIn("SOURCE_NOT_ACQUIRED", page)
        self.assertIn("Crash mechanism evidence gaps", page)
        self.assertIn("bank funding stress", page)
        self.assertIn("not a forecast", page.lower())
        self.assertNotIn("V2GLOBAL", page)
        self.assertNotIn("V2LENSES", page)


    def test_historical_current_bridge_does_not_claim_comparability(self):
        current = {"snapshot_date": "2026-10-30", "rows": []}
        history = {"pathways": {"rows": [["header"]]}, "noncrash": {"rows": [["header"]]}}
        assessment = {"observed_domains": {
            "growth": {"value": 2.1},
            "inflation": {"value": None},
            "labor": {"value": 0.2}}}
        v2 = {"status": "DESCRIPTIVE_ONLY", "crash_parent_clusters": [
            {"gdp_yoy_pct": -1.2, "inflation_pct": 4.1, "unemployment_3m_pp": 0.4},
            {"gdp_yoy_pct": 3.5, "inflation_pct": 2.1, "unemployment_3m_pp": 0.1}]}
        page = make_dashboard(current, history, assessment=assessment, v2=v2)
        self.assertIn("Current conditions vs historical crash contexts", page)
        self.assertIn("-1.2 to 3.5", page)
        self.assertIn("NOT_COMPARABLE_WITHOUT_UNIT_AND_VINTAGE_AUDIT", page)
        self.assertIn("Unavailable", page)
        self.assertNotIn("V2BRIDGE", page)

if __name__ == "__main__":
    unittest.main()
