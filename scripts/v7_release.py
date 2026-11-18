"""Version 7 production integration: monthly build and gate, daily publication, verification.

DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.

* ``monthly``  — run inside the Monthly Economic Cycle Assessment workflow. Builds the V7
  forecast, sector research and site from freshly fetched data, validates the site contract,
  and writes ``v7_release_manifest.json``. The manifest is NEW_QUALIFIED only when the V6 monthly
  gate passed, V7 inputs are fresh, and every check passed; otherwise it is FAILED and the
  daily publisher keeps the last accepted V7 publication.
* ``publish``  — run by the daily Pages workflow. Promotes a qualified monthly V7 bundle, or
  recovers the last accepted live V7 bundle (PRESERVED_PREVIOUS, with a visible notice when it is
  old), or leaves the existing dashboard untouched when V7 has never been published. A live V7
  bundle that cannot be verified is a deployment blocker, never a reason to publish less.
* ``verify``   — checks an assembled directory, or the live site against it.

Only outlooks in APPROVED_OUTLOOKS may ever show a number. Any other outlook that newly passes the
evidence gate is held as "not enough evidence" and listed for owner review in the manifest.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import io
import hashlib
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

try:
    from . import v7_crash_research as crash, v7_forecast_engine as engine, v7_sectors as sectors, v7_site as site
except ImportError:  # executed as a script
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import v7_crash_research as crash, v7_forecast_engine as engine, v7_sectors as sectors, v7_site as site  # type: ignore

VERSION = "7.0"
MANIFEST = "v7_release_manifest.json"
APPROVED_OUTLOOKS = frozenset({("labor_deterioration", 12)})
OUTCOMES = frozenset({"NEW_QUALIFIED", "PRESERVED_PREVIOUS", "FAILED"})
CORE_PAGES = ("index.html", "market-risk.html", "forecast.html", "sectors.html", "research.html", "track-record.html")
NAV_PAGES = ("index.html", "market-risk.html", "forecast.html", "sectors.html", "research.html")
MAX_MARKET_LAG_DAYS = 7      # daily market observations older than this are stale
DISCLAIMER = "not personalized financial advice"
MAX_FRED_LAG_MONTHS = 3      # unemployment data older than this is stale for a monthly conclusion
MAX_FRENCH_LAG_MONTHS = 4    # French Data Library publishes with about a 1–2 month lag
STALE_NOTICE_DAYS = 45       # a preserved bundle accepted longer ago than this gets a visible notice
RESEARCH_EVIDENCE = "docs/evidence/v7_passb_forecast_research_2026-11-18.json"


def months_between(a: str, b: str) -> int:
    ya, ma = map(int, a[:7].split("-"))
    yb, mb = map(int, b[:7].split("-"))
    return (yb - ya) * 12 + (mb - ma)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------
REQUIRED = ("version", "build_commit", "build_time_utc", "assessment_date", "observation_cutoff",
            "source_status", "research_gate", "published_outlooks", "held_for_review", "pages",
            "promotion_outcome")


def validate_manifest(m: dict) -> dict:
    if not isinstance(m, dict):
        raise ValueError("Manifest must be an object")
    missing = [k for k in REQUIRED if k not in m]
    if missing:
        raise ValueError("Missing manifest fields: " + ", ".join(missing))
    if m["version"] != VERSION:
        raise ValueError("Not a V7 manifest")
    if not re.fullmatch(r"[0-9a-f]{40}", str(m["build_commit"])):
        raise ValueError("build_commit must be a full 40-character commit")
    if m["promotion_outcome"] not in OUTCOMES:
        raise ValueError("Invalid promotion outcome")
    if not isinstance(m["research_gate"], dict) or not isinstance(m["research_gate"].get("qualified"), bool):
        raise ValueError("research_gate.qualified must be boolean")
    for o in m["published_outlooks"]:
        if (o.get("target"), o.get("horizon_months")) not in APPROVED_OUTLOOKS:
            raise ValueError("Unapproved outlook published: %r" % (o,))
    pages = m["pages"]
    if not isinstance(pages, dict) or not all(p in pages for p in CORE_PAGES):
        raise ValueError("Manifest must list every core page")
    if len([p for p in pages if p.startswith("sector-")]) != 11:
        raise ValueError("Manifest must list 11 sector pages")
    for name, digest in pages.items():
        if "/" in name or ".." in name or not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
            raise ValueError("Invalid page entry: " + name)
    if m["promotion_outcome"] != "FAILED" and m["research_gate"]["qualified"] is not True:
        raise ValueError("Only a qualified V7 bundle may be published")
    return m


# ---------------------------------------------------------------------------
# Site contract
# ---------------------------------------------------------------------------
class _Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.h1, self.main, self.lang = [], 0, False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main = True
        if tag == "html" and a.get("lang") == "en":
            self.lang = True


def validate_site(root: Path, manifest: dict | None = None) -> dict:
    """Read-only V7 site contract over a built or assembled directory."""
    root = Path(root)
    names = sorted(p.name for p in root.glob("*.html"))
    v7 = [n for n in names if n in CORE_PAGES or (n.startswith("sector-") and not re.fullmatch(r"sector-\d\d\.html", n))]
    for page in CORE_PAGES:
        if page not in v7:
            raise ValueError("Missing V7 page: " + page)
    sector_pages = [n for n in v7 if n.startswith("sector-")]
    if len(sector_pages) != 11:
        raise ValueError("Expected 11 V7 sector pages, found %d" % len(sector_pages))
    if not (root / "forecast_archive.csv").is_file():
        raise ValueError("Missing forecast archive")
    for name in v7:
        html = (root / name).read_text(encoding="utf-8")
        p = _Page()
        p.feed(html)
        if not html.startswith("<!doctype html>") or 'name="viewport"' not in html:
            raise ValueError("Missing doctype or mobile viewport: " + name)
        if not p.lang or not p.main or p.h1 != 1:
            raise ValueError("Missing accessible structure (lang, main, one h1): " + name)
        if DISCLAIMER not in html.lower():
            raise ValueError("Missing educational disclaimer: " + name)
        nav = re.search(r'<nav class="primary"[^>]*>(.*?)</nav>', html, re.S)
        if not nav or re.findall(r'href="([^"]+)"', nav.group(1)) != list(NAV_PAGES):
            raise ValueError("Primary navigation must have exactly the five V7 destinations: " + name)
        for href in p.links:
            u = urlsplit(href)
            if u.scheme or u.netloc or href.startswith(("mailto:", "#")):
                continue
            if href.startswith("/") or ".." in href:
                raise ValueError(f"Unsafe link {href} in {name}")
            if not (root / u.path).is_file():
                raise ValueError(f"Broken link {href} in {name}")
    home = (root / "index.html").read_text()
    if re.search(r"recession[^<]{0,40}\d+%", home, re.I):
        raise ValueError("Home page shows a recession probability")
    for name in ("index.html", "market-risk.html"):
        txt = (root / name).read_text()
        if "crash probability" not in txt or re.search(r"(chance|probability|odds) of a (crash|decline)[^<]{0,20}\d+%", txt, re.I):
            raise ValueError("Market-risk pages must state that no crash probability is published: " + name)
    forecast = (root / "forecast.html").read_text()
    published_badges = forecast.count('<span class="b ok">')
    if manifest is not None:
        if published_badges != len(manifest["published_outlooks"]):
            raise ValueError("Forecast page numbers do not match the manifest")
        for name in v7:
            if manifest["pages"].get(name) != sha((root / name).read_bytes()):
                raise ValueError("Page does not match manifest: " + name)
    if published_badges > len(APPROVED_OUTLOOKS):
        raise ValueError("More published outlooks than approved")
    for name in sector_pages:
        if "Insufficient evidence" not in (root / name).read_text():
            raise ValueError("Investment attractiveness must stay unrated: " + name)
    return {"status": "V7_SITE_CONTRACT_PASS", "pages": len(v7), "sector_pages": len(sector_pages),
            "published_outlooks": published_badges}


# ---------------------------------------------------------------------------
# Monthly build (Monthly Economic Cycle Assessment workflow)
# ---------------------------------------------------------------------------
def hold_unapproved(report: dict) -> list:
    """Withhold any outlook outside the approved set, even if it passes the gate on new data."""
    held = []
    for o in report["current_outlooks"]:
        key = (o["target"], o["horizon_months"])
        if o["state"] == "Published" and key not in APPROVED_OUTLOOKS:
            held.append({"target": key[0], "horizon_months": key[1], "probability": o.get("probability")})
            o.update(state="Insufficient evidence", probability=None, probability_text=None, band=None,
                     reason="Passed the evidence gate on new data; held for owner review before publication")
    for e in report["evaluations"]:
        if e["publishable"] and (e["target"], e["horizon_months"]) not in APPROVED_OUTLOOKS:
            e["publishable"] = False
            e["held_for_review"] = True
    return held


def monthly(fred_dir: Path, research_dir: Path, gate_path: Path, out: Path, as_of: str,
            commit: str, built_at: str, research_evidence: Path = Path(RESEARCH_EVIDENCE),
            crash_dir: Path | None = None) -> dict:
    out = Path(out)
    work = out.parent / "v7-work"
    site_dir = out
    for d in (work, site_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    reasons = []
    gate = json.loads(Path(gate_path).read_text()) if Path(gate_path).is_file() else {}
    if gate.get("status") != "PASS":
        reasons.append("Monthly economic gate is %s, not PASS" % (gate.get("status") or "missing"))
    fred = engine.load(Path(fred_dir))
    fred_latest = max(fred["UNRATE"])
    if months_between(fred_latest, as_of) > MAX_FRED_LAG_MONTHS:
        reasons.append(f"Unemployment data end {fred_latest}; too old for {as_of[:7]}")
    rman = json.loads((Path(research_dir) / "MANIFEST.json").read_text())
    french_latest = rman["sources"]["french_49_industries"]["last"]
    if months_between(french_latest, as_of) > MAX_FRENCH_LAG_MONTHS:
        reasons.append(f"Sector return data end {french_latest}; too old for {as_of[:7]}")

    report = engine.run(fred)
    held = hold_unapproved(report)
    forecast_path = work / "v7_forecast_evaluation.json"
    forecast_path.write_text(json.dumps(report, indent=1) + "\n")
    archive_path = work / "forecast_archive.csv"
    with archive_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "horizon_months", "origin", "probability", "probability_raw", "outcome"])
        w.writerows((r["target"], r["horizon_months"], r["origin"], r["probability"], r["probability_raw"],
                     r["outcome"]) for r in report["forecast_archive"])
    condition, band = sectors.current_inputs(fred_dir, forecast_path)
    sector_report = sectors.build(sectors.load(research_dir, fred_dir), condition, band)
    sectors_path = work / "v7_sectors.json"
    sectors_path.write_text(json.dumps(sector_report, indent=1) + "\n")
    if len(sector_report["sectors"]) != 11:
        reasons.append("Sector research does not cover 11 sectors")
    if any(s["investment_attractiveness"] != "Insufficient evidence" for s in sector_report["sectors"]):
        reasons.append("A sector attractiveness rating appeared without qualified valuation data")

    # Market-risk research on freshly fetched market data (daily observations; monthly conclusions).
    crash_path = work / "v7_crash_research.json"
    if crash_dir is None or not (Path(crash_dir) / "MANIFEST.json").is_file():
        reasons.append("Market data were not fetched")
        crash_path = Path(site.CRASH_EVIDENCE)
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            crash.analyze(Path(crash_dir), crash_path)
        cman = json.loads((Path(crash_dir) / "MANIFEST.json").read_text())
        if cman.get("gaps"):
            reasons.append("Market data gaps: " + "; ".join(cman["gaps"])[:300])
        sp_last = cman.get("fred", {}).get("SP500", {}).get("last")
        if not sp_last or (date.fromisoformat(as_of[:10]) - date.fromisoformat(sp_last)).days > MAX_MARKET_LAG_DAYS:
            reasons.append(f"Daily market data end {sp_last}; too old for {as_of[:10]}")
    inp = site.load_inputs(forecast_path, research_evidence, sectors_path, archive_path, fred_dir, crash_path)
    site.build(site_dir, inp)
    published = [{"target": r["target"], "horizon_months": r["h"], "probability": r["p"], "band": r["band"],
                  "forecast_origin": r["origin"]} for r in site.outlook_matrix(inp) if r["published"]]
    pages = {p.name: sha(p.read_bytes()) for p in sorted(site_dir.glob("*.html"))}
    manifest = {
        "version": VERSION, "build_commit": commit, "build_time_utc": built_at,
        "assessment_date": inp["assessment"]["assessment_date"],
        "observation_cutoff": inp["assessment"]["sources"]["UNRATE"]["latest_used_month"],
        "condition": inp["view"]["condition"], "direction": inp["view"]["direction"],
        "sector_as_of": sector_report["as_of_month"],
        "market_warnings": [{k: w.get(k) for k in ("key", "title", "status", "value", "date", "frequency")}
                            for w in inp["crash"]["site"]["warnings"]],
        "worth_researching_now": [s["sector"] for s in sector_report["sectors"]
                                  if s["research_priority"] == "Worth researching now"],
        "source_status": {"monthly_gate": gate.get("status"), "fred_latest_month": fred_latest,
                          "french_latest_month": french_latest, "research_retrieved": rman.get("retrieved"),
                          "point_in_time_certified": False},
        "published_outlooks": published, "held_for_review": held, "pages": pages,
        "research_gate": {"qualified": False, "reasons": reasons},
        "promotion_outcome": "FAILED",
    }
    try:
        validate_site(site_dir, manifest)
    except ValueError as exc:
        reasons.append("Site contract: %s" % exc)
    if not reasons:
        manifest["research_gate"]["qualified"] = True
        manifest["promotion_outcome"] = "NEW_QUALIFIED"
    validate_manifest(manifest)
    (site_dir / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    for f in (forecast_path, sectors_path) + ((crash_path,) if crash_path.parent == work else ()):
        shutil.copy(f, site_dir / f.name)
    return manifest


# ---------------------------------------------------------------------------
# Daily publication (Milestone 1 Pages workflow)
# ---------------------------------------------------------------------------
def http_get(url: str, attempts: int = 6, wait: float = 10.0, opener=urllib.request.urlopen, sleep=None) -> bytes | None:
    """Return the body, or None on 404. Transient 5xx and network errors are retried a bounded
    number of times; anything still failing raises (fail closed: deployment is refused)."""
    import time
    sleep = sleep or time.sleep
    for attempt in range(attempts):
        try:
            with opener(url, timeout=15) as r:
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status} for {url}")
                return r.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code < 500 or attempt == attempts - 1:
                raise RuntimeError(f"HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == attempts - 1:
                raise RuntimeError(f"Unreachable: {url}: {exc}") from exc
        sleep(wait * (attempt + 1))
    raise RuntimeError("unreachable")


def files_of(manifest: dict) -> list:
    return sorted(manifest["pages"]) + ["forecast_archive.csv"]


def stale_notice(html: str, assessment_date: str) -> str:
    note = ('<p class="note" role="status"><strong>This is the assessment of %s.</strong> A newer monthly assessment '
            'has not yet passed our checks, so this earlier one is shown.</p>' % assessment_date)
    return html.replace('<main id="main">', '<main id="main">' + note, 1)


def find_bundle(source: Path | None) -> Path | None:
    if not source or not Path(source).exists():
        return None
    found = sorted(Path(source).rglob(MANIFEST))
    return found[0].parent if len(found) == 1 else None


def publish(source: Path | None, target: Path, live_base: str, today: date, fetch=http_get) -> dict:
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    base = live_base.rstrip("/") + "/"
    bundle = find_bundle(source)
    raw = fetch(base + MANIFEST)  # the live V7 publication, if any (errors propagate: fail closed)
    rejected = None
    if bundle:
        try:  # an invalid candidate is never published; the accepted publication is kept instead
            m = validate_manifest(json.loads((bundle / MANIFEST).read_text()))
            validate_site(bundle, m) if m["promotion_outcome"] == "NEW_QUALIFIED" else None
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            rejected, bundle = f"Candidate bundle rejected: {exc}", None
    if bundle:
        live_time = validate_manifest(json.loads(raw))["build_time_utc"] if raw is not None else ""
        if m["promotion_outcome"] == "NEW_QUALIFIED" and m["build_time_utc"] >= live_time:
            validate_site(bundle, m)
            for name in files_of(m):
                shutil.copy(bundle / name, target / name)
            (target / MANIFEST).write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
            return {"outcome": "NEW_QUALIFIED", "assessment_date": m["assessment_date"], "commit": m["build_commit"]}
    if raw is None:
        return {"outcome": "NOT_PUBLISHED", "reason": rejected or "No qualified V7 bundle and no previous V7 publication"}
    prev = validate_manifest(json.loads(raw))
    if prev["research_gate"]["qualified"] is not True:
        raise RuntimeError("Previous V7 publication was not qualified; refusing preservation")
    original = prev.get("original_pages") if prev.get("stale_notice") else prev["pages"]
    if not isinstance(original, dict) or set(original) != set(prev["pages"]):
        raise RuntimeError("Previous V7 manifest lacks its original page hashes")
    note = stale_notice('<main id="main">', prev["assessment_date"]).replace('<main id="main">', "", 1)
    for name in files_of(prev):
        body = fetch(base + name)
        if body is None:
            raise RuntimeError("Incomplete previous V7 publication: " + name)
        if name.endswith(".html"):
            body = body.decode("utf-8").replace(note, "", 1).encode("utf-8")  # restore the accepted original
            if sha(body) != original[name]:
                raise RuntimeError("Live page does not match its accepted original: " + name)
        (target / name).write_bytes(body)
    accepted = date.fromisoformat(prev["build_time_utc"][:10])
    old = (today - accepted).days > STALE_NOTICE_DAYS
    out = {k: v for k, v in prev.items() if k not in ("stale_notice", "original_pages")}
    out.update(promotion_outcome="PRESERVED_PREVIOUS", pages=dict(original))
    if old:
        out["stale_notice"] = True
        out["original_pages"] = dict(original)
        for name in original:
            html = stale_notice((target / name).read_text(), prev["assessment_date"])
            (target / name).write_text(html)
            out["pages"][name] = sha(html.encode())
    validate_site(target, out)
    (target / MANIFEST).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return {"outcome": "PRESERVED_PREVIOUS", "assessment_date": prev["assessment_date"], "stale_notice": old,
            **({"rejected_candidate": rejected} if rejected else {})}


def verify_live(target: Path, live_base: str, fetch=http_get) -> dict:
    """Compare the live site with the assembled publication, page by page."""
    target = Path(target)
    if not (target / MANIFEST).is_file():
        return {"status": "NO_V7_PUBLICATION"}
    expected = validate_manifest(json.loads((target / MANIFEST).read_text()))
    base = live_base.rstrip("/") + "/"
    live = fetch(base + MANIFEST)
    if live is None or json.loads(live) != expected:
        raise RuntimeError("Live V7 manifest does not match the accepted publication")
    for name in files_of(expected):
        body = fetch(base + name)
        if body is None or body != (target / name).read_bytes():
            raise RuntimeError("Live V7 file differs from accepted publication: " + name)
    return {"status": "V7_LIVE_VERIFIED", "files": len(files_of(expected)), "outcome": expected["promotion_outcome"]}


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("monthly")
    m.add_argument("--fred-dir", type=Path, default=Path("data/industry_observations"))
    m.add_argument("--research-dir", type=Path, required=True)
    m.add_argument("--crash-dir", type=Path, required=True)
    m.add_argument("--gate", type=Path, default=Path("audit-output/weekly_release_acceptance.json"))
    m.add_argument("--output", type=Path, default=Path("audit-output/v7-site"))
    m.add_argument("--as-of", default=date.today().isoformat())
    m.add_argument("--commit", required=True)
    m.add_argument("--built-at", required=True)
    p = sub.add_parser("publish")
    p.add_argument("--source", type=Path)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--live-base", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--directory", type=Path, required=True)
    v.add_argument("--live-base")
    a = ap.parse_args(argv)
    if a.cmd == "monthly":
        r = monthly(a.fred_dir, a.research_dir, a.gate, a.output, a.as_of, a.commit, a.built_at, crash_dir=a.crash_dir)
        print(json.dumps({k: r[k] for k in ("promotion_outcome", "assessment_date", "observation_cutoff", "condition",
                                            "published_outlooks", "held_for_review", "market_warnings", "worth_researching_now",
                                            "research_gate")}, indent=1))
    elif a.cmd == "publish":
        print(json.dumps(publish(a.source, a.target, a.live_base, date.today())))
    else:
        if a.live_base:
            print(json.dumps(verify_live(a.directory, a.live_base)))
        elif (a.directory / MANIFEST).is_file():
            print(json.dumps(validate_site(a.directory, json.loads((a.directory / MANIFEST).read_text()))))
        else:
            print(json.dumps({"status": "NO_V7_PUBLICATION"}))


if __name__ == "__main__":
    main()
