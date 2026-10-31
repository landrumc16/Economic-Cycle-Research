"""Fail-closed descriptive release checks for the Version 3 weekly dashboard."""
import argparse
import json
from pathlib import Path

def validate(report, page):
    issues = []
    if report.get("report_type") != "V3_WEEKLY_DESCRIPTIVE_ASSESSMENT":
        issues.append("Invalid weekly report contract")
    if report.get("predictive_publication") != "BLOCKED" or report.get("crash_probability") is not None:
        issues.append("Predictive output unexpectedly enabled")
    if report.get("validated_cycle_stage") is not None:
        issues.append("Unvalidated cycle stage published")
    for section in ("change_summary", "macro_narrative", "indicators", "pathway_evidence"):
        if section not in report:
            issues.append("Missing report section: " + section)
    for marker in ("Weekly Economic Intelligence", "What changed", "Economic conditions by domain",
                   "Latest economic indicators", "Distinct crash-pathway evidence", "Predictions blocked"):
        if marker not in page:
            issues.append("Missing dashboard section: " + marker)
    if "<html" not in page or "</html>" not in page:
        issues.append("Dashboard HTML incomplete")
    return {
        "schema_version": 1,
        "status": "PASS_DESCRIPTIVE_RELEASE" if not issues else "FAIL",
        "issues": issues, "predictive_release": "BLOCKED",
        "report_as_of": report.get("as_of"),
        "data_readiness": "NOT_CERTIFIED_BY_THIS_CHECK",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--assessment", default="audit-output/v3_weekly_assessment.json")
    p.add_argument("--dashboard", default="audit-output/dashboard/weekly.html")
    p.add_argument("--output", default="audit-output/v3_release_acceptance.json")
    a = p.parse_args()
    result = validate(json.loads(Path(a.assessment).read_text()), Path(a.dashboard).read_text())
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    if result["issues"]:
        raise SystemExit("; ".join(result["issues"]))
    print(result["status"])

if __name__ == "__main__":
    main()
