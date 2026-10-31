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


if __name__ == "__main__":
    unittest.main()
