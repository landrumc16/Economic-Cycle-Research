"""Audit historical cohorts without inventing verified negative controls or point-in-time data."""
from datetime import date

def month_index(value):
    year, month = map(int, value[:7].split("-"))
    if not 1 <= month <= 12:
        raise ValueError("Invalid month")
    return year * 12 + month - 1

def audit(comparison):
    if comparison.get("status") != "DESCRIPTIVE_ONLY" or comparison.get("publication") != "BLOCKED":
        raise ValueError("Expected blocked V2 descriptive comparison")
    crashes = comparison.get("crash_parent_clusters", [])
    monthly = comparison.get("monthly_stress_baseline", [])
    if len(crashes) != 8:
        raise ValueError("Expected eight canonical parent clusters")
    months = [x["month"] for x in monthly]
    if len(set(months)) != len(months):
        raise ValueError("Duplicate monthly observation")
    event_months = []
    for crash in crashes:
        prior = month_index(crash["prior_month"])
        peak = month_index(crash["peak_date"])
        if peak < prior:
            raise ValueError("Peak predates prior month")
        event_months.append({"parent_cluster": crash["parent_cluster"],
                             "prior_month": crash["prior_month"], "peak_date": crash["peak_date"],
                             "prior_month_index": prior, "peak_month_index": peak,
                             "independent_episode": "NOT_ESTABLISHED",
                             "point_in_time_verified": False})
    # Exclusion flags are conservative research screening, NOT verified negative labels.
    exclusion = set()
    for event in event_months:
        exclusion.update(range(event["prior_month_index"] - 24, event["peak_month_index"] + 13))
    screened = [x for x in monthly if month_index(x["month"]) not in exclusion]
    return {
        "schema_version": 1, "status": "HISTORICAL_COHORT_AUDIT_ONLY",
        "publication": "BLOCKED", "point_in_time_verified": False,
        "canonical_parent_clusters": len(crashes),
        "monthly_observations": len(monthly),
        "candidate_months_outside_conservative_event_windows": len(screened),
        "candidate_months_are_verified_noncrash_controls": False,
        "candidate_month_examples": [x["month"] for x in screened[:12]],
        "event_windows": event_months,
        "exclusion_rule": "Exclude 24 months before prior-month anchor through 12 months after peak; research screen only.",
        "no_lookahead_certified": False, "true_negative_outcomes_available": False,
        "holdout_eras_defined": False, "independent_episode_count": None,
        "predictive_validation": "BLOCKED",
        "limitations": [
            "Screened months are not verified noncrash outcomes or independent samples",
            "Event window bounds are provisional research exclusions, not trained or validated thresholds",
            "Parent cluster episode independence and publisher-original vintages remain unverified",
            "Retrospective exclusions use future crash knowledge and cannot be used as prospective features",
        ],
    }
