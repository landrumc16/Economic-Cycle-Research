import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts import v7_forecast_engine as eng
from scripts import v7_sectors as sec
from scripts import v7_site as site

ROOT = Path(__file__).resolve().parents[1]
FORECAST = ROOT / "docs/evidence/v7_forecast_evaluation_2026-11-17.json"
RESEARCH = ROOT / "docs/evidence/v7_passb_forecast_research_2026-11-18.json"
SECTORS = ROOT / "docs/evidence/v7_sectors_2026-11-18.json"


class SectorFrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = sec.load(ROOT / "data/v7_research", ROOT / "data/v7")
        cls.report = sec.build(cls.data, "Expanding", "Typical")

    def test_all_eleven_sectors_with_gated_attractiveness(self):
        names = [s["sector"] for s in self.report["sectors"]]
        self.assertEqual(len(names), 11)
        self.assertEqual(len(set(names)), 11)
        for s in self.report["sectors"]:
            self.assertEqual(s["investment_attractiveness"], "Insufficient evidence")
            self.assertFalse(s["is_recommendation"])
            self.assertFalse(s["valuation_context"]["qualifies_rating"])
            self.assertIn(s["research_priority"], ("Worth researching now", "Monitor", "Lower priority for now"))
            self.assertTrue(s["what_would_change"] and s["contrary_case"])

    def test_relative_strength_uses_only_past_months(self):
        secs = sec.sector_returns(self.data["industries"])
        it, mkt = secs["Information Technology"], dict(self.data["market"])
        latest = "2020-06"
        before = sec.relative_strength(it, mkt, latest)
        it2 = dict(it)
        for m in list(it2):
            if m >= latest:  # the skipped latest month and everything after
                it2[m] = 999.0
        self.assertEqual(before, sec.relative_strength(it2, mkt, latest))
        it2[eng.shift(latest, -1)] = 999.0  # the most recent month inside the window does count
        self.assertNotEqual(before, sec.relative_strength(it2, mkt, latest))

    def test_persistence_test_matches_preregistered_rule(self):
        t = self.report["relative_strength_test"]
        self.assertEqual(t["historically_informative"],
                         t["t_stat"] >= 2.0 and t["first_half_mean"] > 0 and t["second_half_mean"] > 0)
        self.assertGreater(t["periods"], 100)

    def test_rs_ignored_in_priority_when_signal_not_informative(self):
        secs = sec.sector_returns(self.data["industries"])
        fake = dict(self.report["relative_strength_test"], historically_informative=False)
        latest = self.report["as_of_month"]
        for name in sec.SECTORS:
            item = sec.assess_sector(name, secs[name], self.data, "Mixed", None, fake, latest, False)
            self.assertEqual(item["research_priority"], "Monitor")  # Mixed backdrop scores 0; RS excluded

    def test_deteriorating_economy_flips_cyclical_backdrop(self):
        self.assertEqual(sec.BACKDROP["Deteriorating"]["Cyclical"], "Headwind")
        self.assertEqual(sec.BACKDROP["Deteriorating"]["Defensive"], "Relatively resilient")

    def test_committed_sector_evidence_reproduces(self):
        committed = json.loads(SECTORS.read_text())
        key = lambda r: [(s["sector"], s["cycle_class"], s["economic_backdrop"], s["research_priority"]) for s in r["sectors"]]
        self.assertEqual(key(committed), key(self.report))


