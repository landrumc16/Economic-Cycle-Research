import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from gdp_reconcile import read_bea, read_fred, reconcile

class GDPTests(unittest.TestCase):
    def test_equal_quarters(self):
        self.assertTrue(reconcile({"2020-01-01": 20000.0}, {"2020-01-01": 20000.0}, minimum=1)["pass"])
    def test_mismatch_blocks(self):
        self.assertFalse(reconcile({"2020-01-01": 20000.0}, {"2020-01-01": 20001.0}, minimum=1)["pass"])
    def test_missing_quarters_block(self):
        self.assertFalse(reconcile({}, {"2020-01-01": 20000.0}, minimum=1)["pass"])
    def test_duplicate_bea_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file = pathlib.Path(directory) / "bea.csv"
            file.write_text("date,value\n2020-01-01,20000\n2020-01-01,20000\n")
            with self.assertRaises(ValueError):
                read_bea(file)
    def test_fred_observation_date(self):
        with tempfile.TemporaryDirectory() as directory:
            file = pathlib.Path(directory) / "fred.csv"
            file.write_text("observation_date,GDPC1\n2020-01-01,20000\n")
            self.assertEqual(read_fred(file), {"2020-01-01": 20000.0})

if __name__ == "__main__":
    unittest.main()
