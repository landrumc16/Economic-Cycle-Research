"""V4 descriptive release acceptance: enforce coherent artifacts and honest validation status."""
import argparse
import json
from pathlib import Path

def check(v3, readiness, signals, mechanisms, episodes, social, validation, dashboard):
    expected = {
        "readiness": (readiness, "V4_WEEKLY_DATA_READINESS"),
        "signals": (signals, "V4_EXPLAINABLE_ECONOMIC_SIGNALS"),
        "mechanisms": (mechanisms, "V4_MULTI_MECHANISM_ASSESSMENT"),
        "episodes": (episodes, "V4_HISTORICAL_EPISODE_REGISTRY"),
        "social": (social, "V4_GLOBAL_SOCIAL_EVIDENCE_REGISTER"),
        "validation": (validation, "V4_PREDICTIVE_VALIDATION_GATE"),
    }
    failures = []
    for name, (data, contract) in expected.items():
        if data.get("report_type") != contract:
            failures.append(name + ": invalid report contract")
        if data.get("predictive_publication") != "BLOCKED":
            failures.append(name + ": predictive gate unexpectedly open")
    if v3.get("report_type") != "V3_WEEKLY_DESCRIPTIVE_ASSESSMENT":
        failures.append("V3 assessment contract invalid")
    if any(data.get("as_of") != v3.get("as_of") for data in (readiness, signals, mechanisms)):
        failures.append("V4 weekly dates disagree")
    if len(signals.get("signals", [])) != 9:
        failures.append("Expected nine canonical V4 signals")
    if len(mechanisms.get("pathways", [])) != 7:
        failures.append("Expected seven mechanism pathways")
    if episodes.get("canonical_episode_clusters") != 8:
        failures.append("Expected eight historical clusters")
    if social.get("defined") != len(social.get("channels", [])):
        failures.append("Global/social channel count mismatch")
    if validation.get("status") != "BLOCKED":
        failures.append("Predictive validation must remain blocked pending independent verification")
    if not validation.get("descriptive_product_release_permitted"):
        failures.append("Descriptive release permission missing")
    for phrase in ("Version 4", "Separate downturn mechanisms", "Historical validation", "data readiness"):
        if phrase not in dashboard:
            failures.append("Dashboard missing " + phrase)
    if "<script" in dashboard.lower():
        failures.append("Offline dashboard unexpectedly contains script")
    return {
        "schema_version": 1, "report_type": "V4_DESCRIPTIVE_RELEASE_ACCEPTANCE",
        "as_of": v3.get("as_of"), "passed": not failures,
        "status": "ACCEPTED_DESCRIPTIVE_ONLY" if not failures else "FAILED",
        "failures": failures, "predictive_publication": "BLOCKED",
        "historical_predictive_validation": "NOT_ESTABLISHED",
        "release_scope": "Weekly descriptive economic intelligence; no validated cycle-stage or crash forecast",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", default="audit-output")
    p.add_argument("--output", default="audit-output/v4_release_acceptance.json")
    a = p.parse_args()
    root = Path(a.directory)
    load = lambda name: json.loads((root / name).read_text())
    report = check(load("v3_weekly_assessment.json"), load("v4_data_readiness.json"),
                   load("v4_economic_signals.json"), load("v4_mechanism_assessment.json"),
                   load("v4_historical_episode_registry.json"), load("v4_global_social_register.json"),
                   load("v4_predictive_validation_gate.json"),
                   (root / "dashboard/weekly-v4.html").read_text())
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "failures": report["failures"]}))
    if not report["passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
