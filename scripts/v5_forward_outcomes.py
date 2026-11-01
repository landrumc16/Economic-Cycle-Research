"""V5 historical forward-outcome research, not a deployed forecast.

For each observation month, report whether an NBER recession occurs in the
following 3, 6, or 12 months. Exclude the current month. Historical event
frequencies are descriptive and must not be shown as predictive probabilities.
"""
import argparse
import json
from pathlib import Path

try:
    from scripts.v5_cycle_evaluation import reference_recession
except ModuleNotFoundError:
    from v5_cycle_evaluation import reference_recession

HORIZONS = (3, 6, 12)
REFERENCE_END = "2020-12"


def shift(month, n):
    year, m = map(int, month.split("-"))
    index = year * 12 + m - 1 + n
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def evaluate(estimates):
    if estimates.get("status") != "HISTORICAL_RESEARCH_ONLY":
        raise ValueError("Expected historical cycle estimates")
    rows = estimates["timeline"]
    if not rows:
        raise ValueError("Empty cycle timeline")
    months = {r["month"] for r in rows}
    output = {}
    for horizon in HORIZONS:
        by_phase = {}
        total = positives = 0
        for row in rows:
            month = row["month"]
            if not ("1990-01" <= month <= REFERENCE_END):
                continue
            future = [shift(month, k) for k in range(1, horizon + 1)]
            if future[-1] > REFERENCE_END or not all(m in months for m in future):
                continue
            if row["phase"] == "UNCERTAIN":
                continue
            event = any(reference_recession(m) for m in future)
            counts = by_phase.setdefault(row["phase"], {"months": 0, "events": 0})
            counts["months"] += 1
            counts["events"] += int(event)
            total += 1
            positives += int(event)
        output[str(horizon)] = {
            "eligible_months": total, "event_months": positives,
            "historical_event_frequency": round(positives / total, 4) if total else None,
            "by_estimated_phase": {
                phase: {**counts, "historical_event_frequency":
                        round(counts["events"] / counts["months"], 4)}
                for phase, counts in sorted(by_phase.items())
            },
        }
    return {
        "status": "RETROSPECTIVE_FORWARD_OUTCOMES_ONLY",
        "outcome": "At least one NBER recession month in the next N calendar months, excluding observation month",
        "horizons_months": list(HORIZONS),
        "reference_window_end": REFERENCE_END,
        "results": output,
        "probabilities_approved": False,
        "point_in_time_certified": False,
        "limitations": [
            "Historical event frequencies are not calibrated forward probabilities",
            "Overlapping windows and repeated recession months are not independent events",
            "Current-vintage revised observations and ex-post NBER dates",
            "Reference window deliberately stops at 2020-12; no future outcomes inferred",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("estimates")
    parser.add_argument("--output", default="audit-output/v5_forward_outcomes.json")
    args = parser.parse_args()
    report = evaluate(json.loads(Path(args.estimates).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "horizons": report["horizons_months"]}))


if __name__ == "__main__":
    main()
