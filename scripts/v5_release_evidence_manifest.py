"""Summarize V5 descriptive artifacts without implying source or predictive certification."""
import argparse
import json
from pathlib import Path

REQUIRED = (
    "v5_weekly_research_readout.json",
    "v5_standardized_macro_metrics.json",
    "v5_mechanism_evidence_gate.json",
    "v5_objective_outcomes.json",
    "v5_pit_replay.json",
    "v5_release_acceptance.json",
    "dashboard/weekly-v5.html",
)

def summarize(directory):
    root = Path(directory)
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    if missing:
        return {"report_type": "V5_RELEASE_EVIDENCE_MANIFEST", "status": "INCOMPLETE",
                "missing": missing, "predictive_publication": "BLOCKED"}
    documents = {name: json.loads((root / name).read_text())
                 for name in REQUIRED if name.endswith(".json")}
    weekly = documents["v5_weekly_research_readout.json"]
    macro = documents["v5_standardized_macro_metrics.json"]
    acceptance = documents["v5_release_acceptance.json"]
    date_matches = bool(weekly.get("as_of")) and all(
        doc.get("as_of") in (None, weekly.get("as_of")) for doc in documents.values())
    blocked = all(doc.get("predictive_publication", doc.get("prediction_status")) == "BLOCKED"
                  for doc in documents.values())
    dashboard = (root / "dashboard/weekly-v5.html").read_text()
    dashboard_valid = ("<html" in dashboard and "Predictive publication: BLOCKED" in dashboard
                       and str(weekly.get("as_of", "")) in dashboard)
    passed = (acceptance.get("status") == "PASS_DESCRIPTIVE_ONLY"
              and date_matches and blocked and dashboard_valid)
    return {"schema_version": 1, "report_type": "V5_RELEASE_EVIDENCE_MANIFEST",
            "status": "DESCRIPTIVE_ARTIFACTS_VERIFIED" if passed else "INCOMPLETE",
            "as_of": weekly.get("as_of"), "missing": [], "artifact_paths": list(REQUIRED),
            "macro_available": weekly.get("macro_metric_count", 0),
            "macro_total": weekly.get("macro_metric_total", 0),
            "historical_events": weekly.get("historical_event_count", 0),
            "original_vintage_replay_coverage": weekly.get("original_vintage_replay_coverage", 0),
            "source_freshness_certified": False, "independent_predictive_validation_certified": False,
            "predictive_publication": "BLOCKED",
            "limitations": ["Artifact consistency does not certify source freshness",
                            "Independent historical validation and calibrated predictions remain blocked"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", default="audit-output")
    p.add_argument("--output", default="audit-output/v5_release_evidence_manifest.json")
    a = p.parse_args()
    result = summarize(a.directory)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "missing": result["missing"]}))
    if result["status"] != "DESCRIPTIVE_ARTIFACTS_VERIFIED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
