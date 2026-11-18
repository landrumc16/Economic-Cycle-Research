"""V7 production integration: monthly gate, daily publish/preserve, verification (fail closed)."""
import copy
import csv
import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from scripts import v7_release as rel
from scripts import v7_forecast_engine as engine

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "a" * 40
EVIDENCE = json.loads((ROOT / "docs/evidence/v7_forecast_evaluation_2026-11-17.json").read_text())
with (ROOT / "data/v7/forecast_archive.csv").open(newline="") as f:
    ARCHIVE = [{"target": r["target"], "horizon_months": int(r["horizon_months"]), "origin": r["origin"],
                "probability": float(r["probability"]), "probability_raw": float(r["probability_raw"]),
                "outcome": int(r["outcome"])} for r in csv.DictReader(f)]


def fake_run(_data, _end=None):
    return dict(copy.deepcopy(EVIDENCE), forecast_archive=ARCHIVE)


class _Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.bundle = cls.build("PASS", "2026-11-18", "good")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    @classmethod
    def build(cls, status, as_of, name, run=fake_run, built_at="2026-11-18T06:00:00Z"):
        gate = cls.tmp / f"{name}-gate.json"
        gate.write_text(json.dumps({"status": status}))
        out = cls.tmp / name / "audit-output" / "v7-site"
        with mock.patch.object(engine, "run", run):
            rel.monthly(ROOT / "data/v7", ROOT / "data/v7_research", gate, out, as_of, COMMIT, built_at,
                        ROOT / rel.RESEARCH_EVIDENCE, crash_dir=ROOT / "data/v7_crash")
        return out

    @staticmethod
    def manifest(d):
        return json.loads((Path(d) / rel.MANIFEST).read_text())

    @staticmethod
    def live_from(d):
        files = {p.name: p.read_bytes() for p in Path(d).iterdir() if p.is_file()}
        return lambda url: files.get(url.rsplit("/", 1)[1])


class MonthlyGateTests(_Fixture):
    def test_qualified_bundle_publishes_only_the_approved_outlook(self):
        m = self.manifest(self.bundle)
        self.assertEqual(m["promotion_outcome"], "NEW_QUALIFIED")
        self.assertEqual([(o["target"], o["horizon_months"]) for o in m["published_outlooks"]],
                         [("labor_deterioration", 12)])
        self.assertEqual(len([p for p in m["pages"] if p.startswith("sector-")]), 11)
        self.assertEqual(rel.validate_site(self.bundle, m)["status"], "V7_SITE_CONTRACT_PASS")

    def test_unqualified_monthly_gate_fails_closed(self):
        m = self.manifest(self.build("STALE_RESEARCH_ONLY", "2026-11-18", "stale-gate"))
        self.assertEqual(m["promotion_outcome"], "FAILED")
        self.assertFalse(m["research_gate"]["qualified"])
        self.assertIn("not PASS", " ".join(m["research_gate"]["reasons"]))

    def test_stale_market_data_fail_closed(self):
        m = self.manifest(self.build("PASS", "2026-12-15", "stale-market"))
        self.assertEqual(m["promotion_outcome"], "FAILED")
        self.assertTrue(any("Daily market data" in r for r in m["research_gate"]["reasons"]))

    def test_manifest_records_market_warnings(self):
        m = self.manifest(self.bundle)
        self.assertEqual([w["key"] for w in m["market_warnings"]],
                         ["curve", "trend", "breadth", "conditions", "credit", "valuation"])
        self.assertIn("market-risk.html", m["pages"])

    def test_stale_inputs_fail_closed(self):
        m = self.manifest(self.build("PASS", "2027-06-01", "stale-data"))
        self.assertEqual(m["promotion_outcome"], "FAILED")
        self.assertTrue(any("too old" in r for r in m["research_gate"]["reasons"]))

    def test_newly_passing_unapproved_outlook_is_held_not_published(self):
        def run(_d, _e=None):
            r = fake_run(_d)
            for e in r["evaluations"]:
                if (e["target"], e["horizon_months"]) == ("recession", 12):
                    e["publishable"] = True
            for o in r["current_outlooks"]:
                if (o["target"], o["horizon_months"]) == ("recession", 12):
                    o.update(state="Published", probability=0.4, probability_text="about 40%", band="Elevated")
            return r
        d = self.build("PASS", "2026-11-18", "held", run=run)
        m = self.manifest(d)
        self.assertEqual(m["held_for_review"], [{"target": "recession", "horizon_months": 12, "probability": 0.4}])
        self.assertEqual(len(m["published_outlooks"]), 1)
        self.assertNotIn("about 40%", (d / "forecast.html").read_text())


