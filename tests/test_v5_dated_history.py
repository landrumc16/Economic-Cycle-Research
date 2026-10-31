import json
import tempfile
import unittest
from pathlib import Path
from scripts.v5_dated_history import build
from scripts.v5_standardized_macro import build as metrics

class V5HistoryBridgeTests(unittest.TestCase):
    def test_dated_history_feeds_real_inflation_transformation(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "CPIAUCSL_normalized.json").write_text(json.dumps({
                "2025-09-01": 300.0, "2026-09-01": 309.0, "2026-11-01": 320.0}))
            history = build(tmp, "2026-10-31")
            result = metrics(history)
            cpi = next(x for x in result["metrics"] if x["series"] == "CPIAUCSL")
            self.assertEqual(cpi["value"], 3.0)
            self.assertFalse(cpi["publisher_original_pit_certified"])
            self.assertEqual(history["provenance"]["CPIAUCSL"]["rows"], 2)

    def test_missing_source_stays_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = build(tmp, "2026-10-31")
            self.assertEqual(history["provenance"]["GDPC1"]["status"], "SOURCE_FILE_MISSING")
            self.assertEqual(metrics(history)["available"], 0)

if __name__ == "__main__":
    unittest.main()
