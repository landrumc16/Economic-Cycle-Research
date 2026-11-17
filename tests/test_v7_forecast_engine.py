import math
import random
import unittest
from unittest import mock

from scripts import v7_forecast_engine as eng


def synthetic(start=1955, end=1990, seed=1):
    """Recessions preceded by yield-curve inversion; enough structure to learn."""
    random.seed(seed)
    months = [f"{y}-{m:02d}" for y in range(start, end + 1) for m in range(1, 13)]
    rec = set()
    for s in ("1957-09", "1960-05", "1970-01", "1974-01", "1980-02", "1981-08"):
        for k in range(8):
            rec.add(eng.shift(s, k))
    data = {n: {} for n in eng.SERIES}
    u, cpi, ip, pay = 5.0, 30.0, 30.0, 50000.0
    for mo in months:
        inverted = any(eng.shift(mo, k) in rec for k in range(6, 18))
        tb = 4 + random.gauss(0, .3)
        data["TB3MS"][mo] = max(.1, tb)
        data["GS10"][mo] = max(.1, tb + (-0.5 if inverted else 1.5) + random.gauss(0, .3))
        data["BAA"][mo] = data["GS10"][mo] + 1.5 + (1 if mo in rec else 0)
        data["USREC"][mo] = 1.0 if mo in rec else 0.0
        u = max(3.0, u + (0.15 if mo in rec else -0.03) + random.gauss(0, .05))
        data["UNRATE"][mo] = round(u, 1)
        cpi *= 1 + 0.003 + random.gauss(0, .002)
        data["CPIAUCSL"][mo] = cpi
        ip *= 1 + (-0.006 if mo in rec else 0.002)
        data["INDPRO"][mo] = ip
        pay *= 1 + (-0.003 if mo in rec else 0.0015)
        data["PAYEMS"][mo] = pay
    return data


class PointInTimeTests(unittest.TestCase):
    def test_features_ignore_unpublished_and_future_values(self):
        data = synthetic()
        before = eng.features_at(data, "1980-06")
        # Macro values for the forecast month itself are not yet published...
        for name in ("UNRATE", "PAYEMS", "CPIAUCSL", "INDPRO"):
            data[name]["1980-06"] *= 3
        # ...and nothing after the forecast month is visible at all.
        for name in eng.SERIES:
            for m in list(data[name]):
                if m > "1980-06":
                    data[name][m] = 999.0
        self.assertEqual(before, eng.features_at(data, "1980-06"))

    def test_market_data_for_current_month_is_used(self):
        data = synthetic()
        before = eng.features_at(data, "1980-06")["term_spread"]
        data["GS10"]["1980-06"] += 1
        self.assertAlmostEqual(eng.features_at(data, "1980-06")["term_spread"], before + 1)

    def test_recession_indicator_is_never_a_feature(self):
        data = synthetic()
        before = eng.features_at(data, "1975-06")
        for m in data["USREC"]:
            data["USREC"][m] = 1 - data["USREC"][m]
        self.assertEqual(before, eng.features_at(data, "1975-06"))

    def test_single_unpublished_month_tolerated_but_not_imputed(self):
        data = synthetic()
        full = eng.features_at(data, "1980-06")
        del data["UNRATE"]["1980-04"]
        self.assertIsNotNone(eng.features_at(data, "1980-06"))
        self.assertNotIn("1980-04", data["UNRATE"])  # nothing filled in
        del data["UNRATE"]["1980-05"]
        self.assertIsNone(eng.features_at(data, "1980-06"))  # two missing: withheld
        self.assertIsNotNone(full)

    def test_unpublished_cpi_base_month_uses_previous_month_only(self):
        data = synthetic()
        del data["CPIAUCSL"]["1979-05"]  # year-earlier value for 1980-05
        f = eng.features_at(data, "1980-06")
        self.assertIsNotNone(f)
        del data["CPIAUCSL"]["1979-04"]
        self.assertIsNone(eng.features_at(data, "1980-06"))

    def test_label_availability_delays(self):
        self.assertEqual(eng.label_known_by("recession", "1980-01", 6), "1981-07")
        self.assertEqual(eng.label_known_by("labor_deterioration", "1980-01", 6), "1980-08")


