"""Fetch public FRED graph CSV, reduce daily closes to monthly observations.

Descriptive data only. Graph CSV is not an archival point-in-time vintage.
"""
import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ALLOWED = {"NASDAQCOM": "daily", "CSUSHPINSA": "monthly",
           "TOTALSL": "monthly", "BUSLOANS": "monthly",
           "PI": "monthly"}


def normalize_csv(payload, series):
    if series not in ALLOWED:
        raise ValueError("Series not approved")
    reader = csv.DictReader(io.StringIO(payload))
    if not reader.fieldnames or series not in reader.fieldnames or not ({"observation_date", "DATE"} & set(reader.fieldnames)):
        raise ValueError("Unexpected FRED CSV columns")
    by_month = {}
    valid = 0
    for row in reader:
        raw = row.get(series, "")
        if raw in ("", "."):
            continue
        d = date.fromisoformat(row.get("observation_date") or row.get("DATE"))
        value = float(raw)
        if not (0 < value < float("inf")):
            raise ValueError("Nonpositive or nonfinite observation")
        key = d.strftime("%Y-%m")
        if key not in by_month or d > by_month[key][0]:
            by_month[key] = (d, value)
        valid += 1
    if not valid:
        raise ValueError("No valid observations")
    return [{"date": k + "-01", "value": v[1], "last_observed_date": v[0].isoformat()}
            for k, v in sorted(by_month.items())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("series", choices=sorted(ALLOWED))
    parser.add_argument("--start", default="1980-01-01")
    parser.add_argument("--end", default="2026-10-31")
    parser.add_argument("--output-dir", default="data/industry_observations")
    args = parser.parse_args()
    date.fromisoformat(args.start)
    date.fromisoformat(args.end)
    if args.start > args.end:
        raise ValueError("Start after end")
    query = urllib.parse.urlencode({"id": args.series, "cosd": args.start, "coed": args.end})
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + query
    request = urllib.request.Request(url, headers={"User-Agent": "Economic-Cycle-Research/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8-sig")
    observations = normalize_csv(payload, args.series)
    # The current month is incomplete at a mid-month cutoff. Exclude it uniformly.
    end_date = date.fromisoformat(args.end)
    # Only the last month can be partial; its completion cannot be inferred
    # from the presence of a final daily observation on the cutoff date.
    observations = [row for row in observations
                    if row["date"][:7] < end_date.strftime("%Y-%m")
                    or (end_date.toordinal() + 1 ==
                        (date(end_date.year + (end_date.month == 12),
                              end_date.month % 12 + 1, 1)).toordinal())]
    if not observations:
        raise ValueError("No complete monthly observations")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with (out / (args.series + "_monthly.csv")).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "value"])
        writer.writeheader()
        writer.writerows({"date": row["date"], "value": row["value"]} for row in observations)
    meta = {"series": args.series, "source_url": url, "source_frequency": ALLOWED[args.series],
            "monthly_method": "last_available_observation_in_calendar_month",
            "first_month": observations[0]["date"], "last_month": observations[-1]["date"],
            "observations": len(observations), "point_in_time_certified": False,
            "latest_observed_date": observations[-1]["last_observed_date"],
            "use": "retrospective descriptive only"}
    (out / (args.series + "_metadata.json")).write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
