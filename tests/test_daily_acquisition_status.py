"""Regression tests for daily acquisition evidence and fail-closed status."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.daily_acquisition_status import REPORTS, summarize


class DailyAcquisitionTests(unittest.TestCase):
    def test_complete_reports_never_promote(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for source, path in REPORTS.items():
                report = root / path
                report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text(json.dumps({"promotion": "BLOCKED", "errors": [], "series": {"test": {"observations": 1}}} if source != "BEA" else {"promotion": "BLOCKED", "status": "ACQUIRED NOT RECONCILED", "observations": 1}))
            result = summarize(root, {"FRED": "success", "BLS": "success", "BEA": "success"})
            self.assertTrue(result["acquisition_complete"])
            self.assertEqual(result["source_promotion"], "BLOCKED")
            self.assertFalse(result["workbook_reconciled"])
            self.assertFalse(result["numeric_forecasts_approved"])

    def test_failed_step_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in REPORTS.values():
                report = root / path
                report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text("{}")
            result = summarize(root, {"FRED": "success", "BLS": "failure", "BEA": "success"})
            self.assertFalse(result["acquisition_complete"])

    def test_missing_report_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for key, path in REPORTS.items():
                if key != "BEA":
                    report = root / path
                    report.parent.mkdir(parents=True, exist_ok=True)
                    report.write_text(json.dumps({"promotion": "BLOCKED", "errors": [], "series": {"test": {"observations": 1}}}))
            result = summarize(root, {"FRED": "success", "BLS": "success", "BEA": "success"})
            self.assertFalse(result["acquisition_complete"])

    def test_corrupt_report_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for source, path in REPORTS.items():
                report = root / path
                report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text("not json")
            result = summarize(root, {"FRED": "success", "BLS": "success", "BEA": "success"})
            self.assertFalse(result["acquisition_complete"])
            self.assertFalse(any(result["reports_valid"].values()))

    def test_report_with_errors_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for source, path in REPORTS.items():
                report = root / path
                report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text(json.dumps({"promotion": "BLOCKED", "errors": ["upstream failed"], "series": {"test": {"observations": 1}}} if source != "BEA" else {"promotion": "BLOCKED", "status": "ACQUIRED NOT RECONCILED", "observations": 1}))
            result = summarize(root, {"FRED": "success", "BLS": "success", "BEA": "success"})
            self.assertFalse(result["acquisition_complete"])

    def test_missing_step_outcome_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertFalse(summarize(Path(temp), {})["acquisition_complete"])


if __name__ == "__main__":
    unittest.main()
