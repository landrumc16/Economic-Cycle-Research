import pathlib
import tempfile
import unittest
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from milestone1 import compare, parse_bls, parse_fred

class SourceAuditTests(unittest.TestCase):
    def test_reconcile(self):
        result = compare({"2020-01-01": 3.5}, {"2020-01-01": 3.5}, 0.001, min_overlap=1)
        self.assertTrue(result["numeric_pass"])
    def test_mismatch(self):
        result = compare({"2020-01-01": 3.5}, {"2020-01-01": 4.5}, 0.001, min_overlap=1)
        self.assertFalse(result["numeric_pass"])
        self.assertEqual(result["mismatch_count"], 1)
    def test_bls_trailing_headers_and_annual_exclusion(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "bls.tsv"
            p.write_text("series_id\tyear\tperiod\tvalue \nLNS14000000\t2020\tM01\t3.5\nLNS14000000\t2020\tM13\t3.6\n")
            self.assertEqual(parse_bls(p, "LNS14000000"), {"2020-01-01": 3.5})
    def test_fred_headers(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "fred.csv"
            p.write_text("observation_date,UNRATE \n2020-01-01,3.5\n")
            self.assertEqual(parse_fred(p, "UNRATE"), {"2020-01-01": 3.5})
    def test_missing_not_zero(self):
        self.assertEqual(compare({}, {"2020-01-01": 3.5}, 0.01, min_overlap=1)["missing_bls_count"], 1)
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "fred.csv"
            p.write_text("DATE,UNRATE\n2020-01-01,3.5\n2020-01-01,3.5\n")
            with self.assertRaises(ValueError):
                parse_fred(p, "UNRATE")

if __name__ == "__main__":
    unittest.main()
