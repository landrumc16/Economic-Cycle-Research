"""V6 static public pages from accepted monthly research. No speculative conclusions."""
import argparse
import html
import json
import math
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
try:
    from .v6_sector_intelligence import build_sector_report
    from .v6_historical_validation import validate_episodes
except ImportError:
    from v6_sector_intelligence import build_sector_report
    from v6_historical_validation import validate_episodes

NAV = (("Overview","overview.html"),("Indicators","economic_dashboard.html"),
       ("Sectors & Industries","sectors.html"),("Historical Comparisons","historical.html"),
       ("Monthly Reports","monthly-research.html"),("Research & Methodology","research.html"))
STYLE = """<style>:root{font:16px system-ui,sans-serif;color:#19334c;background:#f2f6fa}*{box-sizing:border-box}body{max-width:1000px;margin:auto;padding:20px;line-height:1.65}header,section,article,details{background:white;border:1px solid #d8e2ec;border-radius:14px;padding:20px;margin:14px 0;overflow-wrap:anywhere}header{background:#17324c;color:white}header a{color:#e4f5ff}nav{display:flex;flex-wrap:wrap;gap:14px}nav a{padding:4px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.grid article{margin:0}main>section:first-of-type{border-top:5px solid #397ba3}h1,h2,h3{line-height:1.25}h2{margin-top:0}li{margin:7px 0}summary{cursor:pointer;font-weight:600}a:focus-visible{outline:3px solid orange}footer{padding:16px;color:#526579;font-size:.85rem}@media(max-width:600px){body{padding:10px}header,section,article,details{padding:14px}nav{display:grid;grid-template-columns:1fr 1fr;gap:8px}h1{font-size:1.65rem}h2{font-size:1.3rem}}</style>"""

def esc(value):
    return html.escape(str(value), quote=True)

def page(title, content):
    links = "".join(f'<a href="{url}">{esc(label)}</a>' for label,url in NAV)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} — Economic Cycle Research</title>{STYLE}</head><body>'
            f'<header><h1>Economic Cycle Research</h1><p>Daily data. Monthly conclusions. One dashboard.</p><nav aria-label="Main navigation">{links}</nav></header>'
            f'<main><h1>{esc(title)}</h1>{content}</main>'
            '<footer><strong>Educational research — not personalized financial advice.</strong> '
            'This site provides general economic and investment research, not recommendations tailored to any individual. '
            'Historical trends and models can be wrong; past performance does not guarantee future results. '
            'Investing involves risk, including loss of principal. '
            'Consult an appropriately qualified professional about individual circumstances. '
            'Numeric crash forecasts are not certified.</footer></body></html>')

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


def observation_summary(assessment, definitions=INDICATORS, as_of=None):
    """Explain source-dated observations without claiming an economic phase."""
    result = []
    for label, series, metric, description in definitions:
        raw = assessment.get(metric)
        sources = assessment.get("sources")
        sources = sources if isinstance(sources, dict) else {}
        source = sources.get(series)
        source = source if isinstance(source, dict) else {}
        observed = source.get("latest_used_month")
        valid_date = isinstance(observed, str) and len(observed) in (7, 10)
        if valid_date:
            try:
                observation_date = date.fromisoformat(observed + "-01" if len(observed) == 7 else observed)
                valid_date = (len(observed) == 7 or observation_date.isoformat() == observed)
                if as_of is not None and observation_date > as_of:
                    valid_date = False
            except ValueError:
                valid_date = False
        url = source.get("source_url")
        parsed = urlparse(url) if isinstance(url, str) else None
        verified_source = (parsed is not None and parsed.scheme == "https"
                           and bool(parsed.hostname)
                           and parsed.hostname not in {"example.com", "example.org", "example.net"})
        valid_value = (isinstance(raw, (int, float)) and not isinstance(raw, bool)
                       and math.isfinite(raw) and valid_date and verified_source)
        value = f"{raw:.2f}%" if valid_value else "Unavailable"
        result.append({"label": label, "description": description, "value": value,
                       "date": observed if valid_date else "unavailable",
                       "source_url": url if valid_date and verified_source else ""})
    return result


