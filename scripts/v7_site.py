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
nav.tabs{position:sticky;bottom:0;background:var(--card);border-top:1px solid var(--line);display:grid;
grid-template-columns:repeat(5,minmax(0,1fr));z-index:6;padding-bottom:env(safe-area-inset-bottom)}
nav.tabs a{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 2px 10px;font-size:.72rem;
color:var(--muted);text-decoration:none;min-height:56px;text-align:center;line-height:1.15;overflow-wrap:anywhere;hyphens:auto;-webkit-hyphens:auto;min-width:0}
nav.tabs a[aria-current=page]{color:var(--brand);font-weight:700}
nav.tabs svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
main{max-width:1120px;margin:auto;padding:18px 16px 24px}
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
footer{max-width:1120px;margin:auto;padding:0 16px 16px;color:var(--muted);font-size:.85rem}
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
/* Pass C compact mobile components */
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.desk{display:none}
.stack{display:grid;gap:12px}
.card.hero svg{max-width:420px}
.card h2.big{font-size:1.9rem;line-height:1.1}
.row-head{display:flex;align-items:baseline;justify-content:space-between;gap:8px;flex-wrap:wrap}
.row-head a{font-weight:600;font-size:.92rem;white-space:nowrap}
ul.rows{list-style:none;margin:8px 0 0;padding:0}
ul.rows li{border-top:1px solid var(--line)}ul.rows li:first-child{border-top:0}
.rowlink,.rowstatic{display:grid;grid-template-columns:1fr auto;gap:4px 10px;align-items:center;padding:9px 0;min-height:48px;color:inherit;text-decoration:none}
.rowlink:hover .rname{text-decoration:underline}
.rname{font-weight:700}.rsub{grid-column:1/-1;font-size:.88rem;color:var(--muted)}
.rval{font-weight:700;font-variant-numeric:tabular-nums;text-align:right}
.mini{position:relative;height:8px;border-radius:4px;background:var(--chip);grid-column:1/-1}
.mini .fill{position:absolute;top:0;bottom:0;left:0;border-radius:4px;background:var(--brand2)}
.mini .base{position:absolute;top:-3px;bottom:-3px;width:2px;background:var(--ink)}
.mini.hatch{background:repeating-linear-gradient(45deg,var(--hatch) 0 3px,transparent 3px 7px)}
.mini.rs .zero{position:absolute;top:-3px;bottom:-3px;left:50%;width:2px;background:var(--muted)}
.mini.rs .pos{position:absolute;top:0;bottom:0;left:50%;border-radius:4px;background:var(--good)}
.mini.rs .neg{position:absolute;top:0;bottom:0;border-radius:4px;background:var(--bad)}
.badges{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.b{font-size:.8rem;font-weight:700;border-radius:8px;padding:3px 8px;background:var(--chip);color:var(--muted);overflow-wrap:anywhere}
.b:not(.ok){background:none;border:1px dashed var(--hatch)}
.b.ok{background:#e3f4ea;color:#14563a}
@media (prefers-color-scheme:dark){.b.ok{background:#163a2a;color:#8ee0b4}}
details.fold{margin:0;border-radius:0;border:0;border-top:1px solid var(--line);padding:0;background:none}
details.fold:first-of-type{border-top:0}
details.fold>summary{padding:12px 0;min-height:48px;display:flex;align-items:center;justify-content:space-between;list-style:none}
details.fold>summary::-webkit-details-marker{display:none}
details.fold>summary::after{content:"+";font-size:1.3rem;color:var(--muted);margin-left:8px}
details.fold[open]>summary::after{content:"−"}
details.fold>div{padding:0 0 12px}
.oneline{margin:.4em 0 0}
.grid>*,.stack>*,.rowlink>*,.rowstatic>*{min-width:0}
main h1,main h2,main p,main li,main summary,.rname,.rsub{overflow-wrap:anywhere}
.row-head a{display:inline-flex;align-items:center;min-height:32px}
code{font-size:.9em;overflow-wrap:anywhere}
@media(max-width:719px){main{padding:12px 14px 16px}.card{padding:14px;border-radius:14px}
h1{font-size:1.35rem;margin:.1em 0 .4em}footer{padding:0 14px 12px}}
@media(min-width:720px){.desk{display:block}nav.primary{display:flex}nav.tabs{display:none}main{padding-bottom:40px}footer{padding-bottom:30px}
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
    w, x0, seg = 320, 10, 100  # compact: 64px tall
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
def mini_prob(p, base):
    if p is None:
        return '<span class="mini hatch" aria-hidden="true"></span>'
    return (f'<span class="mini" aria-hidden="true"><span class="fill" style="width:{100 * p:.0f}%"></span>'
            f'<span class="base" style="left:{100 * base:.0f}%"></span></span>')


def mini_rs(v, top):
    if v is None:
        return '<span class="mini" aria-hidden="true"></span>'
    w = 50 * min(1, abs(v) / top)
    bar = (f'<span class="pos" style="width:{w:.0f}%"></span>' if v >= 0
           else f'<span class="neg" style="left:{50 - w:.0f}%;width:{w:.0f}%"></span>')
    return f'<span class="mini rs" aria-hidden="true"><span class="zero"></span>{bar}</span>'


def fold(title, inner, open_=False):
    return f'<details class="fold"{" open" if open_ else ""}><summary>{esc(title)}</summary><div>{inner}</div></details>'


def home(inp, matrix):
    v, a = inp["view"], inp["assessment"]
    labor = {r["h"]: r for r in matrix if r["target"] == "labor_deterioration"}
    rows = []
    for h in (3, 6, 12):
        r = labor[h]
        val = esc(r["text"]).capitalize() if r["published"] else "Not enough evidence"
        sub = f'{esc(r["band"])} vs the {r["base"]:.0%} historical average' if r["published"] else "Not yet reliable enough to publish"
        aria = (f"Next {h} months: {r['text']} chance, {r['band']} versus a {r['base']:.0%} average" if r["published"]
                else f"Next {h} months: not enough evidence")
        rows.append(f'<li><div class="rowstatic" aria-label="{esc(aria)}"><span class="rname">Next {h} months</span>'
                    f'<span class="rval">{val}</span><span class="rsub">{sub}</span>{mini_prob(r["p"], r["base"] or 0)}</div></li>')
    secs = inp["sectors"]["sectors"]
    top = max(abs(x["relative_strength_12m_pp"] or 0) for x in secs) or 1
    picks = [x for x in secs if x["research_priority"] == "Worth researching now"]
    picks.sort(key=lambda x: -(x["relative_strength_12m_pp"] or 0))
    srows = "".join(
        f'<li><a class="rowlink" href="sector-{x["slug"]}.html"><span class="rname">{esc(x["sector"])}</span>'
        f'<span class="rval">{x["relative_strength_12m_pp"]:+.0f} pts</span>'
        f'<span class="rsub">{esc(x["cycle_class"])} · backdrop {esc(x["economic_backdrop"]).lower()} · past 12 months vs market</span></a></li>'
        for x in picks) or '<li><div class="rowstatic"><span class="rname">No sector stands out right now</span></div></li>'
    pub = [r for r in matrix if r["published"]]
    n_eval = len([r for r in matrix if r["eval"]])
    lst = lambda items: "<ul class=\"clean\">" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"
    headline = v["headline"].replace("Our assessment: ", "")
    body = (
        '<h1>The economy today</h1>'
        '<p class="lede desk">Where the U.S. economy stands, where the evidence suggests it may be heading, and which sectors deserve a closer look.</p>'
        '<div class="grid cols-2">'
        f'<section class="card hero" aria-labelledby="now"><p class="eyebrow">Where we are</p><h2 id="now" class="big">{esc(v["condition"])}</h2>'
        f'{cycle_gauge(v["condition"], v["direction"])}'
        f'<p class="oneline">{esc(headline[:1].upper() + headline[1:])}</p>'
        f'<p class="oneline"><span class="chip">Direction: {esc(v["direction"])}</span><span class="chip">Evidence: {esc(v["evidence_confidence"])}</span></p>'
        f'<small>Data through {esc(a["sources"]["UNRATE"]["latest_used_month"])}. "Evidence" rates data quality, not the odds of any event.</small></section>'
        '<section class="card" aria-labelledby="next"><p class="eyebrow">Where we may be heading</p>'
        '<div class="row-head"><h2 id="next">Chance the job market weakens</h2><a href="forecast.html">Details →</a></div>'
        f'<ul class="rows">{"".join(rows)}</ul>'
        '<p class="oneline"><small>Recession and inflation outlooks: not enough evidence yet. <a href="forecast.html">Why</a></small></p></section>'
        f'<section class="card" aria-labelledby="sec"><p class="eyebrow">Where to look</p>'
        f'<div class="row-head"><h2 id="sec">Sectors worth researching</h2><a href="sectors.html">All 11 →</a></div>'
        f'<ul class="rows">{srows}</ul>'
        '<p class="oneline"><small>Research guidance, not a recommendation. Valuations are not yet qualified.</small></p></section>'
        '<section class="card" aria-labelledby="ev"><h2 id="ev" class="sr-only">Supporting evidence</h2>'
        + fold("Why we think this", lst(v["drivers"][:3]))
        + fold("What could prove us wrong", lst((v["counterevidence"] + v.get("evidence_gaps", []))[:3]))
        + fold("What would change our view", lst(v["reversal_conditions"][1:4] or v["reversal_conditions"]))
        + f'<div class="row-head" style="padding-top:12px;border-top:1px solid var(--line)"><span><strong>{len(pub)} of {n_eval}</strong> outlooks pass our reliability test</span>'
        '<a href="track-record.html">Track record →</a></div></section></div>')
    return page("Economic Outlook", "home", body, "Where the economy is, where it may be heading, and which sectors deserve research.")

def forecast(inp, matrix):
    pub = next((r for r in matrix if r["published"]), None)
    names = {"term_spread": ("Yield curve", "10-year minus 3-month rate; positive is historically calmer."),
             "term_spread_min12": ("Lowest yield curve, past year", "Below zero (inverted) has preceded downturns."),
             "credit_spread": ("Corporate borrowing premium", "Wider means lenders see more risk."),
             "unemp_rise": ("Unemployment rise from yearly low", "0.5 or more has signalled trouble."),
             "payrolls_6m": ("Job growth, 6 months (%)", "Shrinking payrolls are a warning sign.")}
    detail = ""
    if pub:
        inputs = "".join(f'<li><div class="rowstatic"><span class="rname">{esc(names[k][0])}</span><span class="rval">{v:.2f}</span>'
                         f'<span class="rsub">{esc(names[k][1])}</span></div></li>'
                         for k, v in (pub["inputs"] or {}).items() if k in names)
        detail = (f'<section class="card" aria-labelledby="pub"><p class="eyebrow">Published outlook · data through {esc(pub["origin"])}</p>'
                  f'<h2 id="pub">{esc(TARGET_PLAIN[pub["target"]])} within {pub["h"]} months: {esc(pub["text"])}</h2>'
                  f'{probability_bar(pub["p"], pub["base"], "Job market weakens within 12 months")}'
                  f'<p class="oneline"><strong>{esc(pub["band"])}</strong> compared with the long-run average of {pub["base"]:.0%} (the vertical line).</p>'
                  + fold("What the model is reading", f'<ul class="rows">{inputs}</ul>') + '</section>')
    groups = []
    for target in ("labor_deterioration", "recession_onset", "recession", "inflation_rising"):
        rs = [r for r in matrix if r["target"] == target]
        badges = "".join(f'<span class="b ok">{r["h"]} months: {esc(r["text"])}</span>' if r["published"] else
                         f'<span class="b">{r["h"]} months<span class="sr-only">: not enough evidence</span></span>'
                         for r in rs)
        failed = sorted({f for r in rs if not r["published"] for f in r["failed"]})
        why = plain_reason(failed) if failed else "Published: it passed our test."
        if failed and any(r["published"] for r in rs):
            gaps = " and ".join(f'{r["h"]}' for r in rs if not r["published"])
            why = f"{gaps} months — " + why[:1].lower() + why[1:]
        groups.append(f'<li><div class="rowstatic"><span class="rname">{esc(TARGET_LABEL[target])}</span>'
                      f'<span class="rsub">{esc(TARGET_PLAIN[target])} within 3, 6 or 12 months.</span>'
                      f'<span class="badges" style="grid-column:1/-1;justify-content:flex-start">{badges}</span>'
                      f'<span class="rsub">{esc(why)}</span></div></li>')
    body = (
        '<h1>Forecast</h1><p class="lede">Each outlook is tested against history before we publish it. If it fails, we say so instead of showing a number.</p>'
        f'<div class="stack">{detail}'
        f'<section class="card" aria-labelledby="all"><div class="row-head"><h2 id="all">All outlooks</h2><a href="track-record.html">Test results →</a></div>'
        f'<ul class="rows">{"".join(groups)}</ul></section></div>')
    return page("Forecast", "forecast", body, "Tested 3-, 6- and 12-month economic outlooks.")

def sectors_page(inp):
    order = ("Worth researching now", "Monitor", "Lower priority for now")
    items = inp["sectors"]["sectors"]
    top = max(abs(x["relative_strength_12m_pp"] or 0) for x in items) or 1
    test = inp["sectors"]["relative_strength_test"]
    groups = []
    for pr in order:
        xs = sorted((x for x in items if x["research_priority"] == pr), key=lambda x: -(x["relative_strength_12m_pp"] or 0))
        if not xs:
            continue
        rows = "".join(
            f'<li><a class="rowlink" href="sector-{x["slug"]}.html"><span class="rname">{esc(x["sector"])}</span>'
            f'<span class="rval">{"n/a" if x["relative_strength_12m_pp"] is None else f"{x["relative_strength_12m_pp"]:+.0f} pts"}</span>'
            f'<span class="rsub">{esc(x["cycle_class"])} · backdrop {esc(x["economic_backdrop"]).lower()}</span>'
            f'{mini_rs(x["relative_strength_12m_pp"], top)}</a></li>' for x in xs)
        groups.append(f'<section class="card" aria-labelledby="g-{PRIORITY_CLASS[pr]}"><div class="row-head">'
                      f'<h2 id="g-{PRIORITY_CLASS[pr]}"><span class="pill {PRIORITY_CLASS[pr]}">{esc(pr)}</span></h2>'
                      f'<small>{len(xs)} sector{"s" if len(xs) != 1 else ""}</small></div><ul class="rows">{rows}</ul></section>')
    method = ('<ul class="clean">'
              '<li><strong>Backdrop</strong>: how the sector did versus the market in past recessions and expansions, matched to today\'s economy.</li>'
              f'<li><strong>Recent strength</strong> (bars: past 12 months vs market, skipping the latest month) counts because our pre-registered test found it has persisted: '
              f'{test["mean_spread_pp_per_6m"]:+.1f} pts per 6 months, t={test["t_stat"]}, {test["periods"]} periods since {test["first_period"][:4]}.</li>'
              '<li>"Worth researching now" means the evidence points the same way. It is never a recommendation.</li>'
              '<li>Investment attractiveness needs current, licensed valuation data, which is not yet available, so every sector shows "Insufficient evidence".</li>'
              '<li>Sectors are approximated with Kenneth R. French industry portfolios, not official GICS indices.</li></ul>')
    body = (
        '<h1>Sectors</h1>'
        f'<p class="lede">Which sectors deserve research in today\'s <strong>{esc(inp["view"]["condition"]).lower()}</strong> economy, '
        f'based on cycle behaviour and recent strength (to {esc(inp["sectors"]["as_of_month"])}). Not a buy or sell recommendation.</p>'
        f'<div class="stack">{"".join(groups)}<section class="card">{fold("How sectors are ranked", method)}</section></div>')
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
    rate = sens["rate_beta_pct_per_pp"]
    vrow = ("not available" if val["forward_pe_median"] is None else
            f'{val["forward_pe_median"]} vs market {val["market_forward_pe"]} ({val["forward_pe_vs_market"]:+.0%})')
    rs = x["relative_strength_12m_pp"]
    behaved = (f'<p class="muted oneline">Average yearly return vs the market, {esc(sens["period"])}.</p>{bars}'
               f'<p>Each 1-point rise in the 10-year yield: {"n/a" if rate is None else f"{rate:+.1f}%"} relative return (monthly).</p>')
    priced = (f'<p><strong>{esc(x["investment_attractiveness"])}.</strong> {esc(x["attractiveness_reason"])}</p>'
              f'<p>Forward P/E: {esc(vrow)}. Expected 5-year earnings growth: '
              f'{"n/a" if val["expected_growth_5y_median_pct"] is None else str(val["expected_growth_5y_median_pct"]) + "%"}.</p>'
              f'<p><small>{esc(val["vintage"])}. Source: Aswath Damodaran, NYU Stern.</small></p>')
    method = (f'<p>Sector proxy: equal-weighted Kenneth R. French industry portfolios ({esc(", ".join(x["proxy_industries"]))}). '
              f'Relative strength as of {esc(x["relative_strength_as_of"])}. Recession months follow NBER dating. Educational research, not investment advice.</p>')
    body = (
        f'<p class="oneline"><a href="sectors.html">← All sectors</a></p><h1>{esc(x["sector"])}</h1>'
        f'<p><span class="pill {PRIORITY_CLASS[x["research_priority"]]}">{esc(x["research_priority"])}</span> '
        f'<span class="chip">{esc(x["cycle_class"])}</span><span class="chip">Backdrop: {esc(x["economic_backdrop"])}</span>'
        f'<span class="chip">12 months: {"n/a" if rs is None else f"{rs:+.1f} pts vs market"}</span></p>'
        '<div class="grid cols-2">'
        f'<section class="card"><h2>Why it may deserve attention</h2><ul class="clean">{sup}</ul></section>'
        f'<section class="card"><h2>What argues against it</h2><ul class="clean">{ch}</ul></section>'
        f'<section class="card"><h2>What would change this view</h2><ul class="clean">{wc}</ul><p class="oneline"><strong>Watch:</strong> {esc(x["watch"])}</p></section>'
        '<section class="card"><h2 class="sr-only">More evidence</h2>'
        + fold("How it has behaved", behaved) + fold("Is it attractively priced?", priced)
        + fold("When the usual pattern failed", f'<p>{esc(x["contrary_case"])}</p>') + fold("Data and method", method)
        + '</section></div>')
    return page(x["sector"], "sectors", body, f"Economic exposure and research evidence for the {x['sector']} sector.")

def track_page(inp, matrix):
    lab = sorted((r for r in inp["archive"] if r["target"] == "labor_deterioration" and r["h"] == 12), key=lambda r: r["origin"])
    ev = next(e for e in inp["forecast"]["evaluations"] if e["target"] == "labor_deterioration" and e["horizon_months"] == 12)
    fr = next(e for e in inp["research"]["first_release_labor_robustness"] if e["horizon_months"] == 12)
    m, f = ev["full_sample"]["model"], fr["full_sample"]["model"]
    rows = []
    for target in ("labor_deterioration", "recession_onset", "recession", "inflation_rising"):
        rs = [r for r in matrix if r["target"] == target and r["eval"]]
        badges = "".join(
            f'<span class="b{" ok" if r["published"] else ""}">{r["h"]}m <span aria-hidden="true">{"✓" if r["published"] else "✗"}</span>'
            f'<span class="sr-only">{" passes" if r["published"] else " fails"}</span></span>' for r in rs)
        detail = "; ".join(
            f'{r["h"]}m: skill {r["eval"]["full_sample"]["model"]["bss_vs_base_rate"]:+.2f}, ranking {r["eval"]["full_sample"]["model"]["auc"]:.2f}'
            + ("" if r["published"] else " — " + ", ".join(CHECK_SHORT.get(k, k) for k in r["failed"])) for r in rs)
        rows.append(f'<li><div class="rowstatic"><span class="rname">{esc(TARGET_LABEL[target])}</span><span class="badges">{badges}</span>'
                    f'<span class="rsub">{esc(detail)}</span></div></li>')
    test = inp["sectors"]["relative_strength_test"]
    notes = ('<ul class="clean">'
             '<li>The recession-start outlook was registered in advance and evaluated once; it ranks risk well but is too confident, so it is not published.</li>'
             '<li>We added one recalibration step after our first test showed overconfidence — a data-snooping risk we disclose.</li>'
             '<li>Only a handful of recessions since 1972, so recession results are uncertain.</li>'
             f'<li>Sector recent-strength signal: {test["mean_spread_pp_per_6m"]:+.1f} pts per 6 months over {test["periods"]} periods '
             f'(t={test["t_stat"]}; weaker in recent decades: {test["first_half_mean"]:+.1f} then {test["second_half_mean"]:+.1f}).</li></ul>')
    body = (
        '<h1>Track Record</h1><p class="lede">How each outlook would have performed in the past, using only information available at the time. Failures included.</p>'
        '<div class="stack">'
        '<section class="card" aria-labelledby="lab"><p class="eyebrow">Our published outlook</p><h2 id="lab">Job market weakens within 12 months</h2>'
        f'{track_timeline(lab)}'
        f'<p class="oneline">Since {esc(ev["evaluation_start"][:4])}: skill <strong>{m["bss_vs_base_rate"]:+.2f}</strong>, ranking <strong>{m["auc"]:.2f}</strong>, '
        f'{m["episodes"]} episodes. On data as first published: {f["bss_vs_base_rate"]:+.2f} / {f["auc"]:.2f} — still passes.</p>'
        + fold("Do our probabilities mean what they say?", calibration_chart(ev["calibration"])
               + '<p class="muted">Dots near the dashed line: forecasts of 40% came true about 40% of the time.</p>')
        + '</section>'
        '<section class="card" aria-labelledby="tests"><h2 id="tests">Every outlook we test</h2>'
        '<p class="muted oneline">Skill above 0 beats the long-run average; ranking runs from 0.5 (coin flip) to 1.0.</p>'
        f'<ul class="rows">{"".join(rows)}</ul></section>'
        f'<section class="card"><h2 class="sr-only">Notes and data</h2>{fold("Honest notes", notes)}'
        '<p class="oneline"><a href="forecast_archive.csv">Download every past forecast (CSV)</a></p></section></div>')
    return page("Track Record", "track", body, "Historical performance of every outlook, including failures.")

def research_page(inp):
    body = (
        '<h1>Research &amp; Data</h1><p class="lede">Methods, sources and evidence behind every number on this site.</p>'
        '<section class="card">'
        '<details class="fold" open><summary>How the outlooks work</summary><div><ul class="clean">'
        '<li>A small logistic model reads the yield curve, corporate borrowing premium, unemployment trend and job growth.</li>'
        '<li>It is re-fitted once a year using only past data, then tested month by month from 1972 against the long-run average, a yield-curve-only model and our earlier descriptive rules.</li>'
        '<li>Market data are used for the current month; government data only once published (one-month lag). Recession dates are used only to score.</li>'
        '<li>An outlook is published only if it beats the average (skill ≥ 0.05), ranks risk well (≥ 0.70), has at least 3 episodes and is not overconfident.</li></ul></div></details>'
        '<details class="fold"><summary>How sectors are assessed</summary><div><ul class="clean">'
        '<li>Economic sensitivity: each sector\'s return versus the market in recessions, expansions, high-inflation months and when the 10-year yield changes, since 1953.</li>'
        '<li>Recent strength: 12-month return versus the market, skipping the latest month; pre-registered persistence test.</li>'
        '<li>Valuation and earnings: Damodaran annual data shown as dated context. A rating needs current, licensed data, so attractiveness stays "not enough evidence".</li></ul></div></details>'
        '<details class="fold"><summary>Data sources and attribution</summary><div><ul class="clean">'
        '<li>Federal Reserve Bank of St. Louis — FRED and ALFRED (economic data, first releases).</li>'
        '<li>Kenneth R. French Data Library, Tuck School of Business at Dartmouth — industry portfolio and market returns.</li>'
        '<li>Aswath Damodaran, NYU Stern — US industry P/E and expected growth (annual).</li>'
        '<li>NBER — U.S. business-cycle dates (scoring only).</li></ul></div></details>'
        '<details class="fold"><summary>Limitations</summary><div><ul class="clean">'
        '<li>Most history uses today\'s revised data; the job-market outlook was re-checked on data as first published.</li>'
        '<li>Few recessions since 1972; recession outlooks remain unpublished.</li>'
        '<li>Sector figures use industry proxies, not official sector indices.</li>'
        '<li>Educational research, not personalized investment advice.</li></ul></div></details>'
        '<details class="fold"><summary>Pre-registration and evidence files</summary><div><p>Pass B analyses were registered in advance '
        '(<code>docs/V7_PREREGISTRATION_PASS_B.md</code>) and evaluated once. Full evidence: <code>docs/evidence/</code> in the repository.</p></div></details></section>')
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
