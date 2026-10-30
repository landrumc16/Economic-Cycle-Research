import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from validate_pit import validate

BASE = {"series":"UNRATE","observation_date":"2008-08-01",
        "publication_date":"2008-09-05","decision_date":"2008-09-15",
        "vintage_date":"2008-09-05","value":"6.1",
        "source_url":"https://www.bls.gov/news.release/archives/empsit_09052008.htm"}

class PITTests(unittest.TestCase):
    def test_valid_metadata_not_certification(self):
        result = validate([BASE])
        self.assertTrue(result["metadata_pass"])
        self.assertEqual(result["promotion"], "BLOCKED")
    def test_publication_after_decision(self):
        item = dict(BASE, decision_date="2008-09-01")
        self.assertFalse(validate([item])["metadata_pass"])
    def test_later_vintage(self):
        item = dict(BASE, vintage_date="2009-01-09")
        self.assertFalse(validate([item])["metadata_pass"])
    def test_duplicate(self):
        self.assertFalse(validate([BASE, BASE])["metadata_pass"])
    def test_empty(self):
        self.assertFalse(validate([])["metadata_pass"])

if __name__ == "__main__":
    unittest.main()
