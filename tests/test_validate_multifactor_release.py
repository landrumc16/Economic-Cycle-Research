import json
import tempfile
import unittest
from pathlib import Path
from scripts.validate_multifactor_release import check


def artifact(asset, horizon, housing=False):
    cells = {f"acceleration_{a}_indicator_{c}": {
        "months": 10, "declines": 2, "no_decline": 8}
        for a in range(2) for c in range(2)}
    triple_cells = {f"a{a}_f{f}_c{c}": {"months": 5, "declines": 1}
                    for a in range(2) for f in range(2) for c in range(2)}
    return {
        "status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
        "horizon_months": horizon,
        "drawdown_threshold": 0.10 if housing else 0.20,
        "eligible_price_months": 40,
        "joint_comparisons": {
            name: {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
                   "eligible_months": 40, "missing_months": 0,
                   "cells": cells}
            for name in ("consumer_credit_growth", "business_credit_growth")},
        "three_factor_comparisons": {
            name: {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
                   "fundamental_name": "housing_income_divergence",
                   "eligible_months": 40, "missing_months": 0,
                   "cells": triple_cells}
            for name in ("consumer_credit_growth", "business_credit_growth")}
    }


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        out = self.root / "audit-output"
        out.mkdir()
        for asset in ("NASDAQCOM", "CSUSHPINSA"):
            for horizon in (6, 12, 24):
                (out / f"{asset}_credit_joint_{horizon}m.json").write_text(
                    json.dumps(artifact(asset, horizon)))
        for horizon in (6, 12, 24):
            (out / f"CSUSHPINSA_fundamentals_credit_{horizon}m.json").write_text(
                json.dumps(artifact("CSUSHPINSA", horizon, housing=True)))
        (out / "industry_credit_joint_summary.json").write_text(json.dumps({
            "status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
            "results": [{} for _ in range(12)]}))

    def test_complete_fixture_passes(self):
        self.assertEqual(len(check(self.root)["artifacts"]), 9)

    def test_missing_artifact_fails(self):
        (self.root / "audit-output/NASDAQCOM_credit_joint_6m.json").unlink()
        with self.assertRaises(FileNotFoundError):
            check(self.root)

    def test_inconsistent_cell_fails(self):
        path = self.root / "audit-output/NASDAQCOM_credit_joint_6m.json"
        data = json.loads(path.read_text())
        data["joint_comparisons"]["consumer_credit_growth"]["cells"][
            "acceleration_1_indicator_1"]["months"] = 11
        path.write_text(json.dumps(data))
        with self.assertRaises(AssertionError):
            check(self.root)


if __name__ == "__main__":
    unittest.main()
