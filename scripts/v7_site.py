"""V7 M4: human-first economic intelligence site (static, dependency-free).

Five experiences, one home per feature:
  index.html (Home: economic outlook summary) · forecast.html · sectors.html (+11
  sector pages) · track-record.html · research.html (Research & Data).
The homepage summarises and links; detail lives in exactly one place.
All numbers come from gated evidence files; unpublished outlooks render as
"Not enough evidence yet". Nothing here is investment advice.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
from datetime import date
from pathlib import Path

try:
    from .v7_forecast_engine import load as load_fred, shift
    from .v63_historical_replay import assessment_at
    from .v63_interpretation import interpret
except ImportError:
    from v7_forecast_engine import load as load_fred, shift
    from v63_historical_replay import assessment_at
    from v63_interpretation import interpret

NAV = (("Home", "index.html", "home"), ("Forecast", "forecast.html", "forecast"), ("Sectors", "sectors.html", "sectors"),
       ("Track Record", "track-record.html", "track"), ("Research & Data", "research.html", "research"))
TARGET_LABEL = {"labor_deterioration": "Job market weakens", "recession": "Recession under way",
                "recession_onset": "New recession starts", "inflation_rising": "Inflation picks up"}
TARGET_PLAIN = {
    "labor_deterioration": "Unemployment rises at least 0.5 points",
    "recession": "The economy is in a recession at some point",
    "recession_onset": "A new recession begins",
    "inflation_rising": "The yearly inflation rate is higher than today",
}
CHECK_SHORT = {"calibration": "too confident", "bss_vs_base_rate": "no better than average",
               "auc": "weak at ranking risk", "episodes": "too few episodes"}
REASON_PLAIN = {
    "calibration": "our model spots risk well, but its probabilities have historically been too confident",
    "bss_vs_base_rate": "it has not beaten simply using the long-run average",
    "auc": "it has not reliably told higher-risk periods from lower-risk ones",
    "episodes": "there are too few past episodes to judge",
}
ICONS = {
    "home": '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "forecast": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "sectors": '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
    "track": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    "research": '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h8M8 8h4"/>',
}

CSS = """
:root{--bg:#f4f6fb;--card:#fff;--ink:#0f1b2d;--muted:#55657a;--line:#dde3ec;--brand:#1f4e89;--brand2:#2f74c0;
--good:#1d7a4f;--warn:#a35a00;--bad:#b3261e;--chip:#eef3fa;--hatch:#c8d2e0;--focus:#ff9e1b}
@media (prefers-color-scheme:dark){:root{--bg:#0d1420;--card:#152033;--ink:#e8eef7;--muted:#a3b2c6;--line:#26354d;
--brand:#7fb0ff;--brand2:#9cc3ff;--good:#5fd39a;--warn:#ffb74d;--bad:#ff8a80;--chip:#1c2a42;--hatch:#3a4a63}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--brand)}a:focus-visible,button:focus-visible,[tabindex]:focus-visible,summary:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.skip{position:absolute;left:-999px}.skip:focus{left:12px;top:12px;background:var(--card);padding:8px 12px;z-index:9}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.bar{max-width:1120px;margin:auto;padding:10px 16px;display:flex;align-items:center;gap:16px}
.brand{font-weight:800;color:var(--ink);text-decoration:none;letter-spacing:-.01em;display:flex;align-items:center;gap:8px}
.brand .dot{width:10px;height:10px;border-radius:50%;background:var(--brand2)}
nav.primary{margin-left:auto;display:none;gap:4px}
nav.primary a{text-decoration:none;color:var(--muted);padding:8px 12px;border-radius:999px;font-weight:600;font-size:.95rem}
nav.primary a[aria-current=page]{background:var(--chip);color:var(--brand)}
nav.tabs{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--line);display:grid;
grid-template-columns:repeat(5,1fr);z-index:6;padding-bottom:env(safe-area-inset-bottom)}
nav.tabs a{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 2px 10px;font-size:.72rem;
color:var(--muted);text-decoration:none;min-height:56px;text-align:center;line-height:1.15}
nav.tabs a[aria-current=page]{color:var(--brand);font-weight:700}
nav.tabs svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
main{max-width:1120px;margin:auto;padding:18px 16px 96px}
h1{font-size:1.6rem;line-height:1.2;margin:.2em 0 .3em;letter-spacing:-.02em}
h2{font-size:1.2rem;margin:0 0 .5em;line-height:1.25}h3{font-size:1rem;margin:1em 0 .3em}
.lede{color:var(--muted);margin:0 0 1em;max-width:62ch}
.grid{display:grid;gap:14px}.cols-2,.cols-3{grid-template-columns:1fr}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}
.card.hero{background:linear-gradient(135deg,var(--card),var(--chip))}
.eyebrow{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700;margin:0 0 6px}
.big{font-size:2rem;font-weight:800;letter-spacing:-.02em;margin:0}
.chip{display:inline-block;background:var(--chip);color:var(--ink);border-radius:999px;padding:3px 10px;font-size:.82rem;font-weight:600;margin:2px 4px 2px 0}
.chip.good{color:var(--good)}.chip.warn{color:var(--warn)}.chip.bad{color:var(--bad)}.chip.muted{color:var(--muted)}
.muted{color:var(--muted)}small{color:var(--muted)}
ul.clean{padding-left:1.1em;margin:.3em 0}ul.clean li{margin:.35em 0}
.horizons{display:grid;gap:10px;grid-template-columns:1fr}
.hz{border:1px solid var(--line);border-radius:12px;padding:12px}
.hz .label{font-weight:700}.hz .state{font-size:.9rem;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:.92rem}th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.scroll{overflow-x:auto}
.sector-card{display:block;text-decoration:none;color:inherit}
.sector-card:hover{border-color:var(--brand2)}
.pill{font-size:.78rem;font-weight:700;border-radius:8px;padding:2px 8px;display:inline-block}
.p-now{background:#e3f4ea;color:#14563a}.p-mon{background:#fff2dc;color:#7a4300}.p-low{background:#eef1f5;color:#47566b}
@media (prefers-color-scheme:dark){.p-now{background:#163a2a;color:#8ee0b4}.p-mon{background:#3b2a12;color:#ffcf8a}.p-low{background:#222e40;color:#b7c4d6}}
details{border:1px solid var(--line);border-radius:12px;padding:10px 14px;background:var(--card);margin:10px 0}
summary{cursor:pointer;font-weight:700;min-height:28px}
.note{border-left:4px solid var(--brand2);padding:8px 12px;background:var(--chip);border-radius:8px;margin:10px 0}
footer{max-width:1120px;margin:auto;padding:0 16px 110px;color:var(--muted);font-size:.85rem}
svg text{fill:currentColor}
.chart{width:100%;height:auto;display:block;color:var(--ink)}
.chart.square{max-width:340px;margin:auto}
ul.dbars{list-style:none;margin:6px 0;padding:0}
ul.dbars li{display:grid;grid-template-columns:minmax(0,9.5em) 1fr 4.8em;gap:8px;align-items:center;margin:6px 0;font-size:.9rem}
.db-label{overflow-wrap:anywhere}.db-val{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
.db-track{position:relative;height:14px;background:var(--chip);border-radius:7px}
.db-zero{position:absolute;left:50%;top:-3px;bottom:-3px;width:2px;background:var(--muted)}
.db-fill{position:absolute;top:0;bottom:0;border-radius:7px}.db-fill.pos{background:var(--good)}.db-fill.neg{background:var(--bad)}
th[scope=row]{text-transform:none;letter-spacing:0;font-size:.92rem;color:var(--ink);font-weight:600}
@media(min-width:720px){nav.primary{display:flex}nav.tabs{display:none}main{padding-bottom:40px}footer{padding-bottom:30px}
.cols-2{grid-template-columns:1fr 1fr}.cols-3{grid-template-columns:repeat(3,1fr)}.horizons{grid-template-columns:repeat(3,1fr)}h1{font-size:2rem}}
"""


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def icon(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def page(title: str, active: str, body: str, description: str) -> str:
    top = "".join(f'<a href="{u}"{" aria-current=page" if k == active else ""}>{esc(t)}</a>' for t, u, k in NAV)
    tabs = "".join(f'<a href="{u}"{" aria-current=page" if k == active else ""}>{icon(k)}<span>{esc(t)}</span></a>'
                   for t, u, k in NAV)
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<meta name=\"description\" content=\"{esc(description)}\"><title>{esc(title)} — Economic Cycle Research</title>"
            f"<style>{CSS}</style></head><body><a class=\"skip\" href=\"#main\">Skip to content</a>"
            "<header class=\"top\"><div class=\"bar\"><a class=\"brand\" href=\"index.html\"><span class=\"dot\" aria-hidden=\"true\"></span>"
            f"Economic Cycle Research</a><nav class=\"primary\" aria-label=\"Primary\">{top}</nav></div></header>"
            f"<main id=\"main\">{body}</main>"
            "<footer><p><strong>Educational research — not personalized financial advice.</strong> Outlooks are published only "
            "when they pass our historical reliability test; otherwise we say there is not enough evidence. Past performance does "
            "not guarantee future results, and investing involves risk, including loss of principal.</p></footer>"
            f"<nav class=\"tabs\" aria-label=\"Primary\">{tabs}</nav></body></html>")


# --------------------------------------------------------------------------
# Charts (inline SVG, each with a text alternative)
# --------------------------------------------------------------------------
def cycle_gauge(condition: str, direction: str) -> str:
    zones = (("Deteriorating", "var(--bad)"), ("Slowing", "var(--warn)"), ("Expanding", "var(--good)"))
    w, x0, seg = 320, 10, 100
    pos = {"Deteriorating": 0, "Slowing": 1, "Expanding": 2}
    parts = []
    for i, (name, col) in enumerate(zones):
        parts.append(f'<rect x="{x0 + i * seg}" y="30" width="{seg - 4}" height="14" rx="7" fill="{col}" opacity=".85"/>'
                     f'<text x="{x0 + i * seg + seg / 2 - 2}" y="64" text-anchor="middle" font-size="12">{name}</text>')
    if condition in pos:
        cx = x0 + pos[condition] * seg + seg / 2 - 2
        parts.append(f'<circle cx="{cx}" cy="37" r="11" fill="var(--card)" stroke="var(--ink)" stroke-width="3"/>'
                     f'<text x="{cx}" y="18" text-anchor="middle" font-size="12" font-weight="700">We are here</text>')
    else:
        parts.append('<text x="160" y="18" text-anchor="middle" font-size="12" font-weight="700">Signals are mixed</text>')
    label = f"Economic cycle position: {condition}. Direction: {direction}."
    return f'<svg class="chart" viewBox="0 0 {w + 20} 76" role="img" aria-label="{esc(label)}">{"".join(parts)}</svg>'


def probability_bar(p, base, label) -> str:
    """Horizontal bar 0–100% with a marker at the historical base rate."""
    if p is None:
        body = ('<defs><pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="6" stroke="var(--hatch)" stroke-width="3"/></pattern></defs>'
                '<rect x="0" y="6" width="300" height="12" rx="6" fill="url(#h)"/>')
        alt = f"{label}: not enough evidence to publish a probability."
    else:
        body = (f'<rect x="0" y="6" width="300" height="12" rx="6" fill="var(--chip)"/>'
                f'<rect x="0" y="6" width="{300 * p:.0f}" height="12" rx="6" fill="var(--brand2)"/>'
                f'<line x1="{300 * base:.0f}" x2="{300 * base:.0f}" y1="2" y2="22" stroke="var(--ink)" stroke-width="2"/>')
        alt = f"{label}: about {p:.0%}, compared with a historical average of {base:.0%}."
    return f'<svg class="chart" viewBox="0 0 300 24" role="img" aria-label="{esc(alt)}">{body}</svg>'


def diverging_bars(rows, unit="pp", width=None) -> str:
    """Responsive HTML bars around zero (rows: (label, value)); readable at any width."""
    vals = [abs(v) for _, v in rows if v is not None] or [1]
    top = max(vals)
    out = []
    for label, v in rows:
        if v is None:
            bar, txt = "", "n/a"
        else:
            pct = 50 * abs(v) / top
            side = f"left:50%;width:{pct:.1f}%" if v >= 0 else f"left:{50 - pct:.1f}%;width:{pct:.1f}%"
            bar = f'<span class="db-fill {"pos" if v >= 0 else "neg"}" style="{side}"></span>'
            txt = f"{v:+.1f}{unit}"
        out.append(f'<li><span class="db-label">{esc(label)}</span><span class="db-track" aria-hidden="true">'
                   f'<span class="db-zero"></span>{bar}</span><span class="db-val">{esc(txt)}</span></li>')
    return f'<ul class="dbars">{"".join(out)}</ul>'


def track_timeline(rows) -> str:
    """Forecast probability over time (line) with shaded months where the outcome occurred."""
    if not rows:
        return ""
    w, h, n = 640, 150, len(rows)
    x = lambda i: 30 + (w - 40) * i / max(1, n - 1)
    shade = "".join(f'<rect x="{x(i):.1f}" y="10" width="{(w - 40) / n + .6:.1f}" height="{h - 40}" fill="var(--warn)" opacity=".18"/>'
                    for i, r in enumerate(rows) if r["outcome"])
    pts = " ".join(f"{x(i):.1f},{10 + (h - 40) * (1 - r['probability']):.1f}" for i, r in enumerate(rows))
    ticks = "".join(f'<text x="{x(i):.1f}" y="{h - 12}" font-size="10" text-anchor="middle">{r["origin"][:4]}</text>'
                    for i, r in enumerate(rows) if r["origin"].endswith("-01") and int(r["origin"][:4]) % 10 == 0)
    grid = "".join(f'<line x1="30" x2="{w - 10}" y1="{10 + (h - 40) * (1 - g):.0f}" y2="{10 + (h - 40) * (1 - g):.0f}" stroke="var(--line)"/>'
                   f'<text x="2" y="{14 + (h - 40) * (1 - g):.0f}" font-size="10">{int(g * 100)}%</text>' for g in (0, .5, 1))
    hits = sum(r["outcome"] for r in rows)
    alt = (f"Monthly out-of-sample forecasts from {rows[0]['origin']} to {rows[-1]['origin']}. Shaded months ({hits}) "
           "are those where unemployment did rise at least 0.5 points within 12 months.")
    return (f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(alt)}">{grid}{shade}'
            f'<polyline points="{pts}" fill="none" stroke="var(--brand2)" stroke-width="1.6"/>{ticks}</svg>')


def calibration_chart(cal) -> str:
    s = 220
    pts = "".join(f'<circle cx="{20 + (s - 30) * c["mean_forecast"]:.1f}" cy="{s - 20 - (s - 30) * c["observed"]:.1f}" '
                  f'r="{4 + min(10, c["n"] / 25):.1f}" fill="var(--brand2)" opacity=".85"/>' for c in cal)
    alt = "; ".join(f"forecasts around {c['mean_forecast']:.0%} happened {c['observed']:.0%} of the time (n={c['n']})" for c in cal)
    return (f'<svg class="chart square" viewBox="0 0 {s} {s}" role="img" aria-label="Calibration: {esc(alt)}">'
            f'<rect x="20" y="10" width="{s - 30}" height="{s - 30}" fill="none" stroke="var(--line)"/>'
            f'<line x1="20" y1="{s - 20}" x2="{s - 10}" y2="10" stroke="var(--muted)" stroke-dasharray="4 4"/>{pts}'
            f'<text x="{s / 2}" y="{s - 4}" font-size="10" text-anchor="middle">Forecast probability</text>'
            f'<text x="8" y="{s / 2}" font-size="10" transform="rotate(-90 8 {s / 2})" text-anchor="middle">How often it happened</text></svg>')


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
def current_assessment(fred: dict):
    common = min(max(fred[n]) for n in ("INDPRO", "UNRATE", "CPIAUCSL"))
    sub = {"INDPRO": fred["INDPRO"], "UNRATE": fred["UNRATE"], "CPIAUCSL": fred["CPIAUCSL"]}
    month = shift(common, 1)
    a = assessment_at(sub, month)
    while a is None or a.get("cpi_inflation_12m_log_pct") is None:
        month = shift(month, -1)
        a = assessment_at(sub, month)
    view = interpret(a, "PASS", date.fromisoformat(a["assessment_date"]))
    return a, view


def load_inputs(forecast_path, research_path, sectors_path, archive_path, fred_dir):
    fred = load_fred(Path(fred_dir))
    a, view = current_assessment(fred)
    archive = []
    with open(archive_path, newline="") as f:
        for r in csv.DictReader(f):
            archive.append({"target": r["target"], "h": int(r["horizon_months"]), "origin": r["origin"],
                            "probability": float(r["probability"]), "outcome": int(r["outcome"])})
    return {"forecast": json.loads(Path(forecast_path).read_text()),
            "research": json.loads(Path(research_path).read_text()),
            "sectors": json.loads(Path(sectors_path).read_text()),
            "archive": archive, "assessment": a, "view": view, "fred": fred}


def outlook_matrix(inp):
    """Every target × horizon with its published state (research onset included)."""
    rows = []
    gate = {(e["target"], e["horizon_months"]): e for e in inp["forecast"]["evaluations"]}
    for e in inp["research"]["recession_onset"]:
        gate[("recession_onset", e["horizon_months"])] = e
    outlooks = {(o["target"], o["horizon_months"]): o for o in inp["forecast"]["current_outlooks"]}
    for target in ("labor_deterioration", "recession_onset", "recession", "inflation_rising"):
        for h in (3, 6, 12):
            e = gate.get((target, h))
            o = outlooks.get((target, h), {})
            published = bool(e and e["publishable"] and o.get("state") == "Published")
            failed = [k for k, ok in (e or {}).get("gate_checks", {}).items() if not ok]
            rows.append({"target": target, "h": h, "published": published,
                         "p": o.get("probability") if published else None,
                         "text": o.get("probability_text") if published else None,
                         "band": o.get("band") if published else None,
                         "base": o.get("historical_base_rate") or (e and e["full_sample"]["model"]["events"] / max(1, e["full_sample"]["model"]["n"])),
                         "origin": o.get("forecast_origin"), "inputs": o.get("inputs"),
                         "failed": failed, "eval": e})
    return rows


def plain_reason(failed):
    if not failed:
        return "This outlook has not been evaluated yet."
    return "Not enough evidence yet: " + "; ".join(REASON_PLAIN.get(f, f) for f in failed) + "."


PRIORITY_CLASS = {"Worth researching now": "p-now", "Monitor": "p-mon", "Lower priority for now": "p-low"}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def home(inp, matrix):
    v, a = inp["view"], inp["assessment"]
    pub = [r for r in matrix if r["published"]]
    labor = {r["h"]: r for r in matrix if r["target"] == "labor_deterioration"}
    hz = []
    for h in (3, 6, 12):
        r = labor[h]
        state = (f'<strong>{esc(r["text"]).capitalize()}</strong> chance — {esc(r["band"]).lower()} vs history'
                 if r["published"] else "Not enough evidence yet")
        hz.append(f'<div class="hz"><div class="label">Next {h} months</div><div class="state">{state}</div>'
                  f'{probability_bar(r["p"], r["base"] or 0, f"Job market weakens within {h} months")}</div>')
    sectors = sorted(inp["sectors"]["sectors"], key=lambda s: ("Worth researching now", "Monitor", "Lower priority for now").index(s["research_priority"]))
    top = [s for s in sectors if s["research_priority"] == "Worth researching now"]
    chips = "".join(f'<a class="chip good" href="sector-{s["slug"]}.html">{esc(s["sector"])}</a>' for s in top) or \
        '<span class="muted">No sector currently stands out.</span>'
    drivers = "".join(f"<li>{esc(d)}</li>" for d in v["drivers"][:3])
    against = "".join(f"<li>{esc(d)}</li>" for d in (v["counterevidence"] + v.get("evidence_gaps", []))[:3])
    reversal = "".join(f"<li>{esc(d)}</li>" for d in v["reversal_conditions"][1:4] or v["reversal_conditions"])
    n_eval = len([r for r in matrix if r["eval"]])
    body = (
        '<h1>The economy, in plain English</h1>'
        '<p class="lede">Where the U.S. economy is today, where the evidence suggests it may be heading, how much to trust that, '
        'and which sectors deserve a closer look.</p>'
        '<div class="grid cols-2">'
        f'<section class="card hero" aria-labelledby="now"><p class="eyebrow">Where we are</p><h2 id="now" class="big">{esc(v["condition"])}</h2>'
        f'{cycle_gauge(v["condition"], v["direction"])}'
        f'<p>{esc(v["headline"].replace("Our assessment: ", "")[:1].upper() + v["headline"].replace("Our assessment: ", "")[1:])}</p>'
        f'<p><span class="chip">Direction: {esc(v["direction"])}</span><span class="chip">Evidence: {esc(v["evidence_confidence"])}</span></p>'
        f'<small>Based on official data through {esc(a["sources"]["UNRATE"]["latest_used_month"])}. '
        '"Evidence" describes how complete and consistent the data are — not the odds of any event.</small></section>'
        '<section class="card" aria-labelledby="next"><p class="eyebrow">Where we may be heading</p>'
        '<h2 id="next">Chance the job market weakens</h2>'
        f'<div class="horizons">{"".join(hz)}</div>'
        '<p><small>The vertical line marks the historical average. We publish a number only when it has passed our reliability test; '
        'recession and inflation outlooks have not, so we do not show them as forecasts.</small></p>'
        '<p><a href="forecast.html">See every outlook and why →</a></p></section>'
        '</div><div class="grid cols-3" style="margin-top:14px">'
        f'<section class="card" aria-labelledby="sup"><p class="eyebrow">What supports this view</p><h2 id="sup" class="muted" style="font-size:1rem">Evidence for</h2><ul class="clean">{drivers}</ul></section>'
        f'<section class="card" aria-labelledby="ag"><p class="eyebrow">What challenges it</p><h2 id="ag" class="muted" style="font-size:1rem">Evidence against</h2><ul class="clean">{against}</ul></section>'
        f'<section class="card" aria-labelledby="chg"><p class="eyebrow">What would change our view</p><h2 id="chg" class="muted" style="font-size:1rem">Watch for</h2><ul class="clean">{reversal}</ul></section>'
        '</div><div class="grid cols-2" style="margin-top:14px">'
        f'<section class="card" aria-labelledby="sec"><p class="eyebrow">Where to look</p><h2 id="sec">Sectors worth researching now</h2><p>{chips}</p>'
        '<p><small>Based on how each sector has behaved in similar conditions and its recent strength. Not a recommendation; '
        'current valuation data are not yet qualified.</small></p><p><a href="sectors.html">Explore all 11 sectors →</a></p></section>'
        f'<section class="card" aria-labelledby="tr"><p class="eyebrow">How reliable is this?</p><h2 id="tr">{len(pub)} of {n_eval} outlooks pass our test</h2>'
        '<p>We test every outlook against decades of history, using only data that would have been available at the time. '
        'The job-market outlook for the next 12 months passed — including on data as first published. Recession and inflation outlooks did not.</p>'
        '<p><a href="track-record.html">See the full track record →</a></p></section></div>')
    return page("Economic Outlook", "home", body, "Where the economy is, where it may be heading, and which sectors deserve research.")


def forecast(inp, matrix):
    rows = []
    for r in matrix:
        e = r["eval"]
        skill = "" if not e else f'{e["full_sample"]["model"]["bss_vs_base_rate"]:+.2f}'
        auc = "" if not e else f'{e["full_sample"]["model"]["auc"]:.2f}'
        state = (f'<span class="chip good">Published: {esc(r["text"])}</span>' if r["published"]
                 else '<span class="chip muted">Not enough evidence</span>')
        rows.append(f'<tr><th scope="row">{esc(TARGET_LABEL[r["target"]])}</th><td>{r["h"]} months</td><td>{state}</td>'
                    f'<td>{skill}</td><td>{auc}</td></tr>')
    pub = next((r for r in matrix if r["published"]), None)
    detail = ""
    if pub:
        names = {"term_spread": ("Yield curve (10-year minus 3-month, pts)", "Positive means long rates above short rates — historically a calmer sign."),
                 "term_spread_min12": ("Lowest yield-curve reading in the past year", "Inversions (below zero) have preceded past downturns."),
                 "credit_spread": ("Corporate borrowing premium (pts)", "A wider premium signals lenders see more risk."),
                 "unemp_rise": ("Unemployment rise from its yearly low (pts)", "A rise of 0.5 or more has historically signalled trouble."),
                 "payrolls_6m": ("Job growth over 6 months (%)", "Shrinking payrolls are a warning sign.")}
        inputs = "".join(f'<tr><th scope="row">{esc(names[k][0])}</th><td>{v:.2f}</td><td>{esc(names[k][1])}</td></tr>'
                         for k, v in (pub["inputs"] or {}).items() if k in names)
        detail = (f'<section class="card"><p class="eyebrow">Published outlook</p><h2>{esc(TARGET_PLAIN[pub["target"]])} within {pub["h"]} months: {esc(pub["text"])}</h2>'
                  f'{probability_bar(pub["p"], pub["base"], "Job market weakens within 12 months")}'
                  f'<p>That is <strong>{esc(pub["band"]).lower()}</strong> compared with the long-run average of {pub["base"]:.0%}. '
                  f'Forecast made with data through {esc(pub["origin"])}.</p>'
                  f'<h3>What the model is reading</h3><div class="scroll" tabindex="0" role="region" aria-label="Model inputs table"><table><thead><tr><th scope="col">Signal</th><th scope="col">Now</th><th scope="col">Why it matters</th></tr></thead>'
                  f'<tbody>{inputs}</tbody></table></div></section>')
    onset = inp["research"]["recession_onset"]
    body = (
        '<h1>Forecast</h1><p class="lede">Our forward-looking outlooks for 3, 6 and 12 months. Each one is tested against history '
        'before we publish it. If it fails, we say so instead of showing a number.</p>'
        f'{detail}'
        '<section class="card" style="margin-top:14px"><h2>All outlooks</h2><p class="muted">Skill above 0 means better than the long-run average; '
        'the ranking score runs from 0.5 (coin flip) to 1.0.</p><div class="scroll" tabindex="0" role="region" aria-label="All outlooks table">'
        '<table><thead><tr><th scope="col">Outlook</th><th scope="col">Horizon</th>'
        '<th scope="col">Status</th><th scope="col">Skill</th><th scope="col">Ranking</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        '<h3>Why most outlooks are not published</h3><ul class="clean">'
        f'<li><strong>Recession:</strong> {esc(plain_reason([k for k, ok in onset[1]["gate_checks"].items() if not ok]))} '
        'Our models do rank recession risk well, but when they said "very likely", recessions followed much less often than claimed.</li>'
        '<li><strong>Inflation:</strong> no reliable skill with the data we use.</li>'
        '<li><strong>Job market, 3 and 6 months:</strong> probabilities too confident historically.</li></ul>'
        '<p><a href="track-record.html">How we test these →</a></p></section>')
    return page("Forecast", "forecast", body, "Tested 3-, 6- and 12-month economic outlooks.")


def sectors_page(inp):
    order = ("Worth researching now", "Monitor", "Lower priority for now")
    s = sorted(inp["sectors"]["sectors"], key=lambda x: (order.index(x["research_priority"]), -(x["relative_strength_12m_pp"] or 0)))
    test = inp["sectors"]["relative_strength_test"]
    cards = []
    for x in s:
        rs = x["relative_strength_12m_pp"]
        cards.append(f'<a class="card sector-card" href="sector-{x["slug"]}.html"><span class="pill {PRIORITY_CLASS[x["research_priority"]]}">{esc(x["research_priority"])}</span>'
                     f'<h2 style="margin:.4em 0 .2em">{esc(x["sector"])}</h2>'
                     f'<p class="muted" style="margin:0">{esc(x["cycle_class"])} · backdrop: {esc(x["economic_backdrop"])}</p>'
                     f'<p style="margin:.4em 0 0">Past 12 months vs market: <strong>{"n/a" if rs is None else f"{rs:+.1f} pts"}</strong></p></a>')
    bars = diverging_bars([(x["sector"], x["relative_strength_12m_pp"]) for x in s], unit=" pts")
    body = (
        '<h1>Sectors</h1><p class="lede">Which of the 11 market sectors deserve further research right now, and why. '
        'We look at how each sector has behaved in today\'s kind of economy and whether its recent strength is holding. '
        'This is research guidance, not a buy or sell recommendation.</p>'
        f'<div class="note">Current economy: <strong>{esc(inp["view"]["condition"])}</strong>. '
        f'Recent-strength signal: {"historically informative" if test["historically_informative"] else "context only"} '
        f'(tested on {test["periods"]} six-month periods since {test["first_period"][:4]}). '
        'Investment attractiveness: not enough current valuation evidence for any sector.</div>'
        f'<div class="grid cols-3">{"".join(cards)}</div>'
        f'<section class="card" style="margin-top:14px"><h2>Recent strength versus the market</h2><p class="muted">Return over the 12 months ending '
        f'{esc(inp["sectors"]["as_of_month"])} (skipping the latest month), minus the market\'s.</p>{bars}</section>'
        '<details><summary>How sectors are ranked</summary><ul class="clean">'
        '<li><strong>Economic backdrop</strong> comes from how the sector performed relative to the market in past recessions and expansions, matched to today\'s conditions.</li>'
        '<li><strong>Recent strength</strong> counts only because our pre-registered test found it has historically persisted (top minus bottom third: '
        f'{test["mean_spread_pp_per_6m"]:+.1f} pts per 6 months, t={test["t_stat"]}).</li>'
        '<li>"Worth researching now" means both point the same way, or one is clearly positive. It is never a recommendation.</li>'
        '<li>Sectors are approximated with industry portfolios from the Kenneth R. French Data Library, not official GICS indices.</li></ul></details>')
    return page("Sectors", "sectors", body, "Evidence-based research guidance for all 11 market sectors.")


def sector_detail(x, inp):
    sens, val = x["sensitivities"], x["valuation_context"]
    bars = diverging_bars([("In recessions", sens["recession_excess_pct_per_year"]),
                           ("In expansions", sens["expansion_excess_pct_per_year"]),
                           ("High inflation", sens["high_inflation_excess_pct_per_year"]),
                           ("Low inflation", sens["low_inflation_excess_pct_per_year"])], unit="%/yr")
    sup = "".join(f"<li>{esc(t)}</li>" for t in x["supports"]) or "<li>No strong supporting evidence right now.</li>"
    ch = "".join(f"<li>{esc(t)}</li>" for t in x["challenges"]) or "<li>No major contrary evidence flagged.</li>"
    wc = "".join(f"<li>{esc(t)}</li>" for t in x["what_would_change"])
    vrow = ("Not available" if val["forward_pe_median"] is None else
            f'{val["forward_pe_median"]} (market {val["market_forward_pe"]}; {val["forward_pe_vs_market"]:+.0%})')
    rate = sens["rate_beta_pct_per_pp"]
    body = (
        f'<p><a href="sectors.html">← All sectors</a></p><h1>{esc(x["sector"])}</h1>'
        f'<p><span class="pill {PRIORITY_CLASS[x["research_priority"]]}">{esc(x["research_priority"])}</span> '
        f'<span class="chip">{esc(x["cycle_class"])}</span><span class="chip">Backdrop: {esc(x["economic_backdrop"])}</span></p>'
        '<div class="grid cols-2">'
        f'<section class="card"><h2>Why it may deserve attention</h2><ul class="clean">{sup}</ul></section>'
        f'<section class="card"><h2>What argues against it</h2><ul class="clean">{ch}</ul></section>'
        f'<section class="card"><h2>How it has behaved</h2><p class="muted">Average yearly return versus the market, {esc(sens["period"])}.</p>{bars}'
        f'<p>Interest rates: {"n/a" if rate is None else f"{rate:+.1f}% relative return for each 1-point rise in the 10-year yield (monthly average)"}.</p></section>'
        '<section class="card"><h2>Is it attractively priced?</h2>'
        f'<p><strong>{esc(x["investment_attractiveness"])}.</strong> {esc(x["attractiveness_reason"])}</p>'
        f'<table><tbody><tr><th scope="row">Forward P/E (median of industries)</th><td>{esc(vrow)}</td></tr>'
        f'<tr><th scope="row">Expected earnings growth, 5 years</th><td>{"n/a" if val["expected_growth_5y_median_pct"] is None else str(val["expected_growth_5y_median_pct"]) + "%"}</td></tr>'
        f'</tbody></table><p><small>{esc(val["vintage"])}. Source: Aswath Damodaran, NYU Stern.</small></p></section>'
        f'<section class="card"><h2>What would change this view</h2><ul class="clean">{wc}</ul>'
        f'<p><strong>What to watch:</strong> {esc(x["watch"])}</p></section>'
        f'<section class="card"><h2>When the usual pattern failed</h2><p>{esc(x["contrary_case"])}</p></section></div>'
        f'<details><summary>Data and method</summary><p>Sector proxy: equal-weighted Kenneth R. French industry portfolios '
        f'({esc(", ".join(x["proxy_industries"]))}). Relative strength as of {esc(x["relative_strength_as_of"])}. '
        'Recession months follow NBER dating. This page is educational research, not investment advice.</p></details>')
    return page(x["sector"], "sectors", body, f"Economic exposure and research evidence for the {x['sector']} sector.")


def track_page(inp, matrix):
    lab = sorted((r for r in inp["archive"] if r["target"] == "labor_deterioration" and r["h"] == 12), key=lambda r: r["origin"])
    ev = next(e for e in inp["forecast"]["evaluations"] if e["target"] == "labor_deterioration" and e["horizon_months"] == 12)
    fr = next(e for e in inp["research"]["first_release_labor_robustness"] if e["horizon_months"] == 12)
    m, f = ev["full_sample"]["model"], fr["full_sample"]["model"]
    rows = "".join(f'<tr><th scope="row">{esc(TARGET_LABEL[r["target"]])}</th><td>{r["h"]}m</td>'
                   f'<td>{"✓ Passed" if r["published"] else "✗ " + esc(", ".join(CHECK_SHORT.get(k, k) for k in r["failed"]))}</td></tr>' for r in matrix if r["eval"])
    test = inp["sectors"]["relative_strength_test"]
    body = (
        '<h1>Track Record</h1><p class="lede">How our outlooks would have performed in the past, using only information '
        'available at each moment. We show failures as well as successes.</p>'
        '<section class="card"><p class="eyebrow">Our one published outlook</p><h2>Job market weakens within 12 months</h2>'
        f'{track_timeline(lab)}'
        f'<p>Out-of-sample from {esc(ev["evaluation_start"])}: skill <strong>{m["bss_vs_base_rate"]:+.2f}</strong> vs the long-run average, '
        f'ranking score <strong>{m["auc"]:.2f}</strong>, {m["episodes"]} separate episodes. On data <em>as first published</em> '
        f'(no later revisions): skill {f["bss_vs_base_rate"]:+.2f}, ranking {f["auc"]:.2f} — it still passes.</p></section>'
        '<div class="grid cols-2" style="margin-top:14px">'
        f'<section class="card"><h2>Do our probabilities mean what they say?</h2>{calibration_chart(ev["calibration"])}'
        '<p class="muted">Dots near the dashed line mean forecasts of, say, 40% came true about 40% of the time.</p></section>'
        f'<section class="card"><h2>Every outlook we test</h2><div class="scroll" tabindex="0" role="region" aria-label="Outlook test results table"><table><thead><tr><th scope="col">Outlook</th><th scope="col">Horizon</th>'
        f'<th scope="col">Result</th></tr></thead><tbody>{rows}</tbody></table></div>'
        '<p><small>Tests: beats the long-run average, ranks risk well, enough episodes, and probabilities not overconfident.</small></p></section></div>'
        '<section class="card" style="margin-top:14px"><h2>Honest notes</h2><ul class="clean">'
        '<li>The recession-start outlook was registered in advance and evaluated once. It ranks risk well but fails on overconfidence, so it is not published.</li>'
        '<li>We added one recalibration step after our first test showed overconfidence; we flag that as a data-snooping risk.</li>'
        '<li>Only a handful of recessions exist since 1972, so recession results are uncertain.</li>'
        f'<li>Sector recent-strength signal: top-third minus bottom-third {test["mean_spread_pp_per_6m"]:+.1f} pts per 6 months over {test["periods"]} periods '
        f'(t={test["t_stat"]}; sign hit rate {test["sign_hit_rate"]:.0%}).</li></ul>'
        '<p><a href="forecast_archive.csv">Download every past forecast (CSV)</a></p></section>')
    return page("Track Record", "track", body, "Historical performance of every outlook, including failures.")


def research_page(inp):
    body = (
        '<h1>Research &amp; Data</h1><p class="lede">Methods, sources and evidence behind every number on this site.</p>'
        '<details open><summary>How the outlooks work</summary><ul class="clean">'
        '<li>A small logistic model reads the yield curve, corporate borrowing premium, unemployment trend and job growth.</li>'
        '<li>It is re-fitted once a year using only past data, then tested month by month from 1972 against the long-run average, a yield-curve-only model and our earlier descriptive rules.</li>'
        '<li>Market data are used for the current month; government data only once published (one-month lag). Recession dates are used only to score.</li>'
        '<li>An outlook is published only if it beats the average (skill ≥ 0.05), ranks risk well (≥ 0.70), has at least 3 episodes and is not overconfident.</li></ul></details>'
        '<details><summary>How sectors are assessed</summary><ul class="clean">'
        '<li>Economic sensitivity: each sector\'s return versus the market in recessions, expansions, high-inflation months and when the 10-year yield changes, since 1953.</li>'
        '<li>Recent strength: 12-month return versus the market, skipping the latest month; pre-registered persistence test.</li>'
        '<li>Valuation and earnings: Damodaran annual data shown as dated context. A rating needs current, licensed data, so attractiveness stays "not enough evidence".</li></ul></details>'
        '<details><summary>Data sources and attribution</summary><ul class="clean">'
        '<li>Federal Reserve Bank of St. Louis — FRED and ALFRED (economic data, first releases).</li>'
        '<li>Kenneth R. French Data Library, Tuck School of Business at Dartmouth — industry portfolio and market returns.</li>'
        '<li>Aswath Damodaran, NYU Stern — US industry P/E and expected growth (annual).</li>'
        '<li>NBER — U.S. business-cycle dates (scoring only).</li></ul></details>'
        '<details><summary>Limitations</summary><ul class="clean">'
        '<li>Most history uses today\'s revised data; the job-market outlook was re-checked on data as first published.</li>'
        '<li>Few recessions since 1972; recession outlooks remain unpublished.</li>'
        '<li>Sector figures use industry proxies, not official sector indices.</li>'
        '<li>Educational research, not personalized investment advice.</li></ul></details>'
        '<details><summary>Pre-registration and evidence files</summary><p>Pass B analyses were registered in advance '
        '(docs/V7_PREREGISTRATION_PASS_B.md) and evaluated once. Full evidence: docs/evidence/ in the repository.</p></details>')
    return page("Research & Data", "research", body, "Methodology, data sources, limitations and evidence.")


def build(out_dir: Path, inp: dict) -> list:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix = outlook_matrix(inp)
    pages = {"index.html": home(inp, matrix), "forecast.html": forecast(inp, matrix),
             "sectors.html": sectors_page(inp), "track-record.html": track_page(inp, matrix),
             "research.html": research_page(inp)}
    for x in inp["sectors"]["sectors"]:
        pages[f"sector-{x['slug']}.html"] = sector_detail(x, inp)
    for name, content in pages.items():
        if not content.startswith("<!doctype html>"):
            raise ValueError("Invalid page: " + name)
        (out_dir / name).write_text(content)
    with (out_dir / "forecast_archive.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "horizon_months", "origin", "probability", "outcome"])
        w.writerows((r["target"], r["h"], r["origin"], r["probability"], r["outcome"]) for r in inp["archive"])
    return sorted(pages)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast", default="docs/evidence/v7_forecast_evaluation_2026-11-17.json")
    ap.add_argument("--research", default="docs/evidence/v7_passb_forecast_research_2026-11-18.json")
    ap.add_argument("--sectors", default="docs/evidence/v7_sectors_2026-11-18.json")
    ap.add_argument("--archive", default="data/v7/forecast_archive.csv")
    ap.add_argument("--fred-dir", default="data/v7")
    ap.add_argument("--output", default="audit-output/v7-site")
    a = ap.parse_args()
    print(build(Path(a.output), load_inputs(a.forecast, a.research, a.sectors, a.archive, a.fred_dir)))


if __name__ == "__main__":
    main()
