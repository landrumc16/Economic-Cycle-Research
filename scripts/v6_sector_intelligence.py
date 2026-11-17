"""Version 6 sector evidence gate: never infer an investment rating from macro data alone."""
from __future__ import annotations

import json
import math
from urllib.parse import urlparse
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


# V6.3 M3: structural economic sensitivities. These describe how each sector's
# revenues and costs are commonly linked to the economy in published sector
# research; this project has NOT validated them with sector return data. They
# describe economic exposure only and never imply investment attractiveness.
# growth: high/moderate/low sensitivity to the growth-and-jobs cycle.
# inflation: "beneficiary" (pricing tied to commodities), "pressure" (costs or
# purchasing power squeezed) or "rates" (valuation/financing tied to interest rates).
SENSITIVITY = {
    "Communication Services": {"growth": "moderate", "inflation": "rates",
        "contrary": "Advertising-driven companies fell sharply in the 2022 rate shock even though the economy kept growing.",
        "watch": "Advertising spending, subscriber growth and borrowing costs."},
    "Consumer Discretionary": {"growth": "high", "inflation": "pressure",
        "contrary": "In 2008 household spending collapsed faster than production data showed; in 2020 online retail grew during a recession.",
        "watch": "Real household income, consumer credit growth and unemployment."},
    "Consumer Staples": {"growth": "low", "inflation": "pressure",
        "contrary": "In 2021–2022 input-cost inflation squeezed margins despite stable demand.",
        "watch": "Input costs, pricing power and volume trends."},
    "Energy": {"growth": "high", "inflation": "beneficiary",
        "contrary": "Energy outperformed in 2022 while growth slowed, and collapsed in 2014–2016 during a global expansion, because supply decisions dominate.",
        "watch": "Oil and gas prices, production discipline and global demand."},
    "Financials": {"growth": "high", "inflation": "rates",
        "contrary": "Rising rates helped lending margins in 2022 but exposed bank balance-sheet losses in 2023.",
        "watch": "Loan growth, credit losses, yield-curve shape and deposit costs."},
    "Health Care": {"growth": "low", "inflation": None,
        "contrary": "Policy and drug-pricing risk can dominate the economic cycle, as in 2015–2016.",
        "watch": "Reimbursement policy, innovation pipelines and funding conditions."},
    "Industrials": {"growth": "high", "inflation": None,
        "contrary": "Supply bottlenecks in 2021 limited output despite strong orders.",
        "watch": "Industrial production, new orders, business lending and capital spending."},
    "Information Technology": {"growth": "moderate", "inflation": "rates",
        "contrary": "Technology valuations fell steeply in 2000–2002 and 2022 for valuation and rate reasons, not only economic ones.",
        "watch": "Enterprise spending, semiconductor cycles and interest rates."},
    "Materials": {"growth": "high", "inflation": "beneficiary",
        "contrary": "Commodity prices can be driven by global (especially Chinese) demand more than U.S. conditions.",
        "watch": "Industrial production, construction activity and commodity prices."},
    "Real Estate": {"growth": "moderate", "inflation": "rates",
        "contrary": "Office property weakened after 2020 for structural reasons while the broader economy recovered.",
        "watch": "Mortgage and financing rates, vacancies, rents and property credit."},
    "Utilities": {"growth": "low", "inflation": "rates",
        "contrary": "Utilities fell with bonds when interest rates jumped in 2022 despite stable demand.",
        "watch": "Interest rates, regulated rate decisions and electricity demand."},
}
BACKDROP = {
    # condition -> growth sensitivity -> backdrop label
    "Expanding": {"high": "Supportive", "moderate": "Supportive", "low": "Neutral"},
    "Slowing": {"high": "Mixed", "moderate": "Mixed", "low": "Relatively resilient"},
    "Deteriorating": {"high": "Headwind", "moderate": "Headwind", "low": "Relatively resilient"},
    "Mixed": {"high": "Mixed", "moderate": "Mixed", "low": "Mixed"},
}


