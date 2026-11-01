"""Compare preliminary cycle classifications with historical recession reference months.

Retrospective diagnostic only: revised observations and ex-post reference dates
cannot establish point-in-time forecasting accuracy.
"""
import argparse
import json
from pathlib import Path

# NBER peak month is the last expansion month; trough is last recession month.
# Intervals here represent months following peaks through troughs.
REFERENCE_INTERVALS = (
    ("1990-08", "1991-03"),
    ("2001-04", "2001-11"),
    ("2008-01", "2009-06"),
    ("2020-03", "2020-04"),
)


def reference_recession(month):
    return any(start <= month <= end for start, end in REFERENCE_INTERVALS)


def evaluate(report):
    if report.get("status") != "HISTORICAL_RESEARCH_ONLY":
        raise ValueError("Expected historical estimates")
    rows = [r for r in report["timeline"] if "1990-01" <= r["month"] <= "2020-12"]
    if not rows:
        raise ValueError("No reference-period observations")
    counts = {"true_positive": 0, "false_positive": 0,
              "true_negative": 0, "false_negative": 0, "uncertain": 0}
    for row in rows:
        if row["phase"] == "UNCERTAIN":
            counts["uncertain"] += 1
            continue
        predicted = row["phase"] == "CONTRACTION"
        actual = reference_recession(row["month"])
        key = ("true_positive" if predicted and actual else
               "false_positive" if predicted else
               "false_negative" if actual else "true_negative")
        counts[key] += 1
    tp, fp, fn = (counts[k] for k in ("true_positive", "false_positive", "false_negative"))
    return {
        "status": "RETROSPECTIVE_DIAGNOSTIC_ONLY",
        "reference": "NBER business cycle peak/trough chronology",
        "reference_url": "https://www.nber.org/research/business-cycle-dating",
        "window": ["1990-01", "2020-12"],
        "observed_months": len(rows),
        "counts": counts,
        "precision": round(tp / (tp + fp), 4) if tp + fp else None,
        "recall": round(tp / (tp + fn), 4) if tp + fn else None,
        "point_in_time_certified": False,
        "limitations": [
            "Ex-post recession dates are not contemporaneous labels",
            "Current-vintage revised observations are not historical release vintages",
            "Monthly observations overlap and are not independent episodes",
            "No calibrated phase probabilities or forecasting claims",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("estimates")
    parser.add_argument("--output", default="audit-output/v5_cycle_evaluation.json")
    args = parser.parse_args()
    result = evaluate(json.loads(Path(args.estimates).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}))


if __name__ == "__main__":
    main()
