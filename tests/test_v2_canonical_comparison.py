"""Regression checks for Version 2 canonical evidence bridge."""
import json
import unittest
from pathlib import Path
from scripts.v2_canonical_comparison import build

SNAPSHOT = Path("data/workbook_historical_research_snapshot_2026-10-30.json")

class CanonicalComparisonTests(unittest.TestCase):
    def test_full_snapshot_has_expected_parent_clusters_and_monthly_rows(self):
        raw = SNAPSHOT.read_bytes()
        report = build(json.loads(raw), raw)
        self.assertEqual(report["descriptive_comparison"]["crash_parent_clusters"], 8)
        self.assertEqual(report["descriptive_comparison"]["monthly_observations"], 444)
        self.assertEqual(report["descriptive_comparison"]["crash_parent_clusters_with_stress"], 3)
        self.assertEqual(report["publication"], "BLOCKED")
        self.assertIsNone(report["crash_probability"])
        self.assertEqual(len(report["provenance"]["sha256_export"]), 64)
        self.assertEqual(report["provenance"]["extraction_timestamp_status"], "NOT_RECORDED_IN_SOURCE_EXPORT")

    def test_exact_prior_month_matches_preserve_monthly_context(self):
        raw = SNAPSHOT.read_bytes()
        report = build(json.loads(raw), raw)
        matched = [r for r in report["crash_parent_clusters"] if r["matched_prior_month"]]
        self.assertEqual(report["descriptive_comparison"]["crashes_with_exact_prior_month_match"], len(matched))
        for crash in matched:
            self.assertEqual(crash["matched_prior_month"]["month"], crash["prior_month"])
            self.assertEqual(crash["monthly_match_status"], "EXACT_PRIOR_MONTH_DESCRIPTIVE")
        self.assertIn("NOT verified non-crash controls", report["limitations"][0])

    def test_source_approval_is_not_assumed(self):
        raw = SNAPSHOT.read_bytes()
        data = json.loads(raw)
        data["human_approved_for_prediction"] = True
        with self.assertRaises(ValueError):
            build(data, raw)

    def test_rejects_wrong_source_tab(self):
        raw = SNAPSHOT.read_bytes()
        data = json.loads(raw)
        data["noncrash"]["source_tab"] = "UNVERIFIED"
        with self.assertRaises(ValueError):
            build(data, raw)

    def test_missing_values_stay_missing(self):
        raw = SNAPSHOT.read_bytes()
        data = json.loads(raw)
        data["pathways"]["rows"][1][5] = ""
        report = build(data, raw)
        self.assertIsNone(report["crash_parent_clusters"][0]["curve_pp"])

if __name__ == "__main__":
    unittest.main()
