"""Fail-closed Version 2 milestone-1 acceptance, independent of V1 release gate."""
import argparse
import json
from pathlib import Path

def evaluate(comparison, page, state):
    issues = []
    if comparison.get("schema_version") != "2.0.0" or comparison.get("status") != "DESCRIPTIVE_ONLY":
        issues.append("INVALID_V2_SCHEMA_OR_STATUS")
    if comparison.get("publication") != "BLOCKED" or comparison.get("crash_probability") is not None:
        issues.append("PREDICTIVE_GATE_VIOLATION")
    provenance = comparison.get("provenance", {})
    if provenance.get("point_in_time_certified") is not False or provenance.get("human_approved_for_prediction") is not False:
        issues.append("SOURCE_APPROVAL_GATE_VIOLATION")
    if len(provenance.get("sha256_export", "")) != 64:
        issues.append("MISSING_EXPORT_CHECKSUM")
    if provenance.get("extraction_timestamp_status") != "NOT_RECORDED_IN_SOURCE_EXPORT":
        issues.append("UNSUPPORTED_EXTRACTION_TIMESTAMP")
    tabs = provenance.get("tabs", [])
    if {x.get("name") for x in tabs} != {"CRASH PATHWAY TYPOLOGY", "WARNING NONCRASH BASELINES"}:
        issues.append("CANONICAL_TABS_MISSING")
    stats = comparison.get("descriptive_comparison", {})
    if stats.get("crash_parent_clusters") != 8 or stats.get("monthly_observations") != 444:
        issues.append("HISTORICAL_COVERAGE_INCOMPLETE")
    if len(comparison.get("crash_parent_clusters", [])) != 8 or len(comparison.get("monthly_stress_baseline", [])) != 444:
        issues.append("ROW_COUNTS_INCONSISTENT")
    if "Version 2 historical conditions" not in page:
        issues.append("DASHBOARD_V2_SECTION_MISSING")
    if "not verified non-crash controls" not in page:
        issues.append("CONTROL_CAVEAT_MISSING")
    if "V2HISTORICAL" in page:
        issues.append("UNREPLACED_V2_TEMPLATE")
    attached = state.get("v2_historical_comparison")
    if not isinstance(attached, dict) or attached.get("provenance", {}).get("sha256_export") != provenance.get("sha256_export"):
        issues.append("DASHBOARD_STATE_SOURCE_MISMATCH")
    if state.get("publication") != "BLOCKED" or state.get("crash_probability") is not None:
        issues.append("DASHBOARD_PREDICTIVE_GATE_VIOLATION")
    return {"status": "M1_ACCEPTANCE_CANDIDATE" if not issues else "M1_INCOMPLETE",
            "checks_passed": not issues, "predictive_model": "NOT_VALIDATED",
            "publication": "BLOCKED", "issues": issues}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--comparison", default="audit-output/v2_canonical_comparison.json")
    p.add_argument("--html", default="audit-output/dashboard/index.html")
    p.add_argument("--state", default="audit-output/dashboard/state.json")
    p.add_argument("--output", default="audit-output/v2_m1_acceptance.json")
    args = p.parse_args()
    inputs = [Path(args.comparison), Path(args.html), Path(args.state)]
    if all(x.exists() for x in inputs):
        result = evaluate(json.loads(inputs[0].read_text()), inputs[1].read_text(), json.loads(inputs[2].read_text()))
    else:
        result = {"status": "M1_INCOMPLETE", "checks_passed": False, "predictive_model": "NOT_VALIDATED",
                  "publication": "BLOCKED", "issues": ["MISSING:" + str(x) for x in inputs if not x.exists()]}
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["checks_passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
