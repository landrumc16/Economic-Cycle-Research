"""Summarize each crash window with comparable, retrospective economic measures.

Annual CPI inflation uses same-month year-over-year CPI percent change.
GDP growth uses same-quarter year-over-year real GDP percent change.
Unemployment uses percentage-point change from event-window start.
No forward-looking or point-in-time claims are authorized.
"""
import argparse
import csv
import json
from pathlib import Path
from retrospective_event_panel import EVENTS

def summarize(input_dir, output_dir):
    series = {name: json.loads((input_dir / f"{name}_normalized.json").read_text())
              for name in ("UNRATE", "CPIAUCSL", "GDPC1")}
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for event, start, end, mechanism in EVENTS:
        unemployment = [(d, v) for d, v in sorted(series["UNRATE"].items()) if start <= d <= end]
        cpi = [(d, v) for d, v in sorted(series["CPIAUCSL"].items()) if start <= d <= end]
        gdp = [(d, v) for d, v in sorted(series["GDPC1"].items()) if start <= d <= end]
        if not unemployment or not cpi or not gdp:
            raise ValueError(f"Incomplete event data: {event}")
        inflation = []
        for d, value in cpi:
            prior = str(int(d[:4]) - 1) + d[4:]
            base = series["CPIAUCSL"].get(prior)
            if base is not None and base > 0:
                inflation.append(100 * (value / base - 1))
        gdp_growth = []
        for d, value in gdp:
            prior = str(int(d[:4]) - 1) + d[4:]
            base = series["GDPC1"].get(prior)
            if base is not None and base > 0:
                gdp_growth.append(100 * (value / base - 1))
        if not inflation or not gdp_growth:
            raise ValueError(f"Insufficient lagged data: {event}")
        rows.append({
            "event": event, "mechanism_hypothesis": mechanism,
            "start": start, "end": end,
            "unemployment_start_pct": round(unemployment[0][1], 3),
            "unemployment_peak_pct": round(max(v for _, v in unemployment), 3),
            "unemployment_peak_increase_pp": round(max(v for _, v in unemployment) - unemployment[0][1], 3),
            "inflation_yoy_peak_pct": round(max(inflation), 3),
            "inflation_yoy_min_pct": round(min(inflation), 3),
            "real_gdp_yoy_min_pct": round(min(gdp_growth), 3),
            "unemployment_months": len(unemployment), "cpi_months": len(cpi), "gdp_quarters": len(gdp),
            "status": "RETROSPECTIVE_CURRENT_REVISED_NOT_PIT"
        })
    with (output_dir / "event_comparison.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {"events": len(rows), "status": "EXPLORATORY_ONLY_NOT_POINT_IN_TIME",
                "definitions": {"unemployment": "window peak minus first unemployment rate, percentage points",
                                "inflation": "same-month prior-year CPI percent change",
                                "gdp": "same-quarter prior-year real GDP percent change"},
                "historical_prediction_authorized": False}
    (output_dir / "comparison_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="audit-output/fred-api")
    parser.add_argument("--output", default="audit-output/phase2")
    args = parser.parse_args()
    print(json.dumps(summarize(Path(args.input), Path(args.output)), indent=2))
