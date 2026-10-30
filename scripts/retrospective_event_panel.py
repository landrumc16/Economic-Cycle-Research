"""Build a retrospective, read-only crash-event panel from reconciled FRED series.

Uses CURRENT-REVISED values only. Never a point-in-time backtest or promotion.
Input files are created by scripts/fred_api.py. No external dependencies.
"""
import argparse
import csv
import json
from pathlib import Path

EVENTS = (
    ("1973-1975 stagflation", "1973-01-01", "1975-12-31", "inflation / oil shock"),
    ("1980-1982 inflation tightening", "1979-01-01", "1983-12-31", "monetary tightening"),
    ("2000-2002 dot-com", "1999-01-01", "2003-12-31", "equity valuation / technology"),
    ("2007-2009 financial crisis", "2006-01-01", "2010-12-31", "credit / banking"),
    ("2020 pandemic", "2019-01-01", "2021-12-31", "exogenous shutdown"),
)

def build(input_dir, output_dir):
    series = {name: json.loads((input_dir / f"{name}_normalized.json").read_text())
              for name in ("UNRATE", "CPIAUCSL", "GDPC1")}
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for event, start, end, mechanism in EVENTS:
        for name, observations in series.items():
            for date, value in sorted(observations.items()):
                if start <= date <= end:
                    rows.append({"event": event, "mechanism_hypothesis": mechanism,
                                 "series": name, "observation_date": date,
                                 "current_revised_value": value,
                                 "data_status": "CURRENT_REVISED_NOT_POINT_IN_TIME"})
    if not rows:
        raise ValueError("No observations found for defined event windows")
    with (output_dir / "retrospective_event_panel.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {"status": "EXPLORATORY_ONLY_NOT_POINT_IN_TIME",
                "source": "FRED API normalized current-revised observations",
                "events": [event for event, _, _, _ in EVENTS],
                "rows": len(rows), "canonical_spreadsheet_modified": False,
                "historical_signal_or_promotion_authorized": False}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="audit-output/fred-api")
    parser.add_argument("--output", default="audit-output/phase2")
    args = parser.parse_args()
    print(json.dumps(build(Path(args.input), Path(args.output)), indent=2))
