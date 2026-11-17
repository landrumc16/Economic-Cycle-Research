"""V6.3 M2: replay the interpretation rubric over history and score it honestly.

Signals use only observations dated before each replay month (one-month release
lag emulation). Outcomes are evaluated afterwards with later observations and
NBER business-cycle dates, which is legitimate for scoring, never for signals.

IMPORTANT: observations are current-vintage revised FRED data, not archived
point-in-time releases. Results are retrospective and descriptive. Months
overlap and are not independent episodes. No probability or predictive skill is
claimed. The 2020 pandemic recession is reported separately.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

try:
    from .v63_interpretation import derive_metrics, interpret, _shift
except ImportError:
    from v63_interpretation import derive_metrics, interpret, _shift

SERIES = ("INDPRO", "UNRATE", "CPIAUCSL")
# NBER-dated peaks and troughs (public chronology; announced with long delays).
RECESSIONS = (
    ("1980-01", "1980-07", False), ("1981-07", "1982-11", False),
    ("1990-07", "1991-03", False), ("2001-03", "2001-11", False),
    ("2007-12", "2009-06", False), ("2020-02", "2020-04", True),
)
HORIZON = 6          # Months ahead for subsequent-development checks.
ALARM_WINDOW = 12    # A warning without a recession start or labor rise within this is a false alarm.
LABOR_RISE = 0.5     # Subsequent unemployment rise counted as observed deterioration.
WARNING = "Deteriorating"
# Directional scoring uses two DIFFERENT outcome tests. They overlap (a month
# can pass both), so shares are comparable only with their own base rate.
CAUTIOUS = ("Weakening", "Softening")
CONSTRUCTIVE = ("Steady", "Firming", "Strengthening")
OUTCOME_TESTS = {
    "cautious": ("Unemployment rose 0.2 points or more, or 12-month production growth fell "
                 "1 point or more, within the next six months"),
    "constructive": "Unemployment did not rise 0.2 points or more within the next six months",
}
INFORMATIVE_LIFT_PP = 5  # Lift below this is labelled "not informative".
# Months whose signal or six-month outcome window touches the pandemic shock.
PANDEMIC_WINDOW = ("2019-08", "2021-06")


def load(root: Path, name: str) -> dict:
    path = root / "data/industry_observations" / f"{name}_monthly.csv"
    with path.open(newline="") as handle:
        return {row["date"][:7]: float(row["value"]) for row in csv.DictReader(handle)}


def _growth(values, month, months=12):
    import math
    a, b = values.get(month), values.get(_shift(month, months))
    return round(100 * math.log(a / b), 4) if a and b and a > 0 and b > 0 else None


def assessment_at(data: dict, month: str) -> dict | None:
    """Assessment for replay month `month` using only observations through month-1."""
    cutoff = _shift(month, 1)
    visible = {name: {m: v for m, v in values.items() if m <= cutoff} for name, values in data.items()}
    if any(cutoff not in visible[name] for name in SERIES):
        return None
    u, u3 = visible["UNRATE"].get(cutoff), visible["UNRATE"].get(_shift(cutoff, 3))
    result = {
        "stale": False, "assessment_date": month + "-20",
        "industrial_production_growth_12m_log_pct": _growth(visible["INDPRO"], cutoff),
        "cpi_inflation_12m_log_pct": _growth(visible["CPIAUCSL"], cutoff),
        "unemployment_change_3m_pp": round(u - u3, 4) if u3 is not None else None,
        "unemployment_rate_pct": u,
        "sources": {name: {"latest_used_month": cutoff,
                           "source_url": "https://fred.stlouisfed.org/series/" + name}
                    for name in SERIES},
    }
    result.update(derive_metrics(visible["INDPRO"], visible["UNRATE"], visible["CPIAUCSL"]))
    return result


def _in_recession(month):
    return next((r for r in RECESSIONS if r[0] <= month <= r[1]), None)


def _episodes(months):
    """Group consecutive months into runs."""
    runs = []
    for month in months:
        if runs and _shift(month, 1) == runs[-1][-1]:
            runs[-1].append(month)
        else:
            runs.append([month])
    return runs


def replay(data: dict, start: str | None = None, end: str | None = None) -> dict:
    common = sorted(set.intersection(*(set(data[name]) for name in SERIES)))
    if not common:
        raise ValueError("No overlapping observations")
    last_observed = common[-1]
    rows = []
    for month in sorted({_shift(m, -1) for m in common}):
        if (start and month < start) or (end and month > end):
            continue
        a = assessment_at(data, month)
        if a is None or any(a[k] is None for k in ("industrial_production_growth_12m_log_pct",
                                                   "cpi_inflation_12m_log_pct",
                                                   "unemployment_change_3m_pp")):
            continue
        view = interpret(a, "PASS", date.fromisoformat(a["assessment_date"]))
        if view["condition"] == "Insufficient evidence":
            continue
        signal = _shift(month, 1)
        future = [data["UNRATE"].get(_shift(signal, -k)) for k in range(1, HORIZON + 1)]
        evaluable = all(v is not None for v in future) and _shift(signal, -HORIZON) <= last_observed
        rows.append({
            "month": month, "condition": view["condition"], "direction": view["direction"],
            "evidence_confidence": view["evidence_confidence"],
            "unemployment_rise_next_6m_pp": (round(max(future) - data["UNRATE"][signal], 2)
                                             if evaluable else None),
            "ip_growth_change_next_6m_pp": (
                round(_growth(data["INDPRO"], _shift(signal, -HORIZON)) -
                      a["industrial_production_growth_12m_log_pct"], 2)
                if evaluable and _growth(data["INDPRO"], _shift(signal, -HORIZON)) is not None else None),
            "in_recession": bool(_in_recession(month)),
        })
    if not rows:
        raise ValueError("No replayable months")
    return score(rows, last_observed)


def score(rows: list, last_observed: str) -> dict:
    general = [r for r in rows if not PANDEMIC_WINDOW[0] <= r["month"] <= PANDEMIC_WINDOW[1]]
    counts = {}
    for r in rows:
        counts[r["condition"]] = counts.get(r["condition"], 0) + 1

    # False alarms: warning episodes with no recession start and no labor rise soon after.
    warnings = [r["month"] for r in rows if r["condition"] == WARNING]
    by_month = {r["month"]: r for r in rows}
    false_alarms, supported = [], []
    for run in _episodes(warnings):
        first = run[0]
        if _shift(first, -ALARM_WINDOW) > last_observed:
            continue  # Too recent to judge.
        recession = (_in_recession(first) or next(
            (rec for rec in RECESSIONS if first <= rec[0] <= _shift(first, -ALARM_WINDOW)), None))
        rise = any((by_month[m]["unemployment_rise_next_6m_pp"] or 0) >= LABOR_RISE for m in run)
        entry = {"first_month": first, "last_month": run[-1], "months": len(run)}
        (supported if recession or rise else false_alarms).append(entry)

    # Missed deterioration and timing for each NBER recession inside the replay window.
    recessions = []
    first_month, last_month = rows[0]["month"], rows[-1]["month"]
    for peak, trough, pandemic in RECESSIONS:
        if _shift(peak, 12) < first_month or peak > last_month:
            continue
        window = [r for r in rows if _shift(peak, 12) <= r["month"] <= trough]
        hit = next((r["month"] for r in window if r["condition"] == WARNING), None)
        lead = None
        if hit:
            lead = (int(peak[:4]) * 12 + int(peak[5:])) - (int(hit[:4]) * 12 + int(hit[5:]))
        recessions.append({
            "peak": peak, "trough": trough, "pandemic_shock": pandemic,
            "first_warning": hit,
            "warning_months_before_peak": lead,
            "outcome": ("missed" if hit is None else
                        "early warning" if lead > 0 else "confirmation after peak"),
        })
    general_recessions = [r for r in recessions if not r["pandemic_shock"]]
    not_evaluable = [peak for peak, _trough, _p in RECESSIONS
                     if _shift(peak, 12) < first_month and peak <= last_month]

    # Directional agreement with subsequent observed growth/labor developments.
    def worse(r):
        return r["unemployment_rise_next_6m_pp"] >= 0.2 or r["ip_growth_change_next_6m_pp"] <= -1.0

    def calm(r):
        return r["unemployment_rise_next_6m_pp"] < 0.2

    # Base rates over ALL evaluable months: what each test scores with no signal.
    evaluable = [r for r in general if r["unemployment_rise_next_6m_pp"] is not None
                 and r["ip_growth_change_next_6m_pp"] is not None]
    base = {"cautious": round(sum(map(worse, evaluable)) / len(evaluable), 3) if evaluable else None,
            "constructive": round(sum(map(calm, evaluable)) / len(evaluable), 3) if evaluable else None}
    base_rates = {"evaluable_months": len(evaluable),
                  "deterioration_share": base["cautious"],
                  "no_labor_deterioration_share": base["constructive"]}
    agreement = {}
    for label in CAUTIOUS + CONSTRUCTIVE:
        group = "cautious" if label in CAUTIOUS else "constructive"
        test = worse if group == "cautious" else calm
        subset = [test(r) for r in evaluable if r["direction"] == label]
        share = round(sum(subset) / len(subset), 3) if subset else None
        lift = (round(100 * (share - base[group]), 1)
                if share is not None and base[group] is not None else None)
        agreement[label] = {"months": len(subset), "agreed": sum(subset), "share": share,
                            "outcome_test": group, "base_rate": base[group], "lift_pp": lift,
                            "informative": lift is not None and lift >= INFORMATIVE_LIFT_PP}

    changes = []
    for prev, cur in zip(rows, rows[1:]):
        if prev["condition"] != cur["condition"] and _shift(cur["month"], 1) == prev["month"]:
            contradicted = (cur["condition"] == "Expanding"
                            and (cur["unemployment_rise_next_6m_pp"] or 0) >= LABOR_RISE)
            changes.append({"month": cur["month"], "from": prev["condition"], "to": cur["condition"],
                            "contradicted_by_subsequent_labor_rise": contradicted})
    return {
        "status": "RETROSPECTIVE_REPLAY_NOT_POINT_IN_TIME",
        "rubric_version": interpret({}, "PASS", date(2000, 1, 1))["rubric_version"],
        "first_month": first_month, "last_month": last_month,
        "months_replayed": len(rows), "condition_counts": counts,
        "warning_condition": WARNING,
        "warning_episodes": len(supported) + len(false_alarms),
        "false_alarm_episodes": false_alarms,
        "supported_warning_episodes": supported,
        "recessions": recessions,
        "recessions_missed": sum(r["outcome"] == "missed" for r in general_recessions),
        "recessions_evaluated_excluding_pandemic": len(general_recessions),
        "directional_agreement_excluding_pandemic": agreement,
        "directional_base_rates_excluding_pandemic": base_rates,
        "directional_outcome_tests": OUTCOME_TESTS,
        "directional_informative_lift_pp": INFORMATIVE_LIFT_PP,
        "recessions_not_evaluable": not_evaluable,
        "condition_changes": changes[-24:],
        "condition_changes_total": len(changes),
        "predictive_skill_certified": False,
        "probabilities_published": False,
        "limitations": [
            "Current-vintage revised data, not archived real-time releases; early readings were often revised",
            "One-month release lag is emulated; actual publication dates are not certified",
            "Overlapping months are not independent observations; shares are descriptive, not accuracy rates",
            "Few recessions in the sample; timing results are anecdotal, not statistically validated",
            "NBER dates are announced months after the fact and are used only to score, never to signal",
            "The 2020 pandemic recession is a one-off shock reported separately",
            "Recessions whose prior 12 months precede the data coverage are not evaluated",
            "Months whose 12-month change needs an unpublished year-earlier observation are skipped",
            "Cautious and constructive direction calls use different, overlapping outcome tests; "
            "compare each share only with its own base rate, not with each other",
            "Direction scoring uses only months with a direction call; Unconfirmed months are excluded",
        ],
    }


def markdown(card: dict) -> str:
    lines = ["# V6.3 historical replay scorecard", "",
             f"Status: **{card['status']}** — retrospective, not a forecast-accuracy claim.",
             f"Months replayed: {card['months_replayed']} ({card['first_month']} to {card['last_month']})", "",
             "## Recession timing (NBER peaks)", ""]
    for r in card["recessions"]:
        label = " (pandemic shock, reported separately)" if r["pandemic_shock"] else ""
        timing = ("no warning" if r["first_warning"] is None else
                  f"first warning {r['first_warning']} ({r['warning_months_before_peak']:+d} month{'' if abs(r['warning_months_before_peak']) == 1 else 's'} vs peak)")
        shown = {"early warning": "flagged before the peak (one case; not proof of predictive ability)",
                 "confirmation after peak": "confirmed after the peak"}.get(r["outcome"], r["outcome"])
        lines.append(f"- Peak {r['peak']}{label}: {shown} — {timing}")
    lines += ["", f"Warning episodes: {card['warning_episodes']}; false alarms: {len(card['false_alarm_episodes'])}"]
    lines.extend(f"- False alarm {e['first_month']} to {e['last_month']} ({e['months']} month{'' if e['months'] == 1 else 's'})"
                 for e in card["false_alarm_episodes"])
    if card.get("recessions_not_evaluable"):
        lines.append("- Not evaluable (coverage starts too late): " + ", ".join(card["recessions_not_evaluable"]))
    lines += ["", "## Directional agreement with the next six months (excluding 2020)", "",
              "Two different outcome tests are used; compare each share only with its own base rate.", ""]
    tests = card.get("directional_outcome_tests", OUTCOME_TESTS)
    lines += [f"- Cautious calls (Weakening, Softening) agree if: {tests['cautious']}",
              f"- Constructive calls (Steady, Firming, Strengthening) agree if: {tests['constructive']}", "",
              "| Direction | Outcome test | Agreed | Base rate | Lift |", "|---|---|---|---|---|"]
    for label, item in card["directional_agreement_excluding_pandemic"].items():
        if item["months"]:
            flag = "" if item.get("informative") else " (not informative)"
            lines.append(f"| {label} | {item['outcome_test']} | {item['agreed']} / {item['months']} | "
                         f"{item['base_rate']:.0%} | {item['lift_pp']:+.1f} pt{flag} |")
    lines += ["", "## Limitations", ""] + ["- " + x for x in card["limitations"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("audit-output/v63_historical_scorecard.json"))
    parser.add_argument("--start", default="1980-01")
    args = parser.parse_args()
    data = {name: load(args.root, name) for name in SERIES}
    card = replay(data, start=args.start)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(card, indent=2) + "\n")
    args.output.with_suffix(".md").write_text(markdown(card))
    print(markdown(card))


if __name__ == "__main__":
    main()
