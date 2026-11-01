"""Guard against stale or unreviewed Google Sheets promotion evidence."""
from datetime import date
import argparse
import json
from pathlib import Path

MAX_AGE_DAYS = 7


def assess(evidence, today, max_age_days=MAX_AGE_DAYS):
    raw_date = evidence.get("snapshot_retrieval_date")
    try:
        retrieved = date.fromisoformat(raw_date)
    except (TypeError, ValueError):
        retrieved = None
    age = (today - retrieved).days if retrieved else None
    timely = age is not None and 0 <= age <= max_age_days
    reviewed = evidence.get("evidence_reviewed") is True
    approved = reviewed and timely and all(
        evidence.get("macro_promotion", {}).get(s) == "APPROVED"
        for s in ("UNRATE", "CPIAUCSL", "GDPC1")
    )
    return {
        "status": "EVIDENCE_CURRENT" if timely else "EVIDENCE_STALE_OR_MISSING",
        "retrieval_date": raw_date,
        "age_days": age,
        "max_age_days": max_age_days,
        "evidence_reviewed": reviewed,
        "canonical_macro_approved": approved,
        "note": "Freshness alone never authorizes data promotion.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence")
    p.add_argument("--as-of", default=date.today().isoformat())
    p.add_argument("--output", default="audit-output/v5_workbook_freshness.json")
    args = p.parse_args()
    result = assess(json.loads(Path(args.evidence).read_text()), date.fromisoformat(args.as_of))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
