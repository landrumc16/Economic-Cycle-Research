"""Fail descriptive release when input or outcome evidence is incomplete."""
import json
import sys
from pathlib import Path


def validate(root):
    report = {"status": "DESCRIPTIVE_ACCEPTANCE_ONLY", "series": {}}
    for series in ("NASDAQCOM", "CSUSHPINSA"):
        folder = root / "data/industry_observations"
        meta = json.loads((folder / (series + "_metadata.json")).read_text())
        deviations = json.loads((root / "audit-output" / (series + "_deviation.json")).read_text())
        comparison = json.loads((root / "audit-output" / (series + "_comparison.json")).read_text())
        assert meta["series"] == series
        assert meta["point_in_time_certified"] is False
        assert meta["observations"] >= 120, series + ": insufficient observations"
        assert deviations["publication"] == "DESCRIPTIVE_NOT_VALIDATED"
        assert len(deviations["rows"]) >= 100
        assert comparison["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
        groups = comparison["groups"]
        assert sum(g["eligible"] for g in groups.values()) >= 24
        assert sum(g["eligible"] for g in groups.values()) == len(comparison["observations"])
        assert all(0 <= g["drawdown"] <= g["eligible"] for g in groups.values())
        report["series"][series] = {
            "months": meta["observations"],
            "eligible_months": sum(g["eligible"] for g in groups.values()),
            "high_deviation_months": groups["high_deviation"]["eligible"],
            "observed_fraction_difference": comparison[
                "observed_fraction_difference_high_minus_other"],
            "point_in_time_certified": False,
        }
    report["predictive_publication"] = "BLOCKED"
    return report


def main():
    result = validate(Path("."))
    path = Path("audit-output/industry_deviation_acceptance.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, OSError, ValueError) as exc:
        print("Descriptive acceptance FAILED:", exc, file=sys.stderr)
        sys.exit(1)
