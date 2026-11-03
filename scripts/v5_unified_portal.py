"""Build a portable V5 landing page from existing verified release artifacts."""
import argparse
import html
import json
from pathlib import Path


def build(folder):
    required = ["unified_research_status.json", "v5_dashboard.json",
                "weekly_release_acceptance.json"]
    missing = [name for name in required if not (folder / name).is_file()]
    if missing:
        raise ValueError("Missing release artifacts: " + ", ".join(missing))
    unified, historical, monthly = [
        json.loads((folder / name).read_text()) for name in required
    ]
    if unified.get("status") != "UNIFIED_RESEARCH_STATUS":
        raise ValueError("Unverified unified research status")
    if historical.get("status") != "V5_RESEARCH_DASHBOARD_ONLY":
        raise ValueError("Unverified V5 historical dashboard")
    if monthly.get("status") not in ("PASS", "STALE_RESEARCH_ONLY"):
        raise ValueError("Monthly release gate is not accepted")
    if unified.get("github_monthly_release_status") != monthly["status"]:
        raise ValueError("Monthly release status mismatch")
    return {
        "status": "V5_UNIFIED_RESEARCH_PORTAL",
        "monthly_release": monthly["status"],
        "observation_month": historical["observation_month"],
        "preliminary_historical_phase": historical["preliminary_phase"],
        "workbook_reconciliation": unified["workbook_reconciliation"],
        "workbook_snapshot_date": unified.get("workbook_snapshot_retrieval_date"),
        "macro_promotion": unified["macro_promotion"],
        "current_conditions_approved": False,
        "numeric_forecasts_approved": False,
        "research_only": True,
    }


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    rows = "".join(
        f"<tr><th>{esc(series)}</th><td>{esc(state)}</td></tr>"
        for series, state in report["macro_promotion"].items()
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Economic Cycle Research — Version 5</title>
<style>
:root{{font:16px system-ui,sans-serif;color:#192b42;background:#f4f7fb}}
body{{max-width:980px;margin:auto;padding:24px;line-height:1.55}}
h1{{font-size:2rem}}h2{{font-size:1.15rem}}
section{{background:#fff;padding:24px;border:1px solid #dae3ed;border-radius:14px;margin:16px 0}}
nav a{{display:inline-block;margin:6px 14px 6px 0}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #e0e6ed;text-align:left}}
small,.muted{{color:#53647a}}
</style></head><body>
<header><h1>Economic Cycle Research</h1>
<p>Version 5 · Integrated monthly assessment · Research-only release</p></header>
<section><h2>Monthly status: {esc(report["monthly_release"])}</h2>
<p>Historical observation month: <strong>{esc(report["observation_month"])}</strong>.
Preliminary historical phase: <strong>{esc(report["preliminary_historical_phase"])}</strong>.</p>
<p>Current conditions approved: <strong>{'Yes' if report["current_conditions_approved"] else 'No'}</strong>.
Numeric recession forecasts: <strong>Blocked</strong>.</p>
<p class="muted">A historical phase is not a real-time cycle determination or a forecast. A stale monthly release is not a current assessment.</p></section>
<section><h2>Research reports</h2>
<nav><a href="economic_dashboard.html">Monthly economic indicators</a>
<a href="v5_dashboard.html">Historical cycle diagnostics</a>
<a href="v5_executive_brief.md">Research brief</a></nav>
<p class="muted">Links open the companion files included in the same GitHub Actions artifact.</p></section>
<section><h2>Source verification</h2>
<p>Workbook reconciliation: {esc(report["workbook_reconciliation"])}.
Snapshot date: {esc(report["workbook_snapshot_date"] or "Unavailable")}.</p>
<table><thead><tr><th>Macro series</th><th>Promotion status</th></tr></thead>
<tbody>{rows}</tbody></table></section>
<section><h2>Research limitations</h2>
<p>Source vintage certification and numerical forecast validation remain independent
release gates. Missing observations are not imputed. Retrospective revised-data
diagnostics must not be interpreted as live crash predictions.</p></section>
<footer><small>Historical and descriptive research only · Not investment advice</small></footer>
</body></html>"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", default="audit-output")
    args = p.parse_args()
    folder = Path(args.directory)
    report = build(folder)
    (folder / "v5_unified_portal.json").write_text(json.dumps(report, indent=2) + "\n")
    (folder / "index.html").write_text(render(report))
    print(json.dumps({"status": report["status"], "monthly_release": report["monthly_release"]}))


if __name__ == "__main__":
    main()
