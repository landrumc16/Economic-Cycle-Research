"""V6.3 economic interpretation rubric (M1).

One small, deterministic rubric shared by the monthly assessment, the public
homepage and the historical replay. It turns source-dated growth, employment and
inflation observations into:

* a current condition (Expanding / Slowing / Deteriorating / Mixed),
* a conditional near-term direction (never a probability or forecast),
* the observations that drive the view and the evidence against it,
* confidence in *evidence coverage* (not the likelihood of any event),
* explicit, quantitative reversal conditions, and
* what changed since the prior accepted monthly assessment.

Thresholds are deliberately simple, published and identical to the reversal
triggers, so a reader can check every conclusion by hand.
"""
from __future__ import annotations

import math
from datetime import date
from urllib.parse import urlparse

RUBRIC_VERSION = "v6.3-m1"
MAX_AGE_MONTHS = 2  # Same freshness window as the accepted monthly gate.

# Published thresholds (percent / percentage points).
GROWTH_BAND = 0.5          # |IP 12m log growth| below this is "flat".
MOMENTUM_BAND = 0.5        # Change in IP 12m growth over 3 months.
LABOR_DETERIORATING = 0.3  # 3m unemployment rise at/above this is deterioration.
LABOR_IMPROVING = -0.2     # 3m unemployment fall at/below this is improvement.
LABOR_RISE_FROM_LOW = 0.5  # 3m-average unemployment above prior 12m low (Sahm-style).
INFLATION_NEAR_GOAL = 2.5  # CPI 12m at/below: near the Fed's 2% goal range.
INFLATION_HIGH = 4.0       # CPI 12m above: high.
INFLATION_TREND_BAND = 0.3  # Change in CPI 12m rate over 3 months.

PILLARS = {
    "growth": ("INDPRO", "industrial_production_growth_12m_log_pct"),
    "employment": ("UNRATE", "unemployment_change_3m_pp"),
    "inflation": ("CPIAUCSL", "cpi_inflation_12m_log_pct"),
}
THRESHOLDS = {
    "growth_flat_band_pct": GROWTH_BAND,
    "growth_momentum_band_pp": MOMENTUM_BAND,
    "labor_deteriorating_3m_pp": LABOR_DETERIORATING,
    "labor_improving_3m_pp": LABOR_IMPROVING,
    "labor_rise_from_12m_low_pp": LABOR_RISE_FROM_LOW,
    "inflation_near_goal_pct": INFLATION_NEAR_GOAL,
    "inflation_high_pct": INFLATION_HIGH,
    "inflation_trend_band_pp": INFLATION_TREND_BAND,
    "max_observation_age_months": MAX_AGE_MONTHS,
}


# ---------------------------------------------------------------------------
# Metric derivation from monthly series (used by the assessment and replay).
# ---------------------------------------------------------------------------
def _shift(month: str, months: int) -> str:
    year, mon = int(month[:4]), int(month[5:7])
    index = year * 12 + (mon - 1) - months
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def _log_growth(values: dict, month: str, months: int = 12):
    current, prior = values.get(month), values.get(_shift(month, months))
    if current is None or prior is None or current <= 0 or prior <= 0:
        return None
    return round(100 * math.log(current / prior), 4)


def _avg3(values: dict, month: str):
    points = [values.get(_shift(month, k)) for k in range(3)]
    return None if any(p is None for p in points) else sum(points) / 3


def derive_metrics(indpro: dict, unrate: dict, cpi: dict) -> dict:
    """Momentum and labor-trend fields from {YYYY-MM: value} series.

    Each pillar uses its own latest month. Missing history yields None (never
    imputed). Callers must pass only observations available at the assessment
    date.
    """
    out = {}
    if indpro:
        month = max(indpro)
        now, earlier = _log_growth(indpro, month), _log_growth(indpro, _shift(month, 3))
        out["industrial_production_growth_12m_3m_ago_log_pct"] = earlier
        out["industrial_production_momentum_3m_pp"] = (
            round(now - earlier, 4) if now is not None and earlier is not None else None)
    if cpi:
        month = max(cpi)
        now, earlier = _log_growth(cpi, month), _log_growth(cpi, _shift(month, 3))
        out["cpi_inflation_12m_3m_ago_log_pct"] = earlier
        out["cpi_inflation_change_3m_pp"] = (
            round(now - earlier, 4) if now is not None and earlier is not None else None)
    if unrate:
        month = max(unrate)
        current = _avg3(unrate, month)
        prior = [_avg3(unrate, _shift(month, k)) for k in range(1, 13)]
        out["unemployment_3m_avg_rise_from_12m_low_pp"] = (
            round(current - min(prior), 4)
            if current is not None and all(p is not None for p in prior) else None)
    return out


