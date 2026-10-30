import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from api_crosscheck import compare

class ApiCrosscheckTests(unittest.TestCase):
    def test_matching(self):
        x = compare({"2020-01-01": 3.5}, {"2020-01-01": 3.5}, 0.001, 1)
        self.assertTrue(x["revised_series_pass"])
    def test_disagreement(self):
        x = compare({"2020-01-01": 3.5}, {"2020-01-01": 3.6}, 0.001, 1)
        self.assertFalse(x["revised_series_pass"])
        self.assertEqual(x["mismatch_count"], 1)
    def test_insufficient_history(self):
        x = compare({"2020-01-01": 3.5}, {"2020-01-01": 3.5}, 0.001, 600)
        self.assertFalse(x["revised_series_pass"])
    def test_missing_publisher(self):
        x = compare({}, {"2020-01-01": 3.5}, 0.001, 1)
        self.assertEqual(x["missing_publisher_count"], 1)
        self.assertFalse(x["revised_series_pass"])

if __name__ == "__main__":
    unittest.main()
