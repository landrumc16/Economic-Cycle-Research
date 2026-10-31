"""Evidence map for historically distinct mechanisms; no classification or scoring."""
PATHWAYS = {
    "inflation_monetary_tightening": ("CPIAUCSL", "DGS2", "DGS10"),
    "banking_credit_liquidity": ("BAMLH0A0HYM2", "STLFSI4", "T10Y2Y"),
    "labor_growth_slowdown": ("UNRATE", "ICSA", "GDPC1"),
    "speculative_valuation_unwind": (),
    "external_global_shock": (),
}

def pathway_evidence(indicators):
    by_series = {row["series"]: row for row in indicators}
    results = []
    for pathway, required in PATHWAYS.items():
        evidence = []
        for name in required:
            item = by_series.get(name)
            evidence.append({
                "series": name,
                "available": item is not None and item.get("value") is not None,
                "observation_date": item.get("latest_observation") if item else None,
                "delta_new_release": item.get("delta_new_release") if item else None,
            })
        results.append({
            "pathway": pathway, "status": "EVIDENCE_INVENTORY_ONLY",
            "indicators": evidence, "observed": sum(x["available"] for x in evidence),
            "required": len(required), "mechanism_confirmed": False,
            "historical_mechanism_mapping_verified": False,
            "validated_probability": None,
            "limitations": "Indicators do not independently identify a causal mechanism; historical canonical labels remain unverified.",
        })
    return {"status": "DESCRIPTIVE_ONLY", "pathways": results,
            "composite_risk_score": None, "predictive_publication": "BLOCKED"}
