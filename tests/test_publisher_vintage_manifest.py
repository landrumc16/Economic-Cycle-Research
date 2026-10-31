import unittest
from scripts.validate_publisher_vintage_manifest import assess

def fixture():
    return {"series": [
        {"id": id, "publisher": pub, "required": [
            "original_release_url_or_archive", "publisher_release_timestamp_timezone",
            "original_reported_value", "publisher_original_file_hash",
            "decision_timestamp", "independent_crosscheck"
        ], "pit_certified": False, "human_approved": False}
        for id, pub in [("UNRATE", "BLS"), ("CPIAUCSL", "BLS"), ("GDPC1", "BEA")]
    ]}

class ManifestTests(unittest.TestCase):
    def test_contract_pass_does_not_authorize_forecast(self):
        r = assess(fixture())
        self.assertEqual(r["manifest_integrity"], "PASS_CONTRACT_ONLY")
        self.assertFalse(r["forecast_authorized"])
    def test_missing_series_fails(self):
        x = fixture()
        x["series"].pop()
        self.assertEqual(assess(x)["manifest_integrity"], "FAIL_CONTRACT")
    def test_false_certification_fails(self):
        x = fixture()
        x["series"][0]["pit_certified"] = True
        self.assertEqual(assess(x)["manifest_integrity"], "FAIL_CONTRACT")

if __name__ == "__main__":
    unittest.main()
