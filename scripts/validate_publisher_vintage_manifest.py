"""Fail-closed validation of publisher-original vintage evidence readiness."""
import argparse
import json
from pathlib import Path

EXPECTED = {"UNRATE": "BLS", "CPIAUCSL": "BLS", "GDPC1": "BEA"}
REQUIRED = {"original_release_url_or_archive", "publisher_release_timestamp_timezone",
            "original_reported_value", "publisher_original_file_hash",
            "decision_timestamp", "independent_crosscheck"}

def assess(manifest):
    issues = []
    series = manifest.get("series")
    if not isinstance(series, list):
        series = []
        issues.append("MISSING_SERIES_LIST")
    ids = [s.get("id") for s in series if isinstance(s, dict)]
    if len(ids) != len(set(ids)) or set(ids) != set(EXPECTED):
        issues.append("SERIES_UNIVERSE_OR_DUPLICATES")
    results = {}
    for item in series:
        if not isinstance(item, dict) or item.get("id") not in EXPECTED:
            continue
        name = item["id"]
        faults = []
        if item.get("publisher") != EXPECTED[name]:
            faults.append("WRONG_PUBLISHER")
        if not REQUIRED.issubset(set(item.get("required", []))):
            faults.append("INCOMPLETE_EVIDENCE_CONTRACT")
        if item.get("pit_certified") is not False or item.get("human_approved") is not False:
            faults.append("UNSUPPORTED_APPROVAL_OR_CERTIFICATION")
        results[name] = {"quality": "CONTRACT_VALID_EVIDENCE_PENDING" if not faults else "CONTRACT_INVALID",
                         "issues": faults, "pit_certified": False, "publication": "BLOCKED"}
        issues.extend(name + ":" + issue for issue in faults)
    return {"manifest_integrity": "PASS_CONTRACT_ONLY" if not issues else "FAIL_CONTRACT",
            "issues": issues, "series": results, "publication": "BLOCKED",
            "point_in_time_certified": False, "forecast_authorized": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = assess(json.loads(Path(args.input).read_text()))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    if result["manifest_integrity"] != "PASS_CONTRACT_ONLY":
        raise SystemExit("Publisher vintage manifest contract failed; see " + str(out))

if __name__ == "__main__":
    main()