class PublishTests(_Fixture):
    def target(self, name):
        t = self.tmp / ("target-" + name)
        if t.exists():
            shutil.rmtree(t)
        t.mkdir()
        (t / "overview.html").write_text("V6 archive page")
        return t

    def test_new_qualified_bundle_becomes_the_dashboard(self):
        t = self.target("new")
        r = rel.publish(self.bundle.parent.parent, t, "https://example.invalid", date(2026, 11, 19),
                        fetch=lambda u: None)
        self.assertEqual(r["outcome"], "NEW_QUALIFIED")
        self.assertEqual((t / "index.html").read_bytes(), (self.bundle / "index.html").read_bytes())
        self.assertTrue((t / "overview.html").is_file())  # V6 archive left in place

    def test_failed_monthly_preserves_previous_live_bundle(self):
        failed = self.build("STALE_RESEARCH_ONLY", "2026-11-18", "fail2")
        t = self.target("keep")
        r = rel.publish(failed.parent.parent, t, "https://x", date(2026, 12, 1), fetch=self.live_from(self.bundle))
        self.assertEqual(r, {"outcome": "PRESERVED_PREVIOUS", "assessment_date": self.manifest(self.bundle)["assessment_date"],
                             "stale_notice": False})
        m = self.manifest(t)
        self.assertEqual(m["build_commit"], COMMIT)
        self.assertEqual((t / "index.html").read_bytes(), (self.bundle / "index.html").read_bytes())

    def test_old_preserved_bundle_gets_visible_notice_and_stays_recoverable(self):
        t = self.target("old")
        rel.publish(None, t, "https://x", date(2027, 2, 1), fetch=self.live_from(self.bundle))
        self.assertIn("A newer monthly assessment has not yet passed our checks", (t / "index.html").read_text())
        self.assertTrue(self.manifest(t)["stale_notice"])
        # The next day recovers from the notice-carrying live site without stacking notices.
        t2 = self.target("old2")
        rel.publish(None, t2, "https://x", date(2027, 2, 2), fetch=self.live_from(t))
        self.assertEqual((t2 / "index.html").read_text().count("A newer monthly assessment"), 1)
        # A later qualified bundle replaces it with no notice.
        t3 = self.target("old3")
        rel.publish(self.bundle.parent.parent, t3, "https://x", date(2027, 2, 3), fetch=self.live_from(t2))
        self.assertNotIn("A newer monthly assessment", (t3 / "index.html").read_text())

    def test_older_qualified_bundle_never_replaces_newer_live_publication(self):
        newer = self.build("PASS", "2026-11-20", "newer", built_at="2026-12-20T06:00:00Z")
        t = self.target("monotonic")
        r = rel.publish(self.bundle.parent.parent, t, "https://x", date(2026, 12, 21), fetch=self.live_from(newer))
        self.assertEqual(r["outcome"], "PRESERVED_PREVIOUS")
        self.assertEqual(self.manifest(t)["build_time_utc"], "2026-12-20T06:00:00Z")

    def test_invalid_candidate_is_rejected_and_previous_kept(self):
        bad = self.tmp / "bad" / "audit-output" / "v7-site"
        if bad.exists():
            shutil.rmtree(bad)
        shutil.copytree(self.bundle, bad)
        m = self.manifest(bad)
        del m["pages"]["market-risk.html"]
        (bad / rel.MANIFEST).write_text(json.dumps(m))
        t = self.target("badcand")
        r = rel.publish(bad.parent.parent, t, "https://x", date(2026, 12, 1), fetch=self.live_from(self.bundle))
        self.assertEqual(r["outcome"], "PRESERVED_PREVIOUS")
        self.assertIn("rejected", r["rejected_candidate"])
        t2 = self.target("badcand2")
        r = rel.publish(bad.parent.parent, t2, "https://x", date(2026, 12, 1), fetch=lambda u: None)
        self.assertEqual(r["outcome"], "NOT_PUBLISHED")

    def test_no_previous_v7_leaves_dashboard_untouched(self):
        t = self.target("none")
        r = rel.publish(None, t, "https://x", date(2026, 12, 1), fetch=lambda u: None)
        self.assertEqual(r["outcome"], "NOT_PUBLISHED")
        self.assertEqual(sorted(p.name for p in t.iterdir()), ["overview.html"])

    def test_tampered_or_unreachable_live_site_blocks_deployment(self):
        live = self.live_from(self.bundle)
        tampered = lambda u: b"<!doctype html>changed" if u.endswith("/sectors.html") else live(u)
        with self.assertRaises(RuntimeError):
            rel.publish(None, self.target("t1"), "https://x", date(2026, 12, 1), fetch=tampered)
        missing = lambda u: None if u.endswith("/sector-energy.html") else live(u)
        with self.assertRaises(RuntimeError):
            rel.publish(None, self.target("t2"), "https://x", date(2026, 12, 1), fetch=missing)

        def down(u):
            raise RuntimeError("network unreachable")
        with self.assertRaises(RuntimeError):
            rel.publish(None, self.target("t3"), "https://x", date(2026, 12, 1), fetch=down)

    def test_verify_live_compares_every_file(self):
        t = self.target("verify")
        rel.publish(self.bundle.parent.parent, t, "https://x", date(2026, 11, 19), fetch=lambda u: None)
        self.assertEqual(rel.verify_live(t, "https://x", fetch=self.live_from(t))["status"], "V7_LIVE_VERIFIED")
        live = self.live_from(t)
        with self.assertRaises(RuntimeError):
            rel.verify_live(t, "https://x", fetch=lambda u: b"x" if u.endswith("track-record.html") else live(u))


