import unittest
from datetime import date
from scripts.v6_sector_intelligence import SECTORS, build_sector_report


class SectorGateTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 4)

    def test_all_eleven_present_without_data(self):
        result = build_sector_report({}, self.today)
        self.assertEqual(len(result["sectors"]), 11)
        self.assertEqual({s["sector"] for s in result["sectors"]}, set(SECTORS))
        self.assertTrue(all(s["outlook"] == "Insufficient Evidence" for s in result["sectors"]))

    def test_macro_only_cannot_promote_favorable(self):
        evidence = {"Energy": {"outlook": "Favorable", "economic_fit": {"source_url": "https://example.org"}}}
        result = build_sector_report(evidence, self.today)
        self.assertEqual(result["sectors"][3]["outlook"], "Insufficient Evidence")

    def test_future_dated_evidence_is_blocked(self):
        block = {"source_url": "https://example.org", "methodology": "documented",
                 "observation_date": "2026-11-05"}
        evidence = {"Energy": {key: dict(block) for key in
                    ("economic_fit", "earnings", "valuation", "relative_total_return")}}
        evidence["Energy"]["outlook"] = "Favorable"
        evidence["Energy"]["relative_total_return"].update(
            benchmark="broad-market", sample_size=10, point_in_time_verified=True)
        self.assertEqual(build_sector_report(evidence, self.today)["sectors"][3]["outlook"],
                         "Insufficient Evidence")

    def test_qualified_inputs_may_publish(self):
        block = {"source_url": "https://example.org", "methodology": "documented",
                 "observation_date": "2026-10-31", "value": 1.2}
        evidence = {"Energy": {key: dict(block) for key in
                    ("economic_fit", "earnings", "valuation", "relative_total_return")}}
        evidence["Energy"]["outlook"] = "Mixed"
        evidence["Energy"]["rationale"] = "Earnings and relative returns are conflicting"
        evidence["Energy"]["relative_total_return"].update(
            benchmark="broad-market", sample_size=10, point_in_time_verified=True,
            transaction_cost_assumption="excluded", survivorship_bias_note="reviewed")
        self.assertEqual(build_sector_report(evidence, self.today)["sectors"][3]["outlook"], "Mixed")
        del evidence["Energy"]["valuation"]["value"]
        self.assertEqual(build_sector_report(evidence, self.today)["sectors"][3]["outlook"],
                         "Insufficient Evidence")

    def test_unknown_sector_rejected(self):
        with self.assertRaises(ValueError):
            build_sector_report({"Imaginary": {}}, self.today)


    def test_every_sector_has_distinct_exposure_and_industry_examples(self):
        result=build_sector_report({},self.today)
        self.assertEqual(len({x["economic_exposure_hypothesis"] for x in result["sectors"]}),11)
        for item in result["sectors"]:
            self.assertTrue(item["industry_examples"])
            self.assertEqual(item["outlook"],"Insufficient Evidence")

if __name__ == "__main__":
    unittest.main()

