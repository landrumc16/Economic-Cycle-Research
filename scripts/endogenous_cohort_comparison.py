"""Selected drawdown cohort sensitivity; descriptive only."""
import json
from pathlib import Path

def run(snapshot, registry, horizon=12):
    rows = snapshot["noncrash"]["rows"][1:]
    months = [str(row[0]) for row in rows]
    if len(set(months)) != len(months):
        raise ValueError("Duplicate month")
    pos = {month: i for i, month in enumerate(months)}
    result = []
    for cohort in ("endogenous", "endogenous_plus_mixed", "all"):
        events = {
            e["listed_crossing_month"] for e in registry["events"]
            if cohort == "all" or e["provisional_cohort"] == "endogenous"
            or (cohort == "endogenous_plus_mixed" and e["provisional_cohort"] == "mixed_uncertain")
        }
        counts = dict(flagged=0, unflagged=0, flagged_preceding=0,
                      unflagged_preceding=0, missing=0)
        for i, row in enumerate(rows):
            if i + horizon >= len(rows):
                continue
            try:
                curve, credit = float(row[2]), float(row[3])
            except (ValueError, TypeError):
                counts["missing"] += 1
                continue
            flagged = curve < 0 or credit >= 2.5
            hit = any(event in pos and i < pos[event] <= i + horizon for event in events)
            counts["flagged" if flagged else "unflagged"] += 1
            if hit:
                counts["flagged_preceding" if flagged else "unflagged_preceding"] += 1
        result.append({"cohort": cohort, "selected_events": len(events), **counts})
    return {"status": "RETROSPECTIVE_NOT_VALIDATED",
            "point_in_time_certified": False,
            "negative_outcomes_certified": False,
            "results": result}

def main():
    snapshot = json.loads(Path("data/workbook_historical_research_snapshot_2026-10-30.json").read_text())
    registry = json.loads(Path("data/endogenous_event_classification_v1.json").read_text())
    report = run(snapshot, registry)
    path = Path("audit-output/endogenous_cohort_comparison.json")
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
