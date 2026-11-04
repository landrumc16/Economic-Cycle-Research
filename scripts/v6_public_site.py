"""V6 static public pages from accepted monthly research. No speculative conclusions."""
import argparse
import html
import json
import math
from datetime import date
from pathlib import Path
try:
    from .v6_sector_intelligence import build_sector_report
except ImportError:
    from v6_sector_intelligence import build_sector_report

NAV = (("Overview","overview.html"),("Indicators","economic_dashboard.html"),
       ("Sectors & Industries","sectors.html"),("Historical Comparisons","historical.html"),
       ("Monthly Reports","monthly-research.html"),("Research & Methodology","research.html"))
STYLE = """<style>:root{font:16px system-ui,sans-serif;color:#19334c;background:#f2f6fa}body{max-width:1000px;margin:auto;padding:20px;line-height:1.6}header,section,article,details{background:white;border:1px solid #d8e2ec;border-radius:14px;padding:20px;margin:14px 0}header{background:#17324c;color:white}header a{color:#e4f5ff}nav{display:flex;flex-wrap:wrap;gap:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.grid article{margin:0}summary{cursor:pointer}a:focus-visible{outline:3px solid orange}@media(max-width:600px){body{padding:10px}header,section,article,details{padding:14px}nav{display:grid;grid-template-columns:1fr 1fr}}</style>"""

def esc(value):
    return html.escape(str(value), quote=True)

def page(title, content):
    links = "".join(f'<a href="{url}">{esc(label)}</a>' for label,url in NAV)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} — Economic Cycle Research</title>{STYLE}</head><body>'
            f'<header><h1>Economic Cycle Research</h1><p>Daily data. Monthly conclusions. One dashboard.</p><nav aria-label="Main navigation">{links}</nav></header>'
            f'<main><h1>{esc(title)}</h1>{content}</main><footer>Research-only · Not investment advice · Numeric crash forecasts are not certified.</footer></body></html>')

# Add a sourced indicator by appending (label, source-series, metric-key, definition).
# Existing acquisition/assessment pipelines must supply the metric and source date.
INDICATORS = (
    ("Growth", "INDPRO", "industrial_production_growth_12m_log_pct",
     "Industrial production, 12-month log change"),
    ("Jobs", "UNRATE", "unemployment_rate_pct", "Unemployment rate"),
    ("Inflation", "CPIAUCSL", "cpi_inflation_12m_log_pct",
     "Consumer prices, 12-month log change"),
    ("Business credit", "BUSLOANS", "business_credit_growth_12m_log_pct",
     "Business credit growth, 12-month log change (not a direct financial-stress measure)"),
)


def observation_summary(assessment, definitions=INDICATORS):
    """Explain source-dated observations without claiming an economic phase."""
    result = []
    for label, series, metric, description in definitions:
        raw = assessment.get(metric)
        sources = assessment.get("sources")
        sources = sources if isinstance(sources, dict) else {}
        source = sources.get(series)
        source = source if isinstance(source, dict) else {}
        observed = source.get("latest_used_month")
        valid_date = isinstance(observed, str) and len(observed) == 7
        if valid_date:
            try:
                date.fromisoformat(observed + "-01")
            except ValueError:
                valid_date = False
        valid_value = (isinstance(raw, (int, float)) and not isinstance(raw, bool)
                       and math.isfinite(raw) and valid_date)
        value = f"{raw:.2f}%" if valid_value else "Unavailable"
        result.append({"label": label, "description": description, "value": value,
                       "date": observed if valid_date else "unavailable",
                       "source_url": source.get("source_url", "") if valid_date else ""})
    return result

