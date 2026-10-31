"""V4 offline dashboard: augment the accepted V3 view without modifying it."""
import argparse
import html
import json
from pathlib import Path
try:
    from scripts.v3_weekly_dashboard import render as render_v3
except ModuleNotFoundError:
    from v3_weekly_dashboard import render as render_v3

def render(v3, readiness, signals, mechanisms, episodes):
    if (readiness.get("report_type") != "V4_WEEKLY_DATA_READINESS"
        or signals.get("report_type") != "V4_EXPLAINABLE_ECONOMIC_SIGNALS"
        or mechanisms.get("report_type") != "V4_MULTI_MECHANISM_ASSESSMENT"
        or episodes.get("report_type") != "V4_HISTORICAL_EPISODE_REGISTRY"):
        raise ValueError("Incomplete V4 evidence contracts")
    if len({v3["as_of"], readiness["as_of"], signals["as_of"], mechanisms["as_of"]}) != 1:
        raise ValueError("Mismatched reporting dates")
    if any(x.get("predictive_publication") != "BLOCKED" for x in (readiness, signals, mechanisms, episodes)):
        raise ValueError("Predictive gate must remain blocked")
    e = lambda x: html.escape(str(x), quote=True)
    coverage = (f'<section><h2>Version 4 data readiness</h2><p>{e(readiness["numeric_sources"])} numeric series of '
                f'{e(readiness["series_count"])} tracked; {e(readiness["series_with_prior_snapshot"])} with previous snapshot. '
                f'Publisher release dates verified: {e(readiness["verified_release_dates"])}. '
                f'Point-in-time certified: {e(readiness["pit_certified_sources"])}.</p></section>')
    rows = "".join(f'<tr><td>{e(x["series"])}</td><td>{e(x["domain"])}</td><td>{e(x["direction"])}</td>'
                   f'<td>{e(x["interpretation"])}</td><td>{e(x["observation_date"] or "Unavailable")}</td></tr>'
                   for x in signals["signals"])
    domains = (f'<section><h2>Explainable economic-cycle signals</h2><p>Directional observations are not calibrated '
               f'cycle classifications or crash probabilities.</p><div class="scroll"><table><thead><tr>'
               f'<th>Series</th><th>Domain</th><th>Direction</th><th>Interpretation</th><th>Observation date</th>'
               f'</tr></thead><tbody>{rows}</tbody></table></div></section>')
    mechanisms_html = "".join(
        f'<article><h3>{e(x["pathway"].replace("_", " ").title())}</h3>'
        f'<p>{e(x["available_indicators"])} of {e(x["mapped_indicators"])} mapped indicators available.</p>'
        f'<p>Adverse evidence: {e(", ".join(x["adverse_evidence"]) or "None established")}</p>'
        f'<p>Favorable evidence: {e(", ".join(x["favorable_evidence"]) or "None established")}</p>'
        f'<p>Unassessed: {e(", ".join(x["unassessed_indicators"]) or "None")}</p>'
        f'<small>{e(x["interpretation"])}</small></article>' for x in mechanisms["pathways"])
    mechanisms_section = f'<section><h2>Separate downturn mechanisms and counterevidence</h2><div class="cards">{mechanisms_html}</div></section>'
    history = (f'<section><h2>Historical validation</h2><p>{e(episodes["canonical_episode_clusters"])} canonical '
               f'historical parent clusters. Verified negative controls: {e(episodes["verified_noncrash_controls"])}. '
               f'Original point-in-time replay: not certified. Predictive publication: blocked.</p></section>')
    base = render_v3(v3)
    insertion = coverage + domains + mechanisms_section + history
    return base.replace("</footer>", "</footer>" + insertion, 1) if False else base.replace("<footer>", insertion + "<footer>", 1).replace(
        "<h1>Weekly Economic Intelligence</h1>", "<h1>Weekly Economic Intelligence — Version 4</h1>", 1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--v3", default="audit-output/v3_weekly_assessment.json")
    p.add_argument("--readiness", default="audit-output/v4_data_readiness.json")
    p.add_argument("--signals", default="audit-output/v4_economic_signals.json")
    p.add_argument("--mechanisms", default="audit-output/v4_mechanism_assessment.json")
    p.add_argument("--episodes", default="audit-output/v4_historical_episode_registry.json")
    p.add_argument("--output", default="audit-output/dashboard/weekly-v4.html")
    a = p.parse_args()
    read = lambda path: json.loads(Path(path).read_text())
    page = render(read(a.v3), read(a.readiness), read(a.signals), read(a.mechanisms), read(a.episodes))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    print("Built V4 offline descriptive weekly dashboard")

if __name__ == "__main__":
    main()
