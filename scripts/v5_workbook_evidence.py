"""Convert a bounded, reviewed Sheet promotion-gate export to status evidence.

Input is a JSON object with rows in the order returned by a Google Sheets
values read of 'DATA PROMOTION GATE'!A2:H5. Never infer approval from staging.
"""
import argparse
import json
from pathlib import Path

SERIES = ("UNRATE", "CPIAUCSL", "GDPC1")


def convert(rows, source_url, reviewed=False):
    if not source_url.startswith("https://docs.google.com/spreadsheets/d/"):
        raise ValueError("Source must be a Google Sheets URL")
    by_series = {}
    if rows and rows[0] and str(rows[0][0]).strip().lower() == 'series':
        rows = rows[1:]
    for row in rows:
        if not row or row[0] not in SERIES:
            continue
        if len(row) < 8:
            raise ValueError("Missing promotion evidence columns")
        series = row[0]
        if series in by_series:
            raise ValueError("Duplicate macro series")
        approval = str(row[7]).strip().upper()
        if approval not in ("APPROVED", "BLOCKED"):
            approval = "NOT_RECONCILED"
        by_series[series] = {
            "promotion": approval,
            "publisher": str(row[1]),
            "crosscheck": str(row[5]),
            "vintage_review": str(row[6]),
        }
    if set(by_series) != set(SERIES):
        raise ValueError("Missing required macro series")
    # 'APPROVED' cell text is not sufficient: crosscheck and vintage
    # must both explicitly pass, and the evidence must be reviewed.
    promotions = {}
    for series, evidence in by_series.items():
        eligible = (reviewed and evidence["promotion"] == "APPROVED"
                    and evidence["crosscheck"].strip().upper() == "PASS"
                    and evidence["vintage_review"].strip().upper() == "PASS")
        promotions[series] = "APPROVED" if eligible else "BLOCKED"
    return {
        "source_url": source_url,
        "source_range": "'DATA PROMOTION GATE'!A2:H5",
        "evidence_reviewed": bool(reviewed),
        "macro_promotion": promotions,
        "details": by_series,
        "daily_refresh_status": "NOT_RECONCILED",
        "note": "Snapshot only. No live Google Sheets connection or automatic source approval.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--reviewed", action="store_true")
    parser.add_argument("--output", default="audit-output/v5_workbook_evidence.json")
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    result = convert(snapshot["rows"], snapshot["source_url"], args.reviewed)
    result["snapshot_retrieval_date"] = snapshot.get("retrieval_date")
    result["snapshot_review_status"] = snapshot.get("review_status", "UNKNOWN")
    if result["snapshot_review_status"] != "REVIEWED":
        result["evidence_reviewed"] = False
        result["macro_promotion"] = {series: "BLOCKED" for series in SERIES}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"macro_promotion": result["macro_promotion"],
                      "evidence_reviewed": result["evidence_reviewed"]}))


if __name__ == "__main__":
    main()
