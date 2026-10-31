"""Build a usable, offline, descriptive economic-cycle research dashboard."""
import argparse
import html
import json
from pathlib import Path

def make_dashboard(current, history, macro=None):
    rows = current["rows"]
    clusters = history["pathways"]["rows"][1:]
    months = history["noncrash"]["rows"][1:]
    def esc(v):
        return html.escape(str(v))
    cards = []
    for r in rows:
        eligible = r.get("workbook_usable") is True
        cards.append(f'<article class="card"><small>{esc(r["series_id"])} · {esc(r["observation_date"])}</small><h2>{esc(r["value"])}</h2><p>{esc(r["unit"])}</p><span class="{"good" if eligible else "warn"}">{"Workbook usable; model unapproved" if eligible else "Not eligible for model"}</span></article>')
    events = []
    for r in clusters:
        events.append("<tr>"+"".join(f"<td>{esc(x)}</td>" for x in (r[0],r[1],r[2],r[3],r[5],r[6],r[11]))+"</tr>")
    stress = sum(1 for r in months if r[4]=="YES")
    by_id = {r["series_id"]: r for r in rows}
    curve = by_id.get("T10Y2Y")
    credit = by_id.get("BAA10Y")
    # Both contemporaneous inputs must be eligible; missing/unverified is never a zero.
    eligible_pair = all(r is not None and r.get("workbook_usable") is True and
                        r.get("vintage_verified") is True for r in (curve, credit))
    if eligible_pair:
        active = float(curve["value"]) < 0 or float(credit["value"]) >= 2.5
        assessment = ("Historical stress definition met" if active else
                      "Historical stress definition not met")
        explanation = "Both curve and credit spread passed workbook eligibility checks; this is not a crash forecast."
    else:
        assessment = "Not assessable — source eligibility incomplete"
        explanation = "Yield curve and credit spread must both be verified and workbook-usable; an unverified observation cannot be treated as a negative signal."
    macro_html = ""
    if isinstance(macro, dict):
        domains = macro.get("domains", {})
        labels = (("growth", "Real GDP growth"), ("labor", "Unemployment trend"), ("inflation", "Consumer price inflation"))
        panels = []
        for key, label in labels:
            domain = domains.get(key, {})
            value = domain.get("observation")
            value_label = "Unavailable" if value is None else f"{value:g}"
            descriptor = domain.get("description", "MISSING")
            panels.append(f'<article class="card"><small>{esc(label)}</small><h2>{esc(value_label)}</h2><p>{esc(domain.get("unit", ""))}</p><span>{esc(descriptor.replace("_", " ").title())}</span></article>')
        macro_html = '<h2>Growth, labor and inflation</h2><p class="sub">Descriptive current-revised research; no validated cycle-stage inference.</p><div class="cards">' + "".join(panels) + "</div>"
    assessment_html = f'<section class="notice"><strong>Current financial-stress screen: {esc(assessment)}</strong><p>{esc(explanation)}</p><small>Rule: 10Y–2Y spread &lt; 0 pp OR Baa–10Y spread ≥ 2.5 pp. Historical descriptive rule only.</small></section>'
    # Historical comparisons are based on observed spread proximity, not inferred crash likelihood.
    comparisons = []
    if eligible_pair:
        for row in clusters:
            try:
                distance = abs(float(row[5])-float(curve["value"])) + abs(float(row[6])-float(credit["value"]))
                comparisons.append((distance,row))
            except (ValueError, TypeError):
                continue
        comparisons.sort(key=lambda x:x[0])
    comparison_html = ("<ol>" + "".join(f"<li>{esc(r[1])} — curve {esc(r[5])} pp; credit {esc(r[6])} pp</li>" for _,r in comparisons[:3]) + "</ol>") if comparisons else "<p>Unavailable until both current financial spread inputs are eligible.</p>"
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Economic Cycle Research | Descriptive Dashboard</title>
<style>body{margin:0;background:#0c1524;color:#e9f0f9;font:16px system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:32px 20px}h1{font-size:32px}h2{font-size:26px;margin:12px 0}.sub{color:#b3c1d4}.notice{border-left:4px solid #e3b96a;padding:12px 18px;background:#263041;margin:22px 0}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}.card{border:1px solid #36465d;background:#18253a;border-radius:12px;padding:18px}.card small,.card p{color:#b3c1d4}.good{color:#a6dfba}.warn{color:#f1c481}.metrics{display:flex;gap:28px;flex-wrap:wrap;margin:25px 0}.metrics strong{font-size:26px;display:block}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:12px;text-align:left;border-bottom:1px solid #35445b}th{color:#b3c1d4}.scroll{overflow-x:auto}a{color:#b9d6ff}footer{color:#aebbd0;margin-top:35px;font-size:13px}</style>
<main><header><h1>Economic Cycle Research</h1><p class="sub">First working descriptive dashboard · Snapshot: SNAPSHOT · no live sync</p></header>
<div class="notice"><strong>Research only — not a forecast.</strong> Current observations are dated workbook exports, not verified real-time data. No cycle-stage prediction, crash probability, investment recommendation, or point-in-time certification is authorized.</div>
<h2>Current research observations</h2><div class="cards">CARDS</div>
ASSESSMENTMACRO<h2>Closest historical spread profiles (descriptive only)</h2>COMPARISONS<h2>Historical research coverage</h2><div class="metrics"><div><strong>CLUSTERS</strong>Nasdaq parent crash clusters</div><div><strong>MONTHS</strong>Historical monthly observations</div><div><strong>STRESS</strong>Months flagged for contemporaneous financial stress</div></div>
<p class="sub">Monthly observations and forward windows overlap; they are not independent trials. Stress is a descriptive flag, not a validated crash predictor.</p>
<h2>Crash pathway comparison</h2><div class="scroll"><table><thead><tr><th>Cluster</th><th>Daily peak</th><th>Prior month</th><th>20% crossing</th><th>Curve (pp)</th><th>Credit (pp)</th><th>Financial stress?</th></tr></thead><tbody>EVENTS</tbody></table></div>
<footer>Authority: SEM_Historical_Crash_Research_v1 · dated manual research snapshots. Publisher-original release verification, untouched holdouts and model approval remain incomplete.</footer></main></html>"""
    for a,b in {"SNAPSHOT":esc(current["snapshot_date"]),"CARDS":"".join(cards),"CLUSTERS":str(len(clusters)),"MONTHS":str(len(months)),"STRESS":str(stress),"EVENTS":"".join(events),"ASSESSMENT":assessment_html,"COMPARISONS":comparison_html,"MACRO":macro_html}.items():
        page=page.replace(a,b)
    return page

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--current",default="data/workbook_current_risk_snapshot_2026-10-30.json")
    p.add_argument("--historical",default="data/workbook_historical_research_snapshot_2026-10-30.json")
    p.add_argument("--output",default="dashboard/index.html")\n    p.add_argument("--macro",default=None,help="Optional cycle_research_readout.json; missing observations stay unavailable")
    a=p.parse_args()
    current=json.loads(Path(a.current).read_text())
    historical=json.loads(Path(a.historical).read_text())
    target=Path(a.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    macro=json.loads(Path(a.macro).read_text()) if a.macro and Path(a.macro).exists() else None\n    target.write_text(make_dashboard(current,historical,macro),encoding="utf-8")
    print(f"Built {target}")

if __name__=="__main__":
    main()
