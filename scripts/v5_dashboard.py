"""Create an explicitly research-only V5 dashboard section from validated artifacts."""
import argparse
import html
import json
from pathlib import Path


def assemble(estimates, evaluation, baseline, gate, episodes):
    statuses = ("HISTORICAL_RESEARCH_ONLY", "RETROSPECTIVE_DIAGNOSTIC_ONLY",
                "RETROSPECTIVE_OUT_OF_SAMPLE_DIAGNOSTIC_ONLY",
                "FORECAST_RELEASE_BLOCKED", "RETROSPECTIVE_EPISODE_DIAGNOSTIC_ONLY")
    inputs = (estimates, evaluation, baseline, gate, episodes)
    if any(item.get("status") != expected for item, expected in zip(inputs, statuses)):
        raise ValueError("V5 artifact status mismatch")
    if gate["numeric_forecasts_approved"]:
        raise ValueError("Numeric forecasts require a separately approved release")
    if any(gate["horizons"][h]["numeric_forecast_approved"] for h in ("3", "6", "12")):
        raise ValueError("Individual horizon forecasts are not approved")
    counts = evaluation["counts"]
    total = sum(counts.values())
    classified = total - counts["uncertain"]
    return {
        "status": "V5_RESEARCH_DASHBOARD_ONLY",
        "classification_coverage": round(classified / total, 4) if total else None,
        "recession_recall_excluding_uncertain": (round(counts["true_positive"] / (counts["true_positive"] + counts["false_negative"]), 4)
                                                if counts["true_positive"] + counts["false_negative"] else None),
        "observation_month": estimates["as_of_month"],
        "preliminary_phase": estimates["latest"]["phase"],
        "current_conditions_approved": False,
        "forecast_probabilities_approved": False,
        "recession_month_counts": evaluation["counts"],
        "episode_count": episodes["episode_count"],
        "episode_warnings": episodes["pre_recession_warning_episodes"],
        "horizons": gate["horizons"],
        "disclaimer": "Retrospective revised-data research; not a current cycle determination or a validated forecast.",
    }


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    rows = []
    for horizon in ("3", "6", "12"):
        data = report["horizons"][horizon]
        def number(value):
            return "Insufficient evidence" if value is None else f"{value:.4f}"
        rows.append("<tr><th scope='row'>" + horizon + " months</th><td>" +
                    str(data["evaluation_months"]) + "</td><td>" +
                    number(data["baseline_brier"]) + "</td><td>" +
                    number(data["phase_frequency_brier"]) + "</td><td>" +
                    ("Yes" if data["retrospective_benchmark_pass"] else "No") +
                    "</td></tr>")
    counts = report["recession_month_counts"]
    coverage = report["classification_coverage"]
    coverage_text = "Unavailable" if coverage is None else f"{coverage:.1%}"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Economic Cycle Research | Version 5 Historical Diagnostics</title>
<style>
:root{{font-family:system-ui,sans-serif;color:#1b2b42;background:#f5f7fa}}
body{{max-width:1050px;margin:auto;padding:24px;line-height:1.55}}
section{{background:white;border:1px solid #dce4ed;border-radius:12px;padding:22px;margin:18px 0}}
table{{border-collapse:collapse;width:100%;display:block;overflow-x:auto}}
th,td{{border-bottom:1px solid #dce4ed;text-align:left;padding:12px}}
p,small{{color:#526279}}h1{{font-size:1.8rem}}
</style></head><body>
<header><h1>Version 5 · Business-Cycle Historical Research</h1>
<p>Observation month: {esc(report["observation_month"])} · Research-only evidence</p></header>
<section><h2>Preliminary phase: {esc(report["preliminary_phase"].replace("_"," ").title())}</h2>
<p>{esc(report["disclaimer"])}</p></section>
<section><h2>Historical recession-month diagnostic</h2>
<p>Classification coverage: {coverage_text} of evaluated months; uncertain months excluded from precision and recall.</p>
<p>Correct recession flags: {counts["true_positive"]}; missed recession months: {counts["false_negative"]};
false alarms: {counts["false_positive"]}; uncertain months: {counts["uncertain"]}.</p>
<p>Recession episodes examined: {report["episode_count"]}; episodes with a warning in the preceding
12 months: {report["episode_warnings"]}. Warnings are not calibrated.</p></section>
<section><h2>3-, 6-, and 12-month retrospective benchmark</h2>
<table><thead><tr><th>Horizon</th><th>Test months</th><th>Base-rate Brier</th>
<th>Phase Brier</th><th>Phase beats baseline?</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p>Smaller Brier scores are better. Overlapping months and revised data limit interpretation.</p></section>
<section><h2>Forecast release status</h2>
<p><strong>BLOCKED:</strong> No numerical recession probabilities or current-cycle
assessment approved. Historical data vintages and independent calibration are required.</p></section>
<footer><small>Historical research only · No investment advice</small></footer>
</body></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("estimates")
    parser.add_argument("evaluation")
    parser.add_argument("baseline")
    parser.add_argument("gate")
    parser.add_argument("episodes")
    parser.add_argument("--output-dir", default="audit-output")
    args = parser.parse_args()
    inputs = [json.loads(Path(p).read_text()) for p in
              (args.estimates, args.evaluation, args.baseline, args.gate, args.episodes)]
    report = assemble(*inputs)
    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "v5_dashboard.json").write_text(json.dumps(report, indent=2) + "\n")
    (target / "v5_dashboard.html").write_text(render(report))
    print(json.dumps({"status": report["status"], "observation_month": report["observation_month"]}))


if __name__ == "__main__":
    main()
