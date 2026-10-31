"""Version 3 weekly evidence snapshot; descriptive only, no predictive inference."""
import argparse
import json
from datetime import date
import math
from pathlib import Path

def build_weekly_snapshot(refresh, as_of, previous=None, observations=None):
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
        raw = (observations or {}).get(name, {})
        value = None
        if status == "STAGED_REVISED_NOT_PIT" and observed is not None and isinstance(raw, dict):
            candidate = raw.get(last)
            if isinstance(candidate, (int, float)) and not isinstance(candidate, bool) and math.isfinite(candidate):
                value = candidate
        series[name] = {
            "status": status, "latest_observation": last,
            "age_days": (cutoff - observed).days if observed else None,
            "observation_count": source.get("observation_count", 0),
            "publisher_original_pit_certified": source.get("publisher_original_pit_certified") is True,
            "observation_value": value, "value_quality": "REVISED_NOT_PIT" if value is not None else "UNAVAILABLE",
            "release_date": None, "vintage_date": None,
        }
    if previous is not None:
        prior_day = date.fromisoformat(previous["as_of"])
        if prior_day >= cutoff:
            raise ValueError("Previous snapshot must predate this report")
    changes = {}
    for name, current in series.items():
        prior = (previous or {}).get("series", {}).get(name)
        old_value = prior.get("observation_value") if isinstance(prior, dict) else None
        new_value = current["observation_value"]
        comparable = (isinstance(old_value, (int, float)) and not isinstance(old_value, bool)
                      and isinstance(new_value, (int, float)) and not isinstance(new_value, bool)
                      and math.isfinite(old_value) and math.isfinite(new_value)
                      and prior.get("latest_observation") != current["latest_observation"])
        changes[name] = {
            "status_changed": prior is not None and prior.get("status") != current["status"],
            "new_observation_date": prior is not None and prior.get("latest_observation") != current["latest_observation"],
            "previous_snapshot_available": prior is not None,
            "numeric_change": round(new_value - old_value, 6) if comparable else None,
            "reason": "NEW_RELEASED_OBSERVATION_REVISED_NOT_PIT" if comparable else "NO_COMPARABLE_NEW_OBSERVATION",
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
            "Values are attached only when the normalized observation date exactly matches the source manifest; publisher release dates remain unavailable",
            "Numeric changes represent differences between newly available dated observations, not necessarily a seven-day economic movement",
            "Source-reported revised observations are not original point-in-time vintages",
            "Missing or invalid sources remain unavailable, never zero-filled",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", default="audit-output/dashboard/source_refresh_manifest.json")
    p.add_argument("--as-of", required=True)
    p.add_argument("--previous")
    p.add_argument("--observations", default="audit-output/fred-api")
    p.add_argument("--output", default="audit-output/v3_weekly_snapshot.json")
    a = p.parse_args()
    manifest = json.loads(Path(a.refresh).read_text())
    previous = json.loads(Path(a.previous).read_text()) if a.previous else None
    folder = Path(a.observations)
    observations = {}
    for name in manifest["series"]:
        path = folder / f"{name}_normalized.json"
        if path.exists():
            observations[name] = json.loads(path.read_text())
    result = build_weekly_snapshot(manifest, a.as_of, previous, observations)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "source_coverage": result["source_coverage"]}))

if __name__ == "__main__":
    main()
