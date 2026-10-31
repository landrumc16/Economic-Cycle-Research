"""Version 1 research-dashboard release-candidate acceptance gate.

A usable research snapshot is distinct from a predictive model approval.
Missing live sources must be disclosed, never silently promoted.
"""
import argparse
import json
from pathlib import Path

REQUIRED_SECTIONS = (
    "Economic Cycle Research", "Current research observations",
    "Growth, labor and inflation", "Integrated economic-cycle assessment",
    "Financial and housing conditions", "Historical macro similarities",
    "Source readiness", "Crash pathway comparison",
)
FORBIDDEN_TOKENS = ("ASSESSMENTMACRO", "FINANCIALCONTEXTANALOGUES", "CYCLEANALOGUES")

def evaluate(page, state):
    issues = []
    for section in REQUIRED_SECTIONS:
        if section not in page:
            issues.append("MISSING_SECTION:" + section)
    for token in FORBIDDEN_TOKENS:
        if token in page:
            issues.append("UNREPLACED_TEMPLATE_TOKEN:" + token)
    if state.get("publication") != "BLOCKED":
        issues.append("PREDICTIVE_PUBLICATION_MUST_REMAIN_BLOCKED")
    if state.get("crash_probability") is not None or state.get("validated_cycle_stage") is not None:
        issues.append("UNAUTHORIZED_PREDICTIVE_OUTPUT")
    if state.get("point_in_time_certified") is not False:
        issues.append("POINT_IN_TIME_STATUS_MUST_BE_FALSE")
    for field in ("macro_domains", "financial_observations", "current_cycle_assessment",
                  "historical_macro_analogues"):
        if field not in state:
            issues.append("MISSING_STATE_FIELD:" + field)
    current = state.get("current_cycle_assessment")
    analogues = state.get("historical_macro_analogues")
    if not isinstance(current, dict):
        issues.append("CURRENT_ASSESSMENT_UNAVAILABLE")
    if not isinstance(analogues, dict):
        issues.append("HISTORICAL_COMPARISON_UNAVAILABLE")
    elif analogues.get("status") != "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE":
        issues.append("HISTORICAL_COMPARISON_NOT_POPULATED")
    macro = state.get("macro_domains")
    if not isinstance(macro, dict) or any(
        not isinstance(macro.get(name, {}).get("observation"), (int, float))
        or isinstance(macro.get(name, {}).get("observation"), bool)
        for name in ("growth", "labor", "inflation")
    ):
        issues.append("CURRENT_MACRO_VALUES_MISSING")
    financial = state.get("financial_observations")
    if not isinstance(financial, list) or not financial:
        issues.append("FINANCIAL_SNAPSHOT_MISSING")
    if isinstance(current, dict):
        if current.get("publication") != "BLOCKED" or current.get("crash_probability") is not None:
            issues.append("CURRENT_ASSESSMENT_PREDICTIVE_GATE")
        lenses = current.get("mechanism_lenses", {})
        if not isinstance(lenses, dict) or len(lenses) < 5:
            issues.append("MECHANISM_LENSES_INCOMPLETE")
    if isinstance(analogues, dict) and analogues.get("status") == "EXPLORATORY_MACRO_SIMILARITY_NOT_PREDICTIVE":
        entries = analogues.get("analogues")
        if not isinstance(entries, list) or sum(
            isinstance(e, dict) and e.get("status") == "EXPLORATORY_ANALOGUE"
            for e in entries
        ) < 5:
            issues.append("HISTORICAL_EPISODES_INCOMPLETE")
        if analogues.get("crash_probability") is not None:
            issues.append("HISTORICAL_COMPARISON_PREDICTIVE_GATE")
    return {
        "status": "RESEARCH_DASHBOARD_CANDIDATE" if not issues else "INCOMPLETE",
        "predictive_model_status": "NOT_VALIDATED",
        "publication": "BLOCKED",
        "checks_passed": len(issues) == 0,
        "issues": issues,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html", default="audit-output/dashboard/index.html")
    p.add_argument("--state", default="audit-output/dashboard/state.json")
    p.add_argument("--output", default="audit-output/dashboard/v1_acceptance.json")
    args = p.parse_args()
    html_path, state_path = Path(args.html), Path(args.state)
    if html_path.exists() and state_path.exists():
        result = evaluate(html_path.read_text(), json.loads(state_path.read_text()))
    else:
        result = {"status": "INCOMPLETE", "checks_passed": False, "publication": "BLOCKED",
                  "predictive_model_status": "NOT_VALIDATED",
                  "issues": [str(p) + ":MISSING" for p in (html_path, state_path) if not p.exists()]}
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    # Research acquisition is allowed to be unavailable on push; record incomplete
    # rather than misreporting a release candidate or blocking evidence upload.

if __name__ == "__main__":
    main()
