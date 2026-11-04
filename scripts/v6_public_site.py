"""V6 static public pages from accepted monthly research. No speculative conclusions."""
import argparse
import html
import json
from datetime import date
from pathlib import Path
try:
    from .v6_sector_intelligence import build_sector_report
except ImportError:
    from v6_sector_intelligence import build_sector_report

NAV = (("Overview","overview.html"),("Indicators","economic_dashboard.html"),
       ("Sectors & Industries","sectors.html"),("Historical Comparisons","v5_dashboard.html"),
       ("Monthly Reports","monthly.html"),("Research & Methodology","research.html"))
STYLE = """<style>:root{font:16px system-ui,sans-serif;color:#19334c;background:#f2f6fa}body{max-width:1000px;margin:auto;padding:20px;line-height:1.6}header,section,article,details{background:white;border:1px solid #d8e2ec;border-radius:14px;padding:20px;margin:14px 0}header{background:#17324c;color:white}header a{color:#e4f5ff}nav{display:flex;flex-wrap:wrap;gap:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.grid article{margin:0}summary{cursor:pointer}a:focus-visible{outline:3px solid orange}@media(max-width:600px){body{padding:10px}header,section,article,details{padding:14px}nav{display:grid;grid-template-columns:1fr 1fr}}</style>"""

def esc(value):
    return html.escape(str(value), quote=True)

def page(title, content):
    links = "".join(f'<a href="{url}">{esc(label)}</a>' for label,url in NAV)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} — Economic Cycle Research</title>{STYLE}</head><body>'
            f'<header><h1>Economic Cycle Research</h1><p>Daily data. Monthly conclusions. One dashboard.</p><nav aria-label="Main navigation">{links}</nav></header>'
            f'<main><h1>{esc(title)}</h1>{content}</main><footer>Research-only · Not investment advice · Numeric crash forecasts are not certified.</footer></body></html>')

def observation_summary(assessment):
    """Explain observations without claiming an economic phase."""
    definitions = (
        ("Growth", "INDPRO", "industrial_production_growth_12m_log_pct",
         "Industrial production, 12-month log change"),
        ("Jobs", "UNRATE", "unemployment_rate_pct", "Unemployment rate"),
        ("Inflation", "CPIAUCSL", "cpi_inflation_12m_log_pct",
         "Consumer prices, 12-month log change"),
        ("Financial stress", "BUSLOANS", "business_credit_growth_12m_log_pct",
         "Business credit, 12-month log change"),
    )
    result = []
    for label, series, metric, description in definitions:
        raw = assessment.get(metric)
        value = f"{raw:.2f}%" if isinstance(raw, (int, float)) and not isinstance(raw, bool) else "Unavailable"
        source = assessment.get("sources", {}).get(series, {})
        result.append({"label": label, "description": description, "value": value,
                       "date": source.get("latest_used_month", "unavailable"),
                       "source_url": source.get("source_url", "")})
    return result

