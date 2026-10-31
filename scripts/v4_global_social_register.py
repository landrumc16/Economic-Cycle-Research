"""V4 global/social evidence register: no invented measurements or generational causality."""
CHANNELS = {
    "global": (
        "usd_funding_stress", "foreign_sovereign_yields", "foreign_exchange", "global_trade",
        "commodity_supply", "cross_border_credit", "global_equity_contagion", "foreign_bank_stress",
    ),
    "social": (
        "consumer_sentiment", "business_expectations", "household_balance_sheets",
        "household_spending", "labor_participation", "generational_cohort_hypothesis",
    ),
}

def build_register(evidence=None):
    evidence = evidence or {}
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be a dictionary")
    rows = []
    for domain, channels in CHANNELS.items():
        for name in channels:
            item = evidence.get(name, {})
            if not isinstance(item, dict):
                raise ValueError("Invalid channel evidence")
            value = item.get("value")
            # A channel is measurable only if both source and dated numeric evidence are supplied.
            usable = (isinstance(value, (int, float)) and not isinstance(value, bool)
                      and item.get("source") and item.get("observation_date")
                      and item.get("geography") and item.get("unit"))
            rows.append({
                "domain": domain, "channel": name,
                "status": "SOURCE_QUALIFIED_OBSERVATION" if usable else "NOT_ESTABLISHED",
                "value": value if usable else None,
                "source": item.get("source") if usable else None,
                "observation_date": item.get("observation_date") if usable else None,
                "geography": item.get("geography") if usable else None,
                "unit": item.get("unit") if usable else None,
                "causal_hypothesis_verified": False,
                "predictive_incremental_value_verified": False,
            })
    return {
        "schema_version": 1, "report_type": "V4_GLOBAL_SOCIAL_EVIDENCE_REGISTER",
        "status": "RESEARCH_COVERAGE_ONLY",
        "channels": rows, "defined": len(rows),
        "source_qualified": sum(x["status"] == "SOURCE_QUALIFIED_OBSERVATION" for x in rows),
        "generational_hypothesis_validated": False,
        "predictive_publication": "BLOCKED",
        "limitations": [
            "Channels are a research inventory; missing sourced observations remain unknown",
            "Generational or fourth-turning theories are hypotheses, not causal findings",
            "Global and social observations require publication-date and vintage review before prospective testing",
        ],
    }

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--evidence")
    p.add_argument("--output", default="audit-output/v4_global_social_register.json")
    a = p.parse_args()
    evidence = json.loads(Path(a.evidence).read_text()) if a.evidence else None
    result = build_register(evidence)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"channels": result["defined"], "source_qualified": result["source_qualified"]}))
