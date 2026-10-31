"""Version 4 weekly data readiness: distinguish retrieval, numeric evidence and comparison availability."""
from datetime import date

def audit(snapshot):
    if snapshot.get("report_type") != "V3_WEEKLY_ECONOMIC_EVIDENCE":
        raise ValueError("V3 evidence snapshot required")
    as_of = date.fromisoformat(snapshot["as_of"])
    series = snapshot.get("series", {})
    changes = snapshot.get("week_over_week", {})
    details = []
    for key, entry in sorted(series.items()):
        observed = entry.get("latest_observation")
        if observed is not None and date.fromisoformat(observed) > as_of:
            raise ValueError("Future observation: " + key)
        numeric = entry.get("observation_value") is not None
        status = entry.get("status")
        change = changes.get(key, {})
        if not numeric:
            comparison = "NO_NUMERIC_EVIDENCE"
        elif not change.get("previous_snapshot_available"):
            comparison = "NO_PRIOR_SNAPSHOT"
        elif change.get("same_observation_revision_detected"):
            comparison = "REVISION"
        elif change.get("new_observation_date"):
            comparison = ("NEW_DATED_OBSERVATION_COMPARABLE" if change.get("numeric_change") is not None
                          else "NEW_DATED_OBSERVATION_NO_NUMERIC_BASELINE")
        else:
            comparison = "CARRIED_FORWARD"
        details.append({
            "series": key, "source_status": status,
            "source_staged": status == "STAGED_REVISED_NOT_PIT",
            "numeric_evidence_available": numeric,
            "observation_date": observed, "age_days": entry.get("age_days"),
            "comparison_status": comparison,
            "release_date_verified": entry.get("release_date") is not None,
            "point_in_time_certified": entry.get("publisher_original_pit_certified") is True,
        })
    return {
        "schema_version": 1, "report_type": "V4_WEEKLY_DATA_READINESS",
        "as_of": snapshot["as_of"], "status": "DESCRIPTIVE_ONLY",
        "series_count": len(details),
        "staged_sources": sum(x["source_staged"] for x in details),
        "numeric_sources": sum(x["numeric_evidence_available"] for x in details),
        "series_with_prior_snapshot": sum(changes.get(x["series"], {}).get("previous_snapshot_available") is True for x in details),
        "verified_release_dates": sum(x["release_date_verified"] for x in details),
        "pit_certified_sources": sum(x["point_in_time_certified"] for x in details),
        "details": details,
        "weekly_comparison_verified": any(x["comparison_status"] in (
            "REVISION", "NEW_DATED_OBSERVATION_COMPARABLE", "NEW_DATED_OBSERVATION_NO_NUMERIC_BASELINE",
            "CARRIED_FORWARD") for x in details),
        "predictive_publication": "BLOCKED",
        "limitations": [
            "Successful API execution does not prove numeric evidence or source freshness",
            "An available prior snapshot is not proof that a new economic observation was published",
            "Observation dates are not publisher release dates; historical vintages remain unverified",
        ],
    }
