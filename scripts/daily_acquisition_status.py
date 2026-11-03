"""Daily acquisition status is an evidence gate, never a source-promotion gate."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SOURCES = ("FRED", "BLS", "BEA")
REPORTS = {
    "FRED": "fred-api/fred_api_report.json",
    "BLS": "bls-api/bls_api_report.json",
    "BEA": "bea-api/bea_report.json",
}


def summarize(root: Path, outcomes: dict[str, str]) -> dict:
    present = {source: (root / REPORTS[source]).is_file() for source in SOURCES}
    successful = all(outcomes.get(source) == "success" and present[source] for source in SOURCES)
    return {
        "status": "DAILY_SOURCE_ACQUISITION_EVIDENCE",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "step_outcomes": {source: outcomes.get(source, "unknown") for source in SOURCES},
        "reports_present": present,
        "acquisition_complete": successful,
        "source_promotion": "BLOCKED",
        "workbook_reconciled": False,
        "current_assessment_approved": False,
        "numeric_forecasts_approved": False,
        "note": "Acquisition is not verification. Weekly and monthly research retain independent fail-closed release gates.",
    }


def main() -> None:
    root = Path("audit-output")
    root.mkdir(exist_ok=True)
    outcomes = {source: os.environ.get(source + "_OUTCOME", "unknown") for source in SOURCES}
    evidence = summarize(root, outcomes)
    (root / "daily_acquisition_status.json").write_text(json.dumps(evidence, indent=2) + "\n")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as summary:
            summary.write("## Daily economic source acquisition (research only)\n")
            for source in SOURCES:
                summary.write(f"- {source}: {outcomes[source]}; report present: {evidence['reports_present'][source]}\n")
            summary.write("- Source promotion: BLOCKED; canonical Google Sheets reconciliation: NOT VERIFIED\n")
    if not evidence["acquisition_complete"]:
        raise SystemExit("Official-source acquisition incomplete; evidence preserved but daily run cannot pass")


if __name__ == "__main__":
    main()