def indicator_guidance(assessment, status, as_of):
    """Plain-language indicator readings; describe evidence, not trading signals."""
    summaries = observation_summary(assessment, as_of=as_of)
    valid = {item["label"]: item for item in summaries if item["value"] != "Unavailable"}
    guidance = {}
    for item in summaries:
        label = item["label"]
        if status != "PASS" or assessment.get("stale") is not False or label not in valid:
            guidance[label] = (
                "Reading: Insufficient current evidence.",
                "What to do with this: Wait for a qualified, source-dated observation before drawing a current conclusion.",
                "What to watch: The next accepted monthly update and any revisions."
            )
            continue
        metric = {"Growth": "industrial_production_growth_12m_log_pct",
                  "Jobs": "unemployment_rate_pct",
                  "Inflation": "cpi_inflation_12m_log_pct",
                  "Business credit": "business_credit_growth_12m_log_pct"}[label]
        value = assessment[metric]
        if label == "Growth":
            reading = ("Production increased from a year earlier." if value > 0 else
                       "Production decreased from a year earlier." if value < 0 else
                       "Production was flat compared with a year earlier.")
            action = ("Monitor whether the expansion in production continues; one positive reading does not confirm broad economic strength." if value > 0 else
                      "Watch for sustained production weakness alongside employment deterioration; this alone does not establish a recession." if value < 0 else
                      "Watch for a sustained move above or below zero before inferring direction.")
            watch = "Next year-over-year production reading, employment trend, and revisions."
        elif label == "Jobs":
            change = assessment.get("unemployment_change_3m_pp")
            month = item["date"]
            observed = date.fromisoformat(month + "-01" if len(month) == 7 else month)
            age = (as_of.year - observed.year) * 12 + as_of.month - observed.month
            if 0 <= age <= 2 and isinstance(change, (int, float)) and not isinstance(change, bool) and math.isfinite(change):
                reading = ("Unemployment rose over three months." if change > 0 else
                           "Unemployment fell over three months." if change < 0 else
                           "Unemployment was unchanged over three months.")
                action = ("Treat the rising unemployment trend as a labor-market caution, not proof of recession." if change > 0 else
                          "Employment conditions are not showing a rising unemployment trend in this measure; continue monitoring." if change < 0 else
                          "The short-term unemployment trend is flat; do not infer acceleration from the level alone.")
            else:
                reading = "The unemployment level is available, but a qualified recent trend is not."
                action = "Do not label the labor market improving or weakening from the unemployment level alone."
            watch = "Three-month unemployment change and consistency with production."
        elif label == "Inflation":
            reading = ("Consumer prices are higher than a year earlier." if value > 0 else
                       "Consumer prices are lower than a year earlier." if value < 0 else
                       "Consumer prices are unchanged from a year earlier.")
            action = "Use this to assess price pressure, not whether inflation is accelerating; that requires comparable consecutive readings."
            watch = "Changes in the inflation rate across qualified monthly observations."
        else:
            reading = ("Business lending grew from a year earlier." if value > 0 else
                       "Business lending contracted from a year earlier." if value < 0 else
                       "Business lending was flat from a year earlier.")
            action = "Treat lending as credit-activity context, not a standalone measure of financial stress or credit availability."
            watch = "Lending trend alongside bank lending standards, defaults and broader financial conditions."
        guidance[label] = (f"Reading: {reading}", f"Interpretation: {action}", f"What to watch: {watch}")
    return guidance


