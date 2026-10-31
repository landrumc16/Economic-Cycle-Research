"""Explain directional evidence without turning it into an unvalidated risk score."""
from math import isfinite

# Directions are research interpretations of the observed indicator, not predictions.
RULES = {
    "UNRATE": ("labor", 1, "Higher unemployment may indicate labor-market softening", "Lower unemployment may indicate labor-market resilience"),
    "ICSA": ("labor", 1, "Rising initial claims may indicate increasing layoffs", "Falling initial claims may indicate fewer new unemployment claims"),
    "BAMLH0A0HYM2": ("credit", 1, "Widening high-yield spreads may indicate tighter credit risk pricing", "Narrowing high-yield spreads may indicate easing credit risk pricing"),
    "STLFSI4": ("financial_stress", 1, "Rising financial stress index suggests more financial-market stress", "Falling financial stress index suggests less financial-market stress"),
    "T10Y2Y": ("yield_curve", -1, "A steepening 10y-2y spread changes curve shape; cause is not identified", "A flattening 10y-2y spread changes curve shape; cause is not identified"),
    "DGS10": ("rates", 0, "The 10-year Treasury yield rose; the macroeconomic cause is undetermined", "The 10-year Treasury yield fell; the macroeconomic cause is undetermined"),
    "DGS2": ("rates", 0, "The 2-year Treasury yield rose; the macroeconomic cause is undetermined", "The 2-year Treasury yield fell; the macroeconomic cause is undetermined"),
    "CPIAUCSL": ("inflation", 0, "CPI level increased; this alone does not establish inflation acceleration", "CPI level decreased; this alone does not establish sustained disinflation"),
    "GDPC1": ("growth", 0, "Real GDP level increased between observations", "Real GDP level decreased between observations"),
}

def interpret(indicators):
    evidence = []
    for item in indicators:
        key = item["series"]
        if key not in RULES:
            continue
        domain, _direction, up, down = RULES[key]
        delta = item.get("delta_new_release")
        if not isinstance(delta, (int, float)) or isinstance(delta, bool) or not isfinite(delta):
            finding = "NO_COMPARABLE_NEW_OBSERVATION"
            explanation = "No comparable newly dated observation; no direction inferred."
        elif delta > 0:
            finding, explanation = "INCREASED", up
        elif delta < 0:
            finding, explanation = "DECREASED", down
        else:
            finding, explanation = "UNCHANGED", "Observed value unchanged between newly dated observations."
        evidence.append({
            "series": key, "domain": domain, "direction": finding,
            "interpretation": explanation,
            "quality": "DESCRIPTIVE_REVISED_NOT_PIT",
            "caveat": "Difference between dated observations, not necessarily a weekly change; no causal or predictive certification.",
        })
    return {
        "status": "DESCRIPTIVE_ONLY",
        "validated_cycle_stage": None,
        "composite_score": None,
        "crash_probability": None,
        "findings": evidence,
    }
