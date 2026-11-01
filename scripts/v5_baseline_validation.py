"""Expanding-window baseline check for historical recession horizons.

A phase-frequency lookup is compared with the expanding historical base rate.
This is a diagnostic, NOT a deployable probability model: current-vintage
observations and ex-post NBER chronology make it retrospective research.
"""
import argparse
import json
from pathlib import Path

try:
    from scripts.v5_cycle_evaluation import reference_recession
    from scripts.v5_forward_outcomes import shift
except ModuleNotFoundError:
    from v5_cycle_evaluation import reference_recession
    from v5_forward_outcomes import shift

HORIZONS = (3, 6, 12)
REFERENCE_END = "2020-12"
MIN_TRAIN = 120
MIN_PHASE_TRAIN = 24


def brier(pairs):
    return round(sum((prediction - actual) ** 2 for prediction, actual in pairs) / len(pairs), 6) if pairs else None


def evaluate(estimates):
    if estimates.get("status") != "HISTORICAL_RESEARCH_ONLY":
        raise ValueError("Expected historical estimates")
    rows = sorted(estimates["timeline"], key=lambda row: row["month"])
    months = {r["month"] for r in rows}
    output = {}
    for horizon in HORIZONS:
        observations = []
        for row in rows:
            month = row["month"]
            future = [shift(month, k) for k in range(1, horizon + 1)]
            if not ("1990-01" <= month <= REFERENCE_END) or future[-1] > REFERENCE_END:
                continue
            if row["phase"] == "UNCERTAIN" or not all(m in months for m in future):
                continue
            observations.append((month, row["phase"], int(any(reference_recession(m) for m in future))))
        baseline_pairs, phase_pairs = [], []
        for month, phase, actual in observations:
            # A training label is eligible only once its entire future horizon
            # is complete before the test observation month.
            history = [(m, p, y) for m, p, y in observations if shift(m, horizon) < month]
            if len(history) < MIN_TRAIN:
                continue
            base_rate = sum(y for _, _, y in history) / len(history)
            phase_history = [y for _, p, y in history if p == phase]
            if len(phase_history) < MIN_PHASE_TRAIN:
                continue
            phase_rate = sum(phase_history) / len(phase_history)
            baseline_pairs.append((base_rate, actual))
            phase_pairs.append((phase_rate, actual))
        output[str(horizon)] = {
            "evaluation_months": len(phase_pairs),
            "baseline_brier": brier(baseline_pairs),
            "phase_frequency_brier": brier(phase_pairs),
            "phase_beats_baseline": (brier(phase_pairs) < brier(baseline_pairs)
                                     if phase_pairs else None),
        }
    return {
        "status": "RETROSPECTIVE_OUT_OF_SAMPLE_DIAGNOSTIC_ONLY",
        "results": output,
        "probabilities_approved": False,
        "point_in_time_certified": False,
        "training_rule": "Expanding prior observations; completed outcome windows strictly before test month",
        "limitations": [
            "Current-vintage revised indicators, not real-time vintages",
            "Ex-post recession dates, not contemporaneous reference labels",
            "Overlapping observations are dependent; month-level Brier scores are not independent episodes",
            "Phase frequency lookup is a diagnostic baseline, not a calibrated predictive model",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("estimates")
    parser.add_argument("--output", default="audit-output/v5_baseline_validation.json")
    args = parser.parse_args()
    result = evaluate(json.loads(Path(args.estimates).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "results": result["results"]}))


if __name__ == "__main__":
    main()
