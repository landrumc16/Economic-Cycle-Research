# Economic Cycle Research

**Operating model: DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.**

- **Daily source evidence:** `.github/workflows/daily-economic-source-acquisition.yml` acquires FRED, BLS and BEA observations each calendar day, checks acquisition status, and archives evidence. Acquisition alone does not authorize source promotion or predictive claims.
- **Monthly descriptive assessment:** `.github/workflows/industry-deviation-descriptive.yml` runs on the 20th of each month (13:20 UTC), with manual and change-triggered verification available. Each observation retains its own release and freshness limitations. Only an accepted, non-stale assessment qualifies for current publication.
- **One GitHub Pages dashboard:** `.github/workflows/milestone1.yml` validates and deploys the dashboard after relevant changes and completed monthly assessments. It no longer runs the comprehensive historical/weekly research suite on a daily timer. Accepted monthly reporting is primary; older weekly research remains archival.
- **Publication safety:** A failed or unqualified monthly update must not replace a previously accepted monthly report. If a prior report cannot be recovered reliably, publication fails closed.

The historical research and Version 5 descriptive safeguards are retained. Historical publisher-original point-in-time certification, independent predictive validation, and model forecasts remain **BLOCKED** unless explicitly qualified by their existing evidence gates. Successful acquisition is not equivalent to approved current economic conclusions.

**Release evidence:** Review the GitHub Actions run logs and artifacts for each of the three workflows. A manually dispatched success is not proof of a scheduled execution. Do not claim full operational completion until daily and monthly scheduled executions and the public dashboard have been independently verified.

## Version 6 implementation handoff (2026-11-04)

Version 6 work has started on main. The existing V5 monthly research and Pages workflows remain the source of truth. Added `scripts/v6_sector_intelligence.py` and its tests for evidence-gated 11-sector coverage, plus `scripts/v6_public_site.py` and its tests for accessible overview, sector, monthly and research pages. The monthly workflow now generates V6 pages only after V5 integrated acceptance; the existing Pages workflow copies sector and methodology pages only from a qualified PASS monthly artifact.

**Not yet released:** The new pages have not been verified live. Run `python -m unittest discover -s tests -p 'test_v6_*.py' -v`, inspect the triggered monthly Actions run and its uploaded artifact, then verify the Pages run and public links. Monthly PASS artifacts may be unavailable or stale; in that case preserve the existing dashboard and do not claim a current assessment. The sector evidence registry is intentionally empty until verifiable point-in-time total returns, earnings, valuation, benchmark and economic data have been integrated. Do not infer favorable investment ratings from macro data alone.

**Next implementation batch:** Connect sourced sector/industry datasets and histories to the existing acquisition/assessment process; ensure last-good public pages survive failed retrieval; expand indicator provenance and monthly changes; complete end-to-end release checks, actual schedule evidence, and final V6 acceptance. No new roadmap or parallel research workflow is needed.

### V6 follow-up implementation (2026-11-04, later batch)

Additional commits hardened malformed sector inputs, exposed a separate `overview.html` (preserving the legacy root dashboard), populated the four macro cards from dated actual assessment values, copied the complete linked research bundle into Pages, extended public URL checks, and added a recovery path for previously published V6 pages. See commits `b0e2b232`, `d1c6b44d`, `24ae4c4a`, `85384483`, `5a334e0c`, `0d08279a`.

**Release status remains NOT VERIFIED.** The available environment could write GitHub files but could not clone the repository (network DNS failure), inspect live Actions logs, or verify the public site. Do not infer green CI, successful Pages deployment, daily schedule execution, or qualified current research. The actual committed code still needs CI execution, investigation of any failures, and verification of the live Pages URLs. Sector valuations/earnings/point-in-time return evidence remains unavailable; the site intentionally shows Insufficient Evidence. A complete Version 6 closeout requires verified CI and deployed output, not merely these commits.

### V6 integration corrections — 2026-11-04

Commits `34870897`, `1bf57cfb`, `f202e794`, and `8919789e` correct an important publishing collision: the V6 generator no longer writes `monthly.html`, which belongs to the existing accepted monthly publication. Its separate `monthly-research.html` contains dated descriptive findings and uncertainty; the Pages workflow copies and checks that page independently. The generator also rejects a contradictory PASS gate with a stale underlying assessment. These commits were written through GitHub but **the CI run, Pages deployment, and public URLs still need independent verification**.

**Immediate release check:** Review latest `Monthly Economic Cycle Assessment` and `Milestone 1 - Economic Data Acquisition and QA` workflow runs on main. Confirm V6 tests, V5 acceptance, monthly PASS or explicitly stale status, artifact contents, and Pages verification step. If a workflow fails, fix the actual logged failure, not the acceptance gate. Inspect `overview.html`, `sectors.html`, `monthly-research.html`, and `research.html` at the published Pages URL. An unverified or stale candidate must not be described as the current economy. A full V6 release remains blocked until this evidence and sourced sector valuation/returns are available.

### V6 verified source defect / unverified runtime — 2026-11-04

GitHub commits `9ce818d` and `d65b430` fix the literal escaped newline appended to `v6_sector_report.json` and add a JSON-parsing/navigation regression test. This is a concrete source-code correction, **not evidence that CI passed**. The connected GitHub API for commit workflow runs exposes pull-request runs only and returned none for the latest main commit. Local git clone again failed with `Could not resolve host: github.com`. Actual main-branch Actions logs and live Pages verification are therefore not established.

**Resume immediately:** Inspect main-branch Actions runs for the latest commit, fix failing V6 tests, and validate the downloaded monthly artifact. The existing monthly workflow must produce `overview.html`, `sectors.html`, `monthly-research.html`, `research.html`, `v6_sector_report.json` and the V5 research dependencies. Verify Pages publication of each linked file. If the accepted monthly gate is stale, preserve the prior qualified public assessment and show explicit historical-only notices; never relabel stale data as current. Keep the 11 sector outlooks at Insufficient Evidence until source-qualified market/earnings/valuation/benchmark histories are actually present. Do not mark V6 complete before verified CI, deployment, and live URLs.
