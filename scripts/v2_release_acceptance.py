"""Final descriptive V2 release gate; preserves separate V1 data-acquisition status."""
import argparse
import json
from pathlib import Path

def evaluate(v2, v1, state, page):
    issues = []
    if not v2.get("checks_passed") or v2.get("status") != "M1_ACCEPTANCE_CANDIDATE":
        issues.append("V2_INTEGRATION_NOT_ACCEPTED")
    if v2.get("publication") != "BLOCKED" or v2.get("predictive_model") != "NOT_VALIDATED":
        issues.append("V2_PREDICTIVE_GATE_VIOLATION")
    if state.get("publication") != "BLOCKED" or state.get("crash_probability") is not None or state.get("validated_cycle_stage") is not None:
        issues.append("DASHBOARD_PREDICTIVE_GATE_VIOLATION")
    for section in ("Version 2 historical conditions", "Current conditions vs historical crash contexts",
                    "Crash mechanism evidence gaps", "International economic transmission"):
        if section not in page:
            issues.append("MISSING_SECTION:" + section)
    if "CURRENT_UNEMPLOYMENT_LEVEL_NOT_3M_CHANGE" not in page:
        issues.append("MISSING_COMPARABILITY_WARNING")
    for key in ("v2_historical_comparison", "v2_global_transmission", "current_cycle_assessment"):
        if not isinstance(state.get(key), dict):
            issues.append("MISSING_STATE:" + key)
    v1_issues = v1.get("issues", [])
    if not isinstance(v1_issues, list):
        issues.append("V1_REPORT_INVALID")
        v1_issues = []
    if v1.get("publication") != "BLOCKED" or v1.get("predictive_model_status") != "NOT_VALIDATED":
        issues.append("V1_PREDICTIVE_GATE_VIOLATION")
    # Do not reclassify missing macro observations as available.
    missing_data = [x for x in v1_issues if x in
                    ("HISTORICAL_COMPARISON_NOT_POPULATED", "CURRENT_MACRO_VALUES_MISSING")]
    other_v1_issues = [x for x in v1_issues if x not in missing_data]
    if other_v1_issues:
        issues.append("UNEXPECTED_V1_FAILURES:" + ",".join(other_v1_issues))
    if not v1.get("checks_passed") and not missing_data and not other_v1_issues:
        issues.append("V1_ACCEPTANCE_INCONSISTENT")
    return {
        "status": "V2_DESCRIPTIVE_RELEASE_ACCEPTED" if not issues else "V2_RELEASE_BLOCKED",
        "checks_passed": not issues,
        "scope": "DESCRIPTIVE_HISTORICAL_AND_CURRENT_CONTEXT_ONLY",
        "predictive_model": "NOT_VALIDATED", "publication": "BLOCKED",
        "current_macro_complete": "CURRENT_MACRO_VALUES_MISSING" not in missing_data,
        "historical_macro_analogues_complete": "HISTORICAL_COMPARISON_NOT_POPULATED" not in missing_data,
        "inherited_v1_acceptance": v1.get("status"),
        "disclosed_source_gaps": missing_data, "issues": issues,
        "interpretation": "Descriptive V2 integration acceptance does not certify current macro acquisition, original vintages, verified noncrash controls, or prediction."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--v2", default="audit-output/v2_m1_acceptance.json")
    p.add_argument("--v1", default="audit-output/dashboard/v1_acceptance.json")
    p.add_argument("--state", default="audit-output/dashboard/state.json")
    p.add_argument("--html", default="audit-output/dashboard/index.html")
    p.add_argument("--output", default="audit-output/v2_release_acceptance.json")
    a = p.parse_args()
    paths = [Path(a.v2), Path(a.v1), Path(a.state), Path(a.html)]
    if all(p.exists() for p in paths):
        result = evaluate(*(json.loads(p.read_text()) for p in paths[:3]), paths[3].read_text())
    else:
        result = {"status": "V2_RELEASE_BLOCKED", "checks_passed": False,
                  "publication": "BLOCKED", "predictive_model": "NOT_VALIDATED",
                  "issues": ["MISSING:" + str(p) for p in paths if not p.exists()]}
    output = Path(a.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["checks_passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
