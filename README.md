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

### V6 substantive sector and Pages reliability batch — 2026-11-04

Commits `cf46e726`, `54b39961`, `dac80906`, and `333d814a` extend scheduled Pages handling and preserve sector links after recovery; all 11 GICS sectors now show distinct structural economic sensitivities and industry examples while still withholding unsupported current ratings. The coverage test was corrected to be discovered by `unittest`. These are hypotheses for further research, not sourced current investment conclusions.

**Outstanding external release gate:** Main-branch Actions runs and Pages content could not be accessed from the available execution environment. Public site retrieval returned an inaccessible response; git clone failed DNS. No green CI, daily-source refresh, monthly PASS, or successful Pages publication has been established. Use GitHub Actions to run the monthly workflow and Pages workflow, inspect the test/build/deploy logs, fix any actual failures, and verify public URLs before closing V6. Sourced earnings, valuation and benchmark-relative point-in-time return histories are still absent; do not promote sector outlooks without them.

### V6 preservation and evidence-gate correction — 2026-11-04

Commits `270be83b`, `91c92311`, `11c7eba3`, `869b58cb`, `f8262797`, and `a2b309e4` correct the V6 artifact publisher so it does not overwrite the accepted V5 `index.html` (or `monthly.html`), add preservation regression coverage, strengthen Pages verification to parse sector JSON and check navigation, and prohibit sector outlooks without actual numeric observations, rationale, transaction-cost assumptions, and survivorship caveats. The rejected-candidate regression assertion was corrected after source review.

**Release evidence still missing:** local GitHub clone fails DNS, the connected GitHub API exposes no main-branch workflow-run listing/dispatch, and no live Pages verification was obtained. Run the existing monthly workflow, confirm V6 regression tests and artifact gate, then run/inspect Pages and verify the public URLs. No evidence-based sector outlook can be published until qualified datasets are present. These changes are committed but their CI results are not certified.

### V6 fail-closed publication batch — 2026-11-04

Commits `22e72506`, `77af027b`, and `1d1c2832`: repaired the Pages deployment gap when no qualified monthly artifact is present (recover complete previously published V6 bundle, or fail if preservation cannot be verified), validate 11-sector JSON before copying, and render nonfinite or malformed source observations as unavailable. Added regression coverage for NaN/Infinity and invalid provenance. This avoids accidentally publishing a false numeric indicator.

**Not yet certified:** The connected GitHub commit-status endpoint returned no statuses for the latest commit; it does not establish passing Actions tests. Public `https://landrumc16.github.io/Economic-Cycle-Research/overview.html` could not be accessed from the available web tool. A green monthly run, successful Pages deployment, and live site checks remain necessary. Inspect Actions and execute tests before release acceptance; retain explicit Insufficient Evidence outlooks for sectors lacking qualified data.

### V6 monthly-comparison and provenance implementation — 2026-11-04

Commits `50f8dfec`, `856ef061`, `9b55512f`, and `d1e53d2a` reject placeholder sector URLs and nonfinite evidence values, add negative tests, and display actual month-over-month descriptive dashboard metric deltas (with prior assessment date) on `monthly-research.html`. The page states when no prior comparable assessment exists. This reuses `economic_dashboard.json`, not a new analysis pipeline.

**Next release checks:** Run `python -m unittest discover -s tests -p 'test_v6_*.py' -v` in the existing monthly workflow, verify its `economic_dashboard.json` and Pages artifact, inspect the main-branch Pages workflow deployment, and confirm all public V6 URLs. These checks have not been executed successfully in this environment. Source-qualified sector ratings and qualified monthly publication are not certified.

### V6 assessment provenance correction — 2026-11-04

Commits `8c75a13e` and `39cc91fd` distinguish HTML generation date from the official dated monthly assessment; reject stale dashboard comparisons and malformed metric collections instead of implying current changes. Regression tests cover stale comparisons and assessment-date labeling. No new workflow or historical research was introduced.

**Unresolved release gate:** Tests have been committed but not executed against a verified main-branch Actions run; the connected GitHub tool has no dispatch/list-run operation, and live Pages was not independently verified. To resume, inspect the existing monthly and Pages Actions runs, fix concrete failures, verify `overview.html`, `sectors.html`, `monthly-research.html`, `research.html`, and accepted monthly artifacts. Do not claim sector investment ratings without independent, point-in-time market/earnings/valuation evidence.

### V6 first-publication correction — 2026-11-04

Commit `130b1306` fixes a first-publication deadlock: the Pages workflow previously accepted only monthly `PASS` artifacts for V6, although the V6 generator explicitly supports `STALE_RESEARCH_ONLY` as a historical-only research release. Pages now accepts either gate, but requires the explicit **Historical research only** warning on stale V6 overview pages. This does not turn stale data into a current monthly conclusion or approve unsupported sector ratings.

**Release not certified:** Execute the monthly workflow and Pages workflow, inspect test failures and Pages URLs, and verify the dated official assessment and scheduled data refresh. Connected GitHub actions available in this chat support file commits but not workflow dispatch/listing; live deployment verification is outstanding.

### V6 executive overview semantic correction — 2026-11-04

Commits `7dd24895` and `59c47823`: corrected the public overview's misleading **Financial stress** label for BUSLOANS 12-month credit growth (now **Business credit** with explicit qualification); added visible prior-comparison and uncertainty sections to the overview; added regression test. Financial stress cannot be inferred from loan growth alone.

**Current release blockers:** No verified passing CI or Pages deployment run was accessible through connected GitHub tools; public site URL was inaccessible from web retrieval. The daily acquisition schedule, official monthly artifact qualification, and live V6 pages still require operational verification. Resume from the latest commit, run existing monthly and Pages workflows, inspect their logs and evidence artifacts, and only mark release accepted after actual tests and live verification. Do not invent market data or sector ratings.

### V6 sector deep-dive batch — 2026-11-04

Commits `c3b0bbc7`, `a43c6277`, `fec881d6`: generate `sector-01.html` through `sector-11.html` with distinct economic exposure, industry examples, qualified investment evidence or explicit insufficiency; link from sector index. Pages deployment now treats all 11 pages as a required recoverable bundle and verifies each published page. Tests cover links, responsive viewport and evidence-gated status.

**Operational release pending:** Connected GitHub tool does not expose workflow dispatch or run listing. Public GitHub Pages and Actions URLs were not retrievable through the web tool in this session. No CI, deployment, or scheduled execution success is asserted. Run existing workflows, inspect failure logs, verify all 11 live sector pages plus monthly assessment, and close the roadmap only with run/deployment evidence.

### V6 source-date validity gate — 2026-11-04

Commits `d9582dd7` and `66386f2e`: public indicator cards now withhold numeric values when the individual FRED source's `latest_used_month` is missing or not a valid YYYY-MM calendar month. This closes a misleading undated-number pathway while retaining valid dated observations. Regression tests cover missing, impossible and valid months.

**Release verification blocker remains:** Connected GitHub API in this session cannot dispatch or list workflow runs; public `https://landrumc16.github.io/Economic-Cycle-Research/overview.html` could not be retrieved. Unit tests are committed, not claimed passing. Existing monthly workflow runs V6 regression tests and generates the V6 bundle; existing Pages workflow publishes and verifies it. Inspect actual Actions runs and published pages before accepting V6. Note first publication now requires 11 sector detail files alongside the overview and evidence bundle.
