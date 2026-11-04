"""Compare current macro condition tags with historical monthly combinations.

Historical matches are descriptive; not a prediction, recession classification,
or proof that similar conditions have similar future outcomes.
"""
import argparse
import json
from pathlib import Path


def compare(timeline, assessment, max_examples=12):
    if timeline["status"] != "RETROSPECTIVE_DESCRIPTIVE_ONLY":
        raise ValueError("Unapproved historical timeline")
    if assessment["status"] != "RESEARCH_SNAPSHOT_NOT_FORECAST":
        raise ValueError("Unapproved assessment")
    if max_examples < 1:
        raise ValueError("Invalid example count")
    if assessment["stale"]:
        return {"status": "STALE_CURRENT_DATA", "matches": [], "match_count": 0}
    if (assessment.get("historical_comparison_stale", False) or
            any(info.get("latest_used_month") != assessment["common_observation_month"]
                for info in assessment.get("sources", {}).values())):
        return {"status": "STALE_HISTORICAL_DATA", "matches": [], "match_count": 0,
                "observation_month": assessment["common_observation_month"],
                "limitations": ["Current indicators have different observation dates; a same-month historical match would be misleading"]}
    try:
        from .build_economic_dashboard import cycle_conditions
    except ImportError:
        from build_economic_dashboard import cycle_conditions
    current = cycle_conditions(assessment)
    if current["status"] != "DESCRIPTIVE_TAGS_ONLY":
        return {"status": "INSUFFICIENT_CURRENT_DATA", "matches": [], "match_count": 0}
    # Compare the four macro conditions shared with the historical timeline.
    macro_tags = {"LABOR_SOFTENING", "PRODUCTION_CONTRACTION",
                  "POSITIVE_INFLATION", "BROAD_CREDIT_EXPANSION"}
    target = set(current["tags"]) & macro_tags
    # Exclude the current month and all later historical observations.
    prior = [row for row in timeline["timeline"]
             if row["month"] < assessment["common_observation_month"][:7]]
    matches = [row for row in prior if set(row["condition_tags"]) == target]
    # Last 12 matches are examples, never independent samples.
    return {
        "status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
        "assessment_date": assessment["assessment_date"],
        "observation_month": assessment["common_observation_month"],
        "current_macro_tags": sorted(target),
        "historical_months_examined": len(prior),
        "match_count": len(matches),
        "match_fraction": round(len(matches) / len(prior), 6) if prior else None,
        "matches": [{"month": row["month"],
                     "unemployment_change_3m_pp": row["unemployment_change_3m_pp"],
                     "industrial_production_growth_12m_log_pct": row["industrial_production_growth_12m_log_pct"],
                     "cpi_inflation_12m_log_pct": row["cpi_inflation_12m_log_pct"]}
                    for row in matches[-max_examples:]],
        "limitations": [
            "Matches use sign-based macroeconomic conditions, not fitted statistical similarity",
            "Current-vintage revised data are not publication-date adjusted",
            "Overlapping months are dependent; counts are not independent historical episodes",
            "Matching past conditions does not establish future economic or market outcomes",
        ],
    }


def markdown(report):
    lines = ["# Current conditions against historical months", "",
             f"Status: **{report['status']}**", ""]
    if report["status"] != "RETROSPECTIVE_DESCRIPTIVE_ONLY":
        return "\n".join(lines + ["Comparison unavailable due to data quality.", ""])
    lines += [f"Assessment: {report['assessment_date']}",
              f"Observation month: {report['observation_month']}",
              f"Historical months examined: {report['historical_months_examined']}",
              f"Exact condition matches: {report['match_count']}",
              f"Match share: {report['match_fraction']}", "",
              "## Recent matching historical months", "",
              "| Month | Unemployment change (pp) | Production growth (%) | CPI growth (%) |",
              "|---|---:|---:|---:|"]
    for row in report["matches"]:
        lines.append(f"| {row['month']} | {row['unemployment_change_3m_pp']} | "
                     f"{row['industrial_production_growth_12m_log_pct']} | "
                     f"{row['cpi_inflation_12m_log_pct']} |")
    lines += ["", "## Limitations", ""]
    lines += ["- " + item for item in report["limitations"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("timeline")
    parser.add_argument("assessment")
    parser.add_argument("--output-dir", default="audit-output")
    args = parser.parse_args()
    report = compare(json.loads(Path(args.timeline).read_text()),
                     json.loads(Path(args.assessment).read_text()))
    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "historical_condition_comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    (target / "historical_condition_comparison.md").write_text(markdown(report))
    print(markdown(report))


if __name__ == "__main__":
    main()