# ---------------------------------------------------------------------------
# Rubric
# ---------------------------------------------------------------------------
def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _age(observed: str, as_of: date):
    try:
        day = date.fromisoformat(observed + "-01" if len(observed) == 7 else observed)
    except (TypeError, ValueError):
        return None
    if day > as_of:
        return None
    return (as_of.year - day.year) * 12 + as_of.month - day.month


def _verified_source(source: dict) -> bool:
    url = source.get("source_url")
    parsed = urlparse(url) if isinstance(url, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.hostname
                and parsed.hostname not in {"example.com", "example.org", "example.net"})


def pillar_status(assessment: dict, as_of: date) -> dict:
    """current / stale / missing for each pillar, with its observation month."""
    sources = assessment.get("sources") if isinstance(assessment.get("sources"), dict) else {}
    result = {}
    for pillar, (series, metric) in PILLARS.items():
        source = sources.get(series) if isinstance(sources.get(series), dict) else {}
        observed = source.get("latest_used_month")
        age = _age(observed, as_of) if isinstance(observed, str) else None
        if not _number(assessment.get(metric)) or age is None or not _verified_source(source):
            state = "missing"
        elif age > MAX_AGE_MONTHS:
            state = "stale"
        else:
            state = "current"
        result[pillar] = {"status": state, "series": series,
                          "observation_month": observed if age is not None else None,
                          "age_months": age}
    return result


def classify_growth(growth, momentum=None):
    level = ("expanding" if growth >= GROWTH_BAND else
             "contracting" if growth <= -GROWTH_BAND else "flat")
    trend = (None if not _number(momentum) else
             "strengthening" if momentum >= MOMENTUM_BAND else
             "weakening" if momentum <= -MOMENTUM_BAND else "steady")
    return level, trend


def classify_labor(change, rise_from_low=None):
    flag = _number(rise_from_low) and rise_from_low >= LABOR_RISE_FROM_LOW
    if change >= LABOR_DETERIORATING or flag:
        return "deteriorating", bool(flag)
    if change <= LABOR_IMPROVING:
        return "improving", False
    return "stable", False


def classify_inflation(level, change=None):
    band = ("near goal" if level <= INFLATION_NEAR_GOAL else
            "high" if level > INFLATION_HIGH else "elevated")
    trend = (None if not _number(change) else
             "firming" if change >= INFLATION_TREND_BAND else
             "easing" if change <= -INFLATION_TREND_BAND else "stable")
    return band, trend


CONDITIONS = {
    ("expanding", "improving"): "Expanding", ("expanding", "stable"): "Expanding",
    ("expanding", "deteriorating"): "Mixed",
    ("flat", "improving"): "Slowing", ("flat", "stable"): "Slowing",
    ("flat", "deteriorating"): "Deteriorating",
    ("contracting", "deteriorating"): "Deteriorating",
    ("contracting", "improving"): "Mixed", ("contracting", "stable"): "Mixed",
}

HEADLINES = {
    "Expanding": "Our assessment: economic activity is expanding and the labor trend is holding up.",
    "Slowing": "Our assessment: growth has stalled, but the labor market is holding up.",
    "Deteriorating": ("Our assessment: the economy is showing production weakness and "
                      "labor-market deterioration. Downside economic risk deserves priority."),
    "Mixed": ("Our assessment: the economy is not sending a unified signal. "
              "The evidence favors a selective, cautious interpretation over a sweeping call."),
}
OUTLOOKS = {
    "Expanding": ("Working outlook: continued expansion is more consistent with these observations "
                  "than an ongoing broad contraction. This is a conditional research judgment, "
                  "not a calibrated 3–6 month forecast."),
    "Slowing": ("Working outlook: a slower pace of activity is the base case while employment holds; "
                "a sustained rise in unemployment would mark broader deterioration. "
                "This is a conditional judgment, not a forecast."),
    "Deteriorating": ("Working outlook: further weakness is a serious scenario, but a recession "
                      "or market crash is not established by these indicators."),
    "Mixed": ("Working outlook: continued growth and deterioration both remain plausible; "
              "the current evidence does not justify choosing a single future path."),
}


