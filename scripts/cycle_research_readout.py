"""Explain macro conditions using the workbook's existing qualitative framework.

This is a descriptive RESEARCH interpretation, not NBER cycle dating or
a validated real-time stage or crash forecast.
"""
import argparse
import json
from pathlib import Path

def interpret(metrics):
    values = metrics.get("metrics", {})
    def number(key):
        obj = values.get(key, {})
        val = obj.get("value")
        return val if isinstance(val, (float, int)) and not isinstance(val, bool) else None
    growth = number("real_gdp_yoy_pct")
    labor = number("unemployment_3m_change_pp")
    inflation = number("cpi_yoy_pct")
    result = {
        "status": "RESEARCH_ONLY_CURRENT_REVISED_NOT_PIT",
        "publication": "BLOCKED", "validated_cycle_stage": None,
        "crash_probability": None, "sector_recommendation": None,
        "domains": {}
    }
    result["domains"]["growth"] = {
        "observation": growth, "unit": "percent year over year",
        "description": ("MISSING" if growth is None else
                        "POSITIVE_REAL_GROWTH" if growth > 0 else
                        "NEGATIVE_REAL_GROWTH" if growth < 0 else "FLAT_REAL_GROWTH")}
    result["domains"]["labor"] = {
        "observation": labor, "unit": "percentage points over 3 months",
        "description": ("MISSING" if labor is None else
                        "UNEMPLOYMENT_RISING" if labor > 0 else
                        "UNEMPLOYMENT_FALLING" if labor < 0 else "UNCHANGED")}
    result["domains"]["inflation"] = {
        "observation": inflation, "unit": "percent year over year",
        "description": ("MISSING" if inflation is None else
                        "PRICES_RISING" if inflation > 0 else
                        "PRICES_FALLING" if inflation < 0 else "UNCHANGED_PRICE_INDEX")}
    result["cross_domain"] = (
        "INSUFFICIENT_DATA" if growth is None or labor is None or inflation is None
        else "DESCRIPTIVE_ONLY_NO_CYCLE_STAGE_INFERENCE")
    result["limitations"] = [
        "Current-revised observations are not certified point-in-time releases",
        "Direction descriptions do not imply a calibrated recession or crash probability",
        "NBER recession dating and crash pathway classification are separate outcomes"
    ]
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metrics", default="audit-output/descriptive_macro_metrics.json")
    p.add_argument("--output", default="audit-output/cycle_research_readout.json")
    args = p.parse_args()
    metrics = json.loads(Path(args.metrics).read_text())
    result = interpret(metrics)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
