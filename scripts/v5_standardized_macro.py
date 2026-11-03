"""V5 dated macro transformations. Never infer inflation or GDP growth from one level."""
from datetime import date
from math import isfinite

def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v)

def _month(d):
    dt = date.fromisoformat(d)
    return dt.year * 12 + dt.month - 1

def transform(series, observations, as_of):
    """Observations: dated rows with value, optional release_date and vintage_verified."""
    if not isinstance(observations, list):
        raise ValueError("Expected dated observation rows")
    report_date = date.fromisoformat(as_of)
    by_month = {}
    claims_weeks = {}
    for row in observations:
        d = date.fromisoformat(row["date"])
        release = row.get("release_date")
        if d > report_date or (release and date.fromisoformat(release) > report_date):
            raise ValueError("Future observation or publication date")
        value = row.get("value")
        if not _num(value):
            continue
        key = _month(row["date"])
        if series == "ICSA":
            claims_weeks.setdefault(key, []).append(dict(row))
            continue
        if key in by_month:
            raise ValueError("Duplicate observation period; select a vintage explicitly")
        by_month[key] = dict(row)
    if series == "ICSA":
        # ICSA is weekly. Aggregate dated weekly levels to monthly means;
        # never silently select one week or treat it as a monthly observation.
        for key, weeks in claims_weeks.items():
            by_month[key] = {"date": max(w["date"] for w in weeks),
                             "value": sum(w["value"] for w in weeks) / len(weeks),
                             "vintage_verified": all(w.get("vintage_verified") for w in weeks)}
    if not by_month:
        return {"series": series, "status": "INSUFFICIENT_HISTORY", "metric": None,
                "value": None, "observation_date": None, "comparison_date": None}
    current_key = max(by_month)
    current = by_month[current_key]
    specs = {
        "CPIAUCSL": ("CPI_YEAR_OVER_YEAR_PERCENT", 12),
        "GDPC1": ("REAL_GDP_QUARTER_OVER_QUARTER_ANNUALIZED_PERCENT", 3),
        "UNRATE": ("UNEMPLOYMENT_THREE_MONTH_POINT_CHANGE", 3),
        "ICSA": ("INITIAL_CLAIMS_MONTH_OVER_MONTH_PERCENT", 1),
    }
    if series not in specs:
        return {"series": series, "status": "UNSUPPORTED_TRANSFORMATION",
                "metric": None, "value": None, "observation_date": current["date"], "comparison_date": None}
    metric, lag = specs[series]
    if series == "GDPC1" and date.fromisoformat(current["date"]).month not in (1, 4, 7, 10):
        raise ValueError("GDP observation must use a quarter-start date")
    prior = by_month.get(current_key - lag)
    if prior is None:
        return {"series": series, "status": "INSUFFICIENT_HISTORY", "metric": metric,
                "value": None, "observation_date": current["date"], "comparison_date": None}
    if series == "GDPC1" and date.fromisoformat(prior["date"]).month not in (1, 4, 7, 10):
        raise ValueError("GDP comparison must use a quarter-start date")
    a, b = current["value"], prior["value"]
    if series == "UNRATE":
        value = a - b
    elif b <= 0 or (series == "GDPC1" and a <= 0):
        return {"series": series, "status": "INVALID_BASELINE", "metric": metric,
                "value": None, "observation_date": current["date"], "comparison_date": prior["date"]}
    elif series == "GDPC1":
        value = ((a / b) ** 4 - 1) * 100
    else:
        value = (a / b - 1) * 100
    return {
        "series": series, "status": "DESCRIPTIVE_TRANSFORM_AVAILABLE",
        "metric": metric, "value": round(value, 6),
        "observation_date": current["date"], "comparison_date": prior["date"],
        "publisher_original_pit_certified": bool(current.get("vintage_verified") and prior.get("vintage_verified")),
        "predictive_use_approved": False,
    }

def build(history):
    if history.get("schema_version") != 1 or not history.get("as_of"):
        raise ValueError("V5 dated history contract required")
    rows = [transform(key, history.get("series", {}).get(key, []), history["as_of"])
            for key in ("CPIAUCSL", "GDPC1", "UNRATE", "ICSA")]
    return {"schema_version": 1, "report_type": "V5_STANDARDIZED_MACRO_METRICS",
            "as_of": history["as_of"], "metrics": rows,
            "available": sum(x["status"] == "DESCRIPTIVE_TRANSFORM_AVAILABLE" for x in rows),
            "predictive_publication": "BLOCKED",
            "limitations": [
                "Dated historical levels required; single weekly snapshots cannot produce inflation or GDP growth",
                "Initial claims monthly change compares monthly averages of available weekly claims; incomplete months may be provisional",
                "Quarterly GDP annualization assumes comparable real GDP levels",
                "Publisher-original vintage certification is required for prospective replay",
            ]}

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--history", default="audit-output/v5_dated_history.json")
    p.add_argument("--output", default="audit-output/v5_standardized_macro_metrics.json")
    a = p.parse_args()
    path = Path(a.history)
    # Missing history is an explicit coverage gap, never synthetic data.
    source = json.loads(path.read_text()) if path.exists() else {"schema_version": 1, "as_of": date.today().isoformat(), "series": {}}
    result = build(source)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"available": result["available"], "metrics": len(result["metrics"])}))
