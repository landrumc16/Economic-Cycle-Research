"""Accept the integrated monthly V5 research portal only with consistent artifacts."""
import argparse
import json
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from pathlib import Path

try:
    from .build_historical_cycle_timeline import SERIES as TIMELINE_SERIES
except ImportError:
    from build_historical_cycle_timeline import SERIES as TIMELINE_SERIES

FILES = ("index.html", "v5_unified_portal.json", "v5_dashboard.html",
         "v5_dashboard.json", "v5_executive_brief.md",
         "economic_dashboard.html", "economic_dashboard.json",
         "unified_research_status.json", "weekly_release_acceptance.json",
         "v5_forecast_release_gate.json", "weekly_economic_assessment.json")


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(value for key, value in attrs if key == "href" and value)


def verify_html(folder):
    for name in ("index.html", "v5_dashboard.html", "economic_dashboard.html"):
        markup = (folder / name).read_text()
        if 'name="viewport"' not in markup:
            raise ValueError(f"Missing mobile viewport: {name}")
        parser = LocalLinks()
        parser.feed(markup)
        for href in parser.links:
            url = urlsplit(href)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (folder / unquote(url.path)).resolve()
            if not target.is_relative_to(folder.resolve()) or not target.is_file():
                raise ValueError(f"Broken or unsafe artifact link in {name}: {href}")


def _month(value, label):
    """Strict YYYY-MM (optionally YYYY-MM-DD) month key; never coerces bad dates."""
    text = str(value or "")
    try:
        year, month = int(text[:4]), int(text[5:7])
    except ValueError:
        raise ValueError(f"Invalid observation month: {label}") from None
    if len(text) not in (7, 10) or text[4] != "-" or not 1 <= month <= 12 or year < 1900:
        raise ValueError(f"Invalid observation month: {label}")
    return text[:7]


def verify_observation_months(portal, historical, monthly, assessment):
    """Check each module against its OWN documented source coverage.

    The monthly gate's observation month is the latest month shared by every
    monthly-assessment series. The V5 historical timeline uses only
    TIMELINE_SERIES, so its latest month is the latest month shared by those
    series. Publication schedules differ (housing and income lag), so the two
    months may legitimately differ; both are derived from the same dated
    source ledger and neither may be future-dated or internally inconsistent.
    """
    if assessment.get("status") != "RESEARCH_SNAPSHOT_NOT_FORECAST":
        raise ValueError("Unapproved monthly assessment")
    if monthly.get("assessment_date") and monthly["assessment_date"] != assessment.get("assessment_date"):
        raise ValueError("Monthly assessment date mismatch")
    assessment_month = _month(assessment.get("assessment_date"), "assessment date")
    sources = assessment.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Missing monthly source ledger")
    latest = {}
    for name, source in sources.items():
        if not isinstance(source, dict):
            raise ValueError(f"Invalid source entry: {name}")
        latest[name] = _month(source.get("latest_used_month"), name)
        if latest[name] > assessment_month:
            raise ValueError(f"Future-dated observation: {name}")
    missing = [name for name in TIMELINE_SERIES if name not in latest]
    if missing:
        raise ValueError("Source ledger lacks V5 timeline series: " + ", ".join(missing))
    monthly_month = _month(monthly.get("observation_month"), "monthly gate")
    if (monthly_month != _month(assessment.get("common_observation_month"), "assessment")
            or monthly_month != min(latest.values())):
        raise ValueError("Monthly observation date mismatch")
    v5_month = _month(historical.get("observation_month"), "V5 historical")
    if v5_month != min(latest[name] for name in TIMELINE_SERIES):
        raise ValueError("V5 historical observation month does not match its timeline sources")
    if _month(portal.get("observation_month"), "portal") != v5_month:
        raise ValueError("Historical research mismatch")
    return {"monthly_observation_month": monthly_month, "v5_observation_month": v5_month}


def verify(folder):
    missing = [n for n in FILES if not (folder / n).is_file() or not (folder / n).stat().st_size]
    if missing:
        raise ValueError("Missing or empty artifacts: " + ", ".join(missing))
    verify_html(folder)
    read = lambda n: json.loads((folder / n).read_text())
    portal, monthly, unified = map(read, ("v5_unified_portal.json", "weekly_release_acceptance.json",
                                         "unified_research_status.json"))
    forecast, historical = map(read, ("v5_forecast_release_gate.json", "v5_dashboard.json"))
    assessment = read("weekly_economic_assessment.json")
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
    if portal.get("current_conditions_approved") is not False:
        raise ValueError("Uncertified current assessment")
    if monthly["status"] == "STALE_RESEARCH_ONLY" and monthly.get("current_assessment_approved") is True:
        raise ValueError("Stale monthly observations presented as current")
    months = verify_observation_months(portal, historical, monthly, assessment)
    for key in ("daily_refresh_status", "weekly_outlook_status", "monthly_cycle_status", "workbook_snapshot_review_status"):
        if key not in portal or key not in unified or not isinstance(portal[key], str) or not portal[key]:
            raise ValueError(f"Missing unified cadence/review status: {key}")
        if portal.get(key) != unified.get(key):
            raise ValueError(f"Unified cadence/review status mismatch: {key}")
    if unified.get("workbook_reconciliation") != "RECONCILED":
        if unified.get("canonical_macro_approved") is not False:
            raise ValueError("Unreconciled workbook cannot approve canonical macro data")
        if any(value != "BLOCKED" for value in unified.get("macro_promotion", {}).values()):
            raise ValueError("Unreconciled workbook cannot promote macro sources")
    if unified.get("numeric_forecasts_approved") is not False:
        raise ValueError("Unified status claims numeric forecasts")
    if unified.get("canonical_macro_approved") is True and unified.get("workbook_reconciliation") != "RECONCILED":
        raise ValueError("Unreconciled workbook claims approved macro sources")
    if portal.get("workbook_reconciliation") != unified.get("workbook_reconciliation"):
        raise ValueError("Workbook reconciliation mismatch")
    if portal.get("macro_promotion") != unified.get("macro_promotion"):
        raise ValueError("Macro promotion mismatch")
    if "research-only" not in (folder / "index.html").read_text().lower():
        raise ValueError("Missing research-only disclosure")
    return {"status": "V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED",
            "monthly_status": monthly["status"], "forecast_status": "BLOCKED",
            "observation_month": historical["observation_month"],
            "monthly_observation_month": months["monthly_observation_month"],
            "v5_observation_month": months["v5_observation_month"],
            "verified_artifacts": list(FILES)}


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
