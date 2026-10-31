import unittest
from scripts.workbook_historical_observations import validate_coverage

class HistoricalIntegrityTests(unittest.TestCase):
    def test_partial_parent_universe_fails(self):
        row = {"Parent cluster": "1", "Daily peak": "1987-08-26", "Prior month": "1987-07", "First 20% crossing": "1987-10-19"}
        self.assertIn("EXPECTED_8_ROWS_GOT_1", validate_coverage("pathways", [row]))
    def test_duplicate_parent_fails(self):
        row = {"Parent cluster": "1", "Daily peak": "1987-08-26", "Prior month": "1987-07", "First 20% crossing": "1987-10-19"}
        self.assertIn("EMPTY_OR_DUPLICATE_KEYS", validate_coverage("pathways", [row]*8))
    def test_month_gap_detected(self):
        row = lambda m: {"Month": m, "Nasdaq cutoff": m+"-28"}
        self.assertIn("NONCONSECUTIVE_OR_UNSORTED_MONTHS", validate_coverage("noncrash", [row("1987-01"),row("1987-03")]))
    def test_date_leak_detected(self):
        row = {"Parent cluster": "1", "Daily peak": "1987-08-26", "Prior month": "1987-09", "First 20% crossing": "1987-10-19"}
        self.assertIn("INVALID_EVENT_CHRONOLOGY", validate_coverage("pathways", [row]))

if __name__ == "__main__":
    unittest.main()
