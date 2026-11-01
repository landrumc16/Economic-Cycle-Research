"""Compute equity earnings-yield minus Treasury yield as valuation proxy.

A high negative gap can indicate rich equity valuation relative to rates,
but is not itself proof of a bubble. Inputs must be dated and sourced.
"""
import argparse
import csv
import json
import math
from pathlib import Path


def derive(earnings_yield, treasury_yield):
    earnings = {r["date"]: float(r["value"]) for r in earnings_yield}
    treasury = {r["date"]: float(r["value"]) for r in treasury_yield}
    if len(earnings) != len(earnings_yield) or len(treasury) != len(treasury_yield):
        raise ValueError("Duplicate dates")
    if any(not math.isfinite(v) for v in (*earnings.values(), *treasury.values())):
        raise ValueError("Nonfinite yield")
    return [{"date": day, "value": round(treasury[day] - earnings[day], 6)}
            for day in sorted(earnings.keys() & treasury.keys())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("earnings_yield_csv")
    parser.add_argument("treasury_yield_csv")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    def load(path):
        with open(path, newline="") as handle:
            return list(csv.DictReader(handle))
    rows = derive(load(args.earnings_yield_csv), load(args.treasury_yield_csv))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "value"])
        writer.writeheader()
        writer.writerows(rows)
    path.with_suffix(".metadata.json").write_text(json.dumps({
        "name": "equity_earnings_yield_gap",
        "orientation": "Treasury yield minus equity earnings yield; higher means richer relative equity valuation",
        "units": "percentage points",
        "input_units": "both series must be percentage yields, not decimal fractions",
        "source_requirements": "Matched universe, historical earnings methodology, dated source and publication vintage",
        "point_in_time_certified": False,
        "status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
        "limitations": [
            "Risk premium is not measured by the raw yield gap",
            "Earnings yield and Treasury yield need economically compatible horizons",
            "Changing interest rates and earnings cyclicality complicate interpretation",
            "Do not equate broad equity valuation with Nasdaq-specific fundamentals",
        ],
    }, indent=2) + "\n")
    print(f"Matched valuation months: {len(rows)}")


if __name__ == "__main__":
    main()
