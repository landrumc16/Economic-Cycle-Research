"""Build a usable, offline, descriptive economic-cycle research dashboard."""
import argparse
import html
import json
from pathlib import Path

def make_dashboard(current, history):
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
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Economic Cycle Research | Descriptive Dashboard</title>
<style>body{margin:0;background:#0c1524;color:#e9f0f9;font:16px system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:32px 20px}h1{font-size:32px}h2{font-size:26px;margin:12px 0}.sub{color:#b3c1d4}.notice{border-left:4px solid #e3b96a;padding:12px 18px;background:#263041;margin:22px 0}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}.card{border:1px solid #36465d;background:#18253a;border-radius:12px;padding:18px}.card small,.card p{color:#b3c1d4}.good{color:#a6dfba}.warn{color:#f1c481}.metrics{display:flex;gap:28px;flex-wrap:wrap;margin:25px 0}.metrics strong{font-size:26px;display:block}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:12px;text-align:left;border-bottom:1px solid #35445b}th{color:#b3c1d4}.scroll{overflow-x:auto}a{color:#b9d6ff}footer{color:#aebbd0;margin-top:35px;font-size:13px}</style>
<main><header><h1>Economic Cycle Research</h1><p class="sub">First working descriptive dashboard · Snapshot: SNAPSHOT · no live sync</p></header>
<div class="notice"><strong>Research only — not a forecast.</strong> Current observations are dated workbook exports, not verified real-time data. No cycle-stage prediction, crash probability, investment recommendation, or point-in-time certification is authorized.</div>
<h2>Current research observations</h2><div class="cards">CARDS</div>
<h2>Historical research coverage</h2><div class="metrics"><div><strong>CLUSTERS</strong>Nasdaq parent crash clusters</div><div><strong>MONTHS</strong>Historical monthly observations</div><div><strong>STRESS</strong>Months flagged for contemporaneous financial stress</div></div>
<p class="sub">Monthly observations and forward windows overlap; they are not independent trials. Stress is a descriptive flag, not a validated crash predictor.</p>
<h2>Crash pathway comparison</h2><div class="scroll"><table><thead><tr><th>Cluster</th><th>Daily peak</th><th>Prior month</th><th>20% crossing</th><th>Curve (pp)</th><th>Credit (pp)</th><th>Financial stress?</th></tr></thead><tbody>EVENTS</tbody></table></div>
<footer>Authority: SEM_Historical_Crash_Research_v1 · dated manual research snapshots. Publisher-original release verification, untouched holdouts and model approval remain incomplete.</footer></main></html>"""
    for a,b in {"SNAPSHOT":esc(current["snapshot_date"]),"CARDS":"".join(cards),"CLUSTERS":str(len(clusters)),"MONTHS":str(len(months)),"STRESS":str(stress),"EVENTS":"".join(events)}.items():
        page=page.replace(a,b)
    return page

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--current",default="data/workbook_current_risk_snapshot_2026-10-30.json")
    p.add_argument("--historical",default="data/workbook_historical_research_snapshot_2026-10-30.json")
    p.add_argument("--output",default="dashboard/index.html")
    a=p.parse_args()
    current=json.loads(Path(a.current).read_text())
    historical=json.loads(Path(a.historical).read_text())
    target=Path(a.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(make_dashboard(current,historical),encoding="utf-8")
    print(f"Built {target}")

if __name__=="__main__":
    main()
