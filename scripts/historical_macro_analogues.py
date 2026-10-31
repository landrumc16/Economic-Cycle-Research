"""Exploratory macro analogues at historically selected episode starts.

Distances use only common GDP/CPI/unemployment transformations; not forecasts.
Historical observations are current-revised, not publication-time certified.
"""
import argparse
import json
import math
from pathlib import Path

ANCHORS = {
    "1973 inflation / oil shock": "1973-10-01",
    "1980 inflation tightening": "1980-01-01",
    "2000 valuation / dot-com": "2000-03-01",
    "2007 credit / housing": "2007-10-01",
    "2020 external pandemic": "2020-02-01",
}
FEATURES = ("real_gdp_yoy_pct", "cpi_yoy_pct", "unemployment_3m_change_pp")
SCALES = {"real_gdp_yoy_pct": 3.0, "cpi_yoy_pct": 4.0, "unemployment_3m_change_pp": 1.0}

def month_offset(day, delta):
    y, m = map(int, day[:7].split("-"))
    idx = y * 12 + m - 1 + delta
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}-01"

def growth(series, day, prior):
    a, b = series.get(day), series.get(prior)
    return 100 * (a / b - 1) if a is not None and b is not None and b > 0 else None

def features_at(data, day):
    y, m = map(int, day[:7].split("-"))
    quarter = f"{y:04d}-{((m-1)//3)*3+1:02d}-01"
    u = data["UNRATE"]
    un = u.get(day)
    prev = u.get(month_offset(day, -3))
    return {
        "real_gdp_yoy_pct": growth(data["GDPC1"], quarter, month_offset(quarter, -12)),
        "cpi_yoy_pct": growth(data["CPIAUCSL"], day, month_offset(day, -12)),
        "unemployment_3m_change_pp": un - prev if un is not None and prev is not None else None,
    }

def compare(data, current_metrics):
    current = {k: current_metrics.get("metrics", {}).get(k, {}).get("value") for k in FEATURES}
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in current.values()):
        return {"status": "INSUFFICIENT_CURRENT_DATA", "analogues": [], "publication": "BLOCKED"}
    analogues = []
    for name, day in ANCHORS.items():
        historical = features_at(data, day)
        if any(v is None or not math.isfinite(v) for v in historical.values()):
            analogues.append({"episode": name, "anchor": day, "status": "MISSING_DATA"})
            continue
        distance = math.sqrt(sum(((current[k] - historical[k]) / SCALES[k]) ** 2 for k in FEATURES))
        analogues.append({"episode": name, "anchor": day, "status": "EXPLORATORY_ANALOGUE",
                          "historical_metrics": {k: round(v, 3) for k, v in historical.items()},
                          "normalized_distance": round(distance, 3)})
    analogues.sort(key=lambda r: (r.get("normalized_distance", float("inf")), r["episode"]))
    return {
        "status": "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE",
        "publication": "BLOCKED",
        "current_metrics": current,
        "feature_scales": SCALES,
        "analogues": analogues,
        "validated_cycle_stage": None,
        "crash_probability": None,
        "limitations": [
            "Distances measure only GDP, CPI and unemployment; missing credit, valuations, policy and shocks",
            "Anchor dates were selected with hindsight and are not a representative sample",
            "Same-quarter GDP and monthly values may have been published after historical anchor dates",
            "Revised observations are not point-in-time certified",
            "Similarity does not imply that a crash or recession will follow",
        ],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fred", default="audit-output/fred-api")
    parser.add_argument("--metrics", default="audit-output/descriptive_macro_metrics.json")
    parser.add_argument("--output", default="audit-output/historical_macro_analogues.json")
    args = parser.parse_args()
    folder = Path(args.fred)
    data = {k: json.loads((folder / f"{k}_normalized.json").read_text()) for k in ("UNRATE", "CPIAUCSL", "GDPC1")}
    report = compare(data, json.loads(Path(args.metrics).read_text()))
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "analogues": len(report["analogues"])}))

if __name__ == "__main__":
    main()
