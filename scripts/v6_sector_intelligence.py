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


def _qualified(item: dict, as_of: date) -> bool:
    """A sector rating requires dated, attributable investment AND economic evidence."""
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
        and history.get("sample_size", 0) >= 1
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
        qualified = _qualified(item, as_of)
        sectors.append({
            "sector": name,
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
