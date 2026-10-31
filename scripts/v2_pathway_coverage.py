"""Version 2 pathway feature coverage; never infer a mechanism from a market peak."""
import argparse
import json
from pathlib import Path

FEATURES = {
    "growth": "gdp_yoy_pct",
    "inflation": "inflation_pct",
    "labor": "unemployment_3m_pp",
    "policy": "policy_12m_pp",
    "yield_curve": "curve_pp",
    "credit": "credit_pp",
}
UNAVAILABLE = ("housing", "valuation", "social_context", "international_transmission")

def assemble(comparison):
    if comparison.get("status") != "DESCRIPTIVE_ONLY" or comparison.get("publication") != "BLOCKED":
        raise ValueError("Requires blocked canonical descriptive comparison")
    events = comparison.get("crash_parent_clusters", [])
    if len(events) != 8:
        raise ValueError("Unexpected crash parent-cluster universe")
    profiles = []
    for event in events:
        features = {
            domain: {"value": event.get(key), "status": "REVISED_NOT_PIT" if event.get(key) is not None else "MISSING"}
            for domain, key in FEATURES.items()
        }
        features.update({domain: {"value": None, "status": "NOT_IN_CANONICAL_EXPORT"} for domain in UNAVAILABLE})
        profiles.append({
            "parent_cluster": event["parent_cluster"],
            "peak_date": event["peak_date"],
            "prior_month": event["prior_month"],
            "pathway_mechanism": None,
            "pathway_status": "CANONICAL_MECHANISM_MAPPING_NOT_EXPORTED",
            "recession_overlap_hindsight": event["recession_overlap_hindsight"],
            "financial_stress": event["financial_stress"],
            "features": features,
        })
    domains = list(FEATURES) + list(UNAVAILABLE)
    return {
        "schema_version": "2.0.0",
        "status": "DESCRIPTIVE_ONLY",
        "publication": "BLOCKED",
        "predictive_model": "NOT_VALIDATED",
        "source_sha256": comparison["provenance"]["sha256_export"],
        "pathway_profiles": profiles,
        "coverage": {
            domain: {
                "observed_parent_clusters": sum(p["features"][domain]["value"] is not None for p in profiles),
                "total_parent_clusters": len(profiles),
                "status": "REVISED_NOT_PIT" if domain in FEATURES else "NOT_IN_CANONICAL_EXPORT",
            }
            for domain in domains
        },
        "control_status": "NOT_VERIFIED",
        "notes": [
            "Mechanism labels require explicit canonical workbook mapping, not inferred from financial indicators",
            "Monthly stress observations are not verified non-crash controls",
            "Housing, valuation, social and global context are missing from this export; do not fill with assumptions",
            "Historical revised indicators cannot establish what was known at each peak",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--comparison", default="audit-output/v2_canonical_comparison.json")
    p.add_argument("--output", default="audit-output/v2_pathway_coverage.json")
    a = p.parse_args()
    result = assemble(json.loads(Path(a.comparison).read_text()))
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"profiles": len(result["pathway_profiles"]), "control_status": result["control_status"]}))

if __name__ == "__main__":
    main()
