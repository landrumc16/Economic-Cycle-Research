import unittest
from datetime import date
from scripts.v5_workbook_freshness import assess


class FreshnessTests(unittest.TestCase):
    def test_recent_unreviewed_is_not_approved(self):
        result = assess({"snapshot_retrieval_date": "2026-11-01",
                         "evidence_reviewed": False}, date(2026, 11, 1))
        self.assertEqual(result["status"], "EVIDENCE_CURRENT")
        self.assertFalse(result["canonical_macro_approved"])

    def test_stale_reviewed_is_not_approved(self):
        result = assess({"snapshot_retrieval_date": "2026-10-01",
                         "evidence_reviewed": True,
                         "macro_promotion": {s: "APPROVED" for s in ("UNRATE", "CPIAUCSL", "GDPC1")}},
                        date(2026, 11, 1))
        self.assertEqual(result["status"], "EVIDENCE_STALE_OR_MISSING")
        self.assertFalse(result["canonical_macro_approved"])

    def test_future_and_missing_dates_fail(self):
        for d in ("2026-12-01", "nonsense", None):
            with self.subTest(d=d):
                self.assertEqual(assess({"snapshot_retrieval_date": d}, date(2026, 11, 1))["status"],
                                 "EVIDENCE_STALE_OR_MISSING")


if __name__ == "__main__":
    unittest.main()
