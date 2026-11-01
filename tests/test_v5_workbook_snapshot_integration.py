"""End-to-end contract tests against the checked-in workbook evidence snapshot."""
import json
import unittest
from pathlib import Path
from scripts.v5_workbook_evidence import convert
from scripts.v5_unified_research_status import build


class RealWorkbookSnapshotTests(unittest.TestCase):
    def test_snapshot_to_unified_release(self):
        source = Path("data/workbook_evidence/promotion_gate_2026-11-01.json")
        snapshot = json.loads(source.read_text())
        evidence = convert(snapshot["rows"], snapshot["source_url"], reviewed=False)
        status = build(
            {"status": "STALE_RESEARCH_ONLY"},
            {"status": "FORECAST_RELEASE_BLOCKED", "numeric_forecasts_approved": False},
            evidence,
        )
        self.assertEqual(snapshot["review_status"], "UNREVIEWED_AUTOMATED_SNAPSHOT")
        self.assertEqual(snapshot["retrieval_date"], "2026-11-01")
        self.assertEqual(status["workbook_reconciliation"], "NOT_RECONCILED")
        self.assertEqual(status["macro_promotion"],
                         {"UNRATE": "BLOCKED", "CPIAUCSL": "BLOCKED", "GDPC1": "BLOCKED"})
        self.assertFalse(status["canonical_macro_approved"])
        self.assertFalse(status["numeric_forecasts_approved"])
        self.assertEqual(status["github_monthly_release_status"], "STALE_RESEARCH_ONLY")


if __name__ == "__main__":
    unittest.main()
