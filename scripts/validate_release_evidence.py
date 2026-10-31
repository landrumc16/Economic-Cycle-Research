"""Validate publisher-original release records without treating metadata as certification."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

SERIES = {"UNRATE": "BLS", "CPIAUCSL": "BLS", "GDPC1": "BEA"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FIELDS = ("series_id", "publisher", "observation_period", "release_timestamp",
          "decision_timestamp", "reported_value", "original_url", "sha256",
          "independent_crosscheck")

def check_record(row):
    problems = []
    for key in FIELDS:
        if not isinstance(row.get(key), str) or not row[key].strip():
            problems.append("MISSING_" + key.upper())
    if problems:
        return problems
    if row["series_id"] not in SERIES or row["publisher"] != SERIES.get(row["series_id"]):
        problems.append("PUBLISHER_OR_SERIES_MISMATCH")
    try:
        release = dt.datetime.fromisoformat(row["release_timestamp"])
        decision = dt.datetime.fromisoformat(row["decision_timestamp"])
        if release.utcoffset() is None or decision.utcoffset() is None:
            problems.append("TIMESTAMP_MISSING_TIMEZONE")
        elif release > decision:
            problems.append("LOOKAHEAD_RELEASE_AFTER_DECISION")
    except ValueError:
        problems.append("INVALID_TIMESTAMP")
    if not SHA256.fullmatch(row["sha256"]):
        problems.append("INVALID_SHA256")
    if not row["original_url"].startswith("https://"):
        problems.append("INVALID_ORIGINAL_URL")
    return problems

def assess(document):
    records = document.get("records", [])
    if not isinstance(records, list):
        return {"quality": "INVALID_RECORD_COLLECTION", "publication": "BLOCKED", "records": []}
    results = []
    for index, record in enumerate(records):
        issues = check_record(record) if isinstance(record, dict) else ["NOT_AN_OBJECT"]
        results.append({"index": index, "quality": "METADATA_PLAUSIBLE_UNVERIFIED" if not issues else "INVALID",
                        "issues": issues})
    return {"quality": "NO_RECORDS" if not records else ("METADATA_ONLY_UNVERIFIED" if all(not r["issues"] for r in results) else "INVALID_RECORDS"),
            "publication": "BLOCKED", "pit_certified": False,
            "source_authenticity_verified": False, "records": results}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    result = assess(json.loads(Path(a.input).read_text()))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    if result["quality"] in ("INVALID_RECORD_COLLECTION", "INVALID_RECORDS"):
        raise SystemExit("Invalid release metadata; see " + str(target))

if __name__ == "__main__":
    main()
