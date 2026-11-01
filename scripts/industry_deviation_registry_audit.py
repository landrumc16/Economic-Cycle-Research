"""Audit candidate industry episodes without imputing missing measurements."""
import json
from pathlib import Path

REQUIRED = ("id", "track", "industry", "start_month", "end_month",
            "baseline_series", "valuation_series", "fundamentals_series",
            "capital_flows_series", "leverage_series", "drawdown_outcome")

def audit(registry):
    episodes = registry["episodes"]
    ids = [e["id"] for e in episodes]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate episode IDs")
    missing = {}
    for e in episodes:
        absent = [field for field in REQUIRED if field not in e]
        if absent:
            raise ValueError("Missing schema fields for " + e["id"] + ": " + ", ".join(absent))
        if e["track"] not in ("emerging", "established"):
            raise ValueError("Unknown track")
        if e["end_month"] is not None and e["end_month"] < e["start_month"]:
            raise ValueError("Invalid period")
        missing[e["id"]] = [field for field in ("baseline_series", "valuation_series",
            "fundamentals_series", "capital_flows_series", "leverage_series")
            if e[field] is None]
    return {"status": "DATA_GAP_AUDIT_NOT_CRASH_PREDICTION",
            "episode_count": len(episodes),
            "tracks": {t: sum(e["track"] == t for e in episodes)
                       for t in ("emerging", "established")},
            "missing_measurements": missing,
            "validated_crash_outcomes": 0,
            "predictive_publication": "BLOCKED"}

def main():
    data = json.loads(Path("data/industry_deviation_episode_registry_v1.json").read_text())
    report = audit(data)
    target = Path("audit-output/industry_deviation_registry_audit.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
