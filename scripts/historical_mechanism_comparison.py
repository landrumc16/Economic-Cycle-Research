"""Compare simple retrospective signals against selected drawdown crossings.

Descriptive research only: selected events, revised observations, no verified negatives.
"""
import argparse
import json
from pathlib import Path


def parse_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def compare(snapshot, horizons=(3, 6, 12, 24)):
    rows = snapshot["noncrash"]["rows"][1:]
    paths = snapshot["pathways"]["rows"][1:]
    months = [str(r[0]) for r in rows]
    if len(months) != len(set(months)):
        raise ValueError("Duplicate monthly observations")
    positions = {month: index for index, month in enumerate(months)}
    crossings = sorted({str(r[3])[:7] for r in paths if len(r) > 3 and str(r[3])[:7] in positions})
    rules = {
        "yield_curve_inverted": lambda curve, credit, stress: curve is not None and curve < 0,
        "credit_spread_2_5pp": lambda curve, credit, stress: credit is not None and credit >= 2.5,
        "current_stress_flag": lambda curve, credit, stress: stress == "YES",
        "yield_curve_or_credit": lambda curve, credit, stress: (
            (curve is not None and curve < 0) or (credit is not None and credit >= 2.5)),
    }
    results = []
    for horizon in horizons:
        if horizon < 1:
            raise ValueError("Invalid horizon")
        for name, rule in rules.items():
            elevated = 0
            non_elevated = 0
            elevated_preceding = 0
            non_elevated_preceding = 0
            missing = 0
            for index, row in enumerate(rows):
                if index + horizon >= len(rows):
                    continue
                curve, credit = parse_float(row[2]), parse_float(row[3])
                stress = str(row[4]).strip().upper() if len(row) > 4 else ""
                if (name == "yield_curve_inverted" and curve is None
                    or name == "credit_spread_2_5pp" and credit is None
                    or name == "current_stress_flag" and stress not in ("YES", "NO")
                    or name == "yield_curve_or_credit" and (curve is None or credit is None)):
                    missing += 1
                    continue
                outcome = any(index < positions[event] <= index + horizon for event in crossings)
                if rule(curve, credit, stress):
                    elevated += 1
                    elevated_preceding += int(outcome)
                else:
                    non_elevated += 1
                    non_elevated_preceding += int(outcome)
            results.append({
                "rule": name, "horizon_months": horizon,
                "elevated_months": elevated,
                "non_elevated_months": non_elevated,
                "elevated_preceding_listed_crossing": elevated_preceding,
                "non_elevated_preceding_listed_crossing": non_elevated_preceding,
                "missing_months": missing,
                "elevated_followed_by_listed_crossing_share": (
                    round(elevated_preceding / elevated, 4) if elevated else None),
                "non_elevated_followed_by_listed_crossing_share": (
                    round(non_elevated_preceding / non_elevated, 4) if non_elevated else None),
            })
    return {
        "report_type": "HISTORICAL_MECHANISM_RETROSPECTIVE_COMPARISON",
        "source": snapshot.get("source_workbook"),
        "selected_drawdown_crossing_months": crossings,
        "independent_outcome_coverage": False,
        "point_in_time_certified": False,
        "predictive_publication": "BLOCKED",
        "results": results,
        "limitations": [
            "Selected drawdown events, not exhaustive outcome labels",
            "Revised historical observations, not publisher-original point-in-time vintages",
            "Repeated monthly origins are correlated, not independent trials",
            "No-listed-event months are not independently verified non-events",
            "Rules are simple descriptive baselines, not calibrated forecasts",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="data/workbook_historical_research_snapshot_2026-10-30.json")
    parser.add_argument("--output", default="audit-output/historical_mechanism_comparison.json")
    args = parser.parse_args()
    result = compare(json.loads(Path(args.snapshot).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"rules": len(result["results"]), "crossings": len(result["selected_drawdown_crossing_months"]),
                      "point_in_time_certified": False}))


if __name__ == "__main__":
    main()
