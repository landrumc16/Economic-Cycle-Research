"""V5 descriptive release acceptance: require complete, internally consistent artifacts."""
import argparse
import json
from pathlib import Path


def verify(readout, dashboard, mechanisms, replay, outcomes):
    issues = []
    if readout.get("report_type") != "V5_WEEKLY_RESEARCH_READOUT":
        issues.append("INVALID_WEEKLY_READOUT")
    if readout.get("predictive_publication") != "BLOCKED":
        issues.append("PREDICTIVE_GATE_NOT_BLOCKED")
    if readout.get("release_status") != "DESCRIPTIVE_RESEARCH":
        issues.append("UNEXPECTED_RELEASE_STATUS")
    if not readout.get("as_of"):
        issues.append("MISSING_REPORT_DATE")
    if readout.get("macro_metric_count") != len(readout.get("standardized_macro", [])):
        issues.append("MACRO_COUNT_MISMATCH")
    if (readout.get("macro_metric_total", len(readout.get("standardized_macro", []))) !=
            readout.get("macro_metric_count", 0) + len(readout.get("macro_coverage_gaps", []))):
        issues.append("MACRO_COVERAGE_TOTAL_MISMATCH")\n    if mechanisms.get("report_type") != "V5_MECHANISM_EVIDENCE_GATE":
        issues.append("MISSING_MECHANISM_AUDIT")
    elif readout.get("mechanism_readiness") != mechanisms.get("mechanisms"):
        issues.append("MECHANISM_MISMATCH")
    if replay.get("report_type") != "V5_PIT_REPLAY":
        issues.append("MISSING_PIT_AUDIT")
    elif readout.get("original_vintage_replay_coverage") != replay.get("publisher_original_coverage"):
        issues.append("PIT_COVERAGE_MISMATCH")
    if readout.get("outcome_coverage_status") != outcomes.get("coverage_status"):
        issues.append("OUTCOME_COVERAGE_MISMATCH")
    if ("<html" not in dashboard or "Predictive publication: BLOCKED" not in dashboard
            or str(readout.get("as_of", "")) not in dashboard):
        issues.append("DASHBOARD_INCOMPLETE")
    if mechanisms.get("prediction_status") not in (None, "BLOCKED"):
        issues.append("MECHANISM_PREDICTIVE_GATE_NOT_BLOCKED")
    if replay.get("predictive_publication") not in (None, "BLOCKED"):
        issues.append("REPLAY_PREDICTIVE_GATE_NOT_BLOCKED")
    if not readout.get("validation_requirements"):
        issues.append("VALIDATION_DISCLOSURE_MISSING")
    return {"schema_version": 1, "report_type": "V5_RELEASE_ACCEPTANCE",
            "status": "PASS_DESCRIPTIVE_ONLY" if not issues else "FAIL",
            "issues": issues, "predictive_publication": "BLOCKED",
            "independent_validation_certified": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", default="audit-output")
    p.add_argument("--output", default="audit-output/v5_release_acceptance.json")
    a = p.parse_args()
    root = Path(a.directory)
    names = ["v5_weekly_research_readout.json", "v5_mechanism_evidence_gate.json",
             "v5_pit_replay.json", "v5_objective_outcomes.json"]
    missing = [name for name in names if not (root / name).is_file()]
    if not (root / "dashboard/weekly-v5.html").is_file():
        missing.append("dashboard/weekly-v5.html")
    if missing:
        result = {"schema_version": 1, "report_type": "V5_RELEASE_ACCEPTANCE",
                  "status": "FAIL", "issues": ["MISSING_" + x for x in missing],
                  "predictive_publication": "BLOCKED"}
    else:
        docs = [json.loads((root / name).read_text()) for name in names]
        result = verify(docs[0], (root / "dashboard/weekly-v5.html").read_text(), *docs[1:])
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "issues": result["issues"]}))
    if result["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
