"""Mechanism evidence comparison: missingness and falsification before modeling."""
import json
import argparse
from pathlib import Path

MECHANISMS = {
    "monetary": ("yield_curve", "policy_rate"),
    "credit_banking": ("credit_spread", "financial_stress"),
    "labor_growth": ("unemployment", "real_gdp"),
    "housing": ("housing_starts", "house_prices"),
    "speculative": ("equity_drawdown", "valuation"),
    "external_shock": ("global_trade", "global_financial_stress"),
}

SERIES_MAP = {"CPIAUCSL": "inflation", "GDPC1": "real_gdp", "UNRATE": "unemployment",\n              "ICSA": "initial_claims"}\n\ndef adapt_standardized_metrics(document):\n    if document.get("report_type") != "V5_STANDARDIZED_MACRO_METRICS":\n        raise ValueError("Expected V5 standardized macro metrics")\n    mapped = {}\n    for item in document.get("metrics", []):\n        key = SERIES_MAP.get(item.get("series"))\n        if key and item.get("status") == "DESCRIPTIVE_TRANSFORM_AVAILABLE":\n            mapped[key] = {"value": item.get("value"),\n                           "publisher_original_pit_certified": item.get("publisher_original_pit_certified") is True,\n                           "observation_date": item.get("observation_date"),\n                           "metric": item.get("metric")}\n    return mapped\n\ndef assess(metrics, labels=None):
    labels = labels or []
    outcomes = [x for x in labels if x.get("label") in ("POSITIVE_RESEARCH_LABEL", "NEGATIVE_RESEARCH_LABEL")]
    results = {}
    for mechanism, features in MECHANISMS.items():
        present = [key for key in features if isinstance(metrics.get(key), dict)
                   and metrics[key].get("value") is not None
                   and metrics[key].get("publisher_original_pit_certified") is True]
        results[mechanism] = {
            "required_features": list(features), "pit_features_verified": present,
            "missing_or_unverified": [key for key in features if key not in present],
            "model_comparison": "NOT_RUN_INSUFFICIENT_VALIDATED_OUTCOMES",
            "ablation": "NOT_RUN", "falsification": "NOT_RUN",
        }
    return {"schema_version": 1, "report_type": "V5_MECHANISM_EVIDENCE_GATE",
            "mechanisms": results, "research_outcomes_provided": len(outcomes),
            "independent_outcome_validation": False,
            "chronological_holdout_validated": False,
            "prediction_status": "BLOCKED",
            "note": "No performance statistics are computed without independently validated, point-in-time matched outcomes."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metrics")
    p.add_argument("--labels")\n    p.add_argument("--standardized")
    p.add_argument("--output", default="audit-output/v5_mechanism_evidence_gate.json")
    a = p.parse_args()
    metrics = json.loads(Path(a.metrics).read_text()) if a.metrics else {}
    labels = json.loads(Path(a.labels).read_text()) if a.labels else []\n    if a.standardized:\n        metrics.update(adapt_standardized_metrics(json.loads(Path(a.standardized).read_text())))
    if not isinstance(metrics, dict) or not isinstance(labels, list):
        raise ValueError("Expected metrics object and labels array")
    result = assess(metrics, labels)\n    result["standardized_macro_connected"] = bool(a.standardized)
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
