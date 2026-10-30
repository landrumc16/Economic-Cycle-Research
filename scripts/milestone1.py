"""Acquire original BLS/FRED data and compare current-revised monthly values.

No automatic Google Sheets promotion. All output is evidence only.
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import urllib.request
from datetime import datetime, timezone

SOURCES = {
    "unrate_bls": "https://download.bls.gov/pub/time.series/ln/ln.data.1.AllData",
    "unrate_fred": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE",
    "cpi_bls": "https://download.bls.gov/pub/time.series/cu/cu.data.1.AllItems",
    "cpi_fred": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL",
}
SERIES = {
    "UNRATE": ("unrate_bls", "unrate_fred", "LNS14000000", 1e-6),
    "CPIAUCSL": ("cpi_bls", "cpi_fred", "CUSR0000SA0", 0.005),
}

def download(name, directory):
    destination = directory / (name + ".txt")
    request = urllib.request.Request(SOURCES[name], headers={"User-Agent": "Economic-Cycle-Research/1.0 (source-validation)"})
    digest = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(request, timeout=45) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > 150_000_000:
                raise ValueError("Publisher download exceeds 150 MB safety limit")
            output.write(chunk)
            digest.update(chunk)
    return {"path": str(destination), "bytes": total,
            "sha256": digest.hexdigest(), "url": SOURCES[name]}

def parse_bls(path, series):
    out = {}
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for record in reader:
            record = {k.strip(): v.strip() for k, v in record.items() if k is not None and v is not None}
            if record.get("series_id") != series:
                continue
            period = record.get("period", "")
            if not (len(period) == 3 and period.startswith("M") and period[1:].isdigit() and 1 <= int(period[1:]) <= 12):
                continue
            month = f'{int(record["year"]):04d}-{int(period[1:]):02d}-01'
            if month in out:
                raise ValueError(f"Duplicate BLS observation: {series} {month}")
            out[month] = float(record["value"])
    return out

def parse_fred(path, series):
    out = {}
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for record in reader:
            record = {k.strip(): v.strip() for k, v in record.items() if k is not None and v is not None}
            date = record.get("DATE") or record.get("observation_date")
            value = record.get(series)
            if not date or value in (None, "", "."):
                continue
            if date in out:
                raise ValueError(f"Duplicate FRED observation: {series} {date}")
            out[date] = float(value)
    return out

def compare(bls, fred, tolerance, min_overlap=600):
    shared = sorted(set(bls) & set(fred))
    differences = [{"month": date, "bls": bls[date], "fred": fred[date], "difference": round(bls[date] - fred[date], 8)}
                   for date in shared if abs(bls[date] - fred[date]) > tolerance]
    missing_bls = sorted(set(fred) - set(bls))
    missing_fred = sorted(set(bls) - set(fred))
    return {"overlap": len(shared), "first_month": shared[0] if shared else None,
            "last_month": shared[-1] if shared else None, "mismatches": differences[:100],
            "mismatch_count": len(differences), "missing_bls": missing_bls[:100],
            "missing_fred": missing_fred[:100], "missing_bls_count": len(missing_bls),
            "missing_fred_count": len(missing_fred),
            "structural_pass": len(shared) >= min_overlap,
            "numeric_pass": len(shared) >= min_overlap and not differences}

def run(destination):
    destination.mkdir(parents=True, exist_ok=True)
    result = {"checked_utc": datetime.now(timezone.utc).isoformat(),
              "promotion": "BLOCKED", "vintage_certification": "NOT_PERFORMED",
              "downloads": {}, "series": {}, "errors": []}
    for name in SOURCES:
        print(f"Acquiring {name}: {SOURCES[name]}", flush=True)
        try:
            result["downloads"][name] = download(name, destination)
            print("Acquired {}: {} bytes".format(name, result["downloads"][name]["bytes"]), flush=True)
        except Exception as exc:
            result["errors"].append(f"{name}: {type(exc).__name__}: {exc}")
    for series, (bls_key, fred_key, bls_id, tolerance) in SERIES.items():
        if bls_key not in result["downloads"] or fred_key not in result["downloads"]:
            result["series"][series] = {"status": "BLOCKED: source acquisition"}
            continue
        try:
            left = parse_bls(pathlib.Path(result["downloads"][bls_key]["path"]), bls_id)
            right = parse_fred(pathlib.Path(result["downloads"][fred_key]["path"]), series)
            result["series"][series] = compare(left, right, tolerance)
            result["series"][series]["status"] = "REVISED-SERIES CROSSCHECK ONLY"
        except Exception as exc:
            result["errors"].append(f"{series}: {type(exc).__name__}: {exc}")
            result["series"][series] = {"status": "BLOCKED: parser or reconciliation"}
    (destination / "audit_results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="audit-output")
    args = parser.parse_args()
    result = run(pathlib.Path(args.output))
    print(json.dumps({"series": result["series"], "errors": result["errors"],
                      "promotion": result["promotion"]}, indent=2))
    if result["errors"] or any(not v.get("numeric_pass") for v in result["series"].values()):
        raise SystemExit(1)
