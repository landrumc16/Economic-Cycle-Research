"""Read-only operational status for the existing workbook's separate model domains.

Never generates scores from unapproved evidence. The canonical workbook owns
research, definitions and human approvals; this is a fail-closed adapter.
"""
import argparse
import json
from pathlib import Path

DOMAINS = {
    "economic_cycle": "INTEGRATED CYCLE",
    "crash_mechanisms": "CRASH PATHWAY TYPOLOGY",
    "equity_drawdown_vulnerability": "WALK FORWARD RULE AUDIT",
    "sector_opportunities": "SECTOR OPPORTUNITIES",
    "social_context": "SOCIAL CONTEXT",
}

def build_status(gate, approvals=None):
    approvals = approvals or {}
    series = gate.get("series", {})
    required = ("UNRATE", "CPIAUCSL", "GDPC1")
    evidence_pass = gate.get("all_evidence_pass") is True and all(
        all(series.get(name, {}).get(key) is True for key in (
            "publisher_source_acquired", "independent_source_acquired",
            "numeric_reconciliation_pass", "publisher_vintage_authenticated",
            "release_timing_verified", "point_in_time_no_lookahead_pass",
            "coverage_pass")) for name in required)
    human_pass = all(approvals.get(name) == "APPROVED" for name in required)
    # Source approval alone is insufficient for predictive publication.
    result = {"model_status": "NOT_VALIDATED", "canonical_inputs_approved": evidence_pass and human_pass,
              "historical_predictive_validation": "NOT_VERIFIED",
              "publication": "BLOCKED", "scores_generated": False,
              "series_approval": {name: approvals.get(name, "BLOCKED") for name in required},
              "domains": {}}
    for key, owner in DOMAINS.items():
        result["domains"][key] = {"canonical_workbook_tab": owner,
            "status": "CONTEXT_ONLY_NOT_SCORED" if key == "social_context" else "BLOCKED",
            "score": None, "reason": "No approved input and independently validated predictive model"}
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True)
    parser.add_argument("--approvals", help="Explicit human approval record; absent means blocked")
    parser.add_argument("--output", default="audit-output/operational_model_status.json")
    args = parser.parse_args()
    gate = json.loads(Path(args.gate).read_text())
    approvals = json.loads(Path(args.approvals).read_text()) if args.approvals else {}
    status = build_status(gate, approvals)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