def economic_backdrop(name: str, judgment: dict | None) -> dict:
    """How the current qualified macro reading relates to a sector's exposure.

    This is economic context, not an investment rating or recommendation.
    """
    profile = SENSITIVITY[name]
    condition = (judgment or {}).get("condition")
    base = {"growth_sensitivity": profile["growth"], "inflation_channel": profile["inflation"],
            "contrary_case": profile["contrary"], "watch": profile["watch"],
            "is_investment_rating": False}
    if condition not in BACKDROP:
        return dict(base, backdrop="Not assessed",
                    why="No qualified current economic reading is available.",
                    reverse="A qualified monthly assessment is required first.")
    label = BACKDROP[condition][profile["growth"]]
    why = {
        "Supportive": f"Growth is {condition.lower()} and this sector's demand is closely tied to the growth-and-jobs cycle.",
        "Neutral": "Demand here is relatively insensitive to the cycle, so expansion adds little.",
        "Mixed": f"Conditions are {condition.lower()}, and this sector is exposed to the cycle.",
        "Relatively resilient": f"Conditions are {condition.lower()}, and demand here has typically been less cyclical.",
        "Headwind": "Activity and jobs are weakening, and this sector's demand is cyclical.",
    }[label]
    if condition == "Mixed" and profile["growth"] == "low":
        why = "Indicators disagree; this sector's lower cyclical sensitivity does not settle the question."
    reverse = {
        "Supportive": "A turn to Deteriorating or Mixed conditions (production contracting or unemployment rising) would remove this support.",
        "Neutral": "A deterioration in jobs would make this sector's lower sensitivity more relevant.",
        "Mixed": "Production and employment moving together, in either direction, would clarify the backdrop.",
        "Relatively resilient": "A return to broad expansion would reduce the relative advantage of lower sensitivity.",
        "Headwind": "Production recovering and unemployment stabilizing would ease this headwind.",
    }[label]
    notes = []
    classification = (judgment or {}).get("classification", {})
    if classification.get("inflation") in ("elevated", "high"):
        channel = profile["inflation"]
        if channel == "beneficiary":
            notes.append("Above-goal inflation can support pricing tied to commodities.")
        elif channel == "pressure":
            notes.append("Above-goal inflation can squeeze costs or customers' purchasing power.")
        elif channel == "rates":
            notes.append("Above-goal inflation can keep interest rates high, pressuring valuations or financing.")
    return dict(base, backdrop=label, why=why, reverse=reverse, inflation_note=" ".join(notes) or None)


def _qualified(item: dict, as_of: date) -> bool:
    """A sector rating requires dated, attributable investment AND economic evidence."""
    if not isinstance(item, dict):
        return False
    required = ("economic_fit", "earnings", "valuation", "relative_total_return")
    if not all(isinstance(item.get(key), dict) for key in required):
        return False
    for key in required:
        entry = item[key]
        if (not isinstance(entry.get("source_url"), str)
                or urlparse(entry["source_url"]).scheme != "https"
                or not urlparse(entry["source_url"]).hostname
                or urlparse(entry["source_url"]).hostname in {"example.org", "example.com", "example.net"}
                or not isinstance(entry.get("methodology"), str)
                or not entry["methodology"].strip()
                or not isinstance(entry.get("value"), (int, float))
                or isinstance(entry.get("value"), bool)
                or not math.isfinite(entry["value"])):
            return False
        try:
            observed = date.fromisoformat(entry["observation_date"])
        except (KeyError, TypeError, ValueError):
            return False
        if observed > as_of:
            return False
        # A historic observation cannot silently become a current investment call.
        age_months = (as_of.year - observed.year) * 12 + as_of.month - observed.month
        max_age = {"economic_fit": 3, "earnings": 6,
                   "valuation": 3, "relative_total_return": 12}[key]
        if age_months > max_age:
            return False
    history = item["relative_total_return"]
    return (
        isinstance(history.get("benchmark"), str)
        and bool(history["benchmark"].strip())
        and isinstance(item.get("rationale"), str)
        and bool(item["rationale"].strip())
        and isinstance(history.get("transaction_cost_assumption"), str)
        and bool(history["transaction_cost_assumption"].strip())
        and isinstance(history.get("survivorship_bias_note"), str)
        and bool(history["survivorship_bias_note"].strip())
        and isinstance(history.get("sample_size"), int)
        and not isinstance(history.get("sample_size"), bool)
        and history["sample_size"] >= 1
        and history.get("point_in_time_verified") is True
        and item.get("outlook") in ALLOWED
    )


def build_sector_report(evidence: dict, as_of: date, judgment: dict | None = None) -> dict:
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
            "economic_backdrop": economic_backdrop(name, judgment),
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
