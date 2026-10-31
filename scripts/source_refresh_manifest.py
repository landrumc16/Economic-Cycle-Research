"""Fail-closed inventory of refreshed macro series; no implied source certification."""
import argparse
import json
import math
from datetime import date
from pathlib import Path

SERIES = ("UNRATE", "CPIAUCSL", "GDPC1", "DGS10", "DGS2", "T10Y2Y", "BAMLH0A0HYM2", "STLFSI4", "ICSA")

def inventory(folder, as_of):
    cutoff = date.fromisoformat(as_of)
    result = {"as_of": as_of, "status": "DESCRIPTIVE_NOT_PIT_CERTIFIED", "series": {}}
    for series in SERIES:
        path = Path(folder) / f"{series}_normalized.json"
        item = {"status": "MISSING", "latest_observation": None, "observation_count": 0,
                "source_file": str(path), "publisher_original_pit_certified": False}
        if path.exists():
            try:
                values = json.loads(path.read_text())
                if not isinstance(values, dict) or not values:
                    raise ValueError("Empty or invalid normalized series")
                dates = sorted(date.fromisoformat(k) for k in values)
                if dates[-1] > cutoff:
                    raise ValueError("Future observation relative to evaluation date")
                if any(not isinstance(v, (float, int)) or isinstance(v, bool) or not math.isfinite(v) for v in values.values()):
                    raise ValueError("Invalid numeric observation")
                item.update(status="STAGED_REVISED_NOT_PIT", latest_observation=dates[-1].isoformat(),
                            observation_count=len(values), age_days=(cutoff-dates[-1]).days)
            except (ValueError, TypeError, OverflowError):
                item["status"] = "INVALID"
        result["series"][series] = item
    result["complete"] = all(v["status"] == "STAGED_REVISED_NOT_PIT" for v in result["series"].values())
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="audit-output/fred-api")
    p.add_argument("--as-of", required=True)
    p.add_argument("--output", default="audit-output/dashboard/source_refresh_manifest.json")
    a = p.parse_args()
    report = inventory(a.input, a.as_of)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"complete": report["complete"], "statuses": {k:v["status"] for k,v in report["series"].items()}}))

if __name__ == "__main__":
    main()
