"""Checks for readout missingness, freshness ordering and approval boundaries."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from economic_observation_readout import build_readout, REQUIRED_CHECKS, SERIES

class ReadoutTests(unittest.TestCase):
    def test_revised_data_never_published(self):
        raw = {"UNRATE": {"2026-08-01": 4.3, "2026-09-01": 4.2}}
        report = build_readout(raw, {})
        self.assertEqual(report["observations"]["UNRATE"]["value"], 4.2)
        self.assertEqual(report["observations"]["UNRATE"]["quality"], "REVISED_RESEARCH_ONLY")
        self.assertEqual(report["observations"]["GDPC1"]["quality"], "MISSING")
        self.assertEqual(report["publication"], "BLOCKED")
        self.assertIsNone(report["crash_probability"])

    def test_approval_requires_all_evidence(self):
        raw = {"GDPC1": {"2026-07-01": 24000.0}}
        gate = {"all_evidence_pass": True, "series": {"GDPC1": {k: True for k in REQUIRED_CHECKS}}}
        report = build_readout(raw, gate, {"GDPC1": "APPROVED"})
        self.assertEqual(report["observations"]["GDPC1"]["quality"], "APPROVED_SOURCE")
        self.assertFalse(report["observations"]["UNRATE"]["eligible_for_published_model"])
        self.assertEqual(report["publication"], "BLOCKED")

    def test_invalid_numbers_do_not_become_zero(self):
        raw = {"CPIAUCSL": {"2026-08-01": None, "2026-09-01": "NaN", "2026-07-01": 330.1}}
        report = build_readout(raw, {})
        self.assertEqual(report["observations"]["CPIAUCSL"]["observation_date"], "2026-07-01")
        self.assertEqual(report["observations"]["CPIAUCSL"]["value"], 330.1)

if __name__ == "__main__":
    unittest.main()
