"""Fail-closed point-in-time release ledger validator.

Input CSV columns: series, observation_date, publication_date, decision_date,
vintage_date, value, source_url. Dates ISO YYYY-MM-DD.
A release can be used only if publication_date <= decision_date and
vintage_date <= decision_date. This checks metadata consistency, not authenticity.
"""
import argparse
import csv
import json
from datetime import date
from pathlib import Path

REQUIRED = ("series", "observation_date", "publication_date", "decision_date",
            "vintage_date", "value", "source_url")
ALLOWED = {"UNRATE", "CPIAUCSL", "GDPC1"}

def validate(rows):
    errors = []
    checked = 0
    seen = set()
    for n, row in enumerate(rows, 2):
        checked += 1
        try:
            missing = [field for field in REQUIRED if not str(row.get(field, "")).strip()]
            if missing:
                raise ValueError("missing fields: " + ", ".join(missing))
            if row["series"] not in ALLOWED:
                raise ValueError("unsupported series")
            observed, published, decision, vintage = (date.fromisoformat(row[k])
                for k in ("observation_date", "publication_date", "decision_date", "vintage_date"))
            if observed > published:
                raise ValueError("observation later than publication")
            if published > decision:
                raise ValueError("look-ahead: publication later than decision")
            if vintage > decision:
                raise ValueError("look-ahead: vintage later than decision")
            if not row["source_url"].startswith("https://"):
                raise ValueError("source_url must use HTTPS")
            float(row["value"])
            key = (row["series"], row["observation_date"], row["decision_date"])
            if key in seen:
                raise ValueError("duplicate series/observation/decision")
            seen.add(key)
        except (ValueError, TypeError) as exc:
            errors.append({"row": n, "reason": str(exc)})
    return {"rows": checked, "metadata_pass": bool(checked) and not errors,
            "errors": errors, "publisher_authenticity": "NOT VERIFIED",
            "historical_vintage_certification": "NOT VERIFIED",
            "promotion": "BLOCKED"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", default="audit-output/pit_validation.json")
    args = parser.parse_args()
    with open(args.csv, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not set(REQUIRED).issubset(reader.fieldnames or []):
            raise SystemExit("Missing required ledger columns")
        result = validate(reader)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["metadata_pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
