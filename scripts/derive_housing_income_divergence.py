"""Trailing change in house-price/income proxy; not a price-to-income level."""
import argparse
import csv
import json
import math
from pathlib import Path


def derive(prices, incomes, lookback=12):
    if lookback < 1:
        raise ValueError("lookback must be positive")
    p = {r["date"]: float(r["value"]) for r in prices}
    y = {r["date"]: float(r["value"]) for r in incomes}
    if len(p) != len(prices) or len(y) != len(incomes):
        raise ValueError("Duplicate month")
    dates = sorted(set(p) & set(y))
    if any(not math.isfinite(v) or v <= 0 for v in (*p.values(), *y.values())):
        raise ValueError("Levels must be finite and positive")
    months = {date: int(date[:4]) * 12 + int(date[5:7]) for date in dates}
    by_month = {month: date for date, month in months.items()}
    output = []
    for current in dates:
        prior = by_month.get(months[current] - lookback)
        if prior is None:
            continue
        price_growth = math.log(p[current] / p[prior])
        income_growth = math.log(y[current] / y[prior])
        output.append({"date": current,
                       "value": round(100 * (price_growth - income_growth), 6)})
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prices")
    parser.add_argument("income")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    def load(path):
        with open(path, newline="") as handle:
            return list(csv.DictReader(handle))
    rows = derive(load(args.prices), load(args.income))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "value"])
        writer.writeheader()
        writer.writerows(rows)
    (path.with_suffix(".metadata.json")).write_text(json.dumps({
        "name": "housing_price_income_growth_divergence",
        "method": "100*(12m log Case-Shiller national home-price growth - 12m log nominal personal-income growth)",
        "sources": ["CSUSHPINSA", "PI"],
        "units": "percentage points of log growth difference",
        "limitations": [
            "National aggregate personal income is not median household income",
            "Home-price index and aggregate income are not directly comparable levels",
            "Not a housing affordability ratio, valuation multiple, or PIT-certified signal",
            "Income is not adjusted for household counts or housing stock",
        ],
        "status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
    }, indent=2) + "\n")
    print(f"Derived {len(rows)} matched historical months")


if __name__ == "__main__":
    main()
