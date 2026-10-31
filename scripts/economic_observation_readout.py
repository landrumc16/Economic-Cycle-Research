"""Construct an observation-level economic readout from source-gated inputs.

This module reports measurements only. It never assigns a cycle stage, crash
probability, or sector rank. Approved status is explicitly per-series.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

SERIES = {"UNRATE": ("monthly", "percent SA"), "CPIAUCSL": ("monthly", "SA index"),
          "GDPC1": ("quarterly", "billions chained dollars SAAR")}
REQUIRED_CHECKS = ("publisher_source_acquired", "independent_source_acquired",
                   "numeric_reconciliation_pass", "publisher_vintage_authenticated",
                   "release_timing_verified", "point_in_time_no_lookahead_pass",
                   "coverage_pass")

def _parse_observations(raw):
    if not isinstance(raw, dict):
        return {}
    valid = {}
    for day, value in raw.items():
        try:
            date = dt.date.fromisoformat(day)
            number = float(value)
            if not math.isfinite(number):
                continue
            valid[date.isoformat()] = number
        except (TypeError, ValueError, OverflowError):
            continue
    return valid

def build_readout(normalized, gate, approvals=None):
    approvals = approvals or {}
    report = {"publication": "BLOCKED", "cycle_stage": None,
              "crash_probability": None, "sector_rankings": None,
              "research_only": True, "observations": {}}
    for name, (frequency, unit) in SERIES.items():
        item = gate.get("series", {}).get(name, {})
        authenticated = (gate.get("all_evidence_pass") is True and
                         all(item.get(key) is True for key in REQUIRED_CHECKS) and
                         approvals.get(name) == "APPROVED")
        observations = _parse_observations(normalized.get(name))
        latest_date = max(observations) if observations else None
        report["observations"][name] = {
            "frequency": frequency, "unit": unit,
            "observation_date": latest_date,
            "value": observations[latest_date] if latest_date else None,
            "quality": ("APPROVED_SOURCE" if authenticated else
                        "REVISED_RESEARCH_ONLY" if latest_date else "MISSING"),
            "eligible_for_published_model": authenticated,
            "publisher_vintage_verified": item.get("publisher_vintage_authenticated") is True,
            "source_approval": approvals.get(name, "BLOCKED")
        }
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="audit-output/fred-api")
    p.add_argument("--gate", required=True)
    p.add_argument("--approvals")
    p.add_argument("--output", default="audit-output/economic_observation_readout.json")
    a = p.parse_args()
    gate = json.loads(Path(a.gate).read_text())
    approvals = json.loads(Path(a.approvals).read_text()) if a.approvals else {}
    normalized = {}
    for name in SERIES:
        file = Path(a.input) / f"{name}_normalized.json"
        if file.exists():
            normalized[name] = json.loads(file.read_text())
    result = build_readout(normalized, gate, approvals)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
