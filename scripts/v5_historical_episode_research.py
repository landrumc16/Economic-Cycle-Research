"""V5 prospective-label research contract. No retrospective candidate becomes a negative label."""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path


def day(value):
    return date.fromisoformat(value)


def evaluate(registry, candidates=None, horizon_days=180, embargo_days=30, as_of=None):
    if horizon_days < 1 or embargo_days < 0:
        raise ValueError("Invalid horizon or embargo")
    cutoff = day(as_of) if as_of else date.today()
    episodes = registry.get("episodes", [])
    parents = set()
    anchors = []
    for episode in episodes:
        parent = episode["parent_cluster"]
        if parent in parents:
            raise ValueError("Duplicate parent cluster")
        parents.add(parent)
        anchor = day(episode["peak_date"])
        if anchor > cutoff:
            raise ValueError("Future event anchor")
        anchors.append((parent, anchor))
    controls = []
    for candidate in candidates or []:
        start = day(candidate["as_of"])
        if start > cutoff:
            raise ValueError("Future candidate date")
        horizon_end = start + timedelta(days=horizon_days)
        overlap = [parent for parent, anchor in anchors
                   if start - timedelta(days=embargo_days) <= anchor <= horizon_end + timedelta(days=embargo_days)]
        mature = horizon_end <= cutoff
        provenance = candidate.get("outcome_source")
        independently_verified = candidate.get("complete_outcome_coverage") is True and bool(provenance)
        # An event-free registry is not evidence of an event-free historical period.
        eligible = mature and independently_verified and not overlap and candidate.get("no_event_observed") is True
        controls.append({"as_of": start.isoformat(), "horizon_end": horizon_end.isoformat(),
                         "parent_overlap": overlap, "outcome_mature": mature,
                         "outcome_provenance": provenance, "verified_negative": eligible,
                         "status": "VERIFIED_RESEARCH_CONTROL" if eligible else "UNVERIFIED_CANDIDATE"})
    return {"schema_version": 1, "report_type": "V5_HISTORICAL_EPISODE_RESEARCH",
            "as_of": cutoff.isoformat(), "horizon_days": horizon_days,
            "embargo_days": embargo_days, "outcome_definition":
            "Documented event onset within (as_of, as_of + horizon]; event absence requires complete independently sourced outcome coverage",
            "event_parent_clusters": len(parents), "episode_independence_certified": False,
            "positive_labels_certified": 0, "negative_controls_verified": sum(c["verified_negative"] for c in controls),
            "candidate_controls": controls, "point_in_time_replay_certified": False,
            "chronological_holdout_certified": False, "predictive_publication": "BLOCKED",
            "limitations": ["Canonical peaks are not objective verified onset dates",
                            "Historical registry alone cannot prove absence of an event",
                            "No publisher-original PIT vintages or untouched holdout are certified"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episodes", default="audit-output/v4_historical_episode_registry.json")
    p.add_argument("--candidates")
    p.add_argument("--output", default="audit-output/v5_historical_episode_research.json")
    p.add_argument("--as-of")
    a = p.parse_args()
    source = json.loads(Path(a.episodes).read_text())
    candidates = json.loads(Path(a.candidates).read_text()) if a.candidates else []
    if not isinstance(candidates, list):
        raise ValueError("Candidates must be a list")
    report = evaluate(source, candidates, as_of=a.as_of)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
