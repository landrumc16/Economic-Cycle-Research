"""Weekly-ready economic research snapshot from latest complete monthly observations.

Not a real-time nowcast or validated crash probability. Explicit coverage and lag.
"""
import argparse
import csv
import json
import math
from datetime import date
from pathlib import Path

try:
    from .industry_deviation_metrics import calculate
except ImportError:
    from industry_deviation_metrics import calculate


def read(path):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Empty observations: " + str(path))
    return rows


def snapshot(root, as_of):
    date.fromisoformat(as_of)
    directory = root / "data/industry_observations"
    series = ("NASDAQCOM", "CSUSHPINSA", "TOTALSL", "BUSLOANS", "PI",
              "UNRATE", "CPIAUCSL", "INDPRO")
    sources = {}
    for name in series:
        rows = [r for r in read(directory / (name + "_monthly.csv"))
                if r["date"] <= as_of]
        if not rows:
            raise ValueError("No observations on/before assessment date: " + name)
        meta = json.loads((directory / (name + "_metadata.json")).read_text())
        if meta["series"] != name or meta["point_in_time_certified"] is not False:
            raise ValueError("Source metadata incompatible: " + name)
        sources[name] = rows
    common_date = min(rows[-1]["date"] for rows in sources.values())
    # Re-anchor ALL signals to the latest shared month. No mixing different dates.
    trimmed = {name: [r for r in rows if r["date"] <= common_date]
               for name, rows in sources.items()}
    def growth(name, months=12):
        rows = trimmed[name]
        by_date = {r["date"][:7]: float(r["value"]) for r in rows}
        year, month = map(int, common_date[:7].split("-"))
        index = year * 12 + month - months
        prior = f"{(index - 1) // 12:04d}-{(index - 1) % 12 + 1:02d}"
        current = by_date.get(common_date[:7])
        previous = by_date.get(prior)
        if current is None or previous is None or current <= 0 or previous <= 0:
            return None
        return round(100 * math.log(current / previous), 4)
    def acceleration(name):
        rows = trimmed[name]
        signals = calculate(rows)
        if not signals or signals[-1]["date"] != common_date:
            return {"status": "INSUFFICIENT_HISTORY"}
        last = signals[-1]
        percentile = last["historical_percentile"]
        return {"status": "DESCRIPTIVE_ONLY" if percentile is not None else "INSUFFICIENT_HISTORY",
                "trailing_log_return": last["trailing_log_return"],
                "historical_percentile": percentile,
                "high_acceleration": bool(percentile >= 90 and last["trailing_log_return"] > 0)
                if percentile is not None else None}
    equity = acceleration("NASDAQCOM")
    housing = acceleration("CSUSHPINSA")
    home_growth = growth("CSUSHPINSA")
    income_growth = growth("PI")
    divergence = (round(home_growth - income_growth, 4)
                  if home_growth is not None and income_growth is not None else None)
    def age_months(month):
        y, m = map(int, month[:7].split("-"))
        ay, am = map(int, as_of[:7].split("-"))
        return (ay - y) * 12 + am
    def change(name, months):
        by_month = {r["date"][:7]: float(r["value"]) for r in trimmed[name]}
        year, month = map(int, common_date[:7].split("-"))
        index = year * 12 + month - months
        prior = f"{(index - 1) // 12:04d}-{(index - 1) % 12 + 1:02d}"
        current, earlier = by_month.get(common_date[:7]), by_month.get(prior)
        return round(current - earlier, 4) if current is not None and earlier is not None else None
    return {
        "status": "RESEARCH_SNAPSHOT_NOT_FORECAST",
        "assessment_date": as_of,
        "common_observation_month": common_date,
        "months_since_common_observation": age_months(common_date),
        "stale": age_months(common_date) > 2,
        "equity_acceleration": equity,
        "housing_acceleration": housing,
        "consumer_credit_growth_12m_log_pct": growth("TOTALSL"),
        "business_credit_growth_12m_log_pct": growth("BUSLOANS"),
        "housing_price_income_growth_gap_12m_log_pp": divergence,
        "unemployment_rate_pct": float(trimmed["UNRATE"][-1]["value"]),
        "unemployment_change_3m_pp": change("UNRATE", 3),
        "cpi_inflation_12m_log_pct": growth("CPIAUCSL"),
        "industrial_production_growth_12m_log_pct": growth("INDPRO"),
        "sources": {name: {"latest_available_month": sources[name][-1]["date"],
                           "latest_used_month": trimmed[name][-1]["date"],
                           "source_url": json.loads((directory / (name + "_metadata.json")).read_text())["source_url"]}
                    for name in series},
        "limitations": [
            "Weekly publication cadence does not imply weekly input data",
            "This is a common-month retrospective snapshot, not a point-in-time reconstruction",
            "Current-vintage observations may have been revised",
            "Publication dates and release lags are not certified",
            "Credit and income measures are broad national proxies",
            "No crash probability, investment recommendation or validated economic phase classification",
        ],
    }


def markdown(result):
    def show(value):
        return "Unavailable" if value is None else str(value)
    lines = ["# Weekly economic research assessment", "",
             f"Assessment date: **{result['assessment_date']}**",
             f"Latest common observation month: **{result['common_observation_month']}**",
             f"Observation lag: **{result['months_since_common_observation']} months**",
             f"Data freshness: **{'STALE' if result['stale'] else 'Recent monthly observations'}**",
             "", "## Observed indicators", ""]
    for label, key in (("Consumer credit 12m log growth (%)", "consumer_credit_growth_12m_log_pct"),
                       ("Business credit 12m log growth (%)", "business_credit_growth_12m_log_pct"),
                       ("Housing price minus income 12m log growth (pp)", "housing_price_income_growth_gap_12m_log_pp"),
                       ("Unemployment rate (%)", "unemployment_rate_pct"),
                       ("Unemployment change 3m (pp)", "unemployment_change_3m_pp"),
                       ("CPI inflation 12m log growth (%)", "cpi_inflation_12m_log_pct"),
                       ("Industrial production 12m log growth (%)", "industrial_production_growth_12m_log_pct")):
        lines.append(f"- {label}: {show(result[key])}")
    for name in ("equity_acceleration", "housing_acceleration"):
        signal = result[name]
        lines.append(f"- {name}: {show(signal.get('high_acceleration'))}; "
                     f"historical percentile: {show(signal.get('historical_percentile'))}")
    lines += ["", "## Interpretation", "",
              "These are observed conditions, not an estimated recession phase or crash forecast.",
              "A change from last week's assessment may reflect a newly published monthly observation or revised data.",
              "", "## Data limitations", ""]
    lines.extend("- " + note for note in result["limitations"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default="audit-output")
    args = parser.parse_args()
    result = snapshot(Path(args.root), args.as_of)
    target = Path(args.root) / args.output_dir
    target.mkdir(parents=True, exist_ok=True)
    (target / "weekly_economic_assessment.json").write_text(json.dumps(result, indent=2) + "\n")
    (target / "weekly_economic_assessment.md").write_text(markdown(result))
    print(markdown(result))


if __name__ == "__main__":
    main()
