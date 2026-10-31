"""Summarize weekly evidence changes without treating observation age as release age."""

def summarize(indicators):
    buckets = {"new_observations": [], "revisions": [], "carried_forward": [],
               "unavailable": [], "source_transitions": []}
    for item in indicators:
        name = item["series"]
        if item.get("source_availability_changed"):
            buckets["source_transitions"].append(name)
        if item.get("value") is None:
            buckets["unavailable"].append(name)
        elif item.get("same_observation_revision_detected"):
            buckets["revisions"].append(name)
        elif item.get("new_observation_date") and item.get("delta_new_release") is not None:
            buckets["new_observations"].append(name)
        else:
            buckets["carried_forward"].append(name)
    return {
        "status": "DESCRIPTIVE_ONLY",
        "baseline_note": "New means a newer observation date relative to a prior snapshot, not a verified publication within seven days.",
        "categories": buckets,
        "counts": {key: len(value) for key, value in buckets.items()},
        "economic_direction": None,
        "validated_cycle_stage": None,
        "crash_probability": None,
    }
