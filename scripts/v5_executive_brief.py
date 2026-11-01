"""Generate a dated, evidence-grounded V5 research brief without forecast claims."""
import argparse
import json
from pathlib import Path


def build(estimates, outcomes):
    if estimates.get("status") != "HISTORICAL_RESEARCH_ONLY":
        raise ValueError("Unapproved cycle estimate status")
    if outcomes.get("status") != "RETROSPECTIVE_FORWARD_OUTCOMES_ONLY":
        raise ValueError("Unapproved outcome status")
    latest = estimates["latest"]
    month = estimates["as_of_month"]
    phase = latest["phase"].replace("_", " ").title()
    signals = ", ".join(latest["supporting_signals"]) or "none"
    conflicts = ", ".join(latest["conflicting_signals"]) or "none"
    lines = [
        "# Monthly Business-Cycle Research Brief",
        "",
        f"**Observation month:** {month}",
        f"**Preliminary phase heuristic:** {phase}",
        "**Status:** Historical research only; not a validated current assessment.",
        "",
        "## Evidence",
        f"- Signals present: {signals}.",
        f"- Other or conflicting signals: {conflicts}.",
        "",
        "## Forward horizons",
        "The following are historical outcome coverage counts, not forecasts:",
    ]
    for horizon in (3, 6, 12):
        item = outcomes["results"][str(horizon)]
        lines.append(f"- {horizon} months: {item['event_months']} historical event windows "
                     f"among {item['eligible_months']} eligible observation months.")
    lines += ["", "## Limitations",
              "- Current-vintage revised data are not release-time observations.",
              "- Historical recession chronology is known only after the fact.",
              "- No calibrated forecast probabilities or numeric confidence are approved.",
              "- Economic-cycle classifications are preliminary and require out-of-sample validation."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("estimates")
    parser.add_argument("outcomes")
    parser.add_argument("--output", default="audit-output/v5_executive_brief.md")
    args = parser.parse_args()
    text = build(json.loads(Path(args.estimates).read_text()),
                 json.loads(Path(args.outcomes).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
