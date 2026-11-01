import unittest
from scripts.v5_unified_research_status import build


class UnifiedResearchStatusTests(unittest.TestCase):
    def setUp(self):
        self.release = {"status": "STALE_RESEARCH_ONLY"}
        self.forecast = {"status": "FORECAST_RELEASE_BLOCKED",
                         "numeric_forecasts_approved": False}

    def test_missing_workbook_fails_closed(self):
        result = build(self.release, self.forecast)
        self.assertEqual(result["workbook_reconciliation"], "NOT_RECONCILED")
        self.assertFalse(result["canonical_macro_approved"])
        self.assertFalse(result["numeric_forecasts_approved"])

    def test_blocked_workbook_stays_blocked(self):
        result = build(self.release, self.forecast,
                       {"evidence_reviewed": True,
                        "macro_promotion": {"UNRATE": "BLOCKED", "CPIAUCSL": "BLOCKED",
                                            "GDPC1": "BLOCKED"}})
        self.assertEqual(result["workbook_reconciliation"], "RECONCILED")
        self.assertFalse(result["canonical_macro_approved"])

    def test_unreviewed_approval_does_not_promote(self):
        result = build(self.release, self.forecast,
                       {"macro_promotion": {s: "APPROVED" for s in ("UNRATE", "CPIAUCSL", "GDPC1")}})
        self.assertFalse(result["canonical_macro_approved"])

    def test_forecast_must_be_blocked(self):
        with self.assertRaises(ValueError):
            build(self.release, {"status": "PASS", "numeric_forecasts_approved": True})


if __name__ == "__main__":
    unittest.main()
