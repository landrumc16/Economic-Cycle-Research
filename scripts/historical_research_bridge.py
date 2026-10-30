"""Read-only historical research provenance adapter; never converts research to forecasts."""
import argparse
import json
from pathlib import Path

CANONICAL = {
    "pathways": {
        "tab": "CRASH PATHWAY TYPOLOGY",
        "definition": "Parent-cluster pre-peak descriptors; non-exclusive and non-causal",
        "denominator": {"parent_clusters": 8},
        "timing": "last completed month before daily peak",
        "validation": "EXPLORATORY_REVISED_NOT_PIT",
    },
    "noncrash_baselines": {
        "tab": "WARNING NONCRASH BASELINES",
        "definition": "Stress: 10Y-2Y < 0 pp OR Baa-10Y >= 2.5 pp; forward Nasdaq daily running-peak drawdown >=20% within 12 months",
        "denominator": {"monthly_observations": 444},
        "overlap": "FORWARD_WINDOWS_OVERLAP_NOT_INDEPENDENT",
        "validation": "EXPLORATORY_REVISED_NOT_PIT",
    },
    "holdout": {
        "tabs": ["WALK FORWARD RULE AUDIT", "ERA HOLDOUT DIAGNOSTIC"],
        "validation": "NOT_UNTOUCHED_OUT_OF_SAMPLE",
    },
}

def attach(report):
    if not isinstance(report, dict) or report.get("publication") != "BLOCKED":
        raise ValueError("Research evidence requires a blocked integrated report")
    result = dict(report)
    result["historical_research"] = CANONICAL
    result["crash_probability"] = None
    result["composite_risk_score"] = None
    result["validated_cycle_stage"] = None
    result["sector_recommendation"] = None
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="audit-output/integrated_research_readout.json")
    p.add_argument("--output", default="audit-output/integrated_research_readout.json")
    a = p.parse_args()
    result = attach(json.loads(Path(a.input).read_text()))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")

if __name__ == "__main__":
    main()
