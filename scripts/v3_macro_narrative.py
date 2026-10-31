"""Readable macro narrative based only on observed dated changes, not a cycle model."""
DOMAINS = {
    "labor": ("UNRATE", "ICSA"),
    "credit_and_stress": ("BAMLH0A0HYM2", "STLFSI4"),
    "rates_and_curve": ("DGS2", "DGS10", "T10Y2Y"),
    "growth": ("GDPC1",),
    "price_level": ("CPIAUCSL",),
}

def narrative(indicators):
    by_series = {x["series"]: x for x in indicators}
    domains = []
    for name, ids in DOMAINS.items():
        new = [s for s in ids if s in by_series and by_series[s].get("delta_new_release") is not None]
        revised = [s for s in ids if s in by_series and by_series[s].get("same_observation_revision_detected")]
        observed = [s for s in ids if s in by_series and by_series[s].get("value") is not None]
        if new:
            statement = "New dated observations available for " + ", ".join(new) + "; inspect individual changes and units."
        elif revised:
            statement = "Previously reported values were revised for " + ", ".join(revised) + "; no new dated change is established."
        elif observed:
            statement = "Existing observations carried forward; no comparable newly dated change established."
        else:
            statement = "Insufficient numeric evidence for this domain."
        domains.append({
            "domain": name, "observed_series": observed, "new_dated_series": new,
            "revised_series": revised, "statement": statement,
            "economic_direction": "NOT_CLASSIFIED",
        })
    return {
        "status": "EVIDENCE_LIMITED", "domains": domains,
        "overall_cycle_stage": None, "overall_economic_direction": None,
        "conflicting_signals_assessed": False, "crash_probability": None,
        "limitations": "Directional interpretations remain per-indicator; no aggregate weighting, threshold validation, or verified publication dates.",
    }
