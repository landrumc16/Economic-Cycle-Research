"""Build a decision-date point-in-time series from a publisher-verified release ledger.

Ledger fields: series, observation_date, publication_date, decision_date,
vintage_date, value, source_url. This transformation NEVER authenticates
the source_url or the publisher release. It only checks ledger consistency.
"""
import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

FIELDS = ("series", "observation_date", "publication_date", "decision_date",
          "vintage_date", "value", "source_url")

def date(value):
    return dt.date.fromisoformat(value)

def build(rows):
    grouped = defaultdict(list)
    errors = []
    for i, row in enumerate(rows, 2):
        try:
            if any(not str(row.get(k, "")).strip() for k in FIELDS):
                raise ValueError("missing required field")
            publication = date(row["publication_date"])
            decision = date(row["decision_date"])
            vintage = date(row["vintage_date"])
            observation = date(row["observation_date"])
            if publication < observation or vintage < observation:
                raise ValueError("release precedes observation date")
            if publication > decision or vintage > decision:
                raise ValueError("future information at decision date")
            if not row["source_url"].startswith("https://"):
                raise ValueError("non-HTTPS publisher evidence URL")
            value = float(row["value"])
            if not (-float("inf") < value < float("inf")):
                raise ValueError("nonfinite observation")
            grouped[(row["series"], observation.isoformat(), decision.isoformat())].append(
                (publication, vintage, value, row["source_url"]))
        except (ValueError, TypeError) as exc:
            errors.append({"row": i, "reason": str(exc)})
    output = []
    for (series, observation, decision), candidates in sorted(grouped.items()):
        candidates.sort(key=lambda x: (x[0], x[1]))
        latest_date = (candidates[-1][0], candidates[-1][1])
        latest = [c for c in candidates if (c[0], c[1]) == latest_date]
        if len(latest) != 1:
            errors.append({"series": series, "observation_date": observation,
                           "decision_date": decision, "reason": "ambiguous latest vintage"})
            continue
        publication, vintage, value, source = latest[0]
        output.append({"series": series, "observation_date": observation,
            "decision_date": decision, "publication_date": publication.isoformat(),
            "vintage_date": vintage.isoformat(), "value": value, "source_url": source})
    return output, errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", required=True)
    p.add_argument("--output", default="audit-output/pit_series.json")
    args = p.parse_args()
    with open(args.ledger, newline="") as f:
        rows = list(csv.DictReader(f))
    values, errors = build(rows)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {"values": values, "errors": errors, "source_authenticity": "NOT VERIFIED",
              "promotion": "BLOCKED"}
    out.write_text(json.dumps(report, indent=2) + "
")
    print(json.dumps({"selected": len(values), "errors": len(errors),
                      "source_authenticity": "NOT VERIFIED", "promotion": "BLOCKED"}))
    if errors or not values:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
