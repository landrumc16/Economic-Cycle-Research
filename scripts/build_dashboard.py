"""Build a usable, offline, descriptive economic-cycle research dashboard."""
import argparse
import html
import json
from pathlib import Path
from datetime import date

def make_dashboard(current, history, macro=None, refresh=None, assessment=None, analogues=None):
    rows = current["rows"]
    snapshot_date = date.fromisoformat(current["snapshot_date"])
    latest_observation = max((date.fromisoformat(r["observation_date"]) for r in rows if r.get("observation_date")), default=None)
    observation_age = (snapshot_date - latest_observation).days if latest_observation else None
    if observation_age is not None and observation_age < 0:
        raise ValueError("Current snapshot contains an observation after its snapshot date")
    freshness_html = (f'<p class="sub">Latest observation: {latest_observation.isoformat()} '
                      f'({observation_age} days before snapshot). Data may now be older; this is not a live refresh.</p>'
                      if latest_observation else '<p class="sub">No dated observations available.</p>')
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
    stress_rate = (100 * stress / len(months)) if months else None
    quality_counts = {
        "workbook_usable": sum(r.get("workbook_usable") is True for r in rows),
        "model_approved": sum(r.get("human_approved") is True for r in rows),
        "unverified_vintage": sum(r.get("vintage_verified") is not True for r in rows),
    }
    quality_html = ('<section><h2>Source readiness</h2><p class="sub">'
                    + f'{quality_counts["workbook_usable"]} of {len(rows)} workbook-usable observations; '
                    + f'{quality_counts["model_approved"]} model-approved; '
                    + f'{quality_counts["unverified_vintage"]} without verified vintage. '
                    + 'Workbook usability does not authorize predictive use.</p></section>')
    stress_context = (f'{stress} of {len(months)} historical monthly observations ({stress_rate:.1f}%) meet the source stress flag.'
                      if stress_rate is not None else 'No historical monthly observations available.')

    by_id = {r["series_id"]: r for r in rows}
    curve = by_id.get("T10Y2Y")
    credit = by_id.get("BAA10Y")
    # Both contemporaneous inputs must be eligible; missing/unverified is never a zero.
    eligible_pair = all(r is not None and r.get("workbook_usable") is True and
                        r.get("vintage_verified") is True for r in (curve, credit))
    if eligible_pair:
        active = float(curve["value"]) < 0 or float(credit["value"]) >= 2.5
        stress_assessment = ("Historical stress definition met" if active else
                      "Historical stress definition not met")
        explanation = "Both curve and credit spread passed workbook eligibility checks; this is not a crash forecast."
    else:
        stress_assessment = "Not assessable — source eligibility incomplete"
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
            observed = domain.get("latest_date") or "Not available"
            panels.append(f'<article class="card"><small>{esc(label)}</small><h2>{esc(value_label)}</h2><p>{esc(domain.get("unit", ""))}</p><small>Observed: {esc(observed)}</small><span>{esc(descriptor.replace("_", " ").title())}</span></article>')
        macro_html = '<h2>Growth, labor and inflation</h2><p class="sub">Descriptive current-revised research; no validated cycle-stage inference.</p><div class="cards">' + "".join(panels) + "</div>"
    refresh_html = ""
    if isinstance(refresh, dict):
        entries = refresh.get("series", {})
        names = {"UNRATE": "Unemployment", "CPIAUCSL": "Consumer prices", "GDPC1": "Real GDP"}
        cells = []
        for series, label in names.items():
            entry = entries.get(series, {})
            status = entry.get("status", "MISSING")
            observed = entry.get("latest_observation") or "Not available"
            cells.append(f'<article class="card"><small>{esc(label)} · {esc(series)}</small><h2>{esc(status.replace("_", " ").title())}</h2><p>Latest: {esc(observed)}</p><small>Revised-source staging; not point-in-time certified</small></article>')
        refresh_html = '<h2>Economic source refresh</h2><p class="sub">Acquisition status only. Missing source observations are not zeros; historical workbook snapshot remains separate.</p><div class="cards">' + "".join(cells) + '</div>'
    cycle_html = ""
    if isinstance(assessment, dict):
        observed = assessment.get("observed_domains", {})
        descriptions = [f"{key.title()}: {obj.get('interpretation', 'Unknown')}" for key, obj in observed.items()]
        mechanisms = assessment.get("mechanism_lenses", {})
        lenses = "".join(f"<li>{esc(name.replace('_', ' ').title())}: {esc(details.get('status', 'UNKNOWN'))}</li>" for name, details in mechanisms.items())
        cycle_html = '<section><h2>Integrated economic-cycle assessment</h2><p class="sub">' + esc("; ".join(descriptions)) + '</p><p>Crash mechanisms are research lenses, not validated forecasts.</p><ul>' + lenses + '</ul></section>'
    financial_context_html = ""
    if isinstance(assessment, dict):
        financial_context = assessment.get("financial_context", {})
        names = {"credit": "Corporate credit spread", "yield_curve": "Treasury yield curve",
                 "housing_starts": "Housing starts", "household_debt_service": "Household debt service",
                 "equity_volatility": "Market volatility"}
        financial_cards = []
        for key, label in names.items():
            item = financial_context.get(key, {})
            value = item.get("value")
            quality = item.get("quality", "MISSING")
            shown = "Unavailable" if value is None else esc(value)
            date_label = esc(item.get("observation_date") or "No observation")
            financial_cards.append('<article class="card"><small>' + esc(label) + '</small><h2>' +
                shown + '</h2><p>Observed: ' + date_label + '</p><small>Evidence: ' +
                esc(quality.replace("_", " ")) + '</small></article>')
        financial_context_html = ('<section><h2>Financial and housing conditions</h2>'
            '<p class="sub">Dated workbook snapshot; unapproved observations are contextual only. '
            'Different series have different release dates.</p><div class="cards">' +
            "".join(financial_cards) + '</div></section>')
    analogue_html = ""
    if isinstance(analogues, dict):
        entries = analogues.get("analogues", [])
        if analogues.get("status") == "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE":
            items = "".join(
                "<tr><td>" + esc(row.get("episode", "")) + "</td><td>" +
                esc(row.get("normalized_distance", "Unavailable")) + "</td><td>" +
                esc(row.get("status", "")) + "</td></tr>"
                for row in entries
            )
            analogue_html = ('<section><h2>Historical macro similarities</h2>'
                '<p class="sub">GDP, CPI and unemployment only. Smaller distance means closer descriptive resemblance, '
                'not higher crash probability. Historical anchors are hindsight-selected and values are revised.</p>'
                '<div class="scroll"><table><thead><tr><th>Episode</th><th>Normalized distance</th><th>Evidence status</th>'
                '</tr></thead><tbody>' + items + '</tbody></table></div></section>')
        else:
            analogue_html = '<section><h2>Historical macro similarities</h2><p>Unavailable: insufficient comparable data.</p></section>'
    assessment_html = f'<section class="notice"><strong>Current financial-stress screen: {esc(stress_assessment)}</strong><p>{esc(explanation)}</p><small>Rule: 10Y–2Y spread &lt; 0 pp OR Baa–10Y spread ≥ 2.5 pp. Historical descriptive rule only.</small></section>'
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
FRESHNESS<h2>Current research observations</h2><div class="cards">CARDS</div>QUALITY
ASSESSMENTMACROREFRESHCYCLEFINANCIALCONTEXTANALOGUES<h2>Closest historical spread profiles (descriptive only)</h2>COMPARISONS<h2>Historical research coverage</h2><div class="metrics"><div><strong>CLUSTERS</strong>Nasdaq parent crash clusters</div><div><strong>MONTHS</strong>Historical monthly observations</div><div><strong>STRESS</strong>Months flagged for contemporaneous financial stress</div></div>
<p class="sub">HISTORICAL_CONTEXT_TEXT Monthly observations and forward windows overlap; they are not independent trials. Stress is a descriptive flag, not a validated crash predictor.</p>
<h2>Crash pathway comparison</h2><div class="scroll"><table><thead><tr><th>Cluster</th><th>Daily peak</th><th>Prior month</th><th>20% crossing</th><th>Curve (pp)</th><th>Credit (pp)</th><th>Financial stress?</th></tr></thead><tbody>EVENTS</tbody></table></div>
<footer>Authority: SEM_Historical_Crash_Research_v1 · dated manual research snapshots. Publisher-original release verification, untouched holdouts and model approval remain incomplete.</footer></main></html>"""
    for a,b in {"FRESHNESS":freshness_html,"SNAPSHOT":esc(current["snapshot_date"]),"CARDS":"".join(cards),"CLUSTERS":str(len(clusters)),"MONTHS":str(len(months)),"STRESS":str(stress),"EVENTS":"".join(events),"ASSESSMENT":assessment_html,"COMPARISONS":comparison_html,"MACRO":macro_html,"REFRESH":refresh_html,"CYCLE":cycle_html,"FINANCIALCONTEXT":financial_context_html,"ANALOGUES":analogue_html,"QUALITY":quality_html,"HISTORICAL_CONTEXT_TEXT":esc(stress_context)}.items():
        page=page.replace(a,b)
    return page

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--current",default="data/workbook_current_risk_snapshot_2026-10-30.json")
    p.add_argument("--historical",default="data/workbook_historical_research_snapshot_2026-10-30.json")
    p.add_argument("--output",default="dashboard/index.html")
    p.add_argument("--macro",default=None,help="Optional cycle_research_readout.json; missing observations stay unavailable")
    p.add_argument("--json-output",default=None,help="Optional machine-readable dashboard state")
    p.add_argument("--historical-analogues",default=None,help="Optional descriptive historical macro similarities")
    p.add_argument("--cycle-assessment",default=None,help="Optional descriptive current-cycle assessment")
    p.add_argument("--refresh-manifest",default=None,help="Optional source refresh manifest JSON")
    p.add_argument("--strict-macro",action="store_true",help="Fail if the requested macro readout is unavailable")
    p.add_argument("--require-macro-values",action="store_true",help="Fail if growth, labor or inflation observation is missing")
    a=p.parse_args()
    current=json.loads(Path(a.current).read_text())
    historical=json.loads(Path(a.historical).read_text())
    target=Path(a.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    if a.strict_macro and (not a.macro or not Path(a.macro).exists()):
        raise FileNotFoundError("Requested macro readout unavailable")
    macro=json.loads(Path(a.macro).read_text()) if a.macro and Path(a.macro).exists() else None
    refresh=json.loads(Path(a.refresh_manifest).read_text()) if a.refresh_manifest and Path(a.refresh_manifest).exists() else None
    if a.require_macro_values:
        domains = macro.get("domains", {}) if isinstance(macro, dict) else {}
        missing = [key for key in ("growth", "labor", "inflation")
                   if domains.get(key, {}).get("observation") is None]
        if missing:
            raise ValueError("Missing required macro observations: " + ", ".join(missing))
    assessment=json.loads(Path(a.cycle_assessment).read_text()) if a.cycle_assessment and Path(a.cycle_assessment).exists() else None
    analogues=json.loads(Path(a.historical_analogues).read_text()) if a.historical_analogues and Path(a.historical_analogues).exists() else None
    target.write_text(make_dashboard(current,historical,macro,refresh,assessment,analogues),encoding="utf-8")
    if a.json_output:
        state = {
            "snapshot_date": current["snapshot_date"],
            "snapshot_type": current.get("snapshot_type"),
            "publication": "BLOCKED",
            "point_in_time_certified": False,
            "crash_probability": None,
            "validated_cycle_stage": None,
            "macro_domains": macro.get("domains", {}) if isinstance(macro, dict) else {},
            "source_refresh": refresh,
            "current_cycle_assessment": assessment,
            "historical_macro_analogues": analogues,
            "financial_observations": current["rows"],
            "historical_parent_clusters": len(historical["pathways"]["rows"]) - 1,
            "historical_monthly_observations": len(historical["noncrash"]["rows"]) - 1
        }
        output = Path(a.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Built {target}")

if __name__=="__main__":
    main()
