"""Build a standalone offline weekly V3 dashboard from the accepted assessment contract."""
import argparse
import html
import json
from pathlib import Path

def render(report):
    if report.get("report_type") != "V3_WEEKLY_DESCRIPTIVE_ASSESSMENT" or report.get("predictive_publication") != "BLOCKED":
        raise ValueError("Unapproved V3 report contract")
    e = lambda v: html.escape(str(v), quote=True)
    counts = report["change_summary"]["counts"]
    metrics = "".join(f'<article><small>{e(k.replace("_", " ").title())}</small><strong>{e(v)}</strong></article>' for k, v in counts.items())
    domains = "".join(f'<article><h3>{e(d["domain"].replace("_", " ").title())}</h3><p>{e(d["statement"])}</p></article>' for d in report["macro_narrative"]["domains"])
    indicators = "".join('<tr>' + "".join(f'<td>{e(v)}</td>' for v in (
        x["name"], x["latest_observation"] or "Unavailable", x["source_frequency"],
        x["value"] if x["value"] is not None else "Unavailable", x["headline"])) + '</tr>' for x in report["indicators"])
    pathways = "".join(f'<li><b>{e(p["pathway"].replace("_", " ").title())}</b>: {e(p["observed"])} of {e(p["required"])} indicators available; mechanism unverified</li>' for p in report["pathway_evidence"]["pathways"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Weekly Economic Intelligence — {e(report["as_of"])}</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:1160px;margin:auto;padding:24px;background:#f6f8fc;color:#16243a}}
header{{background:#132945;color:white;padding:28px;border-radius:14px}}header p{{color:#d5e2f4}}
section{{margin:30px 0}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px}}
article{{background:white;border:1px solid #dbe2ec;border-radius:10px;padding:16px}}small{{display:block;color:#52647d}}strong{{display:block;font-size:2rem}}
.scroll{{overflow-x:auto}}table{{border-collapse:collapse;background:white;width:100%}}td,th{{padding:12px;border-bottom:1px solid #e3e9f1;text-align:left;vertical-align:top}}th{{background:#e7edf6}}
footer{{border-top:1px solid #cad4e2;padding:18px 0;color:#52647d}}</style></head>
<body><header><h1>Weekly Economic Intelligence</h1><p>As of {e(report["as_of"])} · Descriptive evidence only · Predictions blocked</p><p>{e(report["summary"])}</p></header>
<section><h2>What changed</h2><div class="cards">{metrics}</div><p>{e(report["change_summary"]["baseline_note"])}</p></section>
<section><h2>Economic conditions by domain</h2><div class="cards">{domains}</div></section>
<section><h2>Latest economic indicators</h2><div class="scroll"><table><thead><tr><th>Indicator</th><th>Observation date</th><th>Frequency</th><th>Value</th><th>Assessment</th></tr></thead><tbody>{indicators}</tbody></table></div></section>
<section><h2>Distinct crash-pathway evidence</h2><p>Evidence coverage is not proof of a mechanism or crash forecast.</p><ul>{pathways}</ul></section>
<footer>Economic-cycle stage: not validated. Crash probability: unavailable. Observation dates are not verified release dates; historical vintages are not point-in-time certified.</footer></body></html>"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assessment", default="audit-output/v3_weekly_assessment.json")
    parser.add_argument("--output", default="audit-output/dashboard/weekly.html")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(json.loads(Path(args.assessment).read_text())), encoding="utf-8")

if __name__ == "__main__":
    main()
