"""Acquire BLS observations using the official public JSON API in small year windows.

Source: https://api.bls.gov/publicAPI/v2/timeseries/data/
No registration key required for small, unregistered queries. Limits/rate rules apply.
This is publisher evidence, NOT a replacement for FRED independent reconciliation.
"""
import argparse
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

SERIES = ("LNS14000000", "CUSR0000SA0")

def windows(start, end, span=10):
    for year in range(start, end + 1, span):
        yield year, min(end, year + span - 1)

def fetch(series, start, end, key=None):
    payload = {"seriesid": [series], "startyear": str(start), "endyear": str(end)}
    if key:
        payload["registrationkey"] = key
    request = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data=json.dumps(payload).encode(),
        headers={"User-Agent": "Economic-Cycle-Research/1.0", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(request, timeout=25) as response:
        raw = response.read(5_000_000)
    obj = json.loads(raw)
    if obj.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError("BLS API: " + str(obj.get("message", obj.get("status"))))
    return obj, raw

def run(out, start=1947, end=2026, key=None):
    out.mkdir(parents=True, exist_ok=True)
    report = {"source": "BLS public API v2", "series": {}, "errors": [], "promotion": "BLOCKED"}
    for series in SERIES:
        observations = {}
        raw_hashes = []
        # Unregistered BLS API has restrictive daily request quotas; avoid exhausting it.
        series_windows = list(windows(start, end))
        if not key and len(series_windows) * len(SERIES) > 10:
            report["errors"].append({"series": series, "error": "Unregistered BLS API request quota insufficient for full history; configure BLS_API_KEY or narrow years"})
            break
        for a, b in series_windows:
            print(f"BLS API {series} {a}-{b}", flush=True)
            try:
                obj, raw = fetch(series, a, b, key)
                raw_hashes.append({"years": [a,b], "sha256": hashlib.sha256(raw).hexdigest()})
                for item in obj.get("Results", {}).get("series", []):
                    if item.get("seriesID") != series:
                        continue
                    for datum in item.get("data", []):
                        period = datum.get("period", "")
                        if period.startswith("M") and len(period) == 3 and period[1:].isdigit() and 1 <= int(period[1:]) <= 12:
                            date = f'{int(datum["year"]):04d}-{int(period[1:]):02d}-01'
                            if date in observations:
                                raise ValueError("duplicate " + date)
                            raw_value = str(datum["value"]).strip()
                            if raw_value in ("", "-", "NA", "N/A"):
                                continue
                            observations[date] = float(raw_value)
                (out / f"{series}_{a}_{b}.json").write_bytes(raw)
            except Exception as exc:
                report["errors"].append({"series": series, "years": [a,b], "error": f"{type(exc).__name__}: {exc}"})
            time.sleep(0.3)
        report["series"][series] = {"observations": len(observations),
            "first": min(observations) if observations else None,
            "last": max(observations) if observations else None,
            "raw_chunks": raw_hashes, "status": "ACQUIRED NOT CERTIFIED" if observations else "BLOCKED"}
        (out / f"{series}_normalized.json").write_text(json.dumps(observations, sort_keys=True))
    (out / "bls_api_report.json").write_text(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="audit-output/bls-api")
    p.add_argument("--start", type=int, default=1947)
    p.add_argument("--end", type=int, default=2026)
    args = p.parse_args()
    import os
    report = run(pathlib.Path(args.output), args.start, args.end, os.environ.get("BLS_API_KEY"))
    print(json.dumps({"series": report["series"], "errors": report["errors"]}, indent=2))
    if report["errors"]:
        raise SystemExit(1)
