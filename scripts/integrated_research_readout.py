"""Fail-closed unified research readout. No predictive inference or approval promotion."""
import argparse
import json
from pathlib import Path

WORKBOOK = "SEM_Historical_Crash_Research_v1"
RESEARCH = {
    "crash_mechanisms": {
        "owner": "CRASH PATHWAY TYPOLOGY",
        "evidence_tabs": ["CRASH EVENTS", "NASDAQ PARENT CRASH CLUSTERS", "STRESS FIRST PATHWAY AUDIT"],
        "inference": "HISTORICAL_TAXONOMY_ONLY",
    },
    "false_alarm_controls": {
        "owner": "WARNING NONCRASH BASELINES",
        "evidence_tabs": ["WALK FORWARD RULE AUDIT", "CLEAN SIGNAL RULE SUMMARY",
                          "SIGNAL EPISODE COUNTS", "ERA HOLDOUT DIAGNOSTIC"],
        "inference": "DISCOVERY_NOT_UNTOUCHED_OUT_OF_SAMPLE",
    },
    "social_context": {
        "owner": "SOCIAL CONTEXT", "evidence_tabs": ["SOCIAL CONTEXT"],
        "inference": "INTERPRETIVE_NOT_VALIDATED_PREDICTOR",
    },
    "sector_opportunities": {
        "owner": "SECTOR OPPORTUNITIES", "evidence_tabs": ["SECTOR OPPORTUNITIES"],
        "inference": "NO_AUTHORIZED_RECOMMENDATION",
    },
}

def combine(macro, financial):
    if not isinstance(macro, dict) or not isinstance(financial, dict):
        raise ValueError("Both upstream reports must be JSON objects")
    if not isinstance(macro.get("domains"), dict) or not isinstance(financial.get("domains"), dict):
        raise ValueError("Missing upstream domain objects")
    return {
        "status": "RESEARCH_ONLY_NOT_PIT_CERTIFIED",
        "publication": "BLOCKED",
        "validated_cycle_stage": None,
        "crash_probability": None,
        "composite_risk_score": None,
        "sector_recommendation": None,
        "authority": {"workbook": WORKBOOK, "research_inventory": "docs/EXISTING_RESEARCH_RECONCILIATION.md"},
        "economic_cycle": {
            "domains": macro["domains"],
            "cross_domain": macro.get("cross_domain", "INSUFFICIENT_DATA"),
            "upstream_status": macro.get("status", "UNKNOWN"),
            "provenance": "descriptive_macro_metrics.json / cycle_research_readout.json; revised, not certified PIT",
        },
        "financial_housing": {
            "domains": financial["domains"],
            "snapshot_date": financial.get("snapshot_date"),
            "snapshot_type": financial.get("snapshot_type"),
            "as_of": financial.get("as_of"),
            "upstream_status": financial.get("status", "UNKNOWN"),
            "provenance": "CURRENT RISK INPUTS dated manual snapshot; per-series quality preserved",
        },
        "research_layers": RESEARCH,
        "validation": {
            "publisher_original_vintages": "INCOMPLETE",
            "point_in_time_no_lookahead": "INCOMPLETE",
            "untouched_out_of_sample": "INCOMPLETE",
            "human_model_approval": "NOT_GRANTED",
        },
        "limitations": [
            "Workbook retrospective episodes and noncrash controls are not independent predictive validation",
            "No probability, risk score, cycle-stage prediction, or sector recommendation is authorized",
            "Financial observations retain their original quality and eligibility without promotion",
        ],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--macro", default="audit-output/cycle_research_readout.json")
    p.add_argument("--financial", default="audit-output/financial_housing_overlay.json")
    p.add_argument("--output", default="audit-output/integrated_research_readout.json")
    a = p.parse_args()
    result = combine(json.loads(Path(a.macro).read_text()), json.loads(Path(a.financial).read_text()))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "publication": result["publication"], "output": str(target)}))

if __name__ == "__main__":
    main()
