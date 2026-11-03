import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from scripts.v5_unified_portal import build, render


class PortalTests(unittest.TestCase):
    def test_portal_uses_real_release_status_and_blocks_forecasts(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = {
                "unified_research_status.json": {
                    "status": "UNIFIED_RESEARCH_STATUS",
                    "github_monthly_release_status": "STALE_RESEARCH_ONLY",
                    "workbook_reconciliation": "NOT_RECONCILED",
                    "workbook_snapshot_retrieval_date": "2026-11-01",
                    "macro_promotion": {"UNRATE": "BLOCKED", "CPIAUCSL": "BLOCKED", "GDPC1": "BLOCKED"},
                    "canonical_macro_approved": False,
                },
                "v5_dashboard.json": {
                    "status": "V5_RESEARCH_DASHBOARD_ONLY",
                    "observation_month": "2026-08",
                    "preliminary_phase": "EXPANSION",
                },
                "weekly_release_acceptance.json": {"status": "STALE_RESEARCH_ONLY"},
            }
            for name, data in inputs.items():
                (root / name).write_text(json.dumps(data))
            result = build(root)
            self.assertFalse(result["current_conditions_approved"])
            self.assertFalse(result["numeric_forecasts_approved"])
            self.assertIn("Historical cycle diagnostics", render(result))
            inputs["weekly_release_acceptance.json"]["status"] = "PASS"
            (root / "weekly_release_acceptance.json").write_text(json.dumps(inputs["weekly_release_acceptance.json"]))
            with self.assertRaises(ValueError):
                build(root)


if __name__ == "__main__":
    unittest.main()
