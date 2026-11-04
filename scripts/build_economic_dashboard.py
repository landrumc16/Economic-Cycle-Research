"""Create a portable, self-contained HTML economic research dashboard.

No external JavaScript, data services, or fabricated economic cycle probabilities.
"""
import argparse
import html
import json
from pathlib import Path


FIELDS = (
    ("consumer_credit_growth_12m_log_pct", "Consumer credit", "% log growth / 12m"),
    ("business_credit_growth_12m_log_pct", "Business lending", "% log growth / 12m"),
    ("housing_price_income_growth_gap_12m_log_pp", "Home prices less income", "pp log growth / 12m"),
    ("unemployment_rate_pct", "Unemployment", "%"),
    ("unemployment_change_3m_pp", "Unemployment change", "pp / 3m"),
    ("cpi_inflation_12m_log_pct", "Consumer inflation", "% log growth / 12m"),
    ("industrial_production_growth_12m_log_pct", "Industrial production", "% log growth / 12m"),
)


def delta(current, previous, field):
    a = current.get(field)
    b = previous.get(field) if previous else None
    return round(a - b, 4) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None


def compare(current, previous=None, historical=None):
    if current["status"] != "RESEARCH_SNAPSHOT_NOT_FORECAST":
        raise ValueError("Unapproved assessment status")
    if previous and previous["status"] != "RESEARCH_SNAPSHOT_NOT_FORECAST":
        raise ValueError("Unapproved prior status")
    if previous and previous["assessment_date"] >= current["assessment_date"]:
        raise ValueError("Prior assessment must precede current assessment")
    changed_month = bool(previous and current["common_observation_month"] !=
                         previous["common_observation_month"])
    metrics = []
    for key, title, units in FIELDS:
        metrics.append({"key": key, "title": title, "units": units,
                        "value": current.get(key), "delta": delta(current, previous, key)})
    for key, title in (("equity_acceleration", "Equity acceleration"),
                       ("housing_acceleration", "Housing acceleration")):
        value = current[key]
        old = previous.get(key, {}) if previous else {}
        metrics.append({"key": key, "title": title,
                        "units": "Historical return percentile",
                        "value": value.get("historical_percentile"),
                        "delta": (round(value["historical_percentile"] - old["historical_percentile"], 3)
                                  if isinstance(value.get("historical_percentile"), (int, float))
                                  and isinstance(old.get("historical_percentile"), (int, float))
                                  else None),
                        "high_acceleration": value.get("high_acceleration")})
    return {"status": "DESCRIPTIVE_DASHBOARD",
            "assessment_date": current["assessment_date"],
            "common_observation_month": current["common_observation_month"],
            "stale": current["stale"],
            "months_since_common_observation": current["months_since_common_observation"],
            "previous_assessment_date": previous["assessment_date"] if previous else None,
            "new_observation_month_since_previous": changed_month,
            "metrics": metrics,
            "interpretation": interpret(current),
            "cycle_conditions": cycle_conditions(current),
            "historical_comparison": historical,
            "limitations": current["limitations"],
            "sources": current.get("sources", {}),
            "historical_comparison_stale": current.get("historical_comparison_stale", False)}


def cycle_conditions(current):
    """Transparent condition tags, not an inferred business-cycle phase."""
    if current["stale"]:
        return {"status": "STALE", "tags": [], "reason": "Latest shared observations are stale"}
    required = ("unemployment_change_3m_pp", "industrial_production_growth_12m_log_pct",
                "cpi_inflation_12m_log_pct", "consumer_credit_growth_12m_log_pct",
                "business_credit_growth_12m_log_pct")
    if any(current.get(key) is None for key in required):
        return {"status": "INSUFFICIENT_DATA", "tags": [],
                "reason": "Missing comparable macroeconomic indicators"}
    tags = []
    if current["unemployment_change_3m_pp"] > 0:
        tags.append("LABOR_SOFTENING")
    if current["industrial_production_growth_12m_log_pct"] < 0:
        tags.append("PRODUCTION_CONTRACTION")
    if current["cpi_inflation_12m_log_pct"] > 0:
        tags.append("POSITIVE_INFLATION")
    if (current["consumer_credit_growth_12m_log_pct"] > 0
            and current["business_credit_growth_12m_log_pct"] > 0):
        tags.append("BROAD_CREDIT_EXPANSION")
    for name in ("equity_acceleration", "housing_acceleration"):
        if current[name].get("high_acceleration"):
            tags.append(name.upper())
    return {"status": "DESCRIPTIVE_TAGS_ONLY", "tags": tags,
            "reason": "Conditions are not a calibrated expansion/recession classification"}


