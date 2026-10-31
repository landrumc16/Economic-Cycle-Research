"""Connect weekly evidence to V2 historical feature coverage without predictive analogues."""
DOMAINS = {
    "growth": ("GDPC1", "growth"),
    "inflation": ("CPIAUCSL", "inflation"),
    "labor": ("UNRATE", "labor"),
    "yield_curve": ("T10Y2Y", "yield_curve"),
    "credit": ("BAMLH0A0HYM2", "credit"),
    "financial_stress": ("STLFSI4", None),
}

def bridge(weekly, historical):
    if historical.get("status") != "DESCRIPTIVE_ONLY" or historical.get("publication") != "BLOCKED":
        raise ValueError("Unverified historical evidence contract")
    if historical.get("control_status") != "NOT_VERIFIED":
        raise ValueError("Historical control contract changed; review required")
    by_series = {x["series"]: x for x in weekly.get("indicators", [])}
    coverage = historical.get("coverage", {})
    comparisons = []
    for domain, (series, historical_domain) in DOMAINS.items():
        current = by_series.get(series, {})
        historical_status = coverage.get(historical_domain, {}).get("status") if historical_domain else "NOT_DIRECTLY_COMPARABLE"
        historical_count = coverage.get(historical_domain, {}).get("observed_parent_clusters", 0) if historical_domain else 0
        comparisons.append({
            "domain": domain, "current_series": series,
            "current_observation_available": current.get("value") is not None,
            "current_observation_date": current.get("latest_observation"),
            "historical_parent_clusters_with_domain": historical_count,
            "historical_status": historical_status,
            "direct_numeric_comparison": "BLOCKED_UNMATCHED_TRANSFORMATION_AND_VINTAGE",
            "reason": "Current source level and historical transformed feature are not certified comparable; historical releases are revised, not original point-in-time.",
        })
    return {
        "status": "DESCRIPTIVE_HISTORICAL_BRIDGE_ONLY",
        "historical_parent_clusters": len(historical.get("pathway_profiles", [])),
        "historical_controls_verified": False,
        "historical_source_sha256": historical.get("source_sha256"),
        "domains": comparisons,
        "historical_analogue_rankings": None,
        "crash_probability": None,
        "predictive_publication": "BLOCKED",
    }
