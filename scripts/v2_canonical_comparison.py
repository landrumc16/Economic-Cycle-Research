"""Version 2 read-only canonical research comparison, not a crash predictor.

Preserves provenance, crash/noncrash distinction and non-independent windows.
"""
import argparse
import hashlib
import json
from pathlib import Path

def number(value):
    try:
        return float(value) if value not in (None, "") else None
    except (ValueError, TypeError):
        return None

def build(snapshot, raw_bytes):
    if snapshot.get("point_in_time_certified") is not False or snapshot.get("human_approved_for_prediction") is not False:
        raise ValueError("Unexpected source certification: review before promotion")
    if snapshot.get("export_type") != "dated_read_only_research_snapshot":
        raise ValueError("Canonical dated export required")
    pathways = snapshot["pathways"]
    baseline = snapshot["noncrash"]
    if pathways.get("source_tab") != "CRASH PATHWAY TYPOLOGY" or baseline.get("source_tab") != "WARNING NONCRASH BASELINES":
        raise ValueError("Unexpected canonical workbook tabs")
    if len(pathways["rows"]) < 2 or len(baseline["rows"]) < 2:
        raise ValueError("Canonical rows missing")
    crashes = []
    for row in pathways["rows"][1:]:
        if len(row) < 12:
            raise ValueError("Incomplete crash row")
        crashes.append({
            "parent_cluster": row[0], "peak_date": row[1], "prior_month": row[2],
            "first_20pct_crossing": row[3], "recession_overlap_hindsight": row[4],
            "curve_pp": number(row[5]), "credit_pp": number(row[6]),
            "inflation_pct": number(row[7]), "unemployment_3m_pp": number(row[8]),
            "gdp_yoy_pct": number(row[9]), "policy_12m_pp": number(row[10]),
            "financial_stress": row[11] == "YES",
            "source_status": "REVISED_NOT_PIT_NOT_PREDICTIVE",
        })
    monthly = []
    for row in baseline["rows"][1:]:
        if len(row) < 12:
            raise ValueError("Incomplete monthly baseline row")
        monthly.append({
            "month": row[0], "curve_pp": number(row[2]), "credit_pp": number(row[3]),
            "financial_stress": row[4] == "YES",
            "source_status": "REVISED_NOT_PIT_NOT_PREDICTIVE",
        })
    stress_crashes = sum(r["financial_stress"] for r in crashes)
    stress_months = sum(r["financial_stress"] for r in monthly)
    return {
        "schema_version": "2.0.0", "status": "DESCRIPTIVE_ONLY", "publication": "BLOCKED",
        "crash_probability": None, "validated_cycle_stage": None,
        "provenance": {
            "source_workbook": snapshot["source_workbook"],
            "spreadsheet_id": snapshot["source_spreadsheet_id"],
            "sha256_export": hashlib.sha256(raw_bytes).hexdigest(),
            "tabs": [
                {"name": pathways["source_tab"], "range": pathways["source_range"],
                 "data_rows": len(crashes)},
                {"name": baseline["source_tab"], "range": baseline["source_range"],
                 "data_rows": len(monthly)},
            ],
            "extraction_timestamp": None,
            "extraction_timestamp_status": "NOT_RECORDED_IN_SOURCE_EXPORT",
            "point_in_time_certified": False,
            "human_approved_for_prediction": False,
        },
        "crash_parent_clusters": crashes,
        "monthly_stress_baseline": monthly,
        "descriptive_comparison": {
            "crash_parent_clusters": len(crashes),
            "crash_parent_clusters_with_stress": stress_crashes,
            "crash_stress_fraction": stress_crashes / len(crashes),
            "monthly_observations": len(monthly),
            "monthly_observations_with_stress": stress_months,
            "monthly_stress_fraction": stress_months / len(monthly),
            "interpretation": "Different denominators; these fractions are NOT a predictive test or comparable event probabilities",
        },
        "limitations": [
            "Monthly observations include crash periods and are NOT verified non-crash controls",
            "Overlapping monthly windows are not independent samples",
            "Crash parent clusters and monthly observations have different sampling units",
            "No point-in-time release verification, no untouched out-of-sample validation",
            "No pathway labels inferred from numeric features",
            "Missing housing, valuation and social observations remain missing; do not impute",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", default="data/workbook_historical_research_snapshot_2026-10-30.json")
    p.add_argument("--output", default="audit-output/v2_canonical_comparison.json")
    a = p.parse_args()
    raw = Path(a.snapshot).read_bytes()
    result = build(json.loads(raw), raw)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "clusters": len(result["crash_parent_clusters"]),
                      "months": len(result["monthly_stress_baseline"])}))

if __name__ == "__main__":
    main()
