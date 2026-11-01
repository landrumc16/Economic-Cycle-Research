"""Maintain versioned weekly assessment history and derive prior-week comparisons.

The workflow passes a restored archive from the prior successful run.
"""
import argparse
import json
from pathlib import Path


def update(history, current):
    if current["status"] != "RESEARCH_SNAPSHOT_NOT_FORECAST":
        raise ValueError("Invalid current assessment")
    entries = {item["assessment_date"]: item for item in history}
    entries[current["assessment_date"]] = current
    return [entries[day] for day in sorted(entries)]


def previous(history, day):
    older = [item for item in history if item["assessment_date"] < day]
    return max(older, key=lambda item: item["assessment_date"]) if older else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("assessment")
    parser.add_argument("--history", default="audit-output/weekly_assessment_history.json")
    parser.add_argument("--previous-output", default="audit-output/previous_weekly_assessment.json")
    args = parser.parse_args()
    current = json.loads(Path(args.assessment).read_text())
    path = Path(args.history)
    history = json.loads(path.read_text()) if path.exists() else []
    if not isinstance(history, list):
        raise ValueError("History must be a list")
    prior = previous(history, current["assessment_date"])
    if prior is not None:
        output = Path(args.previous_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(prior, indent=2) + "\n")
    else:
        Path(args.previous_output).unlink(missing_ok=True)
    merged = update(history, current)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, indent=2) + "\n")
    print(json.dumps({"assessments": len(merged),
                      "previous_date": prior["assessment_date"] if prior else None}))


if __name__ == "__main__":
    main()
