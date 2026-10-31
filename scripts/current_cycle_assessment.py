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
    financial = integrated.get("financial_housing", {}).get("domains", {})
    def financial_fact(domain):
        item = financial.get(domain, {})
        return {
            "value": item.get("value"),
            "observation_date": item.get("observation_date"),
            "quality": item.get("quality", "MISSING"),
            "source": item.get("series_id"),
        }
    evidence = {
        "inflation_supply_shock": {
            "observations": {"inflation": inflation},
            "missing": ["supply disruptions", "energy-price dynamics"],
        },
        "monetary_tightening": {
            "observations": {"inflation": inflation, "yield_curve": financial_fact("yield_curve")},
            "missing": ["policy-rate trajectory", "real interest rates"],
        },
        "valuation_speculation": {
            "observations": {"equity_volatility": financial_fact("equity_volatility")},
            "missing": ["equity valuation", "market concentration", "leverage"],
        },
        "credit_housing": {
            "observations": {
                "credit": financial_fact("credit"),
                "housing_starts": financial_fact("housing_starts"),
                "household_debt_service": financial_fact("household_debt_service"),
            },
            "missing": ["bank funding stress", "credit delinquency trends"],
        },
        "external_shock": {
            "observations": {},
            "missing": ["observable exogenous event"],
        },
    }
    for name, lens in mechanisms.items():
        lens["observed_evidence"] = evidence[name]["observations"]
        lens["missing"] = evidence[name]["missing"]
        lens["status"] = "CONTEXT_ONLY_NOT_CLASSIFIED" if any(
            (isinstance(value, dict) and isinstance(value.get("value"), (int, float)) and value.get("quality") == "APPROVED_SOURCE")
            or (isinstance(value, (int, float)) and not isinstance(value, bool))
            for value in evidence[name]["observations"].values()
        ) else "INSUFFICIENT_EVIDENCE"
    financial_status = {name: financial_fact(name) for name in (
        "credit", "yield_curve", "housing_starts", "household_debt_service", "equity_volatility"
    )}
    return {
        "status": "DESCRIPTIVE_CURRENT_REVISED_NOT_PIT",
        "publication": "BLOCKED",
        "validated_cycle_stage": None,
        "crash_probability": None,
        "composite_risk_score": None,
        "investment_recommendation": None,
        "observed_domains": {k: {"value": observed(k), "latest_date": macro.get(k, {}).get("latest_date"), "interpretation": descriptions[k]} for k in descriptions},
        "mechanism_lenses": mechanisms,
        "financial_context": financial_status,
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
