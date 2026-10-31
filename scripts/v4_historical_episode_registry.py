"""V4 episode-level historical evidence registry; never treats screened months as verified controls."""
from datetime import date

def registry(cohort):
    if cohort.get("status") != "HISTORICAL_COHORT_AUDIT_ONLY" or cohort.get("publication") != "BLOCKED":
        raise ValueError("Expected conservative historical cohort audit")
    events = cohort.get("event_windows", [])
    if len(events) != 8:
        raise ValueError("Canonical eight crash parent clusters required")
    episodes = []
    names = set()
    for item in events:
        name = item["parent_cluster"]
        if name in names:
            raise ValueError("Duplicate parent cluster")
        names.add(name)
        prior, peak = item["prior_month"], item["peak_date"]
        if date.fromisoformat(prior[:7] + "-01") > date.fromisoformat(peak[:7] + "-01"):
            raise ValueError("Episode chronology invalid")
        episodes.append({
            "parent_cluster": name, "prior_month": prior, "peak_date": peak,
            "event_type": "CANONICAL_CRASH_PARENT_RESEARCH_CLUSTER",
            "independent_episode_verified": False, "outcome_horizon_verified": False,
            "point_in_time_vintage_verified": False, "available_at_dates_verified": False,
            "label_for_prediction": "NOT_APPROVED",
        })
    return {
        "schema_version": 1, "report_type": "V4_HISTORICAL_EPISODE_REGISTRY",
        "status": "RESEARCH_ONLY", "canonical_episode_clusters": len(episodes),
        "episodes": episodes,
        "screened_months": cohort.get("candidate_months_outside_conservative_event_windows"),
        "verified_noncrash_controls": 0,
        "verified_negative_control_labels_available": False,
        "independent_episodes_verified": False, "point_in_time_replay_certified": False,
        "chronological_holdouts_defined": False, "predictive_publication": "BLOCKED",
        "limitations": [
            "Eight historical parent clusters are research anchors, not certified independent labeled events",
            "Candidate non-event months from retrospective exclusions are not verified negative outcomes",
            "Original publisher vintages and actual publication availability dates are not established",
            "No training, predictive classification or calibrated crash probability is authorized",
        ],
    }

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--cohort", default="audit-output/v3_historical_cohort_audit.json")
    p.add_argument("--output", default="audit-output/v4_historical_episode_registry.json")
    a = p.parse_args()
    result = registry(json.loads(Path(a.cohort).read_text()))
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"clusters": result["canonical_episode_clusters"], "predictive_publication": result["predictive_publication"]}))
