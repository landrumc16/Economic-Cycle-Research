"""Accept the integrated monthly V5 research portal only with consistent artifacts."""
import argparse
import json
from pathlib import Path

FILES = ("index.html", "v5_unified_portal.json", "v5_dashboard.html",
         "v5_dashboard.json", "v5_executive_brief.md",
         "economic_dashboard.html", "economic_dashboard.json",
         "unified_research_status.json", "weekly_release_acceptance.json",
         "v5_forecast_release_gate.json")


def verify(folder):
    missing = [n for n in FILES if not (folder / n).is_file() or not (folder / n).stat().st_size]
    if missing:
        raise ValueError("Missing or empty artifacts: " + ", ".join(missing))
    read = lambda n: json.loads((folder / n).read_text())
    portal, monthly, unified = map(read, ("v5_unified_portal.json", "weekly_release_acceptance.json",
                                         "unified_research_status.json"))
    forecast, historical = map(read, ("v5_forecast_release_gate.json", "v5_dashboard.json"))
    if portal.get("status") != "V5_UNIFIED_RESEARCH_PORTAL":
        raise ValueError("Invalid integrated portal")
    if monthly.get("status") not in ("PASS", "STALE_RESEARCH_ONLY"):
        raise ValueError("Monthly release not accepted")
    if portal.get("monthly_release") != monthly["status"] or unified.get("github_monthly_release_status") != monthly["status"]:
        raise ValueError("Monthly status mismatch")
    if historical.get("status") != "V5_RESEARCH_DASHBOARD_ONLY" or portal.get("observation_month") != historical.get("observation_month"):
        raise ValueError("Historical research mismatch")
    if forecast.get("status") != "FORECAST_RELEASE_BLOCKED" or forecast.get("numeric_forecasts_approved") is not False:
        raise ValueError("Forecast gate violation")
    if portal.get("numeric_forecasts_approved") is not False or portal.get("research_only") is not True:
        raise ValueError("Portal claims unapproved forecasts")
    if monthly["status"] == "STALE_RESEARCH_ONLY" and portal.get("current_conditions_approved") is not False:
        raise ValueError("Stale assessment presented as current")
    if "research-only" not in (folder / "index.html").read_text().lower():
        raise ValueError("Missing research-only disclosure")
    return {"status": "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED",
            "monthly_status": monthly["status"], "forecast_status": "BLOCKED",
            "observation_month": historical["observation_month"], "verified_artifacts": list(FILES)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", default="audit-output")
    args = p.parse_args()
    folder = Path(args.directory)
    result = verify(folder)
    (folder / "v5_integrated_acceptance.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
