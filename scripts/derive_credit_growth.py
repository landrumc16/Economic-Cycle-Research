"""Derive backward-looking 12-month credit growth; descriptive macro proxy."""
import argparse
import csv
import math
from datetime import date
from pathlib import Path


def growth(rows, months=12):
    if months < 1:
        raise ValueError("months must be positive")
    ordered = sorted(rows, key=lambda row: row["date"])
    dates = [date.fromisoformat(row["date"]) for row in ordered]
    values = [float(row["value"]) for row in ordered]
    if len(set(dates)) != len(dates):
        raise ValueError("Duplicate dates")
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Invalid credit level")
    periods = [day.year * 12 + day.month for day in dates]
    if any(b - a != 1 for a, b in zip(periods, periods[1:])):
        raise ValueError("Credit series has missing months")
    return [{"date": ordered[i]["date"],
             "value": round(100 * math.log(values[i] / values[i - months]), 6)}
            for i in range(months, len(values))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.input, newline="") as handle:
        rows = list(csv.DictReader(handle))
    results = growth(rows)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "value"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Credit growth months: {len(results)}")


if __name__ == "__main__":
    main()