def monthly_changes(folder):
    """Reuse the accepted descriptive dashboard's prior-period comparison."""
    source = folder / "economic_dashboard.json"
    if not source.is_file():
        return "<p>Previous comparable assessment unavailable.</p>"
    report = json.loads(source.read_text())
    if report.get("status") != "DESCRIPTIVE_DASHBOARD" or report.get("stale") is True:
        return "<p>Previous comparable assessment unavailable.</p>"
    previous = report.get("previous_assessment_date")
    if not previous:
        return "<p>No previous accepted assessment was supplied for comparison.</p>"
    items = []
    metrics = report.get("metrics")
    if not isinstance(metrics, list):
        return "<p>No comparable indicator series were supplied.</p>"
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        delta = metric.get("delta")
        if not isinstance(delta, (int, float)) or isinstance(delta, bool) or not math.isfinite(delta):
            continue
        title = metric.get("title", "Indicator")
        units = metric.get("units", "")
        items.append(f"<li>{esc(title)}: {delta:+.2f} {esc(units)} since {esc(previous)}</li>")
    if not items:
        return "<p>No comparable changes are available; revisions and missing observations may limit comparison.</p>"
    return "<ul>" + "".join(items) + "</ul>"


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
    assessment_date = gate.get("assessment_date") or assessment.get("assessment_date") or "unavailable"
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
    if status == "PASS" and assessment.get("stale") is True:
        raise ValueError("PASS monthly gate contradicts stale assessment")
    overview = (f'<section><h2>Where is the economy now?</h2><p>{notice}</p>'
                f'<p>Page generated: {as_of.isoformat()}. Official assessment: {esc(assessment_date)}. Historical observation month: {esc(portal.get("observation_month","unavailable"))}. '
                'Each indicator has its own observation date. Historical analogies are not crash probabilities.</p>'
                '<p><strong>Interpretation:</strong> These are dated observations, not a validated economic-cycle classification. '
                'A change in business lending alone cannot establish financial stress.</p>'
                '<h3>What changed?</h3>' + monthly_changes(folder) +
                '<h3>What is uncertain?</h3><p>Release lags, revisions, historical-vintage limitations, '
                'and missing sector investment evidence prevent stronger conclusions.</p>'
                '<a href="monthly-research.html">Monthly assessment</a></section>'
                f'<section><h2>Growth, jobs, prices and credit conditions</h2><div class="grid">{"".join(cards)}</div></section>'
                '<section><h2>Sector research</h2><p>Economic sensitivity and investment valuation are separate questions. '
                'Outlooks remain withheld until dated and point-in-time evidence is verified.</p>'
                '<a href="sectors.html">Explore all 11 sectors</a></section>')
    sector_cards = "".join(f'<article><h2>{esc(s["sector"])}</h2><p><strong>{esc(s["outlook"])}</strong></p>'
                           f'<p>{esc(s["reason"])}</p><p><strong>Economic exposure (hypothesis):</strong> '
                           f'{esc(s["economic_exposure_hypothesis"])}</p>'
                           f'<p><strong>Industries to examine:</strong> {esc(s["industry_examples"])}</p>'
                           '<p>These are structural sensitivities, not verified current investment signals.</p>'
                           '<details><summary>Research evidence</summary>'
                           f'<pre style="white-space:pre-wrap;overflow-wrap:anywhere">{esc(json.dumps({"economic_fit":s["economic_fit"],"investment_fit":s["investment_fit"]},indent=2))}</pre></details></article>'
                           for s in sectors["sectors"])
    # Sector-specific deep links keep the summary readable while exposing the
    # evidence and industry distinctions without adding a framework.
    sector_pages = {}
    for index, sector in enumerate(sectors["sectors"], start=1):
        filename = f"sector-{index:02d}.html"
        details = (f'<section><h2>{esc(sector["sector"])}</h2>'
                   f'<p>Research outlook: <strong>{esc(sector["outlook"])}</strong></p>'
                   f'<p>{esc(sector["reason"])}</p>'
                   f'<h3>Economic sensitivity</h3><p>{esc(sector["economic_exposure_hypothesis"])}</p>'
                   f'<h3>Industry distinctions to research</h3><p>{esc(sector["industry_examples"])}</p>'
                   '<p>These industries have different risks; no company-specific conclusion is implied.</p>'
                   '<h3>Investment evidence</h3>'
                   f'<pre style="white-space:pre-wrap;overflow-wrap:anywhere">{esc(json.dumps({"economic_fit":sector["economic_fit"],"investment_fit":sector["investment_fit"]},indent=2))}</pre>'
                   '<p>Historical analogies are not forward-return forecasts. Missing dated earnings, '
                   'valuation and benchmarked returns prevent an investment rating.</p>'
                   '<a href="sectors.html">Back to all sectors</a></section>')
        sector_pages[filename] = page(sector["sector"] + " Research", details)
    sector_cards = "".join(
        f'<article><h2>{esc(s["sector"])}</h2><p><strong>{esc(s["outlook"])}</strong></p>'
        f'<p>{esc(s["reason"])}</p>'
        f'<p>{esc(s["economic_exposure_hypothesis"])}</p>'
        f'<a href="sector-{i:02d}.html">Read sector and industry research</a></article>'
        for i, s in enumerate(sectors["sectors"], start=1))
    descriptions = []
    for metric in observation_summary(assessment):
        descriptions.append(f'<li><strong>{esc(metric["label"])}:</strong> {esc(metric["description"])} '
                            f'{esc(metric["value"])} (observed {esc(metric["date"])})</li>')
    monthly = (f'<section><h2>Official monthly gate: {esc(status)}</h2><p>{notice}</p>'
               f'<p>Page generated: {as_of.isoformat()}. Official assessment: {esc(assessment_date)}. Historical observation month: '
               f'{esc(portal.get("observation_month","unavailable"))}.</p>'
               '<h3>Observed conditions</h3><ul>' + "".join(descriptions) + '</ul>'
               '<h3>What changed?</h3>' + monthly_changes(folder) +
               '<h3>What remains uncertain?</h3><p>Source publication lags, revisions, '
               'historical-vintage limitations and absent sector valuation evidence. '
               'No validated crash probability is available.</p>'
               '<a href="economic_dashboard.html">Changes and indicator details</a> · '
               '<a href="v5_executive_brief.md">Historical research brief</a></section>')
    research = ('<section><h2>Historical research and methodology</h2><p>Accepted Version 5 studies remain available.</p>'
                '<a href="v5_dashboard.html">Historical mechanisms</a> · '
                '<a href="economic_dashboard.html">Dated indicators</a> · '
                '<a href="v5_executive_brief.md">Research archive</a></section>'
                '<details><summary>Methods and limitations</summary><p>Retrospective revised observations are not certified '
                'point-in-time histories. Sector outlooks require sourced earnings, valuation and benchmark-relative total returns. '
                'Missing values are not fabricated. No certified crash probabilities are published.</p></details>')
    # Display only descriptive counts already present in the accepted dashboard.
    historical_note = "<p>Comparable historical observations are unavailable or unqualified.</p>"
    dashboard_file = folder / "economic_dashboard.json"
    if dashboard_file.is_file():
        dashboard = json.loads(dashboard_file.read_text())
        comparison = dashboard.get("historical_comparison")
        if (dashboard.get("status") == "DESCRIPTIVE_DASHBOARD"
                and isinstance(comparison, dict)
                and comparison.get("status") == "RETROSPECTIVE_DESCRIPTIVE_ONLY"):
            matches = comparison.get("match_count")
            examined = comparison.get("historical_months_examined")
            if (isinstance(matches, int) and not isinstance(matches, bool)
                    and isinstance(examined, int) and not isinstance(examined, bool)
                    and 0 <= matches <= examined and examined > 0):
                historical_note = (
                    f"<p>{matches} matching historical months out of {examined} months examined."
                    " Months are not independent economic episodes; this is not a crash probability.</p>")
    history = (
        "<section><h2>Historical comparison research</h2>" + historical_note +
        "<p>Different market declines can reflect credit contraction, speculative valuation, "
        "industry overinvestment, or external shocks. A matching observation alone does not "
        "identify a crash mechanism or establish inevitability.</p>"
        '<p><a href="v5_dashboard.html">Explore accepted V5 historical research</a> · '
        '<a href="economic_dashboard.html">Inspect source-dated indicators</a></p></section>'
        "<details><summary>Methodology and limitations</summary>"
        "<p>Retrospective data can include later revisions. Matching months can overlap "
        "within the same event, and counterexamples matter. No independently validated "
        "probability or point-in-time predictive skill is asserted.</p></details>")
    pages = {"overview.html":page("Overview",overview),"sectors.html":page("Sectors & Industries",sector_cards),
             "monthly-research.html":page("Monthly Reports",monthly),"research.html":page("Research & Methodology",research),
             "historical.html":page("Historical Comparisons",history)}
    pages.update(sector_pages)
    # Stage all new output first; never replace accepted files on a validation failure.
    for name, content in pages.items():
        if not content.startswith("<!doctype html>"):
            raise ValueError("Invalid public HTML: " + name)
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
