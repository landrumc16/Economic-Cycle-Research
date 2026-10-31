"""Parse canonical workbook row exports without inventing missing historical evidence."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

HEADERS = {
    "pathways": ["Parent cluster", "Daily peak", "Prior month", "First 20% crossing",
                 "Recession overlap hindsight", "Curve pp", "Credit pp", "CPI annualized",
                 "U3 3m change", "GDP YoY", "DFF 12m pp", "Financial stress?"],
    "noncrash": ["Month", "Nasdaq cutoff", "Curve pp", "Credit pp", "Stress current?",
                 "Stress last 3m?", "Stress last 6m?", "Stress last 12m?", "Stress last 24m?",
                 "Months since last stress (0=current)", "Stress count prior 3m", "Stress count prior 6m"],
}

def validate_coverage(name, records):
    expected_count = 8 if name == "pathways" else 444
    problems = []
    if len(records) != expected_count:
        problems.append("EXPECTED_%s_ROWS_GOT_%s" % (expected_count, len(records)))
    key = "Parent cluster" if name == "pathways" else "Month"
    keys = [str(row[key]).strip() for row in records]
    if not all(keys) or len(set(keys)) != len(keys):
        problems.append("EMPTY_OR_DUPLICATE_KEYS")
    if any(any(str(v).strip() == "" for v in row.values()) for row in records):
        problems.append("MISSING_REQUIRED_VALUES")
    if name == "pathways":
        if set(keys) != set(str(i) for i in range(1, 9)):
            problems.append("INVALID_PARENT_CLUSTER_UNIVERSE")
        for row in records:
            try:
                peak = date.fromisoformat(str(row["Daily peak"]))
                prior = date.fromisoformat(str(row["Prior month"]) + "-01")
                crossing = date.fromisoformat(str(row["First 20% crossing"]))
                if not (prior < peak <= crossing):
                    problems.append("INVALID_EVENT_CHRONOLOGY")
                    break
            except (ValueError, TypeError):
                problems.append("INVALID_EVENT_DATE")
                break
    else:
        parsed = []
        for row in records:
            try:
                month = date.fromisoformat(str(row["Month"]) + "-01")
                cutoff = date.fromisoformat(str(row["Nasdaq cutoff"]))
                if (cutoff.year, cutoff.month) != (month.year, month.month):
                    problems.append("CUTOFF_MONTH_MISMATCH")
                parsed.append(month.year * 12 + month.month)
            except (ValueError, TypeError):
                problems.append("INVALID_MONTH_OR_CUTOFF_DATE")
                break
        if len(parsed) == len(records) and any(b - a != 1 for a, b in zip(parsed, parsed[1:])):
            problems.append("NONCONSECUTIVE_OR_UNSORTED_MONTHS")
    return sorted(set(problems))


def parse_export(export):
    if not isinstance(export, dict):
        raise ValueError("Workbook export must be a JSON object")
    result = {"status": "HISTORICAL_RESEARCH_ONLY_NOT_PIT", "publication": "BLOCKED",
              "provenance": "explicit canonical workbook row export, not live synchronization",
              "domains": {}}
    for name, expected in HEADERS.items():
        block = export.get(name)
        if not isinstance(block, dict) or not isinstance(block.get("rows"), list):
            result["domains"][name] = {"quality": "MISSING_EXPORT", "records": []}
            continue
        rows = block["rows"]
        if not rows or rows[0] != expected:
            result["domains"][name] = {"quality": "SCHEMA_MISMATCH", "records": []}
            continue
        if any(not isinstance(row, list) or len(row) != len(expected) for row in rows[1:]):
            result["domains"][name] = {"quality": "ROW_SHAPE_INVALID", "records": []}
            continue
        records = [dict(zip(expected, row)) for row in rows[1:]]
        issues = validate_coverage(name, records)
        result["domains"][name] = {
            "quality": "STAGED_REVISED_NOT_PIT" if not issues else "COVERAGE_OR_TIME_INTEGRITY_FAILED",
            "issues": issues,
            "source_tab": block.get("source_tab"),
            "source_range": block.get("source_range"),
            "record_count": len(records),
            "records": records,
            "independence": "PARENT_CLUSTERS_NOT_MONTHS" if name == "pathways" else "OVERLAPPING_FORWARD_WINDOWS",
        }
    result["integrity"] = "PASS_RESEARCH_ONLY" if all(
        v.get("quality") == "STAGED_REVISED_NOT_PIT" for v in result["domains"].values()
    ) else "BLOCKED_INCOMPLETE_OR_INVALID"
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="audit-output/historical_workbook_observations.json")
    p.add_argument("--require-complete", action="store_true", help="Fail workflow if canonical historical coverage or integrity is incomplete")
    a = p.parse_args()
    result = parse_export(json.loads(Path(a.input).read_text()))
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    if a.require_complete and result["integrity"] != "PASS_RESEARCH_ONLY":
        print("Historical workbook integrity failed; see " + str(dest), file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
