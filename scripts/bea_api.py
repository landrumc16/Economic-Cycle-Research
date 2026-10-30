"""Acquire BEA NIPA Table 1.1.6 line 1 real GDP from the official BEA API.

Requires BEA_API_KEY. Output is publisher evidence, not PIT certification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

ENDPOINT = "https://apps.bea.gov/api/data"

def parse_bea(payload):
    obj = json.loads(payload)
    root = obj.get("BEAAPI", {})
    if root.get("Error") or root.get("Results", {}).get("Error"):
        raise ValueError("BEA API returned an error")
    records = root.get("Results", {}).get("Data", [])
    if not isinstance(records, list) or not records:
        raise ValueError("BEA API response contains no observations")
    result = {}
    for row in records:
        if str(row.get("LineNumber", "")).strip() not in ("1", "1.0"):
            continue
        period = str(row.get("TimePeriod", ""))
        if len(period) != 6 or period[4] != "Q" or period[-1] not in "1234":
            continue
        month = {"1":"01","2":"04","3":"07","4":"10"}[period[-1]]
        date = period[:4] + "-" + month + "-01"
        value = float(str(row["DataValue"]).replace(",", ""))
        if date in result:
            raise ValueError("duplicate BEA GDP quarter: " + date)
        result[date] = value
    if not result:
        raise ValueError("No BEA GDP line 1 quarterly observations")
    return result

def acquire(output, key):
    query = urllib.parse.urlencode({
        "UserID": key, "method": "GetData", "datasetname": "NIPA",
        "TableName": "T10106", "Frequency": "Q", "Year": "ALL",
        "ResultFormat": "JSON"})
    request = urllib.request.Request(ENDPOINT + "?" + query,
        headers={"User-Agent": "Economic-Cycle-Research/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read(30_000_000)
    output.mkdir(parents=True, exist_ok=True)
    # Raw data is retained; the credential-bearing URL is never logged.
    (output / "bea_T10106_original.json").write_bytes(raw)
    observations = parse_bea(raw)
    (output / "bea_gdpc1_normalized.json").write_text(json.dumps(observations, sort_keys=True))
    report = {"source": "BEA NIPA T10106 line 1 quarterly chained-dollar real GDP",
        "sha256": hashlib.sha256(raw).hexdigest(), "observations": len(observations),
        "first": min(observations), "last": max(observations),
        "status": "ACQUIRED NOT RECONCILED", "promotion": "BLOCKED"}
    (output / "bea_report.json").write_text(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="audit-output/bea-api")
    args = parser.parse_args()
    key = os.environ.get("BEA_API_KEY")
    if not key:
        raise SystemExit("BEA_API_KEY missing; BEA source not acquired")
    print(json.dumps(acquire(Path(args.output), key), indent=2))
