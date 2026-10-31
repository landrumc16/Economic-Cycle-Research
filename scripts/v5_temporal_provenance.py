"""V5 temporal integrity and provenance audit for weekly evidence."""
from datetime import date
from math import isfinite

def audit(snapshot):
    if snapshot.get("report_type") != "V3_WEEKLY_ECONOMIC_EVIDENCE":
        raise ValueError("Expected V3 weekly snapshot contract")
    as_of = date.fromisoformat(snapshot["as_of"])
    rows = []
    for name, item in sorted(snapshot.get("series", {}).items()):
        observed = item.get("latest_observation")
        if observed and date.fromisoformat(observed) > as_of:
            raise ValueError("Future-dated economic observation: " + name)
        value = item.get("observation_value")
        numeric = isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)
        release = item.get("release_date")
        vintage = item.get("vintage_date")
        if release and date.fromisoformat(release) > as_of:
            raise ValueError("Release date after report date: " + name)
        if vintage and date.fromisoformat(vintage) > as_of:
            raise ValueError("Future vintage: " + name)
        change = snapshot.get("week_over_week", {}).get(name, {})
        prior = change.get("previous_snapshot_available") is True
        new_observation = change.get("new_observation_date") is True
        changed = change.get("numeric_change")
        comparable = prior and new_observation and numeric and isinstance(changed, (int, float)) and not isinstance(changed, bool) and isfinite(changed) and not change.get("same_observation_revision_detected")
        rows.append({
            "series": name, "observation_date": observed,
            "numeric_available": numeric, "prior_snapshot_linked": prior,
            "new_dated_observation": new_observation,
            "valid_dated_comparison": bool(comparable),
            "publisher_release_verified": bool(release),
            "publisher_original_vintage_verified": bool(vintage and item.get("publisher_original_pit_certified") is True),
            "age_days": item.get("age_days"),
            "reporting_warning": (
                "MISSING_NUMERIC" if not numeric else
                "NO_PRIOR_SNAPSHOT" if not prior else
                "REVISION_NOT_NEW_OBSERVATION" if change.get("same_observation_revision_detected") else
                "CARRIED_FORWARD" if not new_observation else
                "NO_VALID_NUMERIC_COMPARISON" if not comparable else
                "NEW_DATED_COMPARISON"
            ),
        })
    return {
        "schema_version": 1, "report_type": "V5_TEMPORAL_PROVENANCE_AUDIT",
        "as_of": snapshot["as_of"], "status": "DESCRIPTIVE_ONLY",
        "series": rows, "tracked": len(rows),
        "numeric_available": sum(x["numeric_available"] for x in rows),
        "valid_dated_comparisons": sum(x["valid_dated_comparison"] for x in rows),
        "publisher_release_verified": sum(x["publisher_release_verified"] for x in rows),
        "publisher_original_vintage_verified": sum(x["publisher_original_vintage_verified"] for x in rows),
        "two_distinct_dated_weekly_runs_verified": False,
        "predictive_publication": "BLOCKED",
        "limitations": [
            "A prior artifact reference alone does not prove two distinct dated weekly runs",
            "Monthly or quarterly changes between releases are not weekly economic changes",
            "No observation date substitutes for actual publisher release and vintage timestamps",
        ],
    }

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", default="audit-output/v3_weekly_snapshot.json")
    p.add_argument("--output", default="audit-output/v5_temporal_provenance.json")
    a = p.parse_args()
    result = audit(json.loads(Path(a.snapshot).read_text()))
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"tracked": result["tracked"], "valid_comparisons": result["valid_dated_comparisons"]}))
