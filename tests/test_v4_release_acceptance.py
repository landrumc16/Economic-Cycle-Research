import unittest
from scripts.v4_release_acceptance import check

class V4ReleaseTests(unittest.TestCase):
    def fixtures(self):
        v3 = {"report_type": "V3_WEEKLY_DESCRIPTIVE_ASSESSMENT", "as_of": "2026-10-31"}
        def item(kind, **extra):
            return {"report_type": kind, "predictive_publication": "BLOCKED", **extra}
        readiness = item("V4_WEEKLY_DATA_READINESS", as_of="2026-10-31")
        signals = item("V4_EXPLAINABLE_ECONOMIC_SIGNALS", as_of="2026-10-31", signals=[{}] * 9)
        mechanisms = item("V4_MULTI_MECHANISM_ASSESSMENT", as_of="2026-10-31", pathways=[{}] * 7)
        episodes = item("V4_HISTORICAL_EPISODE_REGISTRY", canonical_episode_clusters=8)
        social = item("V4_GLOBAL_SOCIAL_EVIDENCE_REGISTER", defined=1, channels=[{}])
        validation = item("V4_PREDICTIVE_VALIDATION_GATE", status="BLOCKED",
                          descriptive_product_release_permitted=True)
        dashboard = "Version 4 Separate downturn mechanisms Historical validation data readiness"
        return [v3, readiness, signals, mechanisms, episodes, social, validation, dashboard]

    def test_complete_descriptive_release_passes(self):
        self.assertTrue(check(*self.fixtures())["passed"])

    def test_date_mismatch_fails(self):
        fixtures = self.fixtures()
        fixtures[2]["as_of"] = "2026-10-24"
        self.assertFalse(check(*fixtures)["passed"])

    def test_unblocked_predictive_publication_fails(self):
        fixtures = self.fixtures()
        fixtures[3]["predictive_publication"] = "ENABLED"
        self.assertFalse(check(*fixtures)["passed"])

    def test_missing_dashboard_section_fails(self):
        fixtures = self.fixtures()
        fixtures[-1] = "Version 4"
        self.assertFalse(check(*fixtures)["passed"])

if __name__ == "__main__":
    unittest.main()
