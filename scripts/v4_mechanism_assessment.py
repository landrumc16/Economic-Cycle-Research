"""V4 mechanism-by-mechanism descriptive evidence assessment."""
PATHWAYS = {
    "monetary_inflation": ("CPIAUCSL", "DGS2", "DGS10", "T10Y2Y"),
    "banking_credit_liquidity": ("BAMLH0A0HYM2", "STLFSI4"),
    "growth_labor_recession": ("UNRATE", "ICSA", "GDPC1"),
    "housing_leverage": (),
    "speculative_valuation_unwind": (),
    "external_global_shock": (),
    "supply_shock": (),
}

def assess_mechanisms(signals):
    if signals.get("report_type") != "V4_EXPLAINABLE_ECONOMIC_SIGNALS":
        raise ValueError("V4 economic signals required")
    indexed = {x["series"]: x for x in signals.get("signals", [])}
    pathways = []
    for name, required in PATHWAYS.items():
        evidence = []
        for key in required:
            item = indexed.get(key)
            evidence.append({
                "series": key, "available": bool(item and item.get("observation_value") is not None),
                "observation_date": item.get("observation_date") if item else None,
                "direction": item.get("direction") if item else "UNAVAILABLE",
                "risk_evidence": item.get("risk_evidence") if item else "NOT_ASSESSED",
                "interpretation": item.get("interpretation") if item else "No mapped evidence",
            })
        adverse = [x["series"] for x in evidence if x["risk_evidence"] == "ADVERSE_DIRECTIONAL_EVIDENCE"]
        favorable = [x["series"] for x in evidence if x["risk_evidence"] == "FAVORABLE_DIRECTIONAL_EVIDENCE"]
        unknown = [x["series"] for x in evidence if x["risk_evidence"] == "NOT_ASSESSED"]
        pathways.append({
            "pathway": name, "status": "DESCRIPTIVE_EVIDENCE_ONLY",
            "mapped_indicators": len(required),
            "available_indicators": sum(x["available"] for x in evidence),
            "adverse_evidence": adverse, "favorable_evidence": favorable,
            "unassessed_indicators": unknown, "indicator_evidence": evidence,
            "mixed_directional_evidence": bool(adverse and favorable),
            "mechanism_confirmed": False, "validated_risk_probability": None,
            "interpretation": ("No mapped numeric evidence; mechanism cannot be assessed" if not any(x["available"] for x in evidence)
                               else "Mapped indicator evidence only; causation and predictive relevance not established"),
        })
    return {
        "schema_version": 1, "report_type": "V4_MULTI_MECHANISM_ASSESSMENT",
        "as_of": signals["as_of"], "status": "DESCRIPTIVE_ONLY",
        "pathways": pathways, "composite_crash_score": None,
        "validated_cycle_stage": None, "crash_probability": None,
        "predictive_publication": "BLOCKED",
        "limitations": [
            "A single indicator can inform multiple mechanisms and must not be counted as independent proof",
            "Unmapped pathways remain unknown, never zero-risk",
            "Mixed evidence is retained; no forced single risk classification",
            "Directional evidence does not establish causal mechanism or calibrated probability",
        ],
    }

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--signals", default="audit-output/v4_economic_signals.json")
    parser.add_argument("--output", default="audit-output/v4_mechanism_assessment.json")
    a = parser.parse_args()
    result = assess_mechanisms(json.loads(Path(a.signals).read_text()))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pathways": len(result["pathways"]), "predictive_publication": result["predictive_publication"]}))