class HttpTests(unittest.TestCase):
    def opener(self, codes):
        import urllib.error
        seq = iter(codes)

        def op(url, timeout):
            c = next(seq)
            if c == 200:
                class R:
                    status = 200
                    def __enter__(s): return s
                    def __exit__(s, *a): return False
                    def read(s): return b"ok"
                return R()
            raise urllib.error.HTTPError(url, c, "x", {}, None)
        return op

    def test_transient_5xx_is_retried_404_is_absent_and_persistent_failure_blocks(self):
        self.assertEqual(rel.http_get("u", opener=self.opener([503, 503, 200]), sleep=lambda s: None), b"ok")
        self.assertIsNone(rel.http_get("u", opener=self.opener([404]), sleep=lambda s: None))
        with self.assertRaises(RuntimeError):
            rel.http_get("u", attempts=3, opener=self.opener([503, 502, 500]), sleep=lambda s: None)
        with self.assertRaises(RuntimeError):
            rel.http_get("u", opener=self.opener([403]), sleep=lambda s: None)


class ContractTests(_Fixture):
    def test_manifest_rejects_unapproved_outlook_and_bad_commit(self):
        m = self.manifest(self.bundle)
        bad = dict(m, published_outlooks=m["published_outlooks"] + [{"target": "recession", "horizon_months": 6}])
        with self.assertRaises(ValueError):
            rel.validate_manifest(bad)
        with self.assertRaises(ValueError):
            rel.validate_manifest(dict(m, build_commit="abc"))
        with self.assertRaises(ValueError):
            rel.validate_manifest(dict(m, promotion_outcome="NEW_QUALIFIED",
                                       research_gate={"qualified": False, "reasons": ["x"]}))

    def test_site_contract_rejects_missing_disclaimer_and_broken_link(self):
        for edit in (lambda h: h.replace("not personalized financial advice", ""),
                     lambda h: h.replace('href="sectors.html">All 11', 'href="missing.html">All 11')):
            d = self.tmp / "broken"
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(self.bundle, d)
            (d / "index.html").write_text(edit((d / "index.html").read_text()))
            with self.assertRaises(ValueError):
                rel.validate_site(d)


if __name__ == "__main__":
    unittest.main()