def economic_outlook(assessment, status, as_of):
    """Describe observed growth and employment direction without predicting a cycle phase."""
    result = {"phase": "Not established", "direction": "Not established",
              "summary": "The available evidence does not establish a reliable economic-cycle stage.",
              "reasons": [], "limitations": "Historical similarity is not a validated forecast."}
    if status != "PASS" or assessment.get("stale") is not False:
        result["summary"] = "The latest observations are too old for a current economic-cycle conclusion."
        return result
    verified = {m["label"]: m for m in observation_summary(assessment, as_of=as_of)
                if m["value"] != "Unavailable"}
    if not {"Growth", "Jobs", "Inflation"}.issubset(verified):
        result["summary"] = "Not enough source-dated growth, jobs and inflation observations are available to establish economic direction."
        return result
    growth = assessment["industrial_production_growth_12m_log_pct"]
    inflation = assessment["cpi_inflation_12m_log_pct"]
    change = assessment.get("unemployment_change_3m_pp")
    result["reasons"] = [
        "Industrial production is growing from a year earlier." if growth > 0 else
        "Industrial production is declining from a year earlier." if growth < 0 else
        "Industrial production is flat from a year earlier.",
        "Consumer prices are rising year over year; this does not indicate whether inflation is accelerating." if inflation > 0 else
        "Measured consumer price inflation is not positive year over year."
    ]
    # The trend is derived from the same monthly UNRATE series; its source date must
    # be verified and no older than the accepted monthly research freshness window.
    # Do not mix fresh employment with old growth/inflation observations.
    ages = []
    for label in ("Growth", "Jobs", "Inflation"):
        observed = verified[label]["date"]
        month = date.fromisoformat(observed + "-01" if len(observed) == 7 else observed)
        ages.append((as_of.year - month.year) * 12 + as_of.month - month.month)
    trend_qualified = all(0 <= age <= 2 for age in ages)
    if trend_qualified and isinstance(change, (int, float)) and not isinstance(change, bool) and math.isfinite(change):
        result["reasons"].append(
            "Unemployment increased over three months." if change > 0 else
            "Unemployment decreased over three months." if change < 0 else
            "Unemployment is unchanged over three months.")
        if growth > 0 and change < 0:
            result["direction"] = "Growth and employment improving"
            result["summary"] = "Production is growing and unemployment is falling. These observed conditions suggest resilience, but do not establish a historical cycle phase."
        elif growth < 0 and change > 0:
            result["direction"] = "Growth and employment weakening"
            result["summary"] = "Production is contracting and unemployment is rising. These are warning signs, but do not establish a recession or predict a crash."
        else:
            result["direction"] = "Mixed signals"
            result["summary"] = "Production and employment send mixed signals. A confident directional call is not supported."
    else:
        result["summary"] = "Growth, jobs and inflation are dated, but a qualified employment trend is missing; direction remains unconfirmed."
    return result


def cycle_research_contract(outlook, assessment, as_of):
    """Transparent descriptive candidates; never certified phases or forecasts."""
    direction = outlook["direction"]
    if direction == "Growth and employment improving":
        candidate = "Expansion or recovery (not distinguishable from these observations)"
    elif direction == "Growth and employment weakening":
        candidate = "Slowing expansion or contraction (not distinguishable from these observations)"
    elif direction == "Mixed signals":
        candidate = "Transition or mixed conditions"
    else:
        candidate = "Unclassified"
    return {
        "candidate_phase": candidate,
        "certified_phase": None,
        "method": "Industrial production year-over-year direction and unemployment three-month change; inflation contextual only",
        "independent_historical_episodes_validated": 0,
        "negative_controls_validated": 0,
        "historical_analogues": [],
        "disanalogies": [],
        "uncertainty": "No independent episode and non-downturn holdout validation; descriptive candidate only.",
        "contrary_evidence": (
            ["Growth and employment indicators do not jointly confirm one direction"]
            if direction == "Mixed signals" else []),
        "missing_evidence": [
            "Point-in-time historical episode and non-downturn controls",
            "Independent holdout tests with chronology and embargo safeguards",
            "Verified sector earnings, valuation and benchmark-relative return evidence",
        ],
        "what_would_change_the_view": (
            "New source-dated growth, employment and inflation observations, "
            "and independently validated historical comparisons."
        ),
        "as_of": as_of.isoformat(),
    }


