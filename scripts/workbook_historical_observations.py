"""Parse canonical workbook row exports without inventing missing historical evidence."""
import argparse
import json
from pathlib import Path

HEADERS = {
    "pathways": ["Parent cluster", "Daily peak", "Prior month", "First 20% crossing",
                 "Recession overlap hindsight", "Curve pp", "Credit pp", "CPI annualized",
                 "U3 3m change", "GDP YoY", "DFF 12m pp", "Financial stress?"],
    "noncrash": ["Month", "Nasdaq cutoff", "Curve pp", "Credit pp", "Stress current?",
                 "Stress last 3m?", "Stress last 6m?", "Stress last 12m?", "Stress last 24m?",
                 "Months since last stress (0=current)", "Stress count prior 3m", "Stress count prior 6m"],
}

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
        result["domains"][name] = {
            "quality": "STAGED_REVISED_NOT_PIT",
            "source_tab": block.get("source_tab"),
            "source_range": block.get("source_range"),
            "record_count": len(records),
            "records": records,
            "independence": "PARENT_CLUSTERS_NOT_MONTHS" if name == "pathways" else "OVERLAPPING_FORWARD_WINDOWS",
        }
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="audit-output/historical_workbook_observations.json")
    a = p.parse_args()
    result = parse_export(json.loads(Path(a.input).read_text()))
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")

if __name__ == "__main__":
    main()
