import tempfile
import unittest
import json
from pathlib import Path
from scripts.source_refresh_manifest import inventory

class RefreshManifestTests(unittest.TestCase):
    def test_missing_is_not_complete(self):
        with tempfile.TemporaryDirectory() as d:
            r=inventory(d,"2026-10-30")
            self.assertFalse(r["complete"])
            self.assertEqual(r["series"]["UNRATE"]["status"],"MISSING")

    def test_valid_and_future_dated(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"UNRATE_normalized.json"
            path.write_text(json.dumps({"2026-09-01":4.2}))
            r=inventory(d,"2026-10-30")
            self.assertEqual(r["series"]["UNRATE"]["status"],"STAGED_REVISED_NOT_PIT")
            self.assertEqual(r["series"]["UNRATE"]["age_days"],59)
            path.write_text(json.dumps({"2026-11-01":4.2}))
            self.assertEqual(inventory(d,"2026-10-30")["series"]["UNRATE"]["status"],"INVALID")

if __name__=="__main__":
    unittest.main()
