"""Static V5 weekly research dashboard: escaped, offline, descriptive only."""
import argparse
import html
import json
from pathlib import Path


def render(report):
    if report.get("report_type") != "V5_WEEKLY_RESEARCH_READOUT":
        raise ValueError("Expected V5 weekly readout")
    esc = lambda value: html.escape(str(value), quote=True)
    metrics = report.get("standardized_macro", [])
    mechanisms = report.get("mechanism_readiness", {})
    rows = "".join("<tr><td>" + esc(x.get("metric", x.get("series", ""))) +
                   "</td><td>" + esc(x.get("value", "N/A")) + "</td><td>" +
                   esc(x.get("observation_date", "N/A")) + "</td></tr>" for x in metrics)
    if not rows:
        rows = '<tr><td colspan="3">No dated macro transformations available</td></tr>'
    gaps = report.get("macro_coverage_gaps", [])
    coverage = "<p>Available: " + esc(report.get("macro_metric_count", len(metrics))) + " / " + esc(report.get("macro_metric_total", len(metrics))) + " standardized measures</p>"
    if gaps:
        coverage += "<p>Unavailable: " + ", ".join(
            esc(x.get("series", "unknown")) + " (" + esc(x.get("status", "UNAVAILABLE")) + ")"
            for x in gaps) + "</p>"
    pathways = "".join("<li><strong>" + esc(name.replace("_", " ").title()) +
                       "</strong>: " + esc(len(data.get("pit_features_verified", []))) +
                       " verified PIT indicators / " + esc(len(data.get("required_features", []))) +
                       " required</li>" for name, data in sorted(mechanisms.items()))
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Economic Cycle Research — V5 Weekly</title>
<style>body{font:16px system-ui,sans-serif;max-width:980px;margin:40px auto;padding:0 20px;color:#1d2939;background:#f7f9fc}
header{background:#142b45;color:white;padding:28px;border-radius:12px}h1{margin:0 0 8px}
section{background:white;padding:22px;margin:18px 0;border-radius:10px;border:1px solid #dde5ef}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px;border-bottom:1px solid #ddd}
small{color:#576574}header small{color:#dbe6f2}</style></head><body>
<header><h1>Weekly Economic Research</h1><small>Version 5 | As of """ + esc(report["as_of"]) + """</small></header>
<section><h2>Standardized economic measures</h2><table><thead><tr><th>Measure</th><th>Value</th><th>Observation date</th></tr></thead><tbody>""" + rows + """</tbody></table>""" + coverage + """</section>
<section><h2>Downturn mechanisms</h2><ul>""" + pathways + """</ul></section>
<section><h2>Historical validation coverage</h2><p>Historical events with independently supplied outcome evidence: """ + esc(report.get("historical_event_count", 0)) + """</p><p>Outcome coverage: """ + esc(report.get("outcome_coverage_status", "UNVERIFIED")) + """</p>
<p>Publisher-original replay observations: """ + esc(report.get("original_vintage_replay_coverage", 0)) + """</p>
<p><strong>Predictive publication: BLOCKED</strong></p><p>Required before predictive research: """ + esc("; ".join(report.get("validation_requirements", []))) + """</p><small>Descriptive research only; no calibrated forecast or investment recommendation.</small></section></body></html>"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--readout", required=True)
    p.add_argument("--output", default="audit-output/dashboard/weekly-v5.html")
    a = p.parse_args()
    report = json.loads(Path(a.readout).read_text())
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(report), encoding="utf-8")


if __name__ == "__main__":
    main()
