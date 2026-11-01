"""Fail closed on incomplete or inconsistent historical multifactor artifacts."""
import json
from pathlib import Path


ASSETS = ("NASDAQCOM", "CSUSHPINSA")
HORIZONS = (6, 12, 24)
CREDIT = ("consumer_credit_growth", "business_credit_growth")


def check(root):
    folder = root / "audit-output"
    result = {"status": "RETROSPECTIVE_DESCRIPTIVE_ACCEPTED",
              "predictive_publication": "BLOCKED", "artifacts": []}
    for asset in ASSETS:
        for horizon in HORIZONS:
            path = folder / f"{asset}_credit_joint_{horizon}m.json"
            data = json.loads(path.read_text())
            assert data["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY", path
            assert data["horizon_months"] == horizon, path
            assert data["drawdown_threshold"] == 0.20, path
            assert data["eligible_price_months"] >= 24, path
            for name in CREDIT:
                group = data["joint_comparisons"][name]
                assert group["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY", (path, name)
                assert group["eligible_months"] >= 24, (path, name)
                assert group["eligible_months"] + group["missing_months"] == data["eligible_price_months"]
                cells = group["cells"]
                assert len(cells) == 4
                assert sum(v["months"] for v in cells.values()) == group["eligible_months"]
                for cell in cells.values():
                    assert cell["declines"] + cell["no_decline"] == cell["months"]
                    assert 0 <= cell["declines"] <= cell["months"]
            result["artifacts"].append(str(path))
    for horizon in HORIZONS:
        path = folder / f"CSUSHPINSA_fundamentals_credit_{horizon}m.json"
        data = json.loads(path.read_text())
        assert data["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
        assert data["horizon_months"] == horizon
        assert data["drawdown_threshold"] == 0.10
        for name in CREDIT:
            triple = data["three_factor_comparisons"][name]
            assert triple["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
            assert triple["fundamental_name"] == "housing_income_divergence"
            assert triple["eligible_months"] >= 24
            assert triple["eligible_months"] + triple["missing_months"] == data["eligible_price_months"]
            assert len(triple["cells"]) == 8
            assert sum(c["months"] for c in triple["cells"].values()) == triple["eligible_months"]
            assert all(0 <= c["declines"] <= c["months"] for c in triple["cells"].values())
        result["artifacts"].append(str(path))
    summary = json.loads((folder / "industry_credit_joint_summary.json").read_text())
    assert summary["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
    assert len(summary["results"]) == 12
    return result


def main():
    result = check(Path("."))
    output = Path("audit-output/industry_multifactor_acceptance.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "artifacts_checked": len(result["artifacts"]),
                      "predictive_publication": result["predictive_publication"]}))


if __name__ == "__main__":
    main()