class TargetTests(unittest.TestCase):
    def test_target_definitions(self):
        data = synthetic()
        self.assertEqual(eng.outcome(data, "recession", "1973-08", 6), 1)
        self.assertEqual(eng.outcome(data, "recession", "1965-01", 6), 0)
        data["UNRATE"]["1966-01"] = 4.0
        data["UNRATE"]["1966-04"] = 4.5
        self.assertEqual(eng.outcome(data, "labor_deterioration", "1966-02", 3), 1)
        self.assertIsNone(eng.outcome(data, "recession", "1990-10", 6))  # window beyond data


class ModelAndMetricTests(unittest.TestCase):
    def test_logistic_recovers_direction_and_auc(self):
        random.seed(3)
        x = [[random.gauss(0, 1)] for _ in range(400)]
        y = [int(random.random() < 1 / (1 + math.exp(-2 * r[0]))) for r in x]
        model = eng.fit_logistic(x, y)
        self.assertGreater(model[0][1], 1.0)
        self.assertGreater(eng.auc([eng.predict(model, r) for r in x], y), 0.75)

    def test_auc_and_episodes(self):
        self.assertEqual(eng.auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)
        self.assertEqual(eng.auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]), 0.0)
        self.assertIsNone(eng.auc([0.5, 0.5], [1, 1]))
        rows = [{"y": v} for v in (0, 1, 1, 0, 1, 0, 0, 1)]
        self.assertEqual(eng.episodes(rows), 3)

    def test_overconfidence_detected(self):
        cal = [{"n": 20, "mean_forecast": 0.8, "observed": 0.3}]
        self.assertGreater(eng.overconfidence(cal), eng.GATE["max_overconfidence"])


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.multiple(eng, EVAL_START="1966-01", MIN_TRAIN=60)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.data = synthetic()

    def test_out_of_sample_rows_use_only_past_labels(self):
        rows, _ = eng.evaluate(self.data, "recession", 6)
        self.assertTrue(rows)
        self.assertGreaterEqual(rows[0]["origin"], "1966-01")
        # Altering an outcome after a forecast origin must not change that forecast.
        origin = rows[5]["origin"]
        before = rows[5]["model"]
        for k in range(1, 40):
            m = eng.shift(origin, k)
            if m in self.data["USREC"]:
                self.data["USREC"][m] = 1 - self.data["USREC"][m]
        self.data.pop("_rubric_cache", None)
        rows2, _ = eng.evaluate(self.data, "recession", 6)
        self.assertAlmostEqual([r for r in rows2 if r["origin"] == origin][0]["model"], before)

    def test_gate_fails_closed_to_insufficient_evidence(self):
        rows, panel = eng.evaluate(self.data, "recession", 6)
        verdict = eng.assess(rows, "recession", 6)
        verdict["gate_checks"]["auc"] = False
        verdict["publishable"] = False
        out = eng.current_outlook(self.data, panel, "recession", 6, verdict)
        self.assertEqual(out["state"], "Insufficient evidence")
        self.assertIsNone(out["probability"])
        self.assertIn("auc", out["reason"])

    def test_published_probability_is_clamped_and_banded(self):
        rows, panel = eng.evaluate(self.data, "recession", 6)
        verdict = {"publishable": True, "gate_checks": {}}
        out = eng.current_outlook(self.data, panel, "recession", 6, verdict)
        self.assertEqual(out["state"], "Published")
        self.assertTrue(0.05 <= out["probability"] <= 0.95)
        self.assertIn("%", out["probability_text"])
        self.assertIn(out["band"], ("Low", "Typical", "Elevated", "High"))


if __name__ == "__main__":
    unittest.main()


class RecalibrationTests(unittest.TestCase):
    def test_calibrator_uses_only_outcomes_known_at_fit_time(self):
        rows = [{"origin": eng.shift("1970-01", i), "model_raw": 0.9 if i % 2 else 0.1, "y": i % 2}
                for i in range(200)]
        known_by = eng.shift("1970-01", 150)
        a = eng.fit_calibrator(rows, known_by, "labor_deterioration", 6)
        # Flipping outcomes that were not yet known must not change the calibrator.
        later = [dict(r, y=1 - r["y"]) if eng.label_known_by("labor_deterioration", r["origin"], 6) > known_by else r
                 for r in rows]
        b = eng.fit_calibrator(later, known_by, "labor_deterioration", 6)
        self.assertEqual(a, b)

    def test_calibrator_waits_for_enough_history(self):
        rows = [{"origin": eng.shift("1970-01", i), "model_raw": 0.5, "y": i % 2} for i in range(50)]
        self.assertIsNone(eng.fit_calibrator(rows, "1990-01", "labor_deterioration", 6))
