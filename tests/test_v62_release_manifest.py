"""Contract tests for Version 6.2 publication integrity."""
import unittest

from scripts.v62_release_manifest import decide_publication, validate_manifest


def sample(commit="abc", qualified=True):
    return {
        "version": "6.2",
        "build_commit": commit,
        "build_time_utc": "2026-11-04T15:00:00Z",
        "assessment_date": "2026-10-20",
        "observation_cutoff": "2026-10-01",
        "source_status": {"fresh": False},
        "research_gate": {"qualified": qualified},
        "promotion_outcome": "NEW_QUALIFIED",
    }


class ReleaseManifestTests(unittest.TestCase):
    def test_qualified_new_release(self):
        result = decide_publication(sample("new"), sample("old"))
        self.assertEqual(result["build_commit"], "new")
        self.assertEqual(result["promotion_outcome"], "NEW_QUALIFIED")

    def test_unqualified_preserves_accepted_commit_and_date(self):
        result = decide_publication(sample("new", False), sample("old"))
        self.assertEqual(result["build_commit"], "old")
        self.assertEqual(result["assessment_date"], "2026-10-20")
        self.assertEqual(result["promotion_outcome"], "PRESERVED_PREVIOUS")

    def test_unqualified_without_previous_fails_closed(self):
        with self.assertRaises(ValueError):
            decide_publication(sample("new", False), None)

    def test_rejects_missing_provenance(self):
        candidate = sample()
        del candidate["build_commit"]
        with self.assertRaises(ValueError):
            validate_manifest(candidate)

    def test_rejects_bad_status(self):
        candidate = sample()
        candidate["promotion_outcome"] = "DEPLOYED"
        with self.assertRaises(ValueError):
            validate_manifest(candidate)


    def test_rejects_unqualified_previous_release(self):
        with self.assertRaises(ValueError):
            decide_publication(sample("new", False), sample("old", False))

    def test_rejects_failed_previous_release(self):
        previous = sample("old")
        previous["promotion_outcome"] = "FAILED"
        with self.assertRaises(ValueError):
            decide_publication(sample("new", False), previous)

    def test_rejects_missing_gate_boolean(self):
        candidate = sample()
        candidate["research_gate"] = {"qualified": "yes"}
        with self.assertRaises(ValueError):
            decide_publication(candidate, sample("old"))

    def test_rejects_missing_candidate_provenance_even_when_preserving(self):
        candidate = sample("new", False)
        del candidate["assessment_date"]
        with self.assertRaises(ValueError):
            decide_publication(candidate, sample("old"))

if __name__ == "__main__":
    unittest.main()
