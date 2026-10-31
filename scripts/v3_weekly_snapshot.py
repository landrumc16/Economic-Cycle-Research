"""Version 3 weekly evidence snapshot; descriptive only, no predictive inference."""
import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path

def build_weekly_snapshot(refresh, as_of, previous=None):
    cutoff = date.fromisoformat(as_of)
    if not isinstance(refresh, dict) or not isinstance(refresh.get("series"), dict):
        raise ValueError("Source refresh manifest must include series")
    series = {}
    for name, source in sorted(refresh["series"].items()):
        if not isinstance(source, dict):
            raise ValueError("Invalid series metadata")
        last = source.get("latest_observation")
        if last is not None:
            observed = date.fromisoformat(last)
            if observed > cutoff:
                raise ValueError("Future observation: " + name)
        else:
            observed = None
        status = source.get("status", "MISSING")
        if status not in ("MISSING", "INVALID", "STAGED_REVISED_NOT_PIT"):
            raise ValueError("Unknown series status: " + name)
        series[name] = {
            "status": status, "latest_observation": last,
            "age_days": (cutoff - observed).days if observed else None,
            "observation_count": source.get("observation_count", 0),
            "publisher_original_pit_certified": source.get("publisher_original_pit_certified") is True,
            "observation_value": None,  # manifest does not contain numeric observations
            "release_date": None, "vintage_date": None,
        }
    if previous is not None:
        prior_day = date.fromisoformat(previous["as_of"])
        if prior_day >= cutoff:
            raise ValueError("Previous snapshot must predate this report")
    changes = {}
    for name, current in series.items():
        prior = (previous or {}).get("series", {}).get(name)
        changes[name] = {
            "status_changed": prior is not None and prior.get("status") != current["status"],
            "new_observation_date": prior is not None and prior.get("latest_observation") != current["latest_observation"],
            "previous_snapshot_available": prior is not None,
            "numeric_change": None,
            "reason": "NO_NUMERIC_OBSERVATIONS_IN_SOURCE_MANIFEST",
        }
    return {
        "schema_version": 1, "report_type": "V3_WEEKLY_ECONOMIC_EVIDENCE",
        "as_of": as_of, "frequency": "WEEKLY",
        "status": "DESCRIPTIVE_SOURCE_COVERAGE_ONLY",
        "publication": "BLOCKED", "predictive_model": "NOT_VALIDATED",
        "validated_cycle_stage": None, "crash_probability": None,
        "series": series, "week_over_week": changes,
        "source_coverage": {"defined": len(series),
                            "available": sum(x["status"] == "STAGED_REVISED_NOT_PIT" for x in series.values()),
                            "missing_or_invalid": sum(x["status"] != "STAGED_REVISED_NOT_PIT" for x in series.values())},
        "limitations": [
            "Source manifest does not contain observation values or publisher release dates",
            "No week-over-week numeric movement can be calculated from this evidence alone",
            "Source-reported revised observations are not original point-in-time vintages",
            "Missing or invalid sources remain unavailable, never zero-filled",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", default="audit-output/dashboard/source_refresh_manifest.json")
    p.add_argument("--as-of", required=True)
    p.add_argument("--previous")
    p.add_argument("--output", default="audit-output/v3_weekly_snapshot.json")
    a = p.parse_args()
    manifest = json.loads(Path(a.refresh).read_text())
    previous = json.loads(Path(a.previous).read_text()) if a.previous else None
    result = build_weekly_snapshot(manifest, a.as_of, previous)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "source_coverage": result["source_coverage"]}))

if __name__ == "__main__":
    main()