def build(folder, as_of, evidence=None):
    required = ("v5_integrated_acceptance.json","v5_unified_portal.json","weekly_release_acceptance.json","weekly_economic_assessment.json")
    if any(not (folder / n).is_file() for n in required):
        raise ValueError("Missing accepted monthly artifacts")
    acceptance, portal, gate, assessment = [json.loads((folder/n).read_text()) for n in required]
    if acceptance.get("status") != "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED":
        raise ValueError("V5 acceptance not verified")
    status = gate.get("status")
    if status not in ("PASS","STALE_RESEARCH_ONLY") or portal.get("monthly_release") != status:
        raise ValueError("Unqualified monthly assessment")
    if portal.get("numeric_forecasts_approved") is not False:
        raise ValueError("Forecast safeguard violated")
    for name in ("economic_dashboard.html","v5_dashboard.html","v5_executive_brief.md"):
        if not (folder/name).is_file():
            raise ValueError("Missing research link target: "+name)
    sectors = build_sector_report(evidence or {}, as_of)
    notice = ("<strong>Historical research only:</strong> stale observations do not support a current assessment."
              if status == "STALE_RESEARCH_ONLY" else "Monthly descriptive release gate passed.")
    cards = []
    for metric in observation_summary(assessment):
        url = metric["source_url"]
        source_link = (f'<a href="{esc(url)}">Original source</a>' if
                       isinstance(url, str) and url.startswith("https://") else "Source not verified")
        cards.append(f'<article><h2>{esc(metric["label"])}</h2>'
                     f'<p>{esc(metric["description"])}: <strong>{esc(metric["value"])}</strong></p>'
                     f'<p>Observation: {esc(metric["date"])}</p>'
                     f'<p>{source_link} · <a href="economic_dashboard.html">Historical context</a></p></article>')
    overview = (f'<section><h2>Where is the economy now?</h2><p>{notice}</p>'
                f'<p>Report date: {as_of.isoformat()}. Historical observation month: {esc(portal.get("observation_month","unavailable"))}. '
                'Each indicator has its own observation date. Historical analogies are not crash probabilities.</p>'
                '<a href="monthly.html">Monthly assessment</a></section>'
                f'<section><h2>Growth, jobs, prices and vulnerabilities</h2><div class="grid">{"".join(cards)}</div></section>'
                '<section><h2>Sector research</h2><p>Economic sensitivity and investment valuation are separate questions. '
                'Outlooks remain withheld until dated and point-in-time evidence is verified.</p>'
                '<a href="sectors.html">Explore all 11 sectors</a></section>')
    sector_cards = "".join(f'<article><h2>{esc(s["sector"])}</h2><p><strong>{esc(s["outlook"])}</strong></p>'
                           f'<p>{esc(s["reason"])}</p><details><summary>Research evidence</summary>'
                           f'<pre style="white-space:pre-wrap;overflow-wrap:anywhere">{esc(json.dumps({"economic_fit":s["economic_fit"],"investment_fit":s["investment_fit"]},indent=2))}</pre></details></article>'
                           for s in sectors["sectors"])
    monthly = (f'<section><h2>Official monthly gate: {esc(status)}</h2><p>{notice}</p>'
               '<p>Observed strengths, weaknesses and changes require individually dated source evidence; '
               'revisions can alter historical comparisons.</p><a href="economic_dashboard.html">Indicator details</a> · '
               '<a href="v5_executive_brief.md">Historical research brief</a></section>')
    research = ('<section><h2>Historical research and methodology</h2><p>Accepted Version 5 studies remain available.</p>'
                '<a href="v5_dashboard.html">Historical mechanisms</a> · '
                '<a href="economic_dashboard.html">Dated indicators</a> · '
                '<a href="v5_executive_brief.md">Research archive</a></section>'
                '<details><summary>Methods and limitations</summary><p>Retrospective revised observations are not certified '
                'point-in-time histories. Sector outlooks require sourced earnings, valuation and benchmark-relative total returns. '
                'Missing values are not fabricated. No certified crash probabilities are published.</p></details>')
    pages = {"index.html":page("Overview",overview),"overview.html":page("Overview",overview),"sectors.html":page("Sectors & Industries",sector_cards),
             "monthly.html":page("Monthly Reports",monthly),"research.html":page("Research & Methodology",research)}
    for name, content in pages.items():
        (folder/name).write_text(content)
    (folder/"v6_sector_report.json").write_text(json.dumps(sectors,indent=2)+"\n")
    return {"pages":list(pages),"monthly_status":status,"sector_count":len(sectors["sectors"])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,default=Path("audit-output"))
    p.add_argument("--as-of",type=date.fromisoformat,default=date.today())
    p.add_argument("--sector-evidence",type=Path)
    args=p.parse_args()
    evidence=json.loads(args.sector_evidence.read_text()) if args.sector_evidence else None
    print(json.dumps(build(args.directory,args.as_of,evidence)))

if __name__=="__main__":
    main()
