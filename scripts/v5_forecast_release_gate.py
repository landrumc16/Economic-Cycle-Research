"""Conservative V5 forecast release decision based on temporal benchmarks.

No numeric recession probability is approved without point-in-time vintage
validation, even when a retrospective model beats its base-rate benchmark.
"""
import argparse
import json
from pathlib import Path

HORIZONS = ("3", "6", "12")
MIN_EVALUATION_MONTHS = 60


def assess(report):
    if report.get("status") != "RETROSPECTIVE_OUT_OF_SAMPLE_DIAGNOSTIC_ONLY":
        raise ValueError("Expected V5 temporal benchmark")
    horizons = {}
    for horizon in HORIZONS:
        row = report["results"][horizon]
        n = row["evaluation_months"]
        base = row["baseline_brier"]
        phase = row["phase_frequency_brier"]
        sufficient = n >= MIN_EVALUATION_MONTHS and base is not None and phase is not None
        beats = bool(sufficient and phase < base)
        horizons[horizon] = {
            "evaluation_months": n,
            "baseline_brier": base,
            "phase_frequency_brier": phase,
            "retrospective_skill_vs_baseline": round(1 - phase / base, 4) if sufficient and base > 0 else None,
            "retrospective_benchmark_pass": beats,
            "numeric_forecast_approved": False,
            "reason": ("Retrospective improvement only; point-in-time validation required"
                       if beats else "Insufficient evidence of improvement over baseline"),
        }
    return {
        "status": "FORECAST_RELEASE_BLOCKED",
        "point_in_time_certified": False,
        "numeric_forecasts_approved": False,
        "horizons": horizons,
        "decision": "Publish historical research and diagnostics only",
        "limitations": [
            "Historical revisions can inflate apparent forecasting skill",
            "Ex-post recession chronology is not available at historical forecast dates",
            "Overlapping horizons make monthly test scores dependent",
            "Requires vintage-aware out-of-sample calibration before live probability release",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    parser.add_argument("--output", default="audit-output/v5_forecast_release_gate.json")
    args = parser.parse_args()
    result = assess(json.loads(Path(args.benchmark).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "horizons": {k: v["retrospective_benchmark_pass"] for k, v in result["horizons"].items()}}))


if __name__ == "__main__":
    main()
