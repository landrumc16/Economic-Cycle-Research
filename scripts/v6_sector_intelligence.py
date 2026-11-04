"""Version 6 sector evidence gate: never infer an investment rating from macro data alone."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

SECTORS = (
    "Communication Services", "Consumer Discretionary", "Consumer Staples",
    "Energy", "Financials", "Health Care", "Industrials",
    "Information Technology", "Materials", "Real Estate", "Utilities",
)
ALLOWED = {"Favorable", "Mixed", "Caution"}

# Qualitative exposure descriptions are structural hypotheses, not live ratings.
EXPOSURES = {
    "Communication Services": ("Advertising demand and financing costs", "Telecom networks; digital advertising"),
    "Consumer Discretionary": ("Household income, borrowing costs and consumer confidence", "Automobiles; retail; leisure"),
    "Consumer Staples": ("Input-cost inflation and consumer purchasing power", "Food and beverage; household goods"),
    "Energy": ("Oil and gas demand, commodity prices and capital spending", "Exploration; refining; services"),
    "Financials": ("Interest-rate spreads, credit quality and liquidity", "Banks; insurers; capital markets"),
    "Health Care": ("Reimbursement policy, innovation and funding conditions", "Pharmaceuticals; medical devices; providers"),
    "Industrials": ("Capital expenditure, industrial production and public investment", "Machinery; transportation; aerospace"),
    "Information Technology": ("Enterprise spending, financing rates and hardware cycles", "Semiconductors; software; hardware"),
    "Materials": ("Industrial demand, construction and commodity input prices", "Chemicals; metals; construction materials"),
    "Real Estate": ("Financing rates, vacancy, rents and property-specific credit", "Residential; offices; logistics"),
    "Utilities": ("Regulated rates, financing costs and electricity demand", "Electric power; gas; water"),
}


def _qualified(item: dict, as_of: date) -> bool:
    """A sector rating requires dated, attributable investment AND economic evidence."""
    if not isinstance(item, dict):
        return False
    required = ("economic_fit", "earnings", "valuation", "relative_total_return")
    if not all(isinstance(item.get(key), dict) for key in required):
        return False
    for key in required:
        entry = item[key]
        if not entry.get("source_url") or not entry.get("methodology"):
            return False
        try:
            observed = date.fromisoformat(entry["observation_date"])
        except (KeyError, TypeError, ValueError):
            return False
        if observed > as_of:
            return False
    history = item["relative_total_return"]
    return (
        history.get("benchmark") is not None
        and isinstance(history.get("sample_size"), int)
        and not isinstance(history.get("sample_size"), bool)
        and history["sample_size"] >= 1
        and history.get("point_in_time_verified") is True
        and item.get("outlook") in ALLOWED
    )


def build_sector_report(evidence: dict, as_of: date) -> dict:
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be an object")
    unknown = set(evidence) - set(SECTORS)
    if unknown:
        raise ValueError("Unknown sector names: " + ", ".join(sorted(unknown)))
    sectors = []
    for name in SECTORS:
        item = evidence.get(name, {})
        if not isinstance(item, dict):
            item = {}
        qualified = _qualified(item, as_of)
        sectors.append({
            "sector": name,
            "economic_exposure_hypothesis": EXPOSURES[name][0],
            "industry_examples": EXPOSURES[name][1],
            "outlook": item["outlook"] if qualified else "Insufficient Evidence",
            "economic_fit": item.get("economic_fit") if qualified else None,
            "investment_fit": {
                key: item[key] for key in ("earnings", "valuation", "relative_total_return")
            } if qualified else None,
            "reason": item.get("rationale") if qualified else
                "Source-qualified, dated economic, earnings, valuation and point-in-time relative-return evidence is incomplete.",
            "as_of": as_of.isoformat(),
        })
    return {"schema_version": 1, "as_of": as_of.isoformat(), "sectors": sectors,
            "disclaimer": "Descriptive research, not personalized investment advice."}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text()) if args.evidence else {}
    report = build_sector_report(evidence, args.as_of)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n")
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
