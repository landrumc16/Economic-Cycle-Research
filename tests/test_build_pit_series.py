import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from build_pit_series import build

def row(pub, vintage, value, decision="2020-05-01"):
    return {"series":"UNRATE", "observation_date":"2020-01-01",
        "publication_date":pub, "vintage_date":vintage,
        "decision_date":decision, "value":str(value),
        "source_url":"https://example.org/release"}

class PointInTimeSelectionTests(unittest.TestCase):
    def test_latest_available_release_selected(self):
        rows = [row("2020-02-07","2020-02-07",3.6),
                row("2020-03-06","2020-03-06",3.5)]
        selected, errors = build(rows)
        self.assertFalse(errors)
        self.assertEqual(selected[0]["value"], 3.5)
    def test_future_revision_rejected(self):
        selected, errors = build([row("2020-06-01","2020-06-01",3.4)])
        self.assertFalse(selected)
        self.assertTrue(errors)
    def test_ambiguous_release_rejected(self):
        selected, errors = build([row("2020-02-07","2020-02-07",3.6),
                                  row("2020-02-07","2020-02-07",3.7)])
        self.assertFalse(selected)
        self.assertTrue(errors)
    def test_missing_value_rejected(self):
        selected, errors = build([row("2020-02-07","2020-02-07","")])
        self.assertFalse(selected)
        self.assertTrue(errors)
    def test_reject_nonfinite(self):
        selected, errors = build([row("2020-02-07","2020-02-07","nan")])
        self.assertFalse(selected)
        self.assertTrue(errors)
    def test_observation_date_remains_separate(self):
        selected, errors = build([row("2020-02-07","2020-02-07",3.6)])
        self.assertEqual(selected[0]["observation_date"], "2020-01-01")

if __name__ == "__main__":
    unittest.main()
