"""Fetch FRED via the official observations API in date-scoped chunks.

Requires FRED_API_KEY secret. Preserve original responses and SHA256.
Do not interpret a successful revised-series fetch as historical-vintage approval.
"""
import argparse
import hashlib
import json
import os
import pathlib
import urllib.parse
import urllib.request

SERIES = ("UNRATE", "CPIAUCSL", "GDPC1")

def fetch(series, start, end, api_key):
    query = urllib.parse.urlencode({
        "series_id": series, "api_key": api_key, "file_type": "json",
        "observation_start": start, "observation_end": end})
    url = "https://api.stlouisfed.org/fred/series/observations?" + query
    request = urllib.request.Request(url, headers={"User-Agent": "Economic-Cycle-Research/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(8_000_000)
    obj = json.loads(raw)
    if "error_code" in obj:
        raise RuntimeError("FRED API error " + str(obj["error_code"]))
    return obj, raw

def run(out, api_key):
    out.mkdir(parents=True, exist_ok=True)
    report = {"source": "FRED observations API", "series": {}, "errors": [], "promotion": "BLOCKED"}
    for series in SERIES:
        data = {}
        chunks = []
        for start, end in [("1947-01-01","1979-12-31"), ("1980-01-01","2009-12-31"), ("2010-01-01","2026-12-31")]:
            try:
                obj, raw = fetch(series, start, end, api_key)
                filename = f"{series}_{start[:4]}_{end[:4]}.json"
                (out / filename).write_bytes(raw)
                chunks.append({"file": filename, "sha256": hashlib.sha256(raw).hexdigest()})
                for obs in obj.get("observations", []):
                    if obs.get("value") not in (None, ".", ""):
                        if obs["date"] in data:
                            raise ValueError("duplicate date " + obs["date"])
                        data[obs["date"]] = float(obs["value"])
            except Exception as exc:
                report["errors"].append({"series": series, "window": [start,end],
                                         "error": f"{type(exc).__name__}: {exc}"})
        report["series"][series] = {"observations": len(data), "chunks": chunks,
                                    "status": "ACQUIRED NOT CERTIFIED" if data else "BLOCKED"}
        (out / f"{series}_normalized.json").write_text(json.dumps(data, sort_keys=True))
    (out / "fred_api_report.json").write_text(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="audit-output/fred-api")
    args = p.parse_args()
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise SystemExit("FRED_API_KEY not configured; no download attempted")
    report = run(pathlib.Path(args.output), key)
    print(json.dumps({"series": report["series"], "errors": report["errors"]}, indent=2))
    if report["errors"]:
        raise SystemExit(1)
