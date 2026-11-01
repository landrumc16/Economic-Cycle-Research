"""Compare historical deviation bins with later observed drawdowns.

Retrospective descriptive analysis only. Overlapping windows are dependent.
"""
import argparse
import csv
import json
from pathlib import Path

try:
    from .industry_deviation_metrics import calculate
except ImportError:
    from industry_deviation_metrics import calculate


def compare(rows, horizon=12, threshold=0.20, percentile_cutoff=90):
    if horizon < 1 or not 0 < threshold < 1 or not 0 < percentile_cutoff <= 100:
        raise ValueError("Invalid comparison parameters")
    metrics = {r["date"]: r for r in calculate(rows)}
    ordered = sorted(rows, key=lambda r: r["date"])
    summary = {"high_deviation": {"eligible": 0, "drawdown": 0},
               "other": {"eligible": 0, "drawdown": 0}}
    observations = []
    for i, row in enumerate(ordered):
        m = metrics.get(row["date"])
        if not m or m["historical_percentile"] is None or i + horizon >= len(ordered):
            continue
        current = float(row["value"])
        future = [float(r["value"]) for r in ordered[i + 1:i + horizon + 1]]
        # Drawdown from a high established on or after observation month.
        path = [current] + future
        high = path[0]
        maximum_drawdown = 0.0
        for value in path[1:]:
            high = max(high, value)
            maximum_drawdown = max(maximum_drawdown, 1 - value / high)
        group = "high_deviation" if m["historical_percentile"] >= percentile_cutoff else "other"
        outcome = maximum_drawdown >= threshold
        summary[group]["eligible"] += 1
        summary[group]["drawdown"] += int(outcome)
        observations.append({"date": row["date"], "group": group,
                             "max_future_path_drawdown": round(maximum_drawdown, 6),
                             "threshold_crossed": outcome})
    for value in summary.values():
        value["observed_fraction"] = (round(value["drawdown"] / value["eligible"], 6)
                                      if value["eligible"] else None)
    return {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
            "horizon_months": horizon, "drawdown_threshold": threshold,
            "percentile_cutoff": percentile_cutoff,
            "note": "Monthly path drawdown; overlapping horizons; no causal or predictive interpretation.",
            "groups": summary, "observations": observations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--output", default="audit-output/industry_deviation_comparison.json")
    parser.add_argument("--horizon", type=int, default=12)
    parser.add_argument("--threshold", type=float, default=0.20)
    parser.add_argument("--percentile-cutoff", type=float, default=90)
    args = parser.parse_args()
    with open(args.csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    result = compare(rows, args.horizon, args.threshold, args.percentile_cutoff)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["groups"]))


if __name__ == "__main__":
    main()
