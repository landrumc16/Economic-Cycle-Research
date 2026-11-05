"""Regression checks for V6.2 qualified monthly provenance stamping."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.v62_stamp_release import create

COMMIT = "a" * 40
BUILT_AT = "2026-11-04T20:00:00Z"


class StampReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("weekly_release_acceptance.json", {
            "status": "PASS", "assessment_date": "2026-11-04"})
        self.write("weekly_economic_assessment.json", {"stale": False})
        self.write("v5_unified_portal.json", {"observation_month": "2026-10"})

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def test_qualified_stamp(self):
        result = create(self.root, COMMIT, BUILT_AT)
        self.assertEqual(result["build_commit"], COMMIT)
        self.assertEqual(result["assessment_date"], "2026-11-04")
        self.assertEqual(result["promotion_outcome"], "NEW_QUALIFIED")
        self.assertTrue(result["research_gate"]["qualified"])

    def test_stale_gate_rejected(self):
        self.write("weekly_release_acceptance.json", {
            "status": "STALE_RESEARCH_ONLY", "assessment_date": "2026-11-04"})
        self.write("weekly_economic_assessment.json", {"stale": True})
        with self.assertRaisesRegex(ValueError, "Stale monthly"):
            create(self.root, COMMIT, BUILT_AT)

    def test_conflicting_stale_assessment_rejected(self):
        self.write("weekly_economic_assessment.json", {"stale": True})
        with self.assertRaisesRegex(ValueError, "Stale monthly"):
            create(self.root, COMMIT, BUILT_AT)

    def test_missing_assessment_date_rejected(self):
        self.write("weekly_release_acceptance.json", {"status": "PASS"})
        with self.assertRaisesRegex(ValueError, "assessment date"):
            create(self.root, COMMIT, BUILT_AT)

    def test_bad_commit_rejected(self):
        with self.assertRaisesRegex(ValueError, "40-character"):
            create(self.root, "bad", BUILT_AT)


if __name__ == "__main__":
    unittest.main()
