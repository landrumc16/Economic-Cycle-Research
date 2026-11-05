"""Stamp a qualified monthly research artifact with its originating build provenance.

This is called only after the monthly release gate and V6.2 site contract pass.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.v62_release_manifest import validate_manifest


def create(directory: Path, commit: str, built_at: str) -> dict:
    gate = json.loads((directory / "weekly_release_acceptance.json").read_text())
    report = json.loads((directory / "weekly_economic_assessment.json").read_text())
    portal = json.loads((directory / "v5_unified_portal.json").read_text())
    status = gate.get("status")
    if status not in {"PASS", "STALE_RESEARCH_ONLY"}:
        raise ValueError("Monthly gate is not accepted")
    if not commit or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit.lower()):
        raise ValueError("Expected full 40-character source commit")
    datetime.fromisoformat(built_at.replace("Z", "+00:00"))
    assessment_date = gate.get("assessment_date") or report.get("assessment_date")
    if not isinstance(assessment_date, str) or not assessment_date:
        raise ValueError("Missing official assessment date")
    manifest = {
        "version": "6.2",
        "build_commit": commit,
        "build_time_utc": built_at,
        "assessment_date": assessment_date,
        "observation_cutoff": str(portal.get("observation_month") or "unavailable"),
        "source_status": {"monthly_gate": status, "stale": report.get("stale")},
        "research_gate": {"qualified": status == "PASS" and report.get("stale") is False,
                          "status": status},
        "promotion_outcome": "NEW_QUALIFIED" if status == "PASS" else "FAILED",
    }
    validate_manifest(manifest)
    if not manifest["research_gate"]["qualified"]:
        raise ValueError("Stale monthly artifact cannot be promoted as new")
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--built-at", required=True)
    args = p.parse_args()
    manifest = create(args.directory, args.commit, args.built_at)
    (args.directory / "v62_release_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
