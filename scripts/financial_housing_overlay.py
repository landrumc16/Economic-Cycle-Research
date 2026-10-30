"""Financial, housing and household context from an explicit source-evidence export.

Input is a JSON export of the existing CURRENT RISK INPUTS tab, not a live feed.
No auto-promotion, thresholds, cycle stage, or crash score.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

REGISTRY = {
    "BAA10Y": ("credit", "percentage points"),
    "T10Y2Y": ("yield_curve", "percentage points"),
    "HOUST": ("housing_starts", "thousands SAAR"),
    "TDSP": ("household_debt_service", "percent disposable income"),
    "VIXCLS": ("equity_volatility", "index points"),
}
def build_overlay(rows, as_of):
    today = dt.date.fromisoformat(as_of)
    result = {"status": "RESEARCH_CONTEXT_ONLY", "publication": "BLOCKED",
              "composite_risk_score": None, "crash_probability": None,
              "source": "CURRENT RISK INPUTS", "as_of": as_of, "domains": {}}
    if not isinstance(rows, list):
        raise ValueError("Expected explicit list of source rows")
    indexed = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid row")
        key = row.get("series_id")
        if key in REGISTRY:
            if key in indexed:
                raise ValueError(f"Duplicate source series {key}")
            indexed[key] = row
    for key, (domain, unit) in REGISTRY.items():
        row = indexed.get(key, {})
        value, date, issue = None, None, "MISSING"
        if row:
            try:
                date = dt.date.fromisoformat(row["observation_date"])
                number = float(row["value"])
                if not math.isfinite(number):
                    raise ValueError("Nonfinite value")
                if date > today:
                    raise ValueError("Future observation date")
                if number < 0 and key in ("HOUST", "TDSP", "VIXCLS", "BAA10Y"):
                    raise ValueError("Negative level")
                value, issue = number, None
            except (KeyError, TypeError, ValueError, OverflowError):
                issue = "INVALID_OBSERVATION"
        verified = (row.get("publisher_verified") is True and
                    row.get("vintage_verified") is True and
                    row.get("human_approved") is True)
        result["domains"][domain] = {
            "series_id": key, "value": value,
            "observation_date": date.isoformat() if value is not None else None,
            "unit": unit, "quality": "APPROVED_SOURCE" if verified and value is not None
                    else "STAGED_NOT_APPROVED" if value is not None else issue,
            "published_model_eligible": verified and value is not None,
            "interpretation": None
        }
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Explicit source-evidence JSON export")
    p.add_argument("--as-of", required=True, help="Evaluation date YYYY-MM-DD")
    p.add_argument("--output", default="audit-output/financial_housing_overlay.json")
    a = p.parse_args()
    rows = json.loads(Path(a.input).read_text())
    report = build_overlay(rows, a.as_of)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