def interpret(current):
    if current["stale"]:
        return "Data too stale for a current-conditions interpretation."
    equity = current["equity_acceleration"].get("high_acceleration")
    housing = current["housing_acceleration"].get("high_acceleration")
    credit = [current.get("consumer_credit_growth_12m_log_pct"),
              current.get("business_credit_growth_12m_log_pct")]
    if equity is None or housing is None or any(v is None for v in credit):
        return "Insufficient comparable observations to describe the joint conditions."
    elevated = [name for name, condition in (
        ("equity acceleration", equity),
        ("housing acceleration", housing),
        ("positive consumer-credit growth", credit[0] > 0),
        ("positive business-credit growth", credit[1] > 0),
        ("housing-price growth above income growth",
         (current.get("housing_price_income_growth_gap_12m_log_pp") or 0) > 0)
    ) if condition]
    unemployment_change = current.get("unemployment_change_3m_pp")
    output_growth = current.get("industrial_production_growth_12m_log_pct")
    inflation = current.get("cpi_inflation_12m_log_pct")
    if unemployment_change is None or output_growth is None or inflation is None:
        return "Insufficient labor, production, or inflation coverage for an integrated interpretation."
    pressure = []
    if unemployment_change > 0:
        pressure.append("unemployment rising over three months")
    if output_growth < 0:
        pressure.append("industrial production below its year-earlier level")
    if inflation > 0:
        pressure.append("consumer prices higher than a year earlier")
    expansion_text = ", ".join(elevated) if elevated else "none of the tracked expansion conditions"
    pressure_text = ", ".join(pressure) if pressure else "none of the tracked directional pressures"
    return ("Observed expansion-related conditions: " + expansion_text +
            ". Other macroeconomic conditions: " + pressure_text +
            ". This is a descriptive combination, not a calibrated cycle stage, recession forecast, or crash probability.")


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    def fmt(value):
        return "Unavailable" if value is None else f"{value:+.2f}" if isinstance(value, (float, int)) else esc(value)
    cards = []
    for metric in report["metrics"]:
        note = ("No previous assessment" if report["previous_assessment_date"] is None else
                "No comparable prior value" if metric["delta"] is None else
                "Change since previous assessment: " + fmt(metric["delta"]))
        cards.append(f'<section class="metric"><h2>{esc(metric["title"])}</h2>'
                     f'<strong>{fmt(metric["value"])}</strong>'
                     f'<p>{esc(metric["units"])}</p><small>{esc(note)}</small></section>')
    limitations = "".join(f"<li>{esc(note)}</li>" for note in report["limitations"])
    condition_tags = ", ".join(report["cycle_conditions"]["tags"]) or "None / unavailable"
    historical = report.get("historical_comparison")
    history_text = ("Historical comparison unavailable" if not historical else
                    "Historical comparison unavailable: " + historical["status"]
                    if historical["status"] != "RETROSPECTIVE_DESCRIPTIVE_ONLY" else
                    f"{historical['match_count']} matching months among "
                    f"{historical['historical_months_examined']} prior months. "
                    "These are not independent episodes or predictions.")
    comparison = ("No previous assessment supplied" if report["previous_assessment_date"] is None
                  else f'Previous assessment: {esc(report["previous_assessment_date"])}. '
                       f'New observation month: {esc(report["new_observation_month_since_previous"])}.')
    freshness = "STALE" if report["stale"] else "CURRENT INDICATORS: SOURCE-DATED"
    source_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(name), esc(info.get("latest_used_month", "Unavailable")),
            esc(info.get("observation_lag_months", "Unknown")))
        for name, info in sorted(report.get("sources", {}).items()))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Economic Cycle Research | Monthly Assessment</title>
<style>
:root{{font-family:system-ui,Arial,sans-serif;color-scheme:light;background:#f5f7fa;color:#16263b}}
body{{max-width:1100px;margin:auto;padding:24px}}header{{padding:24px 0;border-bottom:2px solid #ccd7e4}}
h1{{font-size:2rem;margin:0 0 10px}}h2{{font-size:1rem;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:28px 0}}
.metric{{background:white;padding:22px;border:1px solid #dbe3ec;border-radius:10px}}
.metric strong{{display:block;font-size:2rem;font-variant-numeric:tabular-nums}}
.metric p,.metric small{{color:#516277}}main>section{{margin:24px 0}}
.note{{background:#eaf0f7;padding:18px;border-radius:8px;line-height:1.6}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #dbe3ec}}
footer{{border-top:1px solid #ccd7e4;padding-top:18px;color:#516277}}
</style></head><body><header><h1>Economic Cycle Research</h1>
<p>Monthly research assessment · {esc(report["assessment_date"])}</p>
<p><b>{freshness}</b> · Common observation month: {esc(report["common_observation_month"])}
 · Historical alignment lag: {report["months_since_common_observation"]} months</p></header>
<main><div class="grid">{''.join(cards)}</div>
<section><h2>Observed conditions</h2><p class="note">{esc(report["interpretation"])}</p></section>
<section><h2>Cycle-condition tags</h2><p>{esc(condition_tags)}</p><small>Descriptive observations, not a calibrated economic phase.</small></section>
<section><h2>Historical context</h2><p>{esc(history_text)}</p></section>
<section><h2>Change since previous assessment</h2><p>{comparison}</p></section>
<section><h2>Observation dates by source</h2><p>Assessment publication date is not the observation date. Different series have different release schedules.</p><table><thead><tr><th>Series</th><th>Latest observation</th><th>Lag (months)</th></tr></thead><tbody>{source_rows}</tbody></table></section>
<section><h2>Method and limitations</h2><ul>{limitations}</ul></section></main>
<footer>Research-only · Current-vintage monthly observations · No investment advice or validated forecasts</footer>
</body></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("assessment")
    parser.add_argument("--previous")
    parser.add_argument("--historical")
    parser.add_argument("--output-dir", default="audit-output")
    args = parser.parse_args()
    current = json.loads(Path(args.assessment).read_text())
    previous = json.loads(Path(args.previous).read_text()) if args.previous else None
    historical = json.loads(Path(args.historical).read_text()) if args.historical else None
    report = compare(current, previous, historical)
    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "economic_dashboard.json").write_text(json.dumps(report, indent=2) + "\n")
    (target / "economic_dashboard.html").write_text(render(report))
    print("Built economic dashboard for", report["assessment_date"])


if __name__ == "__main__":
    main()