def _reversal(condition: str) -> list:
    turn_cautious = [
        f"Industrial production falls below a {-GROWTH_BAND:+.1f}% year-over-year change",
        f"Unemployment rises {LABOR_DETERIORATING:.1f} percentage points or more over three months",
        (f"The three-month average unemployment rate rises {LABOR_RISE_FROM_LOW:.1f} points "
         "or more above its low of the prior year"),
    ]
    return {
        "Expanding": ["We would turn more cautious if any of the following occurred:"] + turn_cautious,
        "Slowing": [
            "We would turn more cautious if unemployment rose "
            f"{LABOR_DETERIORATING:.1f} points or more over three months (or the average rose "
            f"{LABOR_RISE_FROM_LOW:.1f} points above its prior-year low).",
            f"We would turn more constructive if production growth rose above +{GROWTH_BAND:.1f}% year over year.",
        ],
        "Deteriorating": [
            "We would become less cautious if production recovered and unemployment stopped rising:",
            f"Industrial production back above +{GROWTH_BAND:.1f}% year over year",
            f"Three-month unemployment change below +{LABOR_DETERIORATING:.1f} points with no prior-year-low breach",
        ],
        "Mixed": [
            "A sustained alignment of production and employment trends would change this assessment:",
            f"Toward expansion: production above +{GROWTH_BAND:.1f}% with unemployment not rising {LABOR_DETERIORATING:.1f} points",
            f"Toward deterioration: production at or below +{GROWTH_BAND:.1f}% with unemployment rising {LABOR_DETERIORATING:.1f} points or more",
        ],
    }[condition]


def _fmt(value, unit="%"):
    return f"{value:+.2f}{unit}" if unit != "%" else f"{value:.2f}%"


