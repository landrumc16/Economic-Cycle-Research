"""Strict event-outcome labeling with independently documented dates; research only."""
from datetime import date, timedelta


def parse(value):
    return date.fromisoformat(value)


def label_windows(events, windows, as_of, horizon_days=180, embargo_days=30):
    if horizon_days < 1 or embargo_days < 0:
        raise ValueError("Invalid horizon or embargo")
    cutoff = parse(as_of)
    validated = []
    seen = set()
    for event in events:
        parent = event["parent_cluster"]
        if parent in seen:
            raise ValueError("Duplicate event parent")
        seen.add(parent)
        onset = parse(event["onset_date"])
        end = parse(event["end_date"])
        if end < onset or onset > cutoff:
            raise ValueError("Invalid or future event chronology")
        if not event.get("outcome_source") or not event.get("objective_rule"):
            raise ValueError("Objective rule and event provenance required")
        validated.append((parent, onset, end))
    results = []
    for window in windows:
        start = parse(window["as_of"])
        if start > cutoff:
            raise ValueError("Future prediction origin")
        end = start + timedelta(days=horizon_days)
        mature = end <= cutoff
        hits = [p for p, onset, _ in validated if start < onset <= end]
        proximity = [p for p, onset, finish in validated
                     if start - timedelta(days=embargo_days) <= finish
                     and end + timedelta(days=embargo_days) >= onset]
        coverage = window.get("complete_outcome_coverage") is True and bool(window.get("outcome_source"))
        if not mature:
            label = "CENSORED_FUTURE_HORIZON"
        elif not coverage:
            label = "UNVERIFIED_OUTCOME_COVERAGE"
        elif hits:
            label = "POSITIVE_RESEARCH_LABEL"
        elif proximity:
            label = "EMBARGOED"
        else:
            label = "NEGATIVE_RESEARCH_LABEL"
        results.append({"as_of": start.isoformat(), "horizon_end": end.isoformat(),
                        "label": label, "event_parents": hits, "embargo_parents": proximity,
                        "outcome_source": window.get("outcome_source")})
    return {"schema_version": 1, "status": "RESEARCH_ONLY", "as_of": as_of,
            "horizon_days": horizon_days, "embargo_days": embargo_days,
            "event_count": len(validated), "windows": results,
            "point_in_time_features_certified": False,
            "independent_holdout_certified": False, "predictive_publication": "BLOCKED"}

def main():
    import argparse
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--events")
    p.add_argument("--windows")
    p.add_argument("--as-of", required=True)
    p.add_argument("--output", default="audit-output/v5_objective_outcomes.json")
    args = p.parse_args()
    events = json.loads(Path(args.events).read_text()) if args.events else []
    windows = json.loads(Path(args.windows).read_text()) if args.windows else []
    if not isinstance(events, list) or not isinstance(windows, list):
        raise ValueError("Event and window inputs must be arrays")
    report = label_windows(events, windows, args.as_of)
    report["coverage_status"] = "NO_VERIFIED_OUTCOME_INPUTS" if not events or not windows else "INPUTS_REQUIRE_INDEPENDENT_AUDIT"
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
