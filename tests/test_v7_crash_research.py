"""Crash research: bear-market dating, forward targets and point-in-time features."""
import unittest
from scripts import v7_crash_research as cr


class CrashResearchTests(unittest.TestCase):
    def test_bear_market_dating(self):
        path = [100, 110, 95, 85, 80, 90, 111, 120, 100, 119]
        idx = {f"2000-01-{i + 1:02d}": v for i, v in enumerate(path)}
        bears = cr.bear_markets(idx)
        self.assertEqual(len(bears), 1)
        b = bears[0]
        self.assertEqual((b["peak"], b["trough"], b["recovered"]), ("2000-01-02", "2000-01-05", "2000-01-07"))
        self.assertAlmostEqual(b["depth_pct"], -27.3, places=1)  # 120 -> 100 later is only -16.7%: not a bear

    def test_forward_target_uses_only_the_future_window(self):
        idx = {}
        for m, v in [("2001-01", 100), ("2001-02", 100), ("2001-03", 79), ("2001-04", 100), ("2001-05", 100)]:
            idx[m + "-28"] = v
        y = cr.forward_target(idx, cr.monthly_last(idx), 1)
        self.assertEqual(y, {"2001-01": 0, "2001-02": 1, "2001-03": 0, "2001-04": 0})
        y2 = cr.forward_target(idx, cr.monthly_last(idx), 2)
        self.assertEqual(y2["2001-01"], 1)
        self.assertNotIn("2001-04", y2)  # outcome window not yet complete

    def test_features_do_not_change_when_future_data_arrive(self):
        months = [f"{y}-{m:02d}" for y in range(1990, 1996) for m in range(1, 13)]
        fred = {s: {m + "-01": 5.0 + (i % 7) * 0.1 for i, m in enumerate(months)} for s in ("GS10", "TB3MS", "BAA", "UNRATE")}
        mkt = {m + "-28": 100 + i for i, m in enumerate(months)}

        def panel(cut):
            D = {"fred": {s: {d: v for d, v in ser.items() if d[:7] <= cut} for s, ser in fred.items()},
                 "mkt_m": cr.monthly_last({d: v for d, v in mkt.items() if d[:7] <= cut}),
                 "ind": {}, "cape": {}}
            return cr.feature_panel(D)
        early, late = panel("1993-06"), panel("1995-12")
        self.assertEqual(early["1993-06"], late["1993-06"])


if __name__ == "__main__":
    unittest.main()
