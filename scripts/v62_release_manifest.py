"""Version 6.2 immutable-as-published release manifest contract.

The publication workflow must generate this from the actual accepted site bundle.
Do not stamp a preserved site with the attempted build's commit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

OUTCOMES = frozenset({"NEW_QUALIFIED", "PRESERVED_PREVIOUS", "FAILED"})
REQUIRED = frozenset({
    "version", "build_commit", "build_time_utc", "assessment_date",
    "observation_cutoff", "source_status", "research_gate", "promotion_outcome"
})


def validate_manifest(manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object")
    missing = REQUIRED - manifest.keys()
    if missing:
        raise ValueError("Missing manifest fields: " + ", ".join(sorted(missing)))
    for key in REQUIRED - {"source_status", "research_gate"}:
        if not isinstance(manifest[key], str) or not manifest[key].strip():
            raise ValueError(f"{key} must be a nonempty string")
    if manifest["promotion_outcome"] not in OUTCOMES:
        raise ValueError("Invalid promotion outcome")
    if not isinstance(manifest["source_status"], dict):
        raise ValueError("source_status must be an object")
    if not isinstance(manifest["research_gate"], dict):
        raise ValueError("research_gate must be an object")
    if not isinstance(manifest["research_gate"].get("qualified"), bool):
        raise ValueError("research_gate.qualified must be boolean")
    return manifest


def decide_publication(candidate: dict, previous: dict | None) -> dict:
    """Return the actual publishable manifest; fail closed on unqualified input."""
    validate_manifest({**candidate, "promotion_outcome": "FAILED"})
    qualified = candidate["research_gate"]["qualified"] is True
    if qualified:
        result = dict(validate_manifest({**candidate, "promotion_outcome": "NEW_QUALIFIED"}))
        return result
    if previous is not None:
        preserved = dict(validate_manifest(previous))
        if preserved["research_gate"]["qualified"] is not True or preserved["promotion_outcome"] == "FAILED":
            raise ValueError("Previous release was not accepted; refusing preservation")
        # Keep the original accepted bundle's commit and assessment date.
        preserved["promotion_outcome"] = "PRESERVED_PREVIOUS"
        return preserved
    raise ValueError("No qualified candidate or previously accepted release")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text())
    previous = json.loads(args.previous.read_text()) if args.previous and args.previous.exists() else None
    result = decide_publication(candidate, previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
