"""Inventory retrospective historical coverage without certifying predictive performance."""
import argparse
import json
from pathlib import Path


def inventory(snapshot, lead_windows):
    pathways = snapshot.get("pathways", {}).get("rows", [])
    monthly = snapshot.get("noncrash", {}).get("rows", [])
    lead_rows = lead_windows.get("rows", [])
    if not pathways or not monthly or not lead_rows:
        raise ValueError("Historical pathway, monthly and lead-window rows required")
    months = [str(row[0]) for row in monthly[1:] if row and len(str(row[0])) == 7]
    if not months:
        raise ValueError("No dated monthly observations")
    if len(set(months)) != len(months):
        raise ValueError("Duplicate monthly comparison periods")
    clusters = [str(row[0]) for row in pathways[1:] if row]
    if len(set(clusters)) != len(clusters):
        raise ValueError("Duplicate historical parent clusters")
    return {
        "schema_version": 1,
        "report_type": "HISTORICAL_USABILITY_INVENTORY",
        "status": "RETROSPECTIVE_DESCRIPTIVE_PILOT_ELIGIBLE",
        "source_workbook": snapshot.get("source_workbook"),
        "monthly_rows": len(months),
        "first_month": min(months),
        "last_month": max(months),
        "crash_parent_clusters": len(clusters),
        "lead_window_rows": len(lead_rows) - 1,
        "point_in_time_certified": False,
        "predictive_publication": "BLOCKED",
        "coverage_gaps": [
            "No comparable monthly workbook coverage before " + min(months),
            "Historical workbook observations are retrospective, not certified original vintages",
            "No independent verified outcome/non-event panel attached to this inventory",
        ],
        "limitations": [
            "Historical lead flags are descriptive research, not prospective prediction results",
            "NBER recession dates and equity drawdowns require separate outcome definitions",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="data/workbook_historical_research_snapshot_2026-10-30.json")
    parser.add_argument("--lead-windows", default="data/v2_canonical_lead_window_summary_2026-10-31.json")
    parser.add_argument("--output", default="audit-output/historical_usability_inventory.json")
    args = parser.parse_args()
    result = inventory(json.loads(Path(args.snapshot).read_text()),
                       json.loads(Path(args.lead_windows).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