def interpret(assessment: dict, status: str, as_of: date, previous: dict | None = None) -> dict:
    """Apply the rubric. Never raises on incomplete data; it withholds instead."""
    assessment = assessment if isinstance(assessment, dict) else {}
    pillars = pillar_status(assessment, as_of)
    base = {"rubric_version": RUBRIC_VERSION, "thresholds": THRESHOLDS,
            "pillars": pillars, "condition": "Insufficient evidence",
            "direction": "Not established", "evidence_confidence": "None",
            "headline": "Our assessment: Insufficient current evidence for a defensible economic call.",
            "outlook": "No directional outlook is published from stale or incomplete observations.",
            "drivers": [], "counterevidence": [], "reversal_conditions": [],
            "revisions": [], "changes_since_previous": [], "previous_assessment_date": None,
            "is_forecast": False, "probabilities_published": False}
    if status != "PASS" or assessment.get("stale") is not False:
        base["withheld_reason"] = "Monthly gate not passed or observations stale."
        return base
    unavailable = [p for p, info in pillars.items() if info["status"] != "current"]
    if unavailable:
        base["withheld_reason"] = ("Not current: " + ", ".join(
            f"{p} ({pillars[p]['status']})" for p in unavailable))
        return base

    growth = assessment["industrial_production_growth_12m_log_pct"]
    labor = assessment["unemployment_change_3m_pp"]
    inflation = assessment["cpi_inflation_12m_log_pct"]
    momentum = assessment.get("industrial_production_momentum_3m_pp")
    rise = assessment.get("unemployment_3m_avg_rise_from_12m_low_pp")
    inflation_change = assessment.get("cpi_inflation_change_3m_pp")
    g_level, g_trend = classify_growth(growth, momentum)
    l_state, rule_flag = classify_labor(labor, rise)
    i_band, i_trend = classify_inflation(inflation, inflation_change)
    condition = CONDITIONS[(g_level, l_state)]
    month = {p: pillars[p]["observation_month"] for p in pillars}

    growth_text = (f"Industrial production is {g_level} ({_fmt(growth)} over 12 months, "
                   f"observed {month['growth']})")
    labor_text = (f"Unemployment {'rose' if labor > 0 else 'fell' if labor < 0 else 'was unchanged'} "
                  f"{abs(labor):.2f} points over three months — {l_state} (observed {month['employment']})")
    inflation_text = (f"Consumer inflation is {i_band} at {_fmt(inflation)} year over year"
                      + (f" and {i_trend} ({inflation_change:+.2f} points over three months)" if i_trend else "")
                      + f" (observed {month['inflation']})")
    drivers, counter = [growth_text, labor_text], []
    if rule_flag:
        drivers.append(f"Three-month average unemployment is {rise:.2f} points above its prior-year low, "
                       "a historical deterioration signal that has also produced false alarms")
    positive = condition in ("Expanding", "Slowing")
    if g_trend == "weakening":
        (counter if positive or condition == "Mixed" else drivers).append(
            f"Production growth slowed by {abs(momentum):.2f} points over three months")
    if g_trend == "strengthening":
        (drivers if positive else counter).append(
            f"Production growth improved by {momentum:.2f} points over three months")
    if condition == "Mixed":
        counter.append("Growth and employment point in different directions")
    if condition == "Deteriorating" and l_state == "deteriorating" and g_level == "flat":
        counter.append("Production is flat rather than contracting")
    if positive and _number(rise) and 0.3 <= rise < LABOR_RISE_FROM_LOW:
        counter.append(f"Unemployment is {rise:.2f} points above its prior-year low — not yet a warning, but close")
    if i_band != "near goal":
        tension = ("high inflation alongside weakening activity limits room for policy support"
                   if condition in ("Deteriorating", "Mixed") else
                   "above-goal inflation can keep interest rates restrictive")
        counter.append(f"{inflation_text}; {tension}")
    else:
        drivers.append(inflation_text)

    if not _number(momentum):
        direction = "Unconfirmed"
    elif l_state == "deteriorating":
        direction = "Weakening"
    elif g_trend == "weakening":
        direction = "Softening"
    elif g_trend == "strengthening" and l_state == "improving":
        direction = "Strengthening"
    elif g_trend == "strengthening":
        direction = "Firming"
    else:
        direction = "Steady"

    revisions = []
    previous_ok = (isinstance(previous, dict) and previous.get("stale") is False
                   and isinstance(previous.get("assessment_date"), str)
                   and isinstance(assessment.get("assessment_date"), str)
                   and previous["assessment_date"] < assessment["assessment_date"])
    if previous_ok:
        prior_sources = previous.get("sources") if isinstance(previous.get("sources"), dict) else {}
        for pillar, (series, metric) in PILLARS.items():
            before = previous.get(metric)
            src = prior_sources.get(series) if isinstance(prior_sources.get(series), dict) else {}
            if (src.get("latest_used_month") == month[pillar] and _number(before)
                    and abs(before - assessment[metric]) >= 0.005):
                revisions.append(f"{series} {month[pillar]} reading revised from {before:.2f} "
                                 f"to {assessment[metric]:.2f}")

    conflicts = len(counter) + len(revisions) + (0 if _number(momentum) else 1)
    confidence = "High" if conflicts == 0 else "Moderate" if conflicts <= 2 else "Low"

    result = dict(base)
    result.update({
        "condition": condition, "direction": direction, "evidence_confidence": confidence,
        "headline": HEADLINES[condition] + (" Inflation remains a risk to monitor."
                                            if condition == "Expanding" and i_band != "near goal" else ""),
        "outlook": OUTLOOKS[condition],
        "classification": {"growth": g_level, "growth_momentum": g_trend, "labor": l_state,
                           "labor_rule_triggered": rule_flag, "inflation": i_band,
                           "inflation_trend": i_trend},
        "drivers": drivers, "counterevidence": counter,
        "reversal_conditions": _reversal(condition), "revisions": revisions,
    })
    result.pop("withheld_reason", None)
    if previous_ok:
        result["previous_assessment_date"] = previous["assessment_date"]
        prior = interpret(previous, "PASS", date.fromisoformat(previous["assessment_date"]))
        changes = []
        if prior["condition"] != condition:
            changes.append(f"Condition changed from {prior['condition']} to {condition}")
        if prior["direction"] != direction:
            changes.append(f"Direction changed from {prior['direction']} to {direction}")
        old = prior.get("classification", {})
        names = {"growth": "Growth", "labor": "Labor", "inflation": "Inflation",
                 "growth_momentum": "Growth momentum", "inflation_trend": "Inflation trend"}
        for key, label in names.items():
            if old and old.get(key) != result["classification"][key]:
                changes.append(f"{label} moved from {old.get(key) or 'unavailable'} "
                               f"to {result['classification'][key] or 'unavailable'}")
        if not changes:
            changes.append(f"No change in the rubric reading since {previous['assessment_date']}")
        result["changes_since_previous"] = changes
    return result
