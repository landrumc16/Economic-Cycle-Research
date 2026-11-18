"""Daily market monitoring: dated assessments, deterministic change detection, no re-dating of slow data."""
import copy
import json
import unittest
from pathlib import Path

from scripts import v7_market_monitor as mm

ROOT = Path(__file__).resolve().parents[1]
CRASH = json.loads((ROOT / "docs/evidence/v7_crash_research_2026-11-18.json").read_text())
DATA = ROOT / "data/v7_crash"
ECO = {"condition": "Expanding", "through": "2026-09"}


def shifted(a, **obs):
    """Copy of an assessment with some observations replaced by newer readings."""
    b = copy.deepcopy(a)
    for k, (d, v, *extra) in obs.items():
        b["observations"][k].update(date=d, value=v)
        if extra:
            b["observations"][k].update(extra[0])
    b["market_data_through"] = max(o["date"] for o in b["observations"].values())
    return b


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.a = mm.assess(CRASH, DATA, "2026-11-17T12:20:00Z")

    def test_assessment_keeps_each_observation_date_and_frequency(self):
        o = self.a["observations"]
        self.assertEqual(o["spx"]["date"], "2026-11-16")
        self.assertEqual((o["nfci"]["frequency"], o["breadth"]["frequency"]), ("weekly", "monthly"))
        self.assertEqual(o["breadth"]["date"], "2026-09")
        self.assertEqual(self.a["market_data_through"], "2026-11-16")

    def test_no_new_data_means_no_new_assessment(self):
        h, st = mm.update(None, CRASH, DATA, "2026-11-17T12:20:00Z", ECO)
        h2, st2 = mm.update(h, CRASH, DATA, "2026-11-17T22:00:00Z", ECO)
        self.assertEqual((st, st2), ("NEW_ASSESSMENT", "NO_NEW_DATA"))
        self.assertEqual(len(h2["assessments"]), 1)

    def test_unchanged_slow_indicator_is_not_reported_as_new(self):
        b = shifted(self.a, spx=("2026-11-17", self.a["observations"]["spx"]["value"]))
        b["observations"]["breadth"]["value"] = 20.0  # same monthly date: must not be compared
        items, _ = mm.changes(self.a, b)
        self.assertFalse([c for c in items if c["key"] == "breadth"])

    def test_thresholds_tested_vs_monitoring_and_events(self):
        b = shifted(self.a, spx=("2026-11-17", 1, {"dd_pct": -10.4, "d1_pct": -2.6}), vix=("2026-11-17", 31.0),
                    hy=("2026-11-17", 3.9), breadth=("2026-10", 34.0))
        b["warnings"]["trend"]["status"] = "warning"
        items, events = mm.changes(self.a, b)
        kinds = {(c["kind"], c["key"]) for c in items}
        self.assertIn(("tested", "trend"), kinds)
        for key in ("spx", "vix", "hy", "breadth"):
            self.assertIn(("monitoring", key), kinds)
        self.assertEqual(items[0]["kind"], "tested")  # tested changes are listed first
        self.assertIn("New tested warning: Market trend", events)
        self.assertTrue(any("10%" in e for e in events) and any("VIX" in e for e in events) and
                        any("High-yield" in e for e in events))
        self.assertFalse(any("probab" in json.dumps(c).lower() for c in items))

    def test_signal_returning_to_normal_is_reported(self):
        a = copy.deepcopy(self.a)
        a["warnings"]["trend"]["status"] = "warning"
        b = shifted(self.a, spx=("2026-11-17", 1))
        b["warnings"]["trend"]["status"] = "clear"
        items, events = mm.changes(a, b)
        t = [c for c in items if c["key"] == "trend"][0]
        self.assertEqual((t["severity"], t["title"]), ("down", "Market trend: back to clear"))
        self.assertEqual(events, [])

    def test_weekly_interpretation_covers_the_completed_week(self):
        w = mm.weekly(CRASH, DATA, "2026-11-16", ECO)
        self.assertEqual(w["week"], ["2026-11-09", "2026-11-13"])
        topics = [l["topic"] for l in w["lines"]]
        for t in ("Direction of vulnerability", "Breadth and leadership", "Credit and liquidity", "Economy and market",
                  "Sectors", "Historical comparison"):
            self.assertIn(t, topics)
        self.assertIn(w["summary"], ("Meaningful change this week.",
                                     "No meaningful change in tested warnings, credit or volatility this week."))
        self.assertEqual(mm.weekly(CRASH, DATA, "2026-11-13", ECO)["week"], ["2026-11-09", "2026-11-13"])


if __name__ == "__main__":
    unittest.main()
