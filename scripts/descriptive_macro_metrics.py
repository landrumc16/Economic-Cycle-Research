"""Compute transparent descriptive macro transformations without forecasting.

All calculations use available current-revised observations. Historical point-in-
time analysis and publication remain blocked until the separate source gates pass.
"""
import argparse
import json
import math
from pathlib import Path

def change(current, previous, percent=True):
    if current is None or previous is None or previous <= 0:
        return None
    value = 100 * (current / previous - 1) if percent else current - previous
    return round(value, 4) if math.isfinite(value) else None

def describe(normalized):
    unrate = normalized.get("UNRATE", {})
    cpi = normalized.get("CPIAUCSL", {})
    gdp = normalized.get("GDPC1", {})
    report = {"status": "RETROSPECTIVE_CURRENT_REVISED_NOT_PIT",
              "publication": "BLOCKED", "cycle_stage": None,
              "crash_probability": None, "metrics": {}}
    definitions = {
        "unemployment_3m_change_pp": ("UNRATE", 3, False, "percentage points"),
        "unemployment_12m_change_pp": ("UNRATE", 12, False, "percentage points"),
        "cpi_yoy_pct": ("CPIAUCSL", 12, True, "percent"),
        "real_gdp_yoy_pct": ("GDPC1", 4, True, "percent")
    }
    for label, (series, lag, pct, unit) in definitions.items():
        data = normalized.get(series, {})
        # Calendar lags, never count previous available rows: gaps remain gaps.
        dates = sorted(data)
        latest = dates[-1] if dates else None
        if latest is None:
            report["metrics"][label] = {"value": None, "reason": "NO_DATA", "unit": unit}
            continue
        year, month = map(int, latest[:7].split("-"))
        prior_month_index = year * 12 + month - 1 - lag * (3 if series == "GDPC1" else 1)
        prior = f"{prior_month_index // 12:04d}-{prior_month_index % 12 + 1:02d}-01"
        value = change(data[latest], data.get(prior), pct)
        report["metrics"][label] = {
            "value": value, "unit": unit, "latest_date": latest,
            "baseline_date": prior,
            "reason": None if value is not None else "MISSING_BASELINE_OR_INVALID",
            "definition": f"{series} calendar-lag {lag} {'quarters' if series == 'GDPC1' else 'months'}"
        }
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="audit-output/fred-api")
    p.add_argument("--output", default="audit-output/descriptive_macro_metrics.json")
    a = p.parse_args()
    data = {}
    for series in ("UNRATE", "CPIAUCSL", "GDPC1"):
        path = Path(a.input) / f"{series}_normalized.json"
        if path.exists():
            data[series] = json.loads(path.read_text())
    result = describe(data)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
