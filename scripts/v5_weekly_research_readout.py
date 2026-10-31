"""V5 integrated weekly research gate; descriptive continuity is independent of prediction."""
import argparse
import json
from pathlib import Path

def assemble(standardized, mechanisms, outcomes, replay):
    if standardized.get("report_type") != "V5_STANDARDIZED_MACRO_METRICS":
        raise ValueError("Standardized macro evidence missing")
    if mechanisms.get("report_type") != "V5_MECHANISM_EVIDENCE_GATE":
        raise ValueError("Mechanism evidence missing")
    if replay.get("report_type") != "V5_PIT_REPLAY":
        raise ValueError("Replay audit missing")
    rows = standardized.get("metrics", [])
    available = [r for r in rows if r.get("status") == "DESCRIPTIVE_TRANSFORM_AVAILABLE"]
    return {"schema_version": 1, "report_type": "V5_WEEKLY_RESEARCH_READOUT",
            "as_of": standardized["as_of"], "release_status": "DESCRIPTIVE_RESEARCH",
            "standardized_macro": available,
            "macro_metric_count": len(available),
            "mechanism_readiness": mechanisms["mechanisms"],
            "historical_event_count": outcomes.get("event_count", 0),
            "outcome_coverage_status": outcomes.get("coverage_status", "UNVERIFIED"),
            "original_vintage_replay_coverage": replay.get("publisher_original_coverage", 0),
            "predictive_publication": "BLOCKED",
            "validation_requirements": ["independent objective outcome audit",
                                        "publisher-original historical vintages",
                                        "event-parent-separated chronological holdout",
                                        "falsification, calibration and independent review"],
            "limitations": ["Descriptive measures are not forecasts",
                            "Unverified original vintages cannot support historical prediction claims"]}

def main():
    p = argparse.ArgumentParser()
    for key in ("standardized", "mechanisms", "outcomes", "replay"):
        p.add_argument("--" + key, required=True)
    p.add_argument("--output", default="audit-output/v5_weekly_research_readout.json")
    a = p.parse_args()
    documents = [json.loads(Path(getattr(a, k)).read_text()) for k in
                 ("standardized", "mechanisms", "outcomes", "replay")]
    report = assemble(*documents)
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