class OnsetAndFirstReleaseTests(unittest.TestCase):
    def test_onset_scored_only_from_expansion_and_detects_start(self):
        data = {"USREC": {eng.shift("2000-01", i): (1.0 if 14 <= i <= 20 else 0.0) for i in range(40)}}
        self.assertEqual(eng.outcome(data, "recession_onset", "2001-01", 3), 1)   # start in 2001-03
        self.assertEqual(eng.outcome(data, "recession_onset", "2000-06", 3), 0)
        self.assertIsNone(eng.outcome(data, "recession_onset", "2001-04", 3))     # already in recession
        self.assertEqual(eng.label_known_by("recession_onset", "2000-01", 6), "2001-07")

    def test_first_release_series_feed_features_not_outcomes(self):
        try:
            from test_v7_forecast_engine import synthetic
        except ImportError:
            from tests.test_v7_forecast_engine import synthetic
        data = synthetic()
        base = eng.features_at(data, "1980-06")
        d2 = dict(data, UNRATE_FEAT={m: v + 1.0 for m, v in data["UNRATE"].items()})
        self.assertNotEqual(base["unemp_rise"], None)
        self.assertEqual(eng.outcome(d2, "labor_deterioration", "1980-06", 6),
                         eng.outcome(data, "labor_deterioration", "1980-06", 6))

    def test_preregistered_decisions_recorded(self):
        r = json.loads(RESEARCH.read_text())
        self.assertTrue(all(not e["publishable"] for e in r["recession_onset"]))
        labor12 = next(e for e in r["first_release_labor_robustness"] if e["horizon_months"] == 12)
        self.assertTrue(labor12["publishable"])


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.h1, self.main, self.imgs_without_label = [], 0, False, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main = True
        if tag == "svg" and a.get("role") == "img" and not a.get("aria-label"):
            self.imgs_without_label += 1


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        inp = site.load_inputs(FORECAST, RESEARCH, SECTORS, ROOT / "data/v7/forecast_archive.csv", ROOT / "data/v7")
        cls.pages = site.build(cls.out, inp)
        cls.inp = inp

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_five_experiences_and_eleven_sector_pages(self):
        for p in ("index.html", "market-risk.html", "forecast.html", "sectors.html", "track-record.html", "research.html"):
            self.assertIn(p, self.pages)
        self.assertEqual(len([p for p in self.pages if p.startswith("sector-")]), 11)

    def test_every_page_is_accessible_and_links_resolve(self):
        for name in self.pages:
            html = (self.out / name).read_text()
            parser = Links()
            parser.feed(html)
            self.assertTrue(parser.main and parser.h1 == 1, name)
            self.assertEqual(parser.imgs_without_label, 0, name)
            self.assertIn('lang="en"', html)
            self.assertIn("not personalized financial advice", html)
            for href in parser.links:
                if not href.startswith(("http", "#", "mailto:")):
                    path, _, frag = href.partition("#")
                    self.assertTrue((self.out / path).is_file(), f"{name}: broken link {href}")
                    if frag:
                        self.assertIn(f'id="{frag}"', (self.out / path).read_text(), f"{name}: broken anchor {href}")

    def test_primary_navigation_has_exactly_five_destinations(self):
        html = (self.out / "index.html").read_text()
        nav = re.search(r'<nav class="primary"[^>]*>(.*?)</nav>', html).group(1)
        self.assertEqual(re.findall(r'href="([^"]+)"', nav),
                         ["index.html", "market-risk.html", "forecast.html", "sectors.html", "research.html"])

    def test_homepage_leads_with_market_vulnerability_not_a_probability(self):
        html = (self.out / "index.html").read_text()
        main = html.split('<main id="main">')[1].split("</main>")[0]
        self.assertIn('<h1 id="q" class="hero-q">How vulnerable is the stock market to a major decline?</h1>', main)
        self.assertLess(main.index("How vulnerable"), main.index("The economy:"))  # economy is supporting context
        ws = self.inp["crash"]["site"]["warnings"]
        tested = [w for w in ws if w["status"] != "not current"]
        on = sum(w["status"] == "warning" for w in tested)
        self.assertIn(f"{on} of {len(tested)} tested warning signs", main)
        for w in ws:
            self.assertIn(w["title"], main)
            self.assertIn(f'href="market-risk.html#w-{w["key"]}"', main)
        for text in ("Not a crash probability", "Concerning", "Reassuring", "What would raise concern",
                     "What would ease concern", "What this cannot predict", "Supporting context", "Sectors worth researching"):
            self.assertIn(text, main)
        self.assertEqual(main.count('<details class="fold">'), 3)
        self.assertNotRegex(main, r"(chance|probability|odds) of a (crash|decline)[^<]{0,20}\d+%")
        self.assertNotRegex(html, r"recession[^<]{0,40}\d+%")
        # Only the gated economic outlook may show a probability.
        published = [r for r in site.outlook_matrix(self.inp) if r["published"]]
        self.assertEqual([(r["target"], r["h"]) for r in published], [("labor_deterioration", 12)])
        self.assertNotIn("We are here", html)  # the decorative gauge is gone

    def test_market_risk_page_discloses_records_and_the_failed_model(self):
        html = (self.out / "market-risk.html").read_text()
        crash = self.inp["crash"]
        for w in crash["site"]["warnings"]:
            self.assertIn(f'id="w-{w["key"]}"', html)
            self.assertIn(f'Missed {w["record"]["bears_missed"]} of {w["record"]["bears_total"]} bear markets', html)
        self.assertIn("Why we publish no crash probability", html)
        skill = crash["model_T12_core"]["full_sample"]["bss_vs_base_rate"]
        self.assertIn(f"skill {skill:+.2f}", html)
        self.assertFalse(crash["model_T12_core"]["passes_gate"])
        self.assertIn("Which warnings came before past bear markets", html)
        self.assertIn("Today versus past market peaks", html)
        self.assertIn("When the economy and the market disagree", html)
        self.assertEqual(html.count("<li>") >= 16, True)
        last = crash["site"]["charts"]["drawdown"][-1][0]
        self.assertIn(site._fmt_month(last), html)  # charts state the date of their data

    def test_charts_are_interactive_and_theme_aware(self):
        html = (self.out / "market-risk.html").read_text()
        figs = html.count("<figure class=\"fig\" data-chart>")
        self.assertGreaterEqual(figs, 8)
        configs = re.findall(r'<script type="application/json">(.*?)</script>', html)
        self.assertEqual(len(configs), figs)
        for raw in configs:
            cfg = json.loads(raw.replace("<\\/", "</"))
            for sr in cfg["series"]:  # every interactive value is a dated observation from the evidence
                self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", t) and isinstance(v, (int, float)) for t, v in sr["pts"]))
        self.assertIn('data-years="10"', html)
        self.assertIn(":root[data-theme=\"dark\"]", html)
        self.assertIn(":root:not([data-theme=\"light\"])", html)
        self.assertIn('class="theme"', html)
        self.assertNotRegex(html, r"<script[^>]+src=")  # no external scripts

    def test_charts_are_drawn_from_dated_evidence(self):
        ch = self.inp["crash"]["site"]["charts"]
        dd = ch["drawdown"]
        self.assertEqual(dd[0][0], "1926-07")
        self.assertTrue(all(v <= 0 for _, v in dd))
        self.assertEqual(min(v for _, v in dd if _ < "1933"), min(v for _, v in dd))  # 1929-32 is the deepest
        for name in ("index.html", "market-risk.html", "forecast.html"):
            html = (self.out / name).read_text()
            self.assertIn('class="chart ts"', html)
            for label in re.findall(r'<svg class="chart ts"[^>]*aria-label="([^"]+)"', html):
                self.assertRegex(label, r"\d{4}")

    def test_unpublished_outlooks_explained_on_forecast_page(self):
        html = (self.out / "forecast.html").read_text()
        self.assertEqual(html.count('<span class="b">'), 11)  # every unpublished outlook
        self.assertEqual(html.count("not enough evidence</span>"), 11)
        self.assertEqual(html.count('<span class="b ok">'), 1)
        # One feature, one location: skill/ranking metrics live on the Track Record page only.
        self.assertNotIn("ranking", html.lower().split("<footer>")[0])
        self.assertIn("too confident", html)

    def test_bottom_navigation_never_covers_content_or_clips_labels(self):
        html = (self.out / "index.html").read_text()
        # Sticky (in normal flow) rather than fixed: it cannot overlap content at any text size.
        self.assertIn("nav.tabs{position:sticky;bottom:0;", html)
        self.assertIn("grid-template-columns:repeat(5,minmax(0,1fr))", html)
        self.assertLess(html.index('<nav class="tabs"'), html.index("</body>"))
        self.assertGreater(html.index('<nav class="tabs"'), html.index("</footer>"))

    def test_sectors_page_lists_each_sector_once_without_duplicate_chart(self):
        html = (self.out / "sectors.html").read_text()
        for x in self.inp["sectors"]["sectors"]:
            self.assertEqual(html.count(f'href="sector-{x["slug"]}.html"'), 1, x["slug"])
        self.assertNotIn("<svg", html.split('<main id="main">')[1].split("</main>")[0])
        self.assertNotIn('class="dbars"', html)

    def test_sector_pages_separate_exposure_from_attractiveness(self):
        for name in (p for p in self.pages if p.startswith("sector-")):
            html = (self.out / name).read_text()
            for text in ("How it has behaved", "Is it attractively priced?", "Insufficient evidence",
                         "What would change this view", "When the usual pattern failed"):
                self.assertIn(text, html, name)

    def test_track_record_shows_failures_and_archive(self):
        html = (self.out / "track-record.html").read_text()
        self.assertIn("✗", html)
        self.assertIn("as first published", html)
        self.assertTrue((self.out / "forecast_archive.csv").is_file())


if __name__ == "__main__":
    unittest.main()
