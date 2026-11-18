"""V7 daily market monitoring: assessments, change detection, event reviews and weekly interpretation.

DAILY MARKET MONITORING. WEEKLY INTERPRETATION. MONTHLY ECONOMIC RESEARCH.

* An *assessment* records every market observation with its own observation date and frequency.
* A new assessment is made only when at least one observation is newer than in the previous one;
  an unchanged weekly or monthly reading is carried forward with its original date, never re-dated.
* *Changes* compare two assessments with fixed, documented thresholds. Two kinds are kept apart:
  - TESTED: a historically tested warning sign changed state (see docs/V7_PREREGISTRATION_CRASH_RESEARCH.md);
  - MONITORING: a descriptive threshold (drawdown levels, volatility, credit, breadth). These describe the
    market; they are not tested predictors and never produce a probability.
* An *event review* is opened when a large move crosses a documented event threshold.
* A *weekly interpretation* summarises the most recent completed week (Monday–Friday) from the daily data.

Standard library only. Nothing here changes a monthly economic conclusion.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

HISTORY = "v7_market_history.json"
KEEP_ASSESSMENTS, KEEP_WEEKLY = 90, 12
# Descriptive monitoring thresholds (documented; not tested predictors).
DRAWDOWN_LEVELS = (5, 10, 15, 20, 30)        # % below the 1-year high
DAILY_MOVE = {"spx": 2.0, "ndx": 2.5}        # % one-day move worth reporting
VIX_LEVELS, VIX_JUMP = (20, 30, 40), 4.0     # level crossings; points change since the previous reading
HY_LEVELS, HY_JUMP = (4.0, 5.0), 0.30        # high-yield spread (points)
BAA_JUMP = 0.15                              # BAA − 10-year spread change (points)
NFCI_LEVEL, NFCI_JUMP = 0.0, 0.10
BREADTH_LEVELS, BREADTH_JUMP = (40, 50), 10  # % of industries above trend
EVENT = {"drawdown": 10, "vix": 30, "hy_jump": 0.50}
INDEXES = (("spx", "SP500", "S&P 500"), ("ndx", "NASDAQCOM", "Nasdaq Composite"), ("dow", "DJIA", "Dow"))
WHY = {
    "drawdown": "Declines of this size are common, but every bear market passed through them first.",
    "move": "Large daily moves cluster when markets are stressed.",
    "vix": "Higher volatility means investors are paying more for protection against falls.",
    "hy": "Riskier borrowers paying more to borrow is an early sign of financial stress.",
    "baa": "Wider corporate spreads mean lenders see more risk.",
    "nfci": "Tighter financial conditions make shocks harder to absorb.",
    "breadth": "Fewer industries rising means gains depend on a narrower group of leaders.",
}


def _series(data_dir: Path, sid: str) -> dict:
    p = Path(data_dir) / f"fred_{sid}.csv"
    if not p.is_file():
        return {}
    with p.open() as f:
        return {r["date"]: float(r["value"]) for r in csv.DictReader(f)}


def _index_obs(ser: dict) -> dict | None:
    if len(ser) < 2:
        return None
    ds = sorted(ser)
    last, prev = ds[-1], ds[-2]
    year_ago = (date.fromisoformat(last) - timedelta(days=365)).isoformat()
    high = max(v for d, v in ser.items() if d > year_ago)
    return {"date": last, "frequency": "daily", "value": ser[last], "d1_pct": round(100 * (ser[last] / ser[prev] - 1), 2),
            "dd_pct": round(100 * (ser[last] / high - 1), 2)}


def _latest(ser: dict, freq: str) -> dict | None:
    if not ser:
        return None
    d = max(ser)
    return {"date": d, "frequency": freq, "value": round(ser[d], 3)}


def assess(crash: dict, data_dir: Path, assessed_at: str) -> dict:
    """One market assessment from the crash-research output and its dated data snapshot."""
    obs = {}
    for key, sid, label in INDEXES:
        o = _index_obs(_series(data_dir, sid))
        if o:
            obs[key] = dict(o, label=label)
    for key, sid, label, freq in (("vix", "VIXCLS", "VIX volatility index", "daily"),
                                  ("hy", "BAMLH0A0HYM2", "High-yield bond spread", "daily"),
                                  ("baa", "BAA10Y", "BAA corporate spread", "daily"),
                                  ("nfci", "NFCI", "Chicago Fed financial conditions", "weekly")):
        o = _latest(_series(data_dir, sid), freq)
        if o:
            obs[key] = dict(o, label=label)
    warnings = {w["key"]: {"title": w["title"], "status": w["status"], "value": w.get("value"), "date": w.get("date"),
                           "frequency": w.get("frequency")} for w in crash["site"]["warnings"]}
    b = warnings.get("breadth")
    if b and b.get("value") is not None:
        obs["breadth"] = {"date": b["date"], "frequency": "monthly", "value": b["value"], "label": "Industries above trend"}
    through = obs.get("spx", {}).get("date") or max((o["date"] for o in obs.values()), default=None)
    return {"assessed_at_utc": assessed_at, "market_data_through": through, "observations": obs, "warnings": warnings}


def has_new_data(prev: dict | None, cur: dict) -> bool:
    if prev is None:
        return True
    po = prev["observations"]
    return any(o["date"] > po.get(k, {}).get("date", "") for k, o in cur["observations"].items())


def _cross(old, new, levels, deeper_is_lower=False):
    """Levels crossed between old and new (either direction)."""
    out = []
    for lv in levels:
        if (old < lv <= new) or (new < lv <= old):
            out.append(lv)
    return out


def _fmt(v, unit="", digits=1, sign=False):
    s = f"{v:+.{digits}f}" if sign else f"{v:.{digits}f}"
    return s.replace("-", "−") + unit


def changes(prev: dict, cur: dict) -> tuple[list, list]:
    """(changes, events) between two assessments; only observations with a newer date are compared."""
    items, events = [], []
    po, co = prev["observations"], cur["observations"]

    def new(k):
        return k in co and k in po and co[k]["date"] > po[k]["date"]
    order = {"warning": 3, "near": 2, "clear": 1, "not current": 0}
    for k, w in cur["warnings"].items():
        old = prev["warnings"].get(k)
        if old and old["status"] != w["status"]:
            worse = order.get(w["status"], 0) > order.get(old["status"], 0)
            verb = {"warning": "warning switched on", "near": "now near its trigger", "clear": "back to clear",
                    "not current": "data no longer current"}[w["status"]]
            items.append({"kind": "tested", "severity": "up" if worse else "down", "key": k, "date": w.get("date"),
                          "title": f"{w['title']}: {verb}", "detail": f"was {old['status']}, now {w['status']}",
                          "why": "A historically tested warning sign changed state. It has preceded past 20% declines more "
                                 "often than usual, with many misses and false alarms."})
            if w["status"] == "warning" and old["status"] != "warning":
                events.append(f"New tested warning: {w['title']}")
    for key, _, label in INDEXES[:2]:
        if not new(key):
            continue
        a, b = abs(po[key]["dd_pct"]), abs(co[key]["dd_pct"])
        for lv in _cross(a, b, DRAWDOWN_LEVELS):
            deeper = b >= lv
            items.append({"kind": "monitoring", "severity": "up" if deeper else "down", "key": key, "date": co[key]["date"],
                          "title": (f"{label} is now {_fmt(b)}% below its 1-year high" if deeper else
                                    f"{label} recovered to within {lv}% of its 1-year high"),
                          "detail": f"was {_fmt(a)}% below; threshold {lv}%", "why": WHY["drawdown"]})
            if deeper and lv >= EVENT["drawdown"]:
                events.append(f"{label} fell {lv}% or more below its 1-year high")
        d1 = co[key]["d1_pct"]
        if abs(d1) >= DAILY_MOVE[key]:
            items.append({"kind": "monitoring", "severity": "up" if d1 < 0 else "down", "key": key, "date": co[key]["date"],
                          "title": f"{label} moved {_fmt(d1, '%', sign=True)} in one day", "detail": f"threshold ±{DAILY_MOVE[key]}%",
                          "why": WHY["move"]})
    if new("vix"):
        a, b = po["vix"]["value"], co["vix"]["value"]
        crossed = _cross(a, b, VIX_LEVELS)
        if crossed or abs(b - a) >= VIX_JUMP:
            items.append({"kind": "monitoring", "severity": "up" if b > a else "down", "key": "vix", "date": co["vix"]["date"],
                          "title": f"Volatility (VIX) {'rose' if b > a else 'fell'} to {_fmt(b)}",
                          "detail": f"from {_fmt(a)}" + (f"; crossed {', '.join(str(x) for x in crossed)}" if crossed else ""),
                          "why": WHY["vix"]})
            if b >= EVENT["vix"] > a:
                events.append(f"VIX rose above {EVENT['vix']}")
    if new("hy"):
        a, b = po["hy"]["value"], co["hy"]["value"]
        crossed = _cross(a, b, HY_LEVELS)
        if crossed or abs(b - a) >= HY_JUMP:
            items.append({"kind": "monitoring", "severity": "up" if b > a else "down", "key": "hy", "date": co["hy"]["date"],
                          "title": f"High-yield spread {'widened' if b > a else 'narrowed'} to {_fmt(b, digits=2)} points",
                          "detail": f"from {_fmt(a, digits=2)}", "why": WHY["hy"]})
            if b - a >= EVENT["hy_jump"]:
                events.append("High-yield spread widened 0.5 points or more")
    if new("baa"):
        a, b = po["baa"]["value"], co["baa"]["value"]
        if abs(b - a) >= BAA_JUMP:
            items.append({"kind": "monitoring", "severity": "up" if b > a else "down", "key": "baa", "date": co["baa"]["date"],
                          "title": f"BAA corporate spread {'widened' if b > a else 'narrowed'} to {_fmt(b, digits=2)} points",
                          "detail": f"from {_fmt(a, digits=2)}", "why": WHY["baa"]})
    if new("nfci"):
        a, b = po["nfci"]["value"], co["nfci"]["value"]
        if _cross(a, b, (NFCI_LEVEL,)) or abs(b - a) >= NFCI_JUMP:
            items.append({"kind": "monitoring", "severity": "up" if b > a else "down", "key": "nfci", "date": co["nfci"]["date"],
                          "title": f"Financial conditions {'tightened' if b > a else 'eased'} to {_fmt(b, digits=2)}",
                          "detail": f"from {_fmt(a, digits=2)} (weekly; 0 = average)", "why": WHY["nfci"]})
    if new("breadth"):
        a, b = po["breadth"]["value"], co["breadth"]["value"]
        if _cross(a, b, BREADTH_LEVELS) or abs(b - a) >= BREADTH_JUMP:
            items.append({"kind": "monitoring", "severity": "up" if b < a else "down", "key": "breadth", "date": co["breadth"]["date"],
                          "title": f"Breadth {'narrowed' if b < a else 'widened'}: {b:.0f}% of industries above trend",
                          "detail": f"from {a:.0f}% (monthly)", "why": WHY["breadth"]})
    rank = {"tested": 0, "monitoring": 1}
    items.sort(key=lambda i: (rank[i["kind"]], i["severity"] != "up"))
    return items, events


def _week_bounds(through: str) -> tuple[str, str]:
    """Monday and Friday of the most recent completed trading week as of `through`."""
    d = date.fromisoformat(through)
    friday = d - timedelta(days=(d.weekday() - 4) % 7)
    if friday > d:
        friday -= timedelta(days=7)
    return (friday - timedelta(days=4)).isoformat(), friday.isoformat()


def _at(ser: dict, day: str):
    ds = [d for d in ser if d <= day]
    return (max(ds), ser[max(ds)]) if ds else (None, None)


def _plain(code: str) -> str:
    try:
        from .v7_site import INDUSTRY
    except ImportError:
        from v7_site import INDUSTRY
    return INDUSTRY.get(code, code)


def weekly(crash: dict, data_dir: Path, through: str, economy: dict, assessments: list | None = None) -> dict:
    """Interpretation of the most recent completed week, from the daily data; conclusions only from tested evidence."""
    mon, fri = _week_bounds(through)
    before = (date.fromisoformat(mon) - timedelta(days=1)).isoformat()
    lines, meaningful = [], False
    moves = []
    for key, sid, label in INDEXES:
        ser = _series(data_dir, sid)
        (d0, v0), (d1, v1) = _at(ser, before), _at(ser, fri)
        if v0 and v1:
            moves.append((label, 100 * (v1 / v0 - 1), d1))
    warns = crash["site"]["warnings"]
    on = [w["title"] for w in warns if w["status"] == "warning"]
    near = [w["title"] for w in warns if w["status"] == "near"]
    if moves:
        txt = "; ".join(f"{lab} {_fmt(m, '%', sign=True)}" for lab, m, _ in moves)
        big = any(abs(m) >= 3 for _, m, _ in moves)
        meaningful |= big
        lines.append({"topic": "Market moves", "text": f"Week to {fri}: {txt}."})
    in_week = [c for a in (assessments or []) if mon <= (a.get("market_data_through") or "") <= fri
               for c in a.get("changes", []) if c["kind"] == "tested"]
    meaningful |= bool(in_week)
    latest_day = max((w.get("date") or "" for w in warns if w.get("frequency") == "daily"), default=through)
    lines.append({"topic": "Direction of vulnerability",
                  "text": ((f"During the week: {'; '.join(c['title'] for c in in_week)}. " if in_week else
                            "No tested warning changed state during the week. " if assessments else "")
                           + f"Latest readings (data through {latest_day}): tested warnings on: {', '.join(on) or 'none'}; "
                           f"near trigger: {', '.join(near) or 'none'}. A count of historically tested signs, not a probability.")})
    b = next((w for w in warns if w["key"] == "breadth"), None)
    lead = crash["current"].get("industries_French", {})
    if b:
        lines.append({"topic": "Breadth and leadership",
                      "text": f"{b['value']:.0f}% of industries above trend ({b['date']}, monthly; no new breadth data unless "
                              f"a new month is published). Leaders over 12 months: "
                              + ", ".join(_plain(n) for n, _ in lead.get("leaders_12m", [])[:3]) + "."})
    credit = []
    for sid, label, digits in (("BAMLH0A0HYM2", "high-yield spread", 2), ("BAA10Y", "BAA spread", 2), ("NFCI", "NFCI", 2)):
        ser = _series(data_dir, sid)
        (d0, v0), (d1, v1) = _at(ser, before), _at(ser, fri)
        if v0 is not None and v1 is not None and d1 != d0:
            credit.append(f"{label} {_fmt(v1, digits=digits)} ({_fmt(v1 - v0, digits=digits, sign=True)})")
            meaningful |= (sid == "BAMLH0A0HYM2" and abs(v1 - v0) >= HY_JUMP) or (sid == "NFCI" and abs(v1 - v0) >= NFCI_JUMP)
    lines.append({"topic": "Credit and liquidity", "text": ("; ".join(credit) + ".") if credit else "No new credit data this week."})
    trend = next((w for w in warns if w["key"] == "trend"), {})
    lines.append({"topic": "Economy and market",
                  "text": (f"The monthly economic assessment is {economy.get('condition', 'unavailable').lower()} "
                           f"(data through {economy.get('through', 'n/a')}); the market trend sign is {trend.get('status', 'n/a')}. "
                           + ("They diverge: markets can fall 20% or more while the economy is still growing."
                              if economy.get("condition") == "Expanding" and trend.get("status") in ("warning", "near") else
                              "No divergence to flag."))})
    if lead:
        lines.append({"topic": "Sectors", "text": f"Industry returns are monthly (to {lead.get('month')}); laggards over 12 months: "
                                                  + ", ".join(_plain(n) for n, _ in lead.get("laggards_12m", [])[-3:]) + "."})
    bears = crash.get("bear_markets", [])
    dd = [(lab, m) for lab, m, _ in moves]
    if bears:
        depths = sorted(b["depth_pct"] for b in bears)
        lines.append({"topic": "Historical comparison",
                      "text": f"Past bear markets fell between {_fmt(depths[-1], '%', 0)} and {_fmt(depths[0], '%', 0)} from their "
                              "highs; see the decline chart for how today compares."})
    summary = ("Meaningful change this week." if meaningful else
               "No meaningful change in tested warnings, credit or volatility this week.")
    return {"week": [mon, fri], "generated_from_data_through": through, "summary": summary, "meaningful": meaningful,
            "lines": lines}


def update(history: dict | None, crash: dict, data_dir: Path, assessed_at: str, economy: dict,
           baseline: dict | None = None) -> tuple[dict, str]:
    """Return (history, status) where status is NEW_ASSESSMENT or NO_NEW_DATA. Never mutates the input."""
    history = {"assessments": list((history or {}).get("assessments", [])), "weekly": list((history or {}).get("weekly", []))}
    if not history["assessments"] and baseline:
        history["assessments"].append(dict(baseline, changes=[], events=[], baseline=True))
    cur = assess(crash, data_dir, assessed_at)
    prev = history["assessments"][-1] if history["assessments"] else None
    if prev is not None and not has_new_data(prev, cur):
        return history, "NO_NEW_DATA"
    cur["changes"], cur["events"] = changes(prev, cur) if prev else ([], [])
    history["assessments"] = (history["assessments"] + [cur])[-KEEP_ASSESSMENTS:]
    wk = weekly(crash, data_dir, cur["market_data_through"], economy, history["assessments"])
    if not history["weekly"] or history["weekly"][-1]["week"] != wk["week"]:
        history["weekly"] = (history["weekly"] + [wk])[-KEEP_WEEKLY:]
    return history, "NEW_ASSESSMENT"
