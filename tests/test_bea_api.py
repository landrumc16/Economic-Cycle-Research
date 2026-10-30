import json
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from bea_api import parse_bea

def response(rows):
    return json.dumps({"BEAAPI": {"Results": {"Data": rows}}}).encode()

class BEAApiTests(unittest.TestCase):
    def test_quarterly_line_one(self):
        rows = [{"LineNumber":"1", "TimePeriod":"2020Q1", "DataValue":"20,100.500"},
                {"LineNumber":"2", "TimePeriod":"2020Q1", "DataValue":"1.0"}]
        self.assertEqual(parse_bea(response(rows)), {"2020-01-01":20.1005})
    def test_duplicate_quarter_rejected(self):
        rows = [{"LineNumber":"1", "TimePeriod":"2020Q1", "DataValue":"100"}] * 2
        with self.assertRaises(ValueError):
            parse_bea(response(rows))
    def test_missing_quarters_rejected(self):
        with self.assertRaises(ValueError):
            parse_bea(response([]))
    def test_quarter_mapping(self):
        rows = [{"LineNumber":"1", "TimePeriod":"2020Q4", "DataValue":"100"}]
        self.assertEqual(parse_bea(response(rows)), {"2020-10-01":0.1})

if __name__ == "__main__":
    unittest.main()
