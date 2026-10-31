"""Produce a readable, evidence-limited Version 3 weekly economic assessment."""
import argparse
import json
from pathlib import Path
try:
    from scripts.v3_indicator_interpretation import interpret
    from scripts.v3_pathway_evidence import pathway_evidence
    from scripts.v3_historical_bridge import bridge
except ModuleNotFoundError:
    from v3_indicator_interpretation import interpret
    from v3_pathway_evidence import pathway_evidence
    from v3_historical_bridge import bridge

LABELS = {
    "UNRATE": ("Unemployment rate", "percentage points", "MONTHLY"),
    "CPIAUCSL": ("Consumer price index level", "index points", "MONTHLY"),
    "GDPC1": ("Real GDP level", "chained-dollar units", "QUARTERLY"),
    "DGS10": ("10-year Treasury yield", "percentage points", "DAILY"),
    "DGS2": ("2-year Treasury yield", "percentage points", "DAILY"),
    "T10Y2Y": ("10-year minus 2-year Treasury spread", "percentage points", "DAILY"),
    "BAMLH0A0HYM2": ("US high-yield option-adjusted spread", "percentage points", "DAILY"),
    "STLFSI4": ("St. Louis Fed financial stress index", "index points", "WEEKLY"),
    "ICSA": ("Initial unemployment insurance claims", "claims", "WEEKLY"),
}

def assess(snapshot, historical=None):
    if snapshot.get("report_type") != "V3_WEEKLY_ECONOMIC_EVIDENCE":
        raise ValueError("Unsupported snapshot")
    series = snapshot.get("series", {})
    changes = snapshot.get("week_over_week", {})
    rows = []
    for key in sorted(series):
        entry = series[key]
        diff = changes.get(key, {})
        label, unit, frequency = LABELS.get(key, (key, "source units", "SOURCE_FREQUENCY_UNVERIFIED"))
        value = entry.get("observation_value")
        delta = diff.get("numeric_change")
        status = entry.get("status")
        if value is None:
            headline = "No usable numeric observation available"
        elif delta is not None:
            headline = f"Newly observed value {value:g}; change {delta:+g} {unit} since the prior reported observation"
        else:
            headline = f"Latest observed value {value:g}; no comparable newly released observation"
        rows.append({
            "series": key, "name": label, "source_frequency": frequency,
            "latest_observation": entry.get("latest_observation"),
            "age_days": entry.get("age_days"), "status": status,
            "value": value, "delta_new_release": delta,
            "headline": headline, "pit_certified": entry.get("publisher_original_pit_certified") is True,
            "source_availability_changed": diff.get("status_changed", False),
            "new_observation_date": diff.get("new_observation_date", False),
        })
    available = sum(r["value"] is not None for r in rows)
    historical_bridge = bridge({"indicators": rows}, historical) if historical is not None else None
    return {
        "schema_version": 1, "report_type": "V3_WEEKLY_DESCRIPTIVE_ASSESSMENT",
        "as_of": snapshot["as_of"], "status": "EVIDENCE_LIMITED",
        "summary": f"{available} of {len(rows)} tracked series have usable numeric observations. "
                   "This is a descriptive source and release-change assessment, not a validated economic-cycle classification.",
        "indicators": rows,
        "directional_evidence": interpret(rows),
        "pathway_evidence": pathway_evidence(rows),
        "historical_bridge": historical_bridge,
        "validated_cycle_stage": None, "crash_probability": None,
        "pathway_conclusions": [],
        "publication": "DESCRIPTIVE_ONLY",
        "predictive_publication": "BLOCKED",
        "limitations": [
            "Observation date is not publisher release date; publication lag is not yet verified",
            "GDP, CPI, unemployment, yields, spreads, stress and claims have different units and frequencies; do not combine directly",
            "New-release changes are not necessarily seven-day changes and may include revisions",
            "No validated crash pathway inference or economic-cycle classification",
        ],
    }

def render_markdown(report):
    lines = [
        "# Weekly Economic Intelligence — " + report["as_of"],
        "", "**Status:** Evidence-limited descriptive assessment; predictive publication blocked.",
        "", report["summary"], "",
        "## Indicator evidence",
    ]
    for item in report["indicators"]:
        lines.extend(["", f"### {item['name']} ({item['series']})",
                      item["headline"],
                      f"Observation date: {item['latest_observation'] or 'unavailable'}; "
                      f"frequency: {item['source_frequency']}; source status: {item['status']}; "
                      f"age: {str(item['age_days']) + ' days' if item['age_days'] is not None else 'unknown'}."])
        if item["source_availability_changed"]:
            lines.append("Source availability changed since the previous snapshot.")
    lines.extend(["", "## Directional evidence (not predictions)"])
    for finding in report["directional_evidence"]["findings"]:
        lines.append("- **{}**: {}".format(finding["series"], finding["interpretation"]))
    lines.extend(["", "## Crash pathway evidence inventories (not confirmed mechanisms)"])
    for pathway in report["pathway_evidence"]["pathways"]:
        lines.append("- **{}**: {} of {} mapped indicators have numeric observations; causal mechanism not verified.".format(pathway["pathway"], pathway["observed"], pathway["required"]))
    if report.get("historical_bridge") is not None:
        lines.extend(["", "## Historical evidence coverage (not a predictive analogue)"])
        for item in report["historical_bridge"]["domains"]:
            lines.append("- **{}**: {} of {} historical parent clusters with this domain; direct numeric comparison blocked.".format(item["domain"], item["historical_parent_clusters_with_domain"], report["historical_bridge"]["historical_parent_clusters"]))
    lines.extend(["", "## Interpretation limits", *("- " + x for x in report["limitations"]), "",
                  "**Economic-cycle stage:** Not validated.",
                  "**Crash probability:** Not available.", ""])
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", default="audit-output/v3_weekly_snapshot.json")
    p.add_argument("--historical")
    p.add_argument("--json-output", default="audit-output/v3_weekly_assessment.json")
    p.add_argument("--markdown-output", default="audit-output/v3_weekly_assessment.md")
    a = p.parse_args()
    historical = json.loads(Path(a.historical).read_text()) if a.historical else None
    report = assess(json.loads(Path(a.snapshot).read_text()), historical)
    for path, body in ((a.json_output, json.dumps(report, indent=2, sort_keys=True) + "\n"),
                       (a.markdown_output, render_markdown(report))):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    print(report["summary"])

if __name__ == "__main__":
    main()
