"""Compute backward-looking industry deviations from dated monthly observations.

Input CSV: date,value. Output is descriptive, not a crash forecast.
"""
import argparse
import csv
import json
import math
from datetime import date
from pathlib import Path


def calculate(rows, lookback=12, history=60, minimum_history=36):
    """Compare each trailing return with returns observable before that month."""
    if lookback < 1 or history < minimum_history or minimum_history < 2:
        raise ValueError("Invalid lookback/history settings")
    ordered = sorted(rows, key=lambda r: r["date"])
    dates = [date.fromisoformat(r["date"]) for r in ordered]
    values = [float(r["value"]) for r in ordered]
    if len(dates) != len(set(dates)):
        raise ValueError("Duplicate dates")
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError("Values must be finite and positive")
    months = [d.year * 12 + d.month for d in dates]
    if any(b - a != 1 for a, b in zip(months, months[1:])):
        raise ValueError("Monthly input must have no gaps")
    result = []
    for i in range(lookback, len(values)):
        change = math.log(values[i] / values[i - lookback])
        prior = [math.log(values[j] / values[j - lookback])
                 for j in range(lookback, i)]
        prior = prior[-history:]
        entry = {"date": ordered[i]["date"], "trailing_log_return": round(change, 8),
                 "prior_observations": len(prior), "z_score": None,
                 "historical_percentile": None, "status": "INSUFFICIENT_BASELINE"}
        if len(prior) >= minimum_history:
            mean = sum(prior) / len(prior)
            variance = sum((v - mean) ** 2 for v in prior) / len(prior)
            if variance > 0:
                entry["z_score"] = round((change - mean) / math.sqrt(variance), 6)
            entry["historical_percentile"] = round(
                100 * sum(v <= change for v in prior) / len(prior), 3)
            entry["status"] = "DESCRIPTIVE_ONLY"
        result.append(entry)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--output", default="audit-output/industry_deviation_metrics.json")
    parser.add_argument("--lookback", type=int, default=12)
    parser.add_argument("--history", type=int, default=60)
    parser.add_argument("--minimum-history", type=int, default=36)
    args = parser.parse_args()
    with open(args.csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    result = {"method": "trailing log return vs strictly earlier rolling return distribution",
              "publication": "DESCRIPTIVE_NOT_VALIDATED",
              "rows": calculate(rows, args.lookback, args.history, args.minimum_history)}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {len(result['rows'])} observations to {target}")


if __name__ == "__main__":
    main()
