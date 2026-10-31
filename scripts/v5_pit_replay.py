"""Fail-closed publisher-vintage point-in-time feature replay and chronological split audit."""
from datetime import date, timedelta


def replay(records, origins, embargo_days=30):
    if embargo_days < 0:
        raise ValueError("Negative embargo")
    outputs = []
    for origin in origins:
        cutoff = date.fromisoformat(origin)
        selected = {}
        rejected = []
        for row in records:
            name = row["series"]
            observation = date.fromisoformat(row["observation_date"])
            available = row.get("available_at")
            vintage = row.get("vintage_date")
            if not available or not vintage or row.get("publisher_original") is not True:
                rejected.append({"series": name, "reason": "UNVERIFIED_PUBLISHER_VINTAGE"})
                continue
            released = date.fromisoformat(available)
            revised = date.fromisoformat(vintage)
            if observation > cutoff or released > cutoff or revised > cutoff:
                rejected.append({"series": name, "reason": "FUTURE_INFORMATION"})
                continue
            if released < observation or revised < observation:
                raise ValueError("Invalid release or vintage chronology")
            key = (observation, released, revised)
            if name not in selected or key > selected[name][0]:
                selected[name] = (key, row["value"])
        outputs.append({"as_of": origin, "features": {name: {"value": item[1],
                        "observation_date": item[0][0].isoformat(),
                        "available_at": item[0][1].isoformat(),
                        "vintage_date": item[0][2].isoformat()}
                        for name, item in sorted(selected.items())},
                        "rejected": rejected})
    return {"schema_version": 1, "report_type": "V5_PIT_REPLAY",
            "replays": outputs, "publisher_original_coverage": sum(len(x["features"]) for x in outputs),
            "predictive_publication": "BLOCKED", "independent_validation_certified": False}


def chronological_split(rows, train_end, test_start, embargo_days=30):
    train = date.fromisoformat(train_end)
    test = date.fromisoformat(test_start)
    if embargo_days < 0 or train + timedelta(days=embargo_days) >= test:
        raise ValueError("Chronological embargo violation")
    parents_train = {x["parent_cluster"] for x in rows if date.fromisoformat(x["as_of"]) <= train}
    parents_test = {x["parent_cluster"] for x in rows if date.fromisoformat(x["as_of"]) >= test}
    if parents_train & parents_test:
        raise ValueError("Event parent leaks across holdout")
    return {"train_end": train_end, "test_start": test_start,
            "embargo_days": embargo_days, "parent_overlap": [],
            "status": "SPLIT_CONTRACT_PASSED_NOT_VALIDATED"}
