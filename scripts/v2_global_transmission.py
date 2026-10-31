"""V2 global transmission evidence inventory; absence of sources is never a negative signal."""
import argparse
import json
from pathlib import Path

CHANNELS = {
    "cross_border_banking": ("BIS international banking statistics", "Cross-border claims and funding stress"),
    "global_usd_funding": ("BIS and Federal Reserve dollar funding/swap lines", "Offshore dollar liquidity and swap demand"),
    "foreign_yield_curves": ("OECD and national central banks", "Policy and term-structure divergence"),
    "exchange_rates": ("Federal Reserve H.10 and BIS effective exchange rates", "Currency and dollar strength"),
    "trade_demand": ("CPB World Trade Monitor and WTO", "Global goods trade volume"),
    "sovereign_credit": ("IMF and national sovereign market sources", "Sovereign funding and spread stress"),
    "global_equities": ("MSCI or verified national index histories", "International equity drawdown and co-movement"),
    "commodity_shocks": ("World Bank Pink Sheet and EIA", "Energy and raw-material price shocks"),
}
def build(profiles):
    if profiles.get("publication") != "BLOCKED" or profiles.get("status") != "DESCRIPTIVE_ONLY":
        raise ValueError("Unapproved input")
    events = profiles.get("pathway_profiles", [])
    if len(events) != 8:
        raise ValueError("Expected eight canonical crash clusters")
    return {
        "schema_version": "2.0.0", "status": "EVIDENCE_INVENTORY_ONLY",
        "publication": "BLOCKED", "predictive_model": "NOT_VALIDATED",
        "source_crash_snapshot_sha256": profiles["source_sha256"],
        "channels": [{"channel": key, "candidate_primary_source": source, "transmission_question": question,
                      "historical_observation": None, "current_observation": None,
                      "point_in_time_certified": False, "status": "SOURCE_NOT_ACQUIRED"}
                     for key, (source, question) in CHANNELS.items()],
        "crash_channel_matrix": [
            {"parent_cluster": event["parent_cluster"], "peak_date": event["peak_date"],
             "channels": {key: {"value": None, "status": "NOT_ASSESSED"} for key in CHANNELS}}
            for event in events],
        "coverage": {"channels_defined": len(CHANNELS), "channels_with_historical_data": 0,
                     "channels_with_current_data": 0, "parent_clusters": len(events)},
        "limitations": [
            "Candidate sources are acquisition targets, not evidence that observations were retrieved",
            "No contagion or causal attribution from absent international data",
            "Historical vintage and cross-country comparability remain unverified",
            "No forecast, crash score, or probability may be derived from this inventory",
        ],
    }
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profiles", default="audit-output/v2_pathway_coverage.json")
    p.add_argument("--output", default="audit-output/v2_global_transmission.json")
    a = p.parse_args()
    result = build(json.loads(Path(a.profiles).read_text()))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
if __name__ == "__main__":
    main()
