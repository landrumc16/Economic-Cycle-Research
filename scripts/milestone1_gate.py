"""Fail-closed Milestone 1 acceptance manifest.

Requires independently reconciled revised series, publisher-authenticated
release ledgers, and complete no-look-ahead verification for all three series.
No spreadsheet promotion or approval is performed by this program.
"""
import argparse
import json
from pathlib import Path

SERIES = ("UNRATE", "CPIAUCSL", "GDPC1")

def evaluate(evidence):
    checks = {}
    for series in SERIES:
        item = evidence.get("series", {}).get(series, {})
        checks[series] = {
            "publisher_source_acquired": item.get("publisher_source_acquired") is True,
            "independent_source_acquired": item.get("independent_source_acquired") is True,
            "numeric_reconciliation_pass": item.get("numeric_reconciliation_pass") is True,
            "publisher_vintage_authenticated": item.get("publisher_vintage_authenticated") is True,
            "release_timing_verified": item.get("release_timing_verified") is True,
            "point_in_time_no_lookahead_pass": item.get("point_in_time_no_lookahead_pass") is True,
            "coverage_pass": item.get("coverage_pass") is True,
        }
    all_pass = all(all(fields.values()) for fields in checks.values())
    return {"series": checks, "all_evidence_pass": all_pass,
            "promotion": "ELIGIBLE FOR HUMAN REVIEW" if all_pass else "BLOCKED",
            "automatic_promotion": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output", default="audit-output/milestone1_gate.json")
    args = parser.parse_args()
    evidence = json.loads(Path(args.evidence).read_text())
    report = evaluate(evidence)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["all_evidence_pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
