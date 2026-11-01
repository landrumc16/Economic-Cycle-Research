"""Fail-closed reconciliation status for the separate workbook and GitHub pipelines."""
import argparse
import json
from pathlib import Path

REQUIRED_MACRO = ("UNRATE", "CPIAUCSL", "GDPC1")


def build(release, forecast, workbook=None):
    if forecast.get("status") != "FORECAST_RELEASE_BLOCKED":
        raise ValueError("Expected V5 forecast release evidence")
    if forecast.get("numeric_forecasts_approved") is not False:
        raise ValueError("Unapproved forecast status")
    workbook = workbook or {}
    if workbook and not workbook.get("source_url", "").startswith("https://docs.google.com/spreadsheets/d/"):
        raise ValueError("Workbook evidence provenance missing")
    approvals = workbook.get("macro_promotion", {})
    macro = {series: approvals.get(series, "NOT_RECONCILED") for series in REQUIRED_MACRO}
    if any(value not in ("APPROVED", "BLOCKED", "NOT_RECONCILED") for value in macro.values()):
        raise ValueError("Unknown workbook promotion status")
    return {
        "status": "UNIFIED_RESEARCH_STATUS",
        "workbook_reconciliation": ("RECONCILED" if workbook.get("evidence_reviewed") is True
                                    and all(v != "NOT_RECONCILED" for v in macro.values())
                                    else "NOT_RECONCILED"),
        "macro_promotion": macro,
        "canonical_macro_approved": (workbook.get("evidence_reviewed") is True
                                     and all(v == "APPROVED" for v in macro.values())),
        "github_monthly_release_status": release.get("status", "UNKNOWN"),
        "numeric_forecasts_approved": False,
        "daily_refresh_status": workbook.get("daily_refresh_status", "NOT_RECONCILED"),
        "weekly_outlook_status": "DESCRIPTIVE_ONLY",
        "monthly_cycle_status": "RESEARCH_ONLY",
        "note": "GitHub CI success and revised historical research do not override workbook vintage gates.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("monthly_release")
    parser.add_argument("forecast_gate")
    parser.add_argument("--workbook-evidence", default=None)
    parser.add_argument("--output", default="audit-output/unified_research_status.json")
    args = parser.parse_args()
    release = json.loads(Path(args.monthly_release).read_text())
    forecast = json.loads(Path(args.forecast_gate).read_text())
    workbook = json.loads(Path(args.workbook_evidence).read_text()) if args.workbook_evidence else None
    result = build(release, forecast, workbook)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
