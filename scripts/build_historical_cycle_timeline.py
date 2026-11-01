"""Historical economic condition timeline, using only dated observations.

The timeline is descriptive and uses current-vintage revised data; it is NOT a
real-time historical reconstruction, official recession dating, or a forecast.
"""
import argparse
import csv
import json
import math
from pathlib import Path


SERIES = ("UNRATE", "CPIAUCSL", "INDPRO", "TOTALSL", "BUSLOANS")


def load(root, name):
    path = root / "data/industry_observations" / f"{name}_monthly.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        key = row["date"][:7]
        value = float(row["value"])
        if key in result or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid or duplicated monthly observation: " + name)
        result[key] = value
    return result


def lag(month, n):
    year, number = map(int, month.split("-"))
    index = year * 12 + number - 1 - n
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def growth(series, month, n=12):
    a, b = series.get(month), series.get(lag(month, n))
    return round(100 * math.log(a / b), 4) if a is not None and b is not None and a > 0 and b > 0 else None


def build(root):
    data = {name: load(root, name) for name in SERIES}
    months = sorted(set.intersection(*(set(v) for v in data.values())))
    timeline = []
    for month in months:
        u_now, u_prev = data["UNRATE"].get(month), data["UNRATE"].get(lag(month, 3))
        unemployment_change = round(u_now - u_prev, 4) if u_now is not None and u_prev is not None else None
        production = growth(data["INDPRO"], month)
        inflation = growth(data["CPIAUCSL"], month)
        consumer = growth(data["TOTALSL"], month)
        business = growth(data["BUSLOANS"], month)
        if any(x is None for x in (unemployment_change, production, inflation, consumer, business)):
            continue
        tags = []
        if unemployment_change > 0:
            tags.append("LABOR_SOFTENING")
        if production < 0:
            tags.append("PRODUCTION_CONTRACTION")
        if inflation > 0:
            tags.append("POSITIVE_INFLATION")
        if consumer > 0 and business > 0:
            tags.append("BROAD_CREDIT_EXPANSION")
        timeline.append({
            "month": month,
            "unemployment_rate_pct": u_now,
            "unemployment_change_3m_pp": unemployment_change,
            "industrial_production_growth_12m_log_pct": production,
            "cpi_inflation_12m_log_pct": inflation,
            "consumer_credit_growth_12m_log_pct": consumer,
            "business_credit_growth_12m_log_pct": business,
            "condition_tags": tags,
        })
    if not timeline:
        raise ValueError("Insufficient overlapping monthly observations")
    return {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
            "first_month": timeline[0]["month"],
            "last_month": timeline[-1]["month"],
            "months": len(timeline),
            "method": "Fixed direction-of-change tags; no fitted thresholds or future outcomes",
            "point_in_time_certified": False,
            "limitations": [
                "Current-vintage revised data, not what observers knew at each historical date",
                "No official recession dates, phase labels, or forecast probabilities",
                "Overlapping year-over-year changes are dependent",
                "Unemployment and production indicators are not publication-lag adjusted",
            ],
            "timeline": timeline}


def markdown(result):
    counts = {}
    for row in result["timeline"]:
        for tag in row["condition_tags"]:
            counts[tag] = counts.get(tag, 0) + 1
    lines = ["# Historical economic-condition timeline", "",
             "**Retrospective descriptive research, not validated economic-cycle classification.**",
             "", f"Coverage: {result['first_month']} to {result['last_month']} "
             f"({result['months']} complete months).", "",
             "## Condition prevalence", "",
             "| Condition | Months observed | Share of complete months |",
             "|---|---:|---:|"]
    for name in ("LABOR_SOFTENING", "PRODUCTION_CONTRACTION",
                 "POSITIVE_INFLATION", "BROAD_CREDIT_EXPANSION"):
        count = counts.get(name, 0)
        lines.append(f"| {name} | {count} | {count / result['months']:.1%} |")
    lines += ["", "## Method limitations", ""]
    lines += ["- " + item for item in result["limitations"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default="audit-output")
    args = parser.parse_args()
    report = build(Path(args.root))
    target = Path(args.root) / args.output_dir
    target.mkdir(parents=True, exist_ok=True)
    (target / "historical_cycle_timeline.json").write_text(json.dumps(report, indent=2) + "\n")
    (target / "historical_cycle_timeline.md").write_text(markdown(report))
    print(f"Historical condition timeline: {report['months']} months")


if __name__ == "__main__":
    main()
