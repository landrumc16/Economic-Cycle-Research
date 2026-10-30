"""Financial overlay remains descriptive and rejects unsupported observations."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from financial_housing_overlay import build_overlay

class OverlayTests(unittest.TestCase):
    def test_staged_value_not_approved(self):
        rows = [{"series_id": "BAA10Y", "observation_date": "2026-10-28",
                 "value": 1.43, "publisher_verified": True,
                 "vintage_verified": True}]
        report = build_overlay(rows, "2026-10-30")
        self.assertEqual(report["domains"]["credit"]["quality"], "STAGED_NOT_APPROVED")
        self.assertIsNone(report["crash_probability"])
        self.assertEqual(report["publication"], "BLOCKED")

    def test_explicit_approval_does_not_create_score(self):
        rows = [{"series_id": "HOUST", "observation_date": "2026-09-01",
                 "value": 1221, "publisher_verified": True,
                 "vintage_verified": True, "human_approved": True}]
        report = build_overlay(rows, "2026-10-30")
        self.assertTrue(report["domains"]["housing_starts"]["published_model_eligible"])
        self.assertIsNone(report["composite_risk_score"])

    def test_duplicate_and_future_dates_rejected(self):
        row = {"series_id": "TDSP", "observation_date": "2026-11-01", "value": 11}
        report = build_overlay([row], "2026-10-30")
        self.assertEqual(report["domains"]["household_debt_service"]["quality"], "INVALID_OBSERVATION")
        with self.assertRaises(ValueError):
            build_overlay([row, row], "2026-10-30")

if __name__ == "__main__":
    unittest.main()
