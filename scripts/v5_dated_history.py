"""Bridge actual FRED normalized dated observations into V5 history, never PIT-certified."""
import argparse
import json
from datetime import date
from math import isfinite
from pathlib import Path

SERIES = ("CPIAUCSL", "GDPC1", "UNRATE", "ICSA")

def build(folder, as_of):
    cutoff = date.fromisoformat(as_of)
    data = {}
    provenance = {}
    for name in SERIES:
        path = Path(folder) / (name + "_normalized.json")
        if not path.exists():
            data[name] = []
            provenance[name] = {"status": "SOURCE_FILE_MISSING", "rows": 0}
            continue
        raw = json.loads(path.read_text())
        if not isinstance(raw, dict):
            raise ValueError("Expected normalized date-to-value dictionary for " + name)
        rows = []
        for day, value in sorted(raw.items()):
            observed = date.fromisoformat(day)
            if observed > cutoff:
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
                continue
            rows.append({"date": day, "value": value, "release_date": None,
                         "vintage_verified": False, "source": "FRED revised observation series"})
        data[name] = rows
        provenance[name] = {"status": "REVISED_HISTORY_NOT_POINT_IN_TIME" if rows else "NO_USABLE_ROWS",
                            "rows": len(rows), "latest_observation": rows[-1]["date"] if rows else None}
    return {"schema_version": 1, "report_type": "V5_DATED_REVISED_HISTORY",
            "as_of": as_of, "series": data, "provenance": provenance,
            "publisher_original_pit_certified": False, "predictive_publication": "BLOCKED",
            "limitations": ["FRED normalized values may include later revisions; no original publisher vintage is established",
                            "Observation dates are not publication dates; this dataset is descriptive, not prospective replay"]}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--fred", default="audit-output/fred-api")
    p.add_argument("--as-of", required=True)
    p.add_argument("--output", default="audit-output/v5_dated_history.json")
    a = p.parse_args()
    result = build(a.fred, a.as_of)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v["rows"] for k, v in result["provenance"].items()}))
