import unittest
from scripts.validate_release_evidence import assess

class ReleaseEvidenceTests(unittest.TestCase):
    def test_empty_register_is_blocked(self):
        result = assess({"records": []})
        self.assertEqual(result["quality"], "NO_RECORDS")
        self.assertFalse(result["pit_certified"])
    def test_future_release_is_lookahead(self):
        row = {"series_id": "UNRATE", "publisher": "BLS", "observation_period": "2020-01",
               "release_timestamp": "2020-02-07T08:30:00-05:00",
               "decision_timestamp": "2020-02-06T12:00:00-05:00",
               "reported_value": "3.6", "original_url": "https://www.bls.gov/",
               "sha256": "a"*64, "independent_crosscheck": "pending"}
        result = assess({"records": [row]})
        self.assertIn("LOOKAHEAD_RELEASE_AFTER_DECISION", result["records"][0]["issues"])
    def test_metadata_cannot_certify_source(self):
        row = {"series_id": "UNRATE", "publisher": "BLS", "observation_period": "2020-01",
               "release_timestamp": "2020-02-07T08:30:00-05:00",
               "decision_timestamp": "2020-02-08T12:00:00-05:00",
               "reported_value": "3.6", "original_url": "https://www.bls.gov/",
               "sha256": "a"*64, "independent_crosscheck": "pending"}
        result = assess({"records": [row]})
        self.assertFalse(result["source_authenticity_verified"])
        self.assertEqual(result["publication"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
