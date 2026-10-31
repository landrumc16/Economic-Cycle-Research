import unittest
from scripts.workbook_historical_observations import HEADERS, parse_export

class HistoricalWorkbookObservationTests(unittest.TestCase):
    def test_valid_export_retains_observation_and_provenance(self):
        row = ["1", "1987-08-26", "1987-07", "1987-10-19", "NO",
               "1.03", "2.11", "4.7", "-0.4", "2.7", "0.39", "NO"]
        result = parse_export({"pathways": {"source_tab": "CRASH PATHWAY TYPOLOGY",
            "source_range": "A4:L5", "rows": [HEADERS["pathways"], row]}})
        domain = result["domains"]["pathways"]
        self.assertEqual(domain["record_count"], 1)
        self.assertEqual(domain["records"][0]["Daily peak"], "1987-08-26")
        self.assertEqual(result["domains"]["noncrash"]["quality"], "MISSING_EXPORT")
        self.assertEqual(result["publication"], "BLOCKED")

    def test_schema_mismatch_never_accepted(self):
        result = parse_export({"noncrash": {"rows": [["wrong"], ["1987-01"]]}})
        self.assertEqual(result["domains"]["noncrash"]["quality"], "SCHEMA_MISMATCH")

    def test_malformed_rows_fail_closed(self):
        result = parse_export({"pathways": {"rows": [HEADERS["pathways"], ["1"]]}})
        self.assertEqual(result["domains"]["pathways"]["quality"], "ROW_SHAPE_INVALID")

if __name__ == "__main__":
    unittest.main()
