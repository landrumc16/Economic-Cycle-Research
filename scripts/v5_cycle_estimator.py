"""Transparent, retrospective cycle-state heuristic (not a validated forecast).

Only current-row observations are used. This does not reconstruct historical
release-time information and must not be presented as an official NBER phase.
"""
import argparse
import json
from pathlib import Path

REQUIRED = ("unemployment_change_3m_pp", "industrial_production_growth_12m_log_pct",
            "consumer_credit_growth_12m_log_pct", "business_credit_growth_12m_log_pct")


def classify(row):
    missing = [key for key in REQUIRED if not isinstance(row.get(key), (int, float))]
    if missing:
        return {"phase": "UNCERTAIN", "confidence": "INSUFFICIENT_DATA",
                "supporting_signals": [], "conflicting_signals": [],
                "missing": missing}
    labor = row["unemployment_change_3m_pp"]
    production = row["industrial_production_growth_12m_log_pct"]
    credit = (row["consumer_credit_growth_12m_log_pct"] > 0 and
              row["business_credit_growth_12m_log_pct"] > 0)
    if labor > 0 and production < 0:
        phase = "CONTRACTION"
    elif labor <= 0 and production >= 0 and credit:
        phase = "EXPANSION"
    elif labor <= 0 and production >= 0:
        phase = "RECOVERY"
    elif labor > 0 and production >= 0:
        phase = "LATE_CYCLE"
    else:
        phase = "UNCERTAIN"
    signals = {"labor_softening": labor > 0, "production_contracting": production < 0,
               "broad_credit_expansion": credit}
    return {"phase": phase, "confidence": "UNVALIDATED_HEURISTIC",
            "supporting_signals": [k for k, v in signals.items() if v],
            "conflicting_signals": [k for k, v in signals.items() if not v],
            "missing": []}


def build(timeline, as_of=None):
    if timeline.get("status") != "RETROSPECTIVE_DESCRIPTIVE_ONLY":
        raise ValueError("Unexpected timeline status")
    rows = [r for r in timeline["timeline"] if as_of is None or r["month"] <= as_of[:7]]
    if not rows:
        raise ValueError("No historical observations through as-of month")
    estimates = [{"month": r["month"], **classify(r)} for r in rows]
    return {"status": "HISTORICAL_RESEARCH_ONLY", "as_of_month": estimates[-1]["month"],
            "point_in_time_certified": False, "model": "directional_v0_unvalidated",
            "latest": estimates[-1], "months": len(estimates), "timeline": estimates,
            "limitations": ["Unvalidated heuristic; not an official business-cycle phase",
                            "Current-vintage revised data; not release-time point-in-time",
                            "No predictive probability or calibrated confidence"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("timeline")
    parser.add_argument("--as-of")
    parser.add_argument("--output", default="audit-output/v5_cycle_estimates.json")
    args = parser.parse_args()
    report = build(json.loads(Path(args.timeline).read_text()), args.as_of)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "latest": report["latest"]}))


if __name__ == "__main__":
    main()
