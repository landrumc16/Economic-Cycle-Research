"""V4 predictive-validation gate: explicitly fail closed without independently verified cohorts."""
def validate(episodes, global_social=None):
    if episodes.get("report_type") != "V4_HISTORICAL_EPISODE_REGISTRY":
        raise ValueError("Historical registry required")
    checks = {
        "independent_episodes": episodes.get("independent_episodes_verified") is True,
        "genuine_negative_controls": episodes.get("verified_negative_control_labels_available") is True,
        "original_pit_vintages": episodes.get("point_in_time_replay_certified") is True,
        "chronological_holdouts": episodes.get("chronological_holdouts_defined") is True,
        "calibration_report": False,
        "falsification_and_false_alarm_review": False,
        "independent_validation": False,
    }
    return {
        "schema_version": 1, "report_type": "V4_PREDICTIVE_VALIDATION_GATE",
        "status": "BLOCKED" if not all(checks.values()) else "REQUIRES_INDEPENDENT_APPROVAL",
        "checks": checks, "validated_crash_probability": None,
        "validated_cycle_stage": None, "predictive_publication": "BLOCKED",
        "descriptive_product_release_permitted": True,
        "limitations": [
            "A descriptive product can ship while predictive claims remain blocked",
            "Missing original vintages, controls, holdouts, calibration or independent review preclude prediction",
        ],
    }

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--episodes", default="audit-output/v4_historical_episode_registry.json")
    p.add_argument("--output", default="audit-output/v4_predictive_validation_gate.json")
    a = p.parse_args()
    result = validate(json.loads(Path(a.episodes).read_text()))
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "descriptive_release": result["descriptive_product_release_permitted"]}))
