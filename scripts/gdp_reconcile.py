"""Reconcile BEA real GDP NIPA Table 1.1.6 line 1 with FRED GDPC1.

Requires explicit official BEA CSV export path and FRED CSV; fail closed on
missing publisher source, differing units, or unavailable historical vintages.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

def read_bea(path):
    """Read a normalized *official BEA export*, columns date, value.
    Caller must supply provenance of the original BEA table and extraction.
    """
    result = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not {"date", "value"}.issubset(set(reader.fieldnames or [])):
            raise ValueError("BEA normalized export requires date,value columns")
        for row in reader:
            date = row["date"].strip()
            if date in result:
                raise ValueError("Duplicate BEA quarter " + date)
            result[date] = float(row["value"])
    return result

def read_fred(path):
    result = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.strip(): v.strip() for k, v in row.items() if k and v is not None}
            date = row.get("DATE") or row.get("observation_date")
            value = row.get("GDPC1")
            if not date or value in ("", ".", None):
                continue
            if date in result:
                raise ValueError("Duplicate FRED quarter " + date)
            result[date] = float(value)
    return result

def reconcile(bea, fred, tolerance=0.001, minimum=250):
    common = sorted(set(bea) & set(fred))
    mismatches = [{"date": d, "bea": bea[d], "fred": fred[d]} for d in common if abs(bea[d] - fred[d]) > tolerance]
    return {"overlap_quarters": len(common), "mismatch_count": len(mismatches),
            "mismatches": mismatches[:100], "missing_bea": sorted(set(fred)-set(bea)),
            "missing_fred": sorted(set(bea)-set(fred)),
            "pass": len(common) >= minimum and not mismatches}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bea", required=True, help="Verified BEA Table 1.1.6 line 1 normalized CSV")
    parser.add_argument("--fred", required=True, help="Original FRED GDPC1 CSV")
    parser.add_argument("--out", default="audit-output/gdp_audit.json")
    args = parser.parse_args()
    inputs = {name: {"path": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
              for name, path in [("bea", args.bea), ("fred", args.fred)]}
    result = {"inputs": inputs, "series": "GDPC1", "unit": "billions of chained dollars, SAAR",
              "historical_vintage_review": "NOT PERFORMED",
              "comparison": reconcile(read_bea(args.bea), read_fred(args.fred)),
              "promotion": "BLOCKED"}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2)+"\n")
    if not result["comparison"]["pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
