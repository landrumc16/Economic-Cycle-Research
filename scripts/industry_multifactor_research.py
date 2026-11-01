"""Research joint associations between acceleration and independently sourced indicators.

Inputs are dated monthly CSVs with date,value. No forward fill or future data.
This is an analysis harness, not a fitted prediction model.
"""
import argparse
import csv
import json
import math
from pathlib import Path

try:
    from .industry_deviation_metrics import calculate
except ImportError:
    from industry_deviation_metrics import calculate


def read_csv(path):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or set(("date", "value")) - set(rows[0]):
        raise ValueError("Expected date,value CSV: " + str(path))
    dates = [r["date"] for r in rows]
    if len(dates) != len(set(dates)):
        raise ValueError("Duplicate dates: " + str(path))
    for row in rows:
        value = float(row["value"])
        if not math.isfinite(value):
            raise ValueError("Nonfinite value: " + str(path))
    return rows


def analyze(prices, indicators, horizon=12, drawdown_threshold=0.20,
            acceleration_cutoff=90):
    if horizon < 1 or not 0 < drawdown_threshold < 1:
        raise ValueError("Invalid horizon or drawdown")
    ordered = sorted(prices, key=lambda r: r["date"])
    deviations = {r["date"]: r for r in calculate(ordered)}
    aligned = {}
    for name, rows in indicators.items():
        if not name or name == "acceleration":
            raise ValueError("Invalid indicator name")
        aligned[name] = {r["date"]: float(r["value"]) for r in rows}
    records = []
    for i, row in enumerate(ordered):
        metric = deviations.get(row["date"])
        if not metric or metric["historical_percentile"] is None or i + horizon >= len(ordered):
            continue
        path = [float(r["value"]) for r in ordered[i:i + horizon + 1]]
        peak = path[0]
        worst = 0.0
        for value in path[1:]:
            peak = max(peak, value)
            worst = max(worst, 1 - value / peak)
        record = {
            "date": row["date"],
            "acceleration": bool(metric["historical_percentile"] >= acceleration_cutoff
                                 and metric["trailing_log_return"] > 0),
            "subsequent_drawdown": worst >= drawdown_threshold,
            "max_forward_path_drawdown": round(worst, 6),
            "indicators": {name: series.get(row["date"]) for name, series in aligned.items()},
        }
        records.append(record)
    groups = {}
    for name in ("acceleration", *sorted(indicators)):
        eligible = [r for r in records if name == "acceleration" or
                    r["indicators"][name] is not None]
        if name == "acceleration":
            # Acceleration is an explicit binary indicator.
            positive = [r for r in eligible if r["acceleration"]]
            negative = [r for r in eligible if not r["acceleration"]]
            threshold = None
        else:
            # Median computed over the complete retrospective sample: descriptive only.
            values = sorted(r["indicators"][name] for r in eligible)
            threshold = values[len(values) // 2] if values else None
            positive = [r for r in eligible if r["indicators"][name] is not None
                        and threshold is not None and r["indicators"][name] > threshold]
            negative = [r for r in eligible if r not in positive]
        def summarize(subset):
            return {"months": len(subset),
                    "declines": sum(r["subsequent_drawdown"] for r in subset),
                    "fraction": round(sum(r["subsequent_drawdown"] for r in subset) /
                                      len(subset), 6) if subset else None}
        groups[name] = {"threshold": threshold, "above": summarize(positive),
                        "other": summarize(negative),
                        "missing_months": len(records) - len(eligible)}
    return {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
            "horizon_months": horizon, "drawdown_threshold": drawdown_threshold,
            "eligible_price_months": len(records),
            "groups": groups, "observations": records,
            "limitations": [
                "Indicator medians use the full sample and must not be used as live thresholds",
                "Inputs must have separately documented source, units and observation availability",
                "Monthly dates are aligned by label, not certified release timestamps",
                "Overlapping future windows are dependent",
                "Missing indicator observations are excluded, never imputed",
                "No multivariate causal or predictive claim is supported",
            ]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prices")
    parser.add_argument("--indicator", action="append", default=[],
                        help="name=path/to/monthly.csv; may be repeated")
    parser.add_argument("--horizon", type=int, default=12)
    parser.add_argument("--threshold", type=float, default=0.20)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    indicators = {}
    for item in args.indicator:
        name, sep, path = item.partition("=")
        if not sep or not name or name in indicators:
            raise ValueError("Use unique --indicator name=path")
        indicators[name] = read_csv(path)
    result = analyze(read_csv(args.prices), indicators, args.horizon, args.threshold)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["groups"]))


if __name__ == "__main__":
    main()
