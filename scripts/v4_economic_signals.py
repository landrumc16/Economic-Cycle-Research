"""Explainable V4 economic-cycle domain signals, without a composite forecast."""
from math import isfinite

RULES = {
    "UNRATE": ("labor", "higher", "Unemployment rose; possible labor-market softening", "Unemployment fell; possible labor-market resilience"),
    "ICSA": ("labor", "higher", "Initial claims rose; possible labor-market softening", "Initial claims fell; possible labor-market resilience"),
    "GDPC1": ("growth", "lower", "Real GDP level rose between released observations", "Real GDP level fell between released observations"),
    "CPIAUCSL": ("prices", "neutral", "CPI price level rose; inflation acceleration cannot be inferred", "CPI price level fell; sustained disinflation cannot be inferred"),
    "BAMLH0A0HYM2": ("credit", "higher", "High-yield spreads widened; credit risk pricing tightened", "High-yield spreads narrowed; credit risk pricing eased"),
    "STLFSI4": ("financial_stress", "higher", "Financial stress index increased", "Financial stress index decreased"),
    "T10Y2Y": ("yield_curve", "neutral", "Yield curve steepened; recession implications depend on its cause", "Yield curve flattened; recession implications depend on its cause"),
    "DGS2": ("rates", "neutral", "Two-year Treasury yield rose; cause not established", "Two-year Treasury yield fell; cause not established"),
    "DGS10": ("rates", "neutral", "Ten-year Treasury yield rose; cause not established", "Ten-year Treasury yield fell; cause not established"),
}

def build_signals(snapshot):
    if snapshot.get("report_type") != "V3_WEEKLY_ECONOMIC_EVIDENCE":
        raise ValueError("Expected Version 3 evidence contract")
    observations = snapshot.get("series", {})
    changes = snapshot.get("week_over_week", {})
    signals = []
    for series, (domain, risk_direction, up, down) in RULES.items():
        entry = observations.get(series, {})
        change = changes.get(series, {})
        value = entry.get("observation_value")
        delta = change.get("numeric_change")
        usable = isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)
        comparable = (usable and change.get("new_observation_date") is True
                      and isinstance(delta, (int, float)) and not isinstance(delta, bool) and isfinite(delta))
        if not usable:
            direction, interpretation = "UNAVAILABLE", "No usable numeric observation"
        elif change.get("same_observation_revision_detected"):
            direction, interpretation = "REVISED", "Previously dated value revised; not a new economic observation"
        elif not comparable:
            direction, interpretation = "CARRIED_OR_UNCOMPARABLE", "No comparable newly dated observation; direction not inferred"
        elif delta > 0:
            direction, interpretation = "INCREASED", up
        elif delta < 0:
            direction, interpretation = "DECREASED", down
        else:
            direction, interpretation = "UNCHANGED", "Observed value unchanged across dated observations"
        risk_evidence = "NOT_ASSESSED"
        if comparable and not change.get("same_observation_revision_detected") and delta != 0 and risk_direction != "neutral":
            adverse = (delta > 0) if risk_direction == "higher" else (delta < 0)
            risk_evidence = "ADVERSE_DIRECTIONAL_EVIDENCE" if adverse else "FAVORABLE_DIRECTIONAL_EVIDENCE"
        signals.append({
            "series": series, "domain": domain, "observation_date": entry.get("latest_observation"),
            "observation_value": value if usable else None, "source_status": entry.get("status", "MISSING"),
            "release_date": entry.get("release_date"), "vintage_date": entry.get("vintage_date"),
            "point_in_time_certified": entry.get("publisher_original_pit_certified") is True,
            "direction": direction, "interpretation": interpretation, "risk_evidence": risk_evidence,
            "change_between_observations": delta if comparable else None,
            "transformation": "NEW_DATED_OBSERVATION_DIFFERENCE" if comparable else "NONE",
        })
    domains = {}
    for signal in signals:
        domain = signal["domain"]
        domains.setdefault(domain, {"adverse": 0, "favorable": 0, "unassessed": 0})
        key = {"ADVERSE_DIRECTIONAL_EVIDENCE": "adverse", "FAVORABLE_DIRECTIONAL_EVIDENCE": "favorable"}.get(signal["risk_evidence"], "unassessed")
        domains[domain][key] += 1
    return {"schema_version": 1, "report_type": "V4_EXPLAINABLE_ECONOMIC_SIGNALS",
            "as_of": snapshot["as_of"], "status": "DESCRIPTIVE_ONLY", "signals": signals,
            "domains": domains, "validated_cycle_stage": None, "composite_score": None,
            "crash_probability": None, "predictive_publication": "BLOCKED",
            "limitations": [
                "Differences between observation dates are not necessarily weekly changes",
                "CPI level changes do not measure acceleration; GDP level changes are not annualized growth rates",
                "Directional risk evidence is qualitative, not a validated recession or crash probability",
                "Publisher-original vintages and release-time availability remain unverified",
            ]}

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="audit-output/v3_weekly_snapshot.json")
    parser.add_argument("--output", default="audit-output/v4_economic_signals.json")
    args = parser.parse_args()
    result = build_signals(json.loads(Path(args.snapshot).read_text()))
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"signals": len(result["signals"]), "domains": len(result["domains"])}))