def monthly_changes(folder, monthly_status="PASS", as_of=None, accepted_date=None):
    """Reuse qualified comparisons, never stale research as a current change."""
    if monthly_status != "PASS":
        return "<p>Previous comparable assessment unavailable: monthly data are stale.</p>"
    source = folder / "economic_dashboard.json"
    if not source.is_file():
        return "<p>Previous comparable assessment unavailable.</p>"
    report = json.loads(source.read_text())
    if report.get("status") != "DESCRIPTIVE_DASHBOARD" or report.get("stale") is True:
        return "<p>Previous comparable assessment unavailable.</p>"
    previous = report.get("previous_assessment_date")
    if not previous:
        return "<p>No previous accepted assessment was supplied for comparison.</p>"
    try:
        previous_date = date.fromisoformat(previous)
        current_date = date.fromisoformat(report["assessment_date"])
    except (TypeError, ValueError, KeyError):
        return "<p>Previous comparison dates are missing or invalid.</p>"
    if (previous_date >= current_date or (as_of is not None and current_date > as_of)
            or (accepted_date is not None and current_date != accepted_date)):
        return "<p>Previous comparison chronology is invalid; changes withheld.</p>"
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
    # A stale research-only monthly release cannot certify current sector ratings.
    # Preserve the sector inventory, but withhold investment outlooks entirely.
    sectors = build_sector_report((evidence or {}) if status == "PASS" else {}, as_of)
    assessment_date = gate.get("assessment_date") or assessment.get("assessment_date") or "unavailable"
    if status == "PASS":
        try:
            accepted_date = date.fromisoformat(assessment_date)
        except (TypeError, ValueError):
            raise ValueError("PASS monthly release requires a valid assessment date")
        if accepted_date > as_of:
            raise ValueError("Future-dated monthly assessment cannot be published as current")
    notice = ("<strong>Historical research only:</strong> stale observations do not support a current assessment."
              if status == "STALE_RESEARCH_ONLY" else "Monthly descriptive release gate passed.")
    cards = []
    guidance = indicator_guidance(assessment, status, as_of)
    for metric in observation_summary(assessment, as_of=as_of):
        url = metric["source_url"]
        source_link = (f'<a href="{esc(url)}">Original source</a>' if
                       isinstance(url, str) and url.startswith("https://") else "Source not verified")
        cards.append(f'<article><h2>{esc(metric["label"])}</h2>'
                     f'<p>{esc(metric["description"])}: <strong>{esc(metric["value"])}</strong></p>'
                     f'<p>Observation: {esc(metric["date"])}</p>'
                     + "".join(f'<p>{esc(line)}</p>' for line in guidance[metric["label"]])
                     f'<p>{source_link} · <a href="economic_dashboard.html">Historical context</a></p></article>')
    if status == "PASS" and assessment.get("stale") is True:
        raise ValueError("PASS monthly gate contradicts stale assessment")
    outlook = economic_outlook(assessment, status, as_of)
    reasons = "".join(f"<li>{esc(reason)}</li>" for reason in outlook["reasons"])
    sector_order = {"Favorable": 0, "Mixed": 1, "Caution": 2, "Insufficient Evidence": 3}
    ranked = sorted(sectors["sectors"], key=lambda s: (sector_order.get(s["outlook"], 4), s["sector"]))
    qualified_count = sum(s["outlook"] != "Insufficient Evidence" for s in ranked)
    sector_note = (f"{qualified_count} of 11 sectors currently have evidence-qualified investment outlooks. "
                   "An unqualified sector is not automatically unattractive.")
    # One pass over the sector inventory; keep ranking separate from original detail URLs.
    sector_urls = {s["sector"]: f"sector-{i:02d}.html" for i, s in enumerate(sectors["sectors"], 1)}
    # Do not present an alphabetical sample as a ranked investment shortlist.
    qualified_sectors = [s for s in ranked if s["outlook"] != "Insufficient Evidence"]
    if qualified_sectors:
        featured = qualified_sectors
    else:
        featured = []
    sector_highlights = "".join(
        f'<li><a href="{sector_urls[s["sector"]]}">{esc(s["sector"])}</a>: '
        f'<strong>{esc(s["outlook"])}</strong></li>'
        for s in featured[:5])
    executive = ('<section><h2>Where We Are</h2>'
                 f'<h3>{esc(outlook["phase"])}</h3><p>{esc(outlook["summary"])}</p>'
                 '<h2>Where We Are Heading</h2>'
                 f'<p><strong>{esc(outlook["direction"])}</strong></p>'
                 f'<ul>{reasons}</ul><p>{esc(outlook["limitations"])}</p>'
                 '<p><a href="historical.html">Explore historical comparisons</a></p></section>'
                 '<section><h2>Where Investors Should Look</h2>'
                 '<p>We compare all 11 market sectors, but historical economic fit is not the same as an attractive investment today. '
                 'Only sectors with verified earnings, valuation and historical returns receive an outlook; the others remain Insufficient Evidence.</p>'
                 f'<p>{esc(sector_note)}</p>'
                 + (f'<ol>{sector_highlights}</ol>' if featured else
                    '<p><strong>No sector currently qualifies for a buy-oriented ranking.</strong> '
                    'All 11 remain available for historical economic-sensitivity research.</p>') +
                 '<a href="sectors.html">See all 11 sector assessments</a></section>')
    overview = (f'<section><h2>Where is the economy now?</h2><p>{notice}</p>'
                f'<p>Page generated: {as_of.isoformat()}. Official assessment: {esc(assessment_date)}. Historical observation month: {esc(portal.get("observation_month","unavailable"))}. '
                'Each indicator has its own observation date. Historical analogies are not crash probabilities.</p>'
                '<p><strong>Interpretation:</strong> These are dated observations, not a validated economic-cycle classification. '
                'A change in business lending alone cannot establish financial stress.</p>'
                '<h3>What changed?</h3>' + monthly_changes(folder, status, as_of, accepted_date if status == "PASS" else None) +
                '<h3>What is uncertain?</h3><p>Release lags, revisions, historical-vintage limitations, '
                'and missing sector investment evidence prevent stronger conclusions.</p>'
                '<a href="monthly-research.html">Monthly assessment</a></section>'
                f'<section><h2>Growth, jobs, prices and credit conditions</h2><div class="grid">{"".join(cards)}</div></section>'
                '<section><h2>Sector research</h2><p>Economic sensitivity and investment valuation are separate questions. '
                'Evidence-qualified outlooks appear only when dated research passes validation; otherwise Insufficient Evidence is shown.</p>'
                '<a href="sectors.html">Explore all 11 sectors</a></section>')
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
                   '<p>Historical analogies are not forward-return forecasts. An investment outlook is '
                   'published only when dated earnings, valuation and benchmarked returns pass '
                   'the evidence gate; otherwise the rating is Insufficient Evidence.</p>'
                   '<a href="sectors.html">Back to all sectors</a></section>')
        sector_pages[filename] = page(sector["sector"] + " Research", details)
    sector_cards = "".join(
        f'<article><h2>{esc(s["sector"])}</h2><p><strong>{esc(s["outlook"])}</strong></p>'
        f'<p>{esc(s["reason"])}</p>'
        f'<p>{esc(s["economic_exposure_hypothesis"])}</p>'
        f'<a href="sector-{i:02d}.html">Read sector and industry research</a></article>'
        for i, s in enumerate(sectors["sectors"], start=1))
    descriptions = []
    for metric in observation_summary(assessment, as_of=as_of):
        descriptions.append(f'<li><strong>{esc(metric["label"])}:</strong> {esc(metric["description"])} '
                            f'{esc(metric["value"])} (observed {esc(metric["date"])})</li>')
    monthly = (f'<section><h2>Official monthly gate: {esc(status)}</h2><p>{notice}</p>'
               f'<p>Page generated: {as_of.isoformat()}. Official assessment: {esc(assessment_date)}. Historical observation month: '
               f'{esc(portal.get("observation_month","unavailable"))}.</p>'
               '<h3>Observed conditions</h3><ul>' + "".join(descriptions) + '</ul>'
               '<h3>What changed?</h3>' + monthly_changes(folder, status, as_of, accepted_date if status == "PASS" else None) +
               '<h3>What remains uncertain?</h3><p>Source publication lags, revisions, '
               'historical-vintage limitations and absent sector valuation evidence. '
               'No validated crash probability is available.</p>'
               '<a href="economic_dashboard.html">Changes and indicator details</a> · '
               '<a href="v5_executive_brief.md">Historical research brief</a></section>')
    research = ('<section><h2>Research Library</h2><p>Explore the evidence behind the economic and sector conclusions. '
                'The executive homepage deliberately keeps the technical details here.</p></section>'
                '<details><summary>Economic indicators and observation dates</summary>'
                '<p><a href="economic_dashboard.html">Open dated economic indicators and source data</a></p></details>'
                '<details><summary>Historical cycles and downturn mechanisms</summary>'
                '<p><a href="historical.html">Review historical comparisons</a> and '
                '<a href="v5_dashboard.html">accepted Version 5 historical research</a>.</p></details>'
                '<details><summary>Sector and industry evidence</summary>'
                '<p><a href="sectors.html">Explore all 11 sector assessments</a>. Economic sensitivity and '
                'investment valuation are assessed separately.</p></details>'
                '<details><summary>Monthly research and earlier reports</summary>'
                '<p><a href="monthly-research.html">Official monthly research</a> and '
                '<a href="v5_executive_brief.md">research archive</a>.</p></details>'
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
    outlook["historical_research"] = cycle_research_contract(outlook, assessment, as_of)
    historical_evidence_file = folder / "v6_historical_episodes.json"
    if historical_evidence_file.is_file():
        episodes = json.loads(historical_evidence_file.read_text())
        historical_validation = validate_episodes(episodes, as_of=as_of)
        outlook["historical_research"]["validation"] = historical_validation
        outlook["historical_research"]["independent_historical_episodes_validated"] = historical_validation["independent_events"]
        outlook["historical_research"]["negative_controls_validated"] = historical_validation["negative_controls"]
        # Coverage alone never promotes an observed candidate to a certified phase.
    else:
        outlook["historical_research"]["validation"] = validate_episodes([])
    history_validation = outlook["historical_research"]["validation"]
    history_counts = (
        f'<p>Independently checked contraction episodes: {history_validation["independent_events"]}; '
        f'non-downturn controls: {history_validation["negative_controls"]}; '
        f'other historical phases: {history_validation["other_phases"]}. '
        'These counts do not certify forecasting skill.</p>')
    history = (
        "<section><h2>Historical comparison research</h2>" + historical_note + history_counts +
        "<p>Different market declines can reflect credit contraction, speculative valuation, "
        "industry overinvestment, or external shocks. A matching observation alone does not "
        "identify a crash mechanism or establish inevitability.</p>"
        '<p><a href="v5_dashboard.html">Explore accepted V5 historical research</a> · '
        '<a href="economic_dashboard.html">Inspect source-dated indicators</a></p></section>'
        "<details><summary>Methodology and limitations</summary>"
        "<p>Retrospective data can include later revisions. Matching months can overlap "
        "within the same event, and counterexamples matter. No independently validated "
        "probability or point-in-time predictive skill is asserted.</p></details>")
    pages = {"overview.html":page("Overview",executive+overview),"sectors.html":page("Sectors & Industries",sector_cards),
             "monthly-research.html":page("Monthly Reports",monthly),"research.html":page("Research & Methodology",research),
             "historical.html":page("Historical Comparisons",history)}
    pages.update(sector_pages)
    # Keep the headline and its evidence together for auditing and future expansion.
    outlook["evidence"] = [
        {"indicator": m["label"], "value": m["value"], "observation_date": m["date"],
         "source_url": m["source_url"]}
        for m in observation_summary(assessment, as_of=as_of)
    ]
    # Stage all new output first; never replace accepted files on a validation failure.
    for name, content in pages.items():
        if not content.startswith("<!doctype html>"):
            raise ValueError("Invalid public HTML: " + name)
    for name, content in pages.items():
        (folder/name).write_text(content)
    (folder/"v6_sector_report.json").write_text(json.dumps(sectors,indent=2)+"\n")
    (folder/"v6_1_economic_outlook.json").write_text(json.dumps({
        "schema_version": 1, "generated_as_of": as_of.isoformat(),
        "official_assessment_date": assessment_date,
        "monthly_gate": status, "observed_outlook": outlook,
        "historical_phase_certified": False,
        "numeric_forecasts_approved": False,
        "sector_outlooks_qualified": qualified_count,
        "sector_count": len(sectors["sectors"]),
        "historical_validation": outlook["historical_research"]["validation"],
    }, indent=2) + "\n")

    return {"pages":list(pages),"monthly_status":status,"sector_count":len(sectors["sectors"])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,default=Path("audit-output"))
    p.add_argument("--as-of",type=date.fromisoformat,default=date.today())
    p.add_argument("--sector-evidence",type=Path)
    args=p.parse_args()
    evidence_path = args.sector_evidence or (args.directory / "v6_sector_evidence.json")
    evidence = json.loads(evidence_path.read_text()) if evidence_path.is_file() else None
    print(json.dumps(build(args.directory,args.as_of,evidence)))

if __name__=="__main__":
    main()
