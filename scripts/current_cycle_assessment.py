"""Non-predictive present-day economic-cycle research assessment.

Uses existing integrated readout, preserves all source-quality restrictions.
No stage dating, probabilities, composite risk score, or investment advice.
"""
import argparse
import json
from pathlib import Path

def assess(integrated):
    macro = integrated.get("economic_cycle", {}).get("domains", {})
    def observed(key):
        obj = macro.get(key, {})
        value = obj.get("observation")
        return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None
    growth, labor, inflation = (observed(k) for k in ("growth", "labor", "inflation"))
    descriptions = {
        "growth": "Positive real output growth" if growth is not None and growth > 0 else "Nonpositive real output growth" if growth is not None else "Unknown",
        "labor": "Unemployment increasing" if labor is not None and labor > 0 else "Unemployment stable or decreasing" if labor is not None else "Unknown",
        "inflation": "Positive consumer price inflation" if inflation is not None and inflation > 0 else "Nonpositive consumer price inflation" if inflation is not None else "Unknown",
    }
    mechanisms = {
        "inflation_supply_shock": {"evidence": ["inflation"], "status": "CONTEXT_ONLY"},
        "monetary_tightening": {"evidence": ["inflation"], "missing": ["policy-rate trajectory", "real yields"], "status": "INCOMPLETE"},
        "valuation_speculation": {"missing": ["valuation and positioning measures"], "status": "INCOMPLETE"},
        "credit_housing": {"missing": ["verified current credit and housing stress measures"], "status": "INCOMPLETE"},
        "external_shock": {"missing": ["observable external shock event"], "status": "NOT_FORECASTABLE_FROM_MACRO"},
    }
    return {
        "status": "DESCRIPTIVE_CURRENT_REVISED_NOT_PIT",
        "publication": "BLOCKED",
        "validated_cycle_stage": None,
        "crash_probability": None,
        "composite_risk_score": None,
        "investment_recommendation": None,
        "observed_domains": {k: {"value": observed(k), "latest_date": macro.get(k, {}).get("latest_date"), "interpretation": descriptions[k]} for k in descriptions},
        "mechanism_lenses": mechanisms,
        "assessment": "Growth, labor and inflation are described separately; no validated crash mechanism or economic-cycle stage inferred.",
        "limitations": ["Historical analogues are not validated predictors", "Current revised macro data are not certified historical vintages", "Financial snapshot has separate dates and eligibility", "Social and generational context is interpretive, not a proven predictive variable"],
        "financial_snapshot_date": integrated.get("financial_housing", {}).get("snapshot_date"),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="audit-output/integrated_research_readout.json")
    parser.add_argument("--output", default="audit-output/current_cycle_assessment.json")
    args = parser.parse_args()
    result = assess(json.loads(Path(args.input).read_text()))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "output": str(target)}))

if __name__ == "__main__":
    main()
