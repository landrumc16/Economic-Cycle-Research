"""V6.1 release artifact contract: verify a complete, evidence-gated public bundle."""
import argparse
import json
from pathlib import Path

PAGES = ("overview.html", "sectors.html", "monthly-research.html",
         "research.html", "historical.html")
SECTOR_PAGES = tuple(f"sector-{i:02d}.html" for i in range(1, 12))


def validate(directory: Path) -> dict:
    root = Path(directory)
    required = PAGES + SECTOR_PAGES + ("v6_sector_report.json", "v6_1_economic_outlook.json")
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise ValueError("Missing V6.1 artifacts: " + ", ".join(missing))
    outlook = json.loads((root / "v6_1_economic_outlook.json").read_text())
    sectors = json.loads((root / "v6_sector_report.json").read_text())
    if outlook.get("schema_version") != 1 or outlook.get("sector_count") != 11:
        raise ValueError("Invalid V6.1 outlook schema")
    if outlook.get("monthly_gate") not in {"PASS", "STALE_RESEARCH_ONLY"}:
        raise ValueError("Unaccepted monthly gate")
    if outlook.get("numeric_forecasts_approved") is not False:
        raise ValueError("Unverified numeric forecast")
    if outlook.get("historical_phase_certified") is not False:
        raise ValueError("Unverified cycle phase")
    validation = outlook.get("historical_validation")
    if not isinstance(validation, dict) or validation.get("predictive_skill_certified") is not False:
        raise ValueError("Unverified historical prediction")
    if not isinstance(outlook.get("observed_outlook", {}).get("evidence"), list):
        raise ValueError("Missing observation evidence ledger")
    items = sectors.get("sectors")
    if not isinstance(items, list) or len(items) != 11:
        raise ValueError("Missing 11-sector inventory")
    qualified = sum(item.get("outlook") != "Insufficient Evidence" for item in items)
    if qualified != outlook.get("sector_outlooks_qualified"):
        raise ValueError("Sector counts disagree")
    for name in PAGES + SECTOR_PAGES:
        html = (root / name).read_text()
        if not html.lower().startswith("<!doctype html>") or 'name="viewport"' not in html:
            raise ValueError("Invalid mobile public page: " + name)
    overview = (root / "overview.html").read_text()
    for headline in ("Where We Are", "Where We Are Heading", "Where Investors Should Look"):
        if headline not in overview:
            raise ValueError("Missing executive headline: " + headline)
    for page in PAGES[1:] + SECTOR_PAGES:
        if f'href="{page}"' not in "".join((root / n).read_text() for n in PAGES):
            raise ValueError("Unlinked public page: " + page)
    return {"status": "V6_1_ARTIFACTS_VALIDATED", "monthly_gate": outlook["monthly_gate"],
            "sector_count": 11, "sector_outlooks_qualified": qualified,
            "pages_checked": len(PAGES) + len(SECTOR_PAGES)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("audit-output"))
    args = parser.parse_args()
    print(json.dumps(validate(args.directory), indent=2))


if __name__ == "__main__":
    main()
