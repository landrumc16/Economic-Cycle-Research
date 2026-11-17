import unittest

from scripts.v63_historical_replay import assessment_at, replay, markdown
from scripts.v63_interpretation import _shift


def months(start, end):
    out, m = [], start
    while m <= end:
        out.append(m)
        m = _shift(m, -1)
    return out


def synthetic():
    """2000–2012: calm growth, a 2003 false-alarm dip, and a 2008 downturn."""
    indpro, unrate, cpi = {}, {}, {}
    level, rate, price = 100.0, 5.0, 100.0
    for m in months("2000-01", "2012-12"):
        if "2003-01" <= m <= "2003-08":
            level *= 0.996          # brief production dip
            rate += 0.11            # unemployment drifts up, then reverses
        elif "2003-09" <= m <= "2004-06":
            level *= 1.004
            rate -= 0.09
        elif "2007-10" <= m <= "2009-06":
            level *= 0.993
            rate += 0.25
        elif "2009-07" <= m:
            level *= 1.004
            rate = max(5.0, rate - 0.08)
        else:
            level *= 1.0025
        price *= 1.002
        indpro[m], unrate[m], cpi[m] = round(level, 4), round(rate, 2), round(price, 4)
    return {"INDPRO": indpro, "UNRATE": unrate, "CPIAUCSL": cpi}


class ReplayTests(unittest.TestCase):
    def test_signal_uses_only_prior_month_observations(self):
        data = synthetic()
        before = assessment_at(data, "2006-05")
        data["INDPRO"]["2006-05"] = 1.0  # same-month and later values must be invisible
        data["UNRATE"]["2006-09"] = 99.0
        after = assessment_at(data, "2006-05")
        self.assertEqual(before, after)
        self.assertEqual(before["sources"]["INDPRO"]["latest_used_month"], "2006-04")

    def test_scorecard_reports_timing_false_alarms_and_limits(self):
        card = replay(synthetic(), start="2001-06")
        self.assertEqual(card["status"], "RETROSPECTIVE_REPLAY_NOT_POINT_IN_TIME")
        self.assertFalse(card["predictive_skill_certified"])
        self.assertFalse(card["probabilities_published"])
        peaks = {r["peak"]: r for r in card["recessions"]}
        self.assertIn("2007-12", peaks)
        self.assertNotEqual(peaks["2007-12"]["outcome"], "missed")
        self.assertIsNotNone(peaks["2007-12"]["warning_months_before_peak"])
        self.assertGreaterEqual(len(card["false_alarm_episodes"]), 1)
        self.assertTrue(any(e["first_month"].startswith("2003") for e in card["false_alarm_episodes"]))
        self.assertTrue(any("not archived real-time" in x for x in card["limitations"]))
        self.assertGreater(card["months_replayed"], 100)
        text = markdown(card)
        self.assertIn("not a forecast-accuracy claim", text)
        self.assertIn("False alarm", text)

    def test_recent_warnings_without_outcome_window_are_not_scored(self):
        data = synthetic()
        card = replay(data, start="2001-06", end="2008-06")
        # Outcomes after the data end cannot be judged; the 2008 episode remains scoreable.
        for row in card["false_alarm_episodes"]:
            self.assertLessEqual(row["first_month"], "2012-01")

    def test_pandemic_months_excluded_from_general_agreement(self):
        data = synthetic()
        for name in data:
            for m in months("2013-01", "2021-12"):
                data[name][m] = data[name]["2012-12"] if name != "UNRATE" else 5.0
        data["UNRATE"]["2020-04"] = 14.0
        card = replay(data, start="2018-01")
        total = sum(v["months"] for v in card["directional_agreement_excluding_pandemic"].values())
        self.assertLess(total, card["months_replayed"])
        pandemic = [r for r in card["recessions"] if r["pandemic_shock"]]
        self.assertEqual(len(pandemic), 1)
        self.assertEqual(card["recessions_evaluated_excluding_pandemic"], 0)

    def test_empty_data_fails_closed(self):
        with self.assertRaises(ValueError):
            replay({"INDPRO": {}, "UNRATE": {}, "CPIAUCSL": {}})


if __name__ == "__main__":
    unittest.main()


class ScorecardPageTests(unittest.TestCase):
    def test_scorecard_renders_and_rejects_skill_claims(self):
        from scripts.v6_public_site import scorecard_section
        card = replay(synthetic(), start="2001-06")
        html = scorecard_section(card)
        self.assertIn("not a measure of forecasting accuracy and not a probability", html)
        self.assertIn("False alarms", html)
        self.assertIn("2003-05", html)
        self.assertIn("versus", html)
        self.assertIn("The two tests overlap", html)
        self.assertIn('<th scope="col">Base rate</th>', html)
        self.assertIn('<th scope="rowgroup" colspan="4">Cautious calls</th>', html)
        self.assertNotIn("1 months", html)
        self.assertNotIn("early warning", html.lower())
        self.assertIn("not proof that the rules predict recessions", html)
        agreement = card["directional_agreement_excluding_pandemic"]
        self.assertEqual(agreement["Weakening"]["outcome_test"], "cautious")
        self.assertEqual(agreement["Steady"]["outcome_test"], "constructive")
        for item in agreement.values():
            if item["months"]:
                self.assertAlmostEqual(item["lift_pp"], round(100 * (item["share"] - item["base_rate"]), 1))
                self.assertEqual(item["informative"], item["lift_pp"] >= card["directional_informative_lift_pp"])
        self.assertIn("unemployment rose 0.2 points", html.lower())
        self.assertIn("different, overlapping outcome tests", " ".join(card["limitations"]))
        self.assertIn("| Direction | Outcome test |", markdown(card))
        self.assertIn("base rate", html)
        base = card["directional_base_rates_excluding_pandemic"]
        self.assertGreater(base["evaluable_months"], 100)
        self.assertAlmostEqual(base["deterioration_share"] + base["no_labor_deterioration_share"], 1.0, delta=0.35)
        self.assertIn("<details>", html)
        for key, bad in (("predictive_skill_certified", True), ("probabilities_published", True),
                         ("status", "VALIDATED_FORECAST")):
            with self.assertRaises(ValueError):
                scorecard_section(dict(card, **{key: bad}))


class EarlyWarningWordingTests(unittest.TestCase):
    def test_flagged_before_peak_is_not_presented_as_proven_prediction(self):
        from scripts.v6_public_site import scorecard_section
        card = replay(synthetic(), start="2001-06")
        card["recessions"] = [{"peak": "2001-03", "trough": "2001-11", "pandemic_shock": False,
                               "first_warning": "2001-02", "warning_months_before_peak": 1,
                               "outcome": "early warning"}]
        html = scorecard_section(card)
        self.assertIn("flagged before the peak", html)
        self.assertIn("1 month before the peak", html)
        self.assertNotIn("early warning", html.lower())
        self.assertIn("not proof that the rules predict recessions", html)
