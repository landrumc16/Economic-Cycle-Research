"""Retrospective historical warning-rule usability study; NOT a point-in-time backtest."""
import argparse
import json
from pathlib import Path


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def scorecard(snapshot, leads, horizon_months=12):
    if horizon_months < 1:
        raise ValueError("horizon_months must be positive")
    monthly = snapshot["noncrash"]["rows"][1:]
    pathways = snapshot["pathways"]["rows"][1:]
    lead_rows = leads["rows"]
    events = [str(r[3])[:7] for r in pathways if len(r) > 3 and str(r[3]).startswith(("19", "20"))]
    months = [str(r[0]) for r in monthly]
    if len(months) != len(set(months)):
        raise ValueError("Duplicate months")
    event_indices = {m: i for i, m in enumerate(months)}
    evaluations = []
    for row in monthly:
        month = str(row[0])
        curve, credit = number(row[2]), number(row[3])
        if curve is None or credit is None:
            signal = "INSUFFICIENT_DATA"
        else:
            signal = "ELEVATED" if curve < 0 or credit >= 2.5 else "NOT_ELEVATED"
        idx = event_indices[month]
        # Exclude current month; outcome is a listed drawdown crossing within the forward horizon.
        future = [e for e in events if e in event_indices and idx < event_indices[e] <= idx + horizon_months]
        outcome = "EVENT_WITHIN_HORIZON" if future else "NO_LISTED_EVENT_WITHIN_HORIZON"
        # Last horizon months have incomplete future coverage: never score them as negatives.
        mature = idx + horizon_months < len(months)
        evaluations.append({"month": month, "curve_pp": curve, "credit_pp": credit,
                            "signal": signal, "retrospective_listed_peak_outcome": outcome if mature else "UNMATURED",
                            "retrospective_drawdown_crossing_outcome": outcome if mature else "UNMATURED",
                            "future_coverage_complete": False,
                            "point_in_time_eligible": False})
    mature_rows = [r for r in evaluations if r["retrospective_listed_peak_outcome"] != "UNMATURED"
                   and r["signal"] != "INSUFFICIENT_DATA"]
    flagged = [r for r in mature_rows if r["signal"] == "ELEVATED"]
    flagged_with_listed_peak = sum(r["retrospective_listed_peak_outcome"] == "EVENT_WITHIN_HORIZON" for r in flagged)
    unflagged_with_listed_peak = sum(r["retrospective_listed_peak_outcome"] == "EVENT_WITHIN_HORIZON"
                                     for r in mature_rows if r["signal"] == "NOT_ELEVATED")
    return {
        "report_type": "HISTORICAL_USABILITY_RETROSPECTIVE_SCORECARD",
        "method": "Simple inverted yield curve OR credit spread >=2.5 pp, using revised workbook values",
        "outcome": "Listed first 20% market-drawdown crossing in following months; selected retrospective events, not complete independently verified outcomes",
        "horizon_months": horizon_months,
        "monthly_observations": len(evaluations),
        "mature_observations": len(mature_rows),
        "flagged_months": len(flagged),
        "flagged_followed_by_listed_peak": flagged_with_listed_peak,
        "unflagged_followed_by_listed_peak": unflagged_with_listed_peak,
        "listed_peak_count": len(events),
        "listed_drawdown_crossing_count": len(events),
        "flagged_followed_by_drawdown_crossing": flagged_with_listed_peak,
        "unflagged_followed_by_drawdown_crossing": unflagged_with_listed_peak,
        "event_target": "FIRST_20_PERCENT_DRAWDOWN_CROSSING",
        "lead_window_rows": len(lead_rows),
        "point_in_time_certified": False,
        "negative_outcome_coverage_certified": False,
        "predictive_publication": "BLOCKED",
        "monthly_assessments": evaluations,
        "evaluation_caveat": "Selected drawdown crossings only; apparent non-events are not verified negative outcomes",
        "limitations": [
            "Retrospective, revised observations; no verified contemporaneous release dates",
            "Event list contains selected historical drawdown crossings, not complete independent outcomes",
            "No-listed-event months cannot be interpreted as verified negatives or used to claim false-alarm rate",
            "Monthly observations are correlated; this is not an event-independent holdout",
            "Signals in crossing month are excluded from forward outcomes",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="data/workbook_historical_research_snapshot_2026-10-30.json")
    parser.add_argument("--lead-windows", default="data/v2_canonical_lead_window_summary_2026-10-31.json")
    parser.add_argument("--output", default="audit-output/historical_usability_scorecard.json")
    parser.add_argument("--horizon-months", type=int, default=12)
    args = parser.parse_args()
    result = scorecard(json.loads(Path(args.snapshot).read_text()),
                       json.loads(Path(args.lead_windows).read_text()), args.horizon_months)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "monthly_assessments"}))


if __name__ == "__main__":
    main()
