"""Join canonical lead-window summary to V2 profiles without inferring mechanisms."""
import argparse
import hashlib
import json
from pathlib import Path

def enrich(profiles, source, raw):
    if source.get("source_tab") != "CRASH LEAD WINDOW SUMMARY" or source.get("source_range") != "A4:O12":
        raise ValueError("Unrecognized canonical source")
    if source.get("point_in_time_certified") is not False or source.get("human_approved_for_prediction") is not False:
        raise ValueError("Source promotion requires separate approval")
    if profiles.get("publication") != "BLOCKED" or len(profiles.get("pathway_profiles", [])) != 8:
        raise ValueError("Unexpected profile universe")
    if len(source.get("rows", [])) != 8 or len(source.get("headers", [])) != 15:
        raise ValueError("Incomplete lead-window source")
    by_id = {}
    for row in source["rows"]:
        if len(row) != 15 or row[0] in by_id:
            raise ValueError("Duplicate or malformed source event")
        by_id[row[0]] = dict(zip(source["headers"], row))
    joined = []
    for profile in profiles["pathway_profiles"]:
        key = str(profile["parent_cluster"])
        record = by_id.get(key)
        if record is None or record["Daily market peak"] != profile["peak_date"]:
            raise ValueError("Crash ID and peak-date mismatch")
        count = int(record["Available prior months"])
        if not 1 <= count <= 24:
            raise ValueError("Invalid canonical coverage")
        def number(value):
            return None if value == "MISSING" else int(value)
        joined.append({
            "parent_cluster": key, "peak_date": profile["peak_date"],
            "available_prior_months_canonical": count,
            "parent_max_drawdown": float(record["Parent max DD"]),
            "recession_overlap_hindsight": record["Recession overlap (hindsight)"],
            "financial_watch_any_24m": record["Either financial any 24m?"],
            "financial_watch_any_12m": record["Financial any prior 12m?"],
            "curve_inverted_any_24m": record["Curve inverted any 24m?"],
            "credit_elevated_any_24m": record["Credit >=2.5 any 24m?"],
            "oldest_warning_lead_months": number(record["Earliest warning lead (months)"]),
            "most_recent_warning_lead_months": number(record["Most recent warning lead (months)"]),
            "policy_tightening_any_24m": record["DFF tightening any 24m?"],
            "policy_easing_any_24m": record["DFF easing any 24m?"],
            "inflation_high_any_24m": record["CPI >=4% any 24m?"],
            "labor_worsening_any_24m": record["U3 3m >=0.3pp any 24m?"],
            "status": "CANONICAL_REVISED_NOT_PIT",
        })
    if set(by_id) != {str(x["parent_cluster"]) for x in profiles["pathway_profiles"]}:
        raise ValueError("Extra canonical source event")
    return {
        "schema_version": "2.0.0", "status": "DESCRIPTIVE_ONLY",
        "publication": "BLOCKED", "predictive_model": "NOT_VALIDATED",
        "provenance": {"source_tab": source["source_tab"], "source_range": source["source_range"],
                       "source_sha256": hashlib.sha256(raw).hexdigest(),
                       "source_spreadsheet_id": source["source_spreadsheet_id"],
                       "extraction_date": source["extraction_date"],
                       "point_in_time_certified": False},
        "lead_window_summary": joined,
        "notes": ["Warning oldest lead is not onset", "Financial watch is not credit-spread stress",
                  "Flags overlap and are not mutually exclusive mechanisms",
                  "Source selected on crashes; no specificity estimate or verified noncrash controls",
                  "1987 has only 7 months of canonical lead-trajectory coverage"],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profiles", default="audit-output/v2_pathway_coverage.json")
    p.add_argument("--source", default="data/v2_canonical_lead_window_summary_2026-10-31.json")
    p.add_argument("--output", default="audit-output/v2_lead_window_summary.json")
    a = p.parse_args()
    raw = Path(a.source).read_bytes()
    result = enrich(json.loads(Path(a.profiles).read_text()), json.loads(raw), raw)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")

if __name__ == "__main__":
    main()
