"""Fail closed if weekly dashboard outputs are missing or inconsistent."""
import json
from pathlib import Path


def validate(root):
    folder = root / "audit-output"
    names = ("weekly_economic_assessment.json", "economic_dashboard.json",
             "economic_dashboard.html", "historical_cycle_timeline.json",
             "historical_condition_comparison.json")
    missing = [name for name in names if not (folder / name).is_file()]
    if missing:
        raise ValueError("Missing weekly release outputs: " + ", ".join(missing))
    read = lambda name: json.loads((folder / name).read_text())
    current = read(names[0])
    dashboard = read(names[1])
    timeline = read(names[3])
    comparison = read(names[4])
    if current["status"] != "RESEARCH_SNAPSHOT_NOT_FORECAST":
        raise ValueError("Invalid weekly assessment status")
    if dashboard["status"] != "DESCRIPTIVE_DASHBOARD":
        raise ValueError("Invalid dashboard status")
    if timeline["status"] != "RETROSPECTIVE_DESCRIPTIVE_ONLY":
        raise ValueError("Invalid historical timeline status")
    if comparison["status"] not in ("RETROSPECTIVE_DESCRIPTIVE_ONLY",
                                    "STALE_CURRENT_DATA", "INSUFFICIENT_CURRENT_DATA",
                                    "STALE_HISTORICAL_DATA"):
        raise ValueError("Invalid historical comparison status")
    if (comparison["status"] != "RETROSPECTIVE_DESCRIPTIVE_ONLY"
            and comparison["status"] != "STALE_HISTORICAL_DATA" and not current["stale"]):
        raise ValueError("Historical comparison unavailable for complete release: "
                         + comparison["status"] + "; common observation month "
                         + str(current["common_observation_month"]) + ", lag "
                         + str(current.get("months_since_common_observation"))
                         + " months. Preserve the freshness gate; do not label stale data current.")
    if comparison["status"] == "STALE_HISTORICAL_DATA" and not current.get("historical_comparison_stale"):
        raise ValueError("Historical staleness not established by assessment")
    if dashboard.get("historical_comparison") != comparison:
        raise ValueError("Dashboard historical comparison does not match generated report")
    if dashboard.get("stale") != current["stale"]:
        raise ValueError("Dashboard freshness flag differs")
    if dashboard["assessment_date"] != current["assessment_date"]:
        raise ValueError("Dashboard and assessment date differ")
    if dashboard["common_observation_month"] != current["common_observation_month"]:
        raise ValueError("Dashboard observation month differs")
    if (comparison["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
            and comparison["observation_month"] != current["common_observation_month"]):
        raise ValueError("Historical comparison month differs")
    if not timeline["timeline"] or timeline["months"] != len(timeline["timeline"]):
        raise ValueError("Historical timeline coverage invalid")
    html = (folder / "economic_dashboard.html").read_text()
    if "Economic Cycle Research" not in html or current["assessment_date"] not in html:
        raise ValueError("HTML dashboard does not match assessment")
    if len(dashboard.get("metrics", [])) < 9:
        raise ValueError("Expected integrated economic indicators missing")
    return {"status": "STALE_RESEARCH_ONLY" if current["stale"] else "PASS", "assessment_date": current["assessment_date"],
            "observation_month": current["common_observation_month"],
            "historical_months": timeline["months"],
            "dashboard_metrics": len(dashboard["metrics"]),
            "current_assessment_approved": not current["stale"]}


def main():
    result = validate(Path("."))
    target = Path("audit-output/weekly_release_acceptance.json")
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
