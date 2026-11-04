"""Independent historical episode validation. No future data in a retrospective signal."""
from datetime import date

ALLOWED = {"expansion", "slowing_expansion", "contraction", "recovery", "non_downturn"}

def validate_episodes(episodes, as_of=None):
    """Return transparent coverage, not a probability or an accuracy claim."""
    if not isinstance(episodes, list):
        raise ValueError("Episodes must be a list")
    seen = set()
    intervals = []
    accepted = []
    for item in episodes:
        if not isinstance(item, dict):
            raise ValueError("Invalid episode")
        name = item.get("id")
        label = item.get("outcome")
        if not isinstance(name, str) or not name or name in seen or label not in ALLOWED:
            raise ValueError("Duplicate, missing or invalid episode")
        seen.add(name)
        try:
            signal = date.fromisoformat(item["signal_date"])
            cutoff = date.fromisoformat(item["data_available_date"])
            outcome = date.fromisoformat(item["outcome_date"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid historical chronology") from exc
        if cutoff > signal or outcome <= signal or (as_of is not None and outcome > as_of):
            raise ValueError("Lookahead or invalid outcome chronology")
        if item.get("point_in_time_verified") is not True:
            raise ValueError("Historical episode lacks point-in-time verification")
        # Overlapping signal/outcome windows are not independent episodes.
        if any(signal <= end and start <= outcome for start, end in intervals):
            raise ValueError("Overlapping historical episodes cannot count independently")
        intervals.append((signal, outcome))
        accepted.append({"id": name, "outcome": label, "signal_date": signal.isoformat()})
    controls = sum(x["outcome"] == "non_downturn" for x in accepted)
    events = sum(x["outcome"] == "contraction" for x in accepted)
    other_phases = len(accepted) - controls - events
    return {"episodes": accepted, "independent_events": events,
            "negative_controls": controls, "other_phases": other_phases, "ready_for_holdout": events >= 3 and controls >= 3,
            "predictive_skill_certified": False,
            "note": "Coverage alone does not establish forecasting skill; holdout calibration and embargo remain required."}
