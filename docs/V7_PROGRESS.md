# V7 Progress

**Branch:** `v7-development`, created from the V6.3 release record `11f0996` (which contains production `7dfc811`).
**Production:** V6.3 on `main` (`7dfc811`) is unchanged. V7 is not merged or deployed.
**Pass A (M1 + M2):** complete. Result: **1 of 9 outlooks passes the evidence gate.** The rest are honestly reported as *Insufficient evidence*.

## M1 — Research and forecasting foundation

### Inventory and reuse decisions
| Existing component | V7 use |
|---|---|
| `scripts/fetch_industry_observations.py` (official FRED API, monthly normalisation, provenance metadata) | Reused; allow-list extended with GS10, TB3MS, BAA, USREC, PAYEMS, ICSA |
| Monthly pipeline (`industry-deviation-descriptive.yml`) and daily publisher (`milestone1.yml`) | Unchanged in Pass A; integration is M5 |
| V6.3 rubric (`v63_interpretation.py`) and replay (`v63_historical_replay.py`) | Reused as a **benchmark**: does the descriptive "Deteriorating" condition forecast anything? |
| V6.3 safeguards (gates, stale withholding, manifest, rollback) | Preserved; no production code changed |
| New: `.github/workflows/v7-forecast-research.yml` | Research-only CI. Runs on pushes to `v7-development`, fetches data, runs the suite and the engine. Never publishes, and does not trigger the production Milestone 1 workflow |

### Data snapshot (provenance)
- `data/v7/*_monthly.csv` plus `data/v7/SNAPSHOT.json`: official FRED API series retrieved by V7 Forecast Research run 44099072909 (2026-11-17).
- **Coverage:**

| Series | Range |
|---|---|
| GS10 | 1953-04 to 2026-10 |
| TB3MS, BAA, USREC, PAYEMS | 1948-01 to 2026-10 |
| UNRATE, CPIAUCSL | 1948-01 to 2026-10, with October 2025 unpublished (left missing) |
| INDPRO | to 2026-09 |
| ICSA | 1967-01 to 2026-10 |

- Treasury and BAA yields are never revised. The macro series are current-vintage and may have been revised.

### Forecast targets (forecast made at the end of month *t*; *h* = 3, 6, 12)
| Target | Definition | Why |
|---|---|---|
| `recession` | The economy is in an NBER-dated recession at some point in months *t*+1 … *t*+*h* | The question investors ask; NBER dates are the reference chronology |
| `labor_deterioration` | Unemployment rises ≥ 0.5 pt above its latest known level within *h* months | Directly observable, timely, and ties to the V6.3 labor rule |
| `inflation_rising` | The 12-month CPI rate *h* months ahead is above the latest known rate | The inflation-direction question |

### Point-in-time rules (tested)
- Market data (GS10, TB3MS, BAA) for month *t* are used. UNRATE, PAYEMS and CPI are used through *t*−1, INDPRO likewise.
- USREC is **never** a model input. As a training label it counts as known only 12 months after its window closes. Macro labels count as known 1 month after.
- One unpublished month (October 2025) is tolerated inside 3-month averages, and CPI and payrolls fall back to the previous month only when that month and its own base month exist. Nothing is imputed. Two missing months withhold the features.
- Tests prove that changing same-month macro values, any later values, or USREC does not change a forecast.

### Baselines
- **Historical base rate:** training-period frequency.
- **Yield curve only:** the classic single-indicator model.
- **V6.3 rubric:** outcome frequency when the descriptive condition was "Deteriorating" versus not.

## M2 — Forward-looking economic engine

### Method (`scripts/v7_forecast_engine.py`, standard-library Python)
- **Features** (fixed before evaluation):
  - recession and labor: term spread, 12-month minimum term spread, BAA–10-year credit spread, unemployment 3-month average rise over its prior-year low, 6-month payroll growth;
  - inflation: 3-month versus 12-month CPI momentum, 12-month CPI, unemployment rise, term spread.
- **Model:** L2 logistic regression, re-fitted every 12 months on an expanding window. Out-of-sample forecasts are monthly from 1972.
- **Chronological recalibration:** each year a one-variable logistic is fitted on the model's *past* out-of-sample forecasts whose outcomes were already known, and applied only forward. It is active for about 78% of forecasts; earlier forecasts are raw.
- **Gate** (unchanged from the roadmap; full sample including 2020): Brier skill vs base rate ≥ 0.05, AUC ≥ 0.70, ≥ 3 independent episodes, overconfidence ≤ 0.20.

### Real-data results (out-of-sample 1972 to the latest month with a known outcome; `docs/evidence/v7_forecast_evaluation_2026-11-17.json`)
| Target | h | Episodes | BSS vs base | AUC | Overconfidence | Raw BSS | Yield-curve-only BSS | V6.3 rubric BSS | Gate |
|---|---|---|---|---|---|---|---|---|---|
| Recession | 3 | 7 | 0.239 | 0.847 | 0.278 | 0.109 | 0.163 | 0.117 | ✗ calibration |
| Recession | 6 | 7 | 0.281 | 0.839 | 0.327 | 0.137 | 0.228 | 0.087 | ✗ calibration |
| Recession | 12 | 7 | 0.266 | 0.853 | 0.271 | 0.245 | 0.321 | 0.039 | ✗ calibration |
| Labor deterioration | 3 | 11 | 0.169 | 0.867 | 0.387 | 0.133 | 0.028 | 0.154 | ✗ calibration |
| Labor deterioration | 6 | 16 | 0.218 | 0.809 | 0.283 | 0.181 | 0.166 | 0.128 | ✗ calibration |
| **Labor deterioration** | **12** | **15** | **0.325** | **0.828** | **0.117** | 0.333 | 0.328 | 0.092 | **✓ PUBLISHABLE** |
| Inflation rising | 3 | 62 | 0.031 | 0.620 | 0.184 | 0.026 | 0.050 | 0.040 | ✗ skill, AUC |
| Inflation rising | 6 | 49 | 0.056 | 0.650 | 0.124 | 0.042 | 0.108 | 0.038 | ✗ AUC |
| Inflation rising | 12 | 33 | −0.088 | 0.484 | 0.531 | −0.137 | 0.007 | −0.021 | ✗ all |

Excluding the 2019-03 to 2020-12 pandemic window, model skill is higher (for example recession 6 months 0.338, labor 12 months 0.348). The gate deliberately uses the full sample.

### Findings
1. **Recession and labor risk are genuinely forecastable in ranking terms.** AUC is 0.81–0.87 and skill over the base rate is +0.17 to +0.33 out of sample. But the probabilities are **overconfident at the top end**: when the model says 85–95%, recessions followed only 63–75% of the time. Misses cluster near recession endings (the target counts recessions still under way), the 2020 shock, and the 2006 and 2022–2025 yield-curve inversions. So no recession probability is published.
2. **A simple yield-curve-only model beats the multi-feature model on raw recession skill at 6 and 12 months** (0.23 / 0.32 vs 0.14 / 0.25 raw). Extra features did not help recession forecasting; recalibration closed most of the gap.
3. **Inflation direction is not forecastable with these inputs** (AUC 0.48–0.65). It is reported as Insufficient evidence.
4. **The V6.3 descriptive rubric has little forward value** (BSS 0.04–0.15). This confirms it should not be presented as a forecast.
5. **Publishable now: labor-market deterioration within 12 months**, origin 2026-10: **about 30%, "Typical"** against a 28% historical base rate. Inputs: term spread 1.08, 12-month minimum spread 0.31, credit spread 1.46, unemployment rise 0.0, payrolls +0.30% over 6 months.

### Honesty notes
- Recalibration was added **after** the first real-data run showed overconfidence (run 44099072909). That's a data-snooping risk. The gate thresholds, targets and features were not changed, and model iteration stopped after this one standard step.
- Current-vintage macro data: revision effects make history look somewhat better than real time would have been.
- There are only 7 recession episodes in the evaluation window, so recession metrics have wide uncertainty.
- **Forecast archive:** `data/v7/forecast_archive.csv` holds 5,822 monthly out-of-sample forecasts (raw and recalibrated) with outcomes, for future performance tracking.

## Next: Pass B (M3 + M4)
1. **M3 sector intelligence:**
   - link the 11 sectors' economic sensitivity to the M2 labor outlook and the V6.3 condition;
   - source valuation, earnings and relative-strength data. This needs the owner's decision on a qualified, licensable market-data provider (FRED has no sector valuation data).
   - Attractiveness stays Insufficient evidence until then.
2. **M4 interface:** a mobile-first redesign around the cycle visual, the outlook (showing published and Insufficient-evidence states honestly), sector discovery, track record (from the forecast archive) and Research & Data.
3. **Optional M2 research, pre-registered before running:**
   - a recession target defined as *onset* within *h* months (removes the recession-ending misses);
   - real-time vintages (ALFRED first releases) for UNRATE and PAYEMS to remove revision bias.

---

# Pass B (M3 + M4) — 2026-11-18

**Status:** M3 complete (framework, tests, outputs for all 11 sectors). M4 complete (working redesigned site, 16 pages). Forecast research improvements done as pre-registered. Investment attractiveness remains **Insufficient evidence** pending an owner decision on a licensed valuation source.

## Forecasting research (pre-registered in `docs/V7_PREREGISTRATION_PASS_B.md`, commit `84105b9`, before any results)
| Analysis | Result | Decision |
|---|---|---|
| Recession **onset** 3 / 6 / 12 months (expansion months only) | AUC 0.87 / 0.90 / 0.89; BSS −0.04 / +0.15 / +0.10; overconfidence 0.52 / 0.55 / 0.39 | Fails the calibration gate at every horizon, so recession stays **Insufficient evidence** |
| Labor deterioration on **ALFRED first-release** UNRATE/PAYEMS inputs | 12 months: BSS 0.309, AUC 0.823, overconfidence 0.182, **passes** (3 / 6 months fail, as on revised data) | Revision bias does not drive the published outlook; it stays published |

No model was promoted from previously examined data. Evidence: `docs/evidence/v7_passb_forecast_research_2026-11-18.json`.

## M3 — Sector investment intelligence (`scripts/v7_sectors.py`)
**Data (CI-fetched, SHA-256 verified, `data/v7_research/MANIFEST.json`):**
- Kenneth R. French 49 industries and market factors, 1926-07 to 2026-09;
- Damodaran US industry P/E and growth (96 industries, annual vintage);
- ALFRED first releases (UNRATE from 1960-03, PAYEMS from 1955-05).

**Method:**
- GICS sectors are approximated by equal-weighting mapped French industries (documented proxy).
- Per sector:
  - recession, expansion, rate and inflation sensitivity since 1953;
  - 12-month relative strength (skip 1);
  - Damodaran valuation and growth as dated context;
  - economic backdrop matched to the current condition (V6.3 rubric) and the published labor outlook;
  - a transparent research priority, plus supports, challenges, what would change the view, and contrary cases.
- Attractiveness is fail-closed.

**Relative-strength persistence test (pre-registered), 133 non-overlapping 6-month periods, 1960–2026:**
- Spread +1.65 pts per 6 months, t = 2.15, first half +2.25, second half +1.06, sign hit rate 55.8%. This **meets** the rule (t ≥ 2, both halves positive), so it is used as a signal.
- **Integrity note:** the first implementation did not skip the latest month as pre-registered (it gave t = 2.71). It was corrected to the registered specification before acceptance, and only the corrected result is used. The weakening in the second half is disclosed.

**Results** (condition Expanding; labor outlook Typical; data to 2026-09):

| Sector | Cycle class | Backdrop | 12-month RS vs market (pts) | Recession / expansion excess (%/yr) | Rate beta (%/pp) | Forward P/E (vs market, annual) | Research priority |
|---|---|---|---|---|---|---|---|
| Communication Services | Neutral | Neutral | −26.9 | +2.3 / +0.3 | −0.21 | 26.5 (−4%) | Lower priority for now |
| Consumer Discretionary | Neutral | Neutral | −17.3 | +3.9 / −0.5 | −0.23 | 21.9 (−21%) | Lower priority for now |
| Consumer Staples | Defensive | Less favored | −11.5 | +6.6 / −0.1 | −0.52 | 17.0 (−38%) | Lower priority for now |
| Energy | Cyclical | Supportive | +31.1 | −3.6 / +2.3 | +2.42 | 28.1 (+2%) | **Worth researching now** |
| Financials | Neutral | Neutral | −6.4 | +0.2 / +0.7 | −1.14 | 16.4 (−41%) | Lower priority for now |
| Health Care | Defensive | Less favored | −2.5 | +9.1 / +0.8 | −0.59 | 39.9 (+44%) | Lower priority for now |
| Industrials | Neutral | Neutral | +1.8 | −3.0 / +1.5 | +0.19 | 22.3 (−20%) | **Worth researching now** |
| Information Technology | Neutral | Neutral | +25.7 | +4.2 / +2.8 | +0.93 | 36.7 (+33%) | **Worth researching now** |
| Materials | Neutral | Neutral | +5.6 | +0.1 / +0.2 | −0.15 | 17.3 (−38%) | **Worth researching now** |
| Real Estate | Cyclical | Supportive | −21.1 | −6.9 / −1.1 | −1.48 | 44.4 (+60%) | Monitor |
| Utilities | Defensive | Less favored | −11.5 | +3.7 / −2.1 | −1.70 | 18.1 (−34%) | Lower priority for now |

All 11 sectors: investment attractiveness **Insufficient evidence**; `is_recommendation: false`.

**Caveats:**
- The French "RlEst" portfolio is real-estate operating firms, not REITs.
- Forward P/E medians are an annual vintage.
- Industry equal-weighting differs from GICS market-cap weights.

**Provider recommendation:** `docs/V7_MARKET_DATA_PROVIDERS.md`.
- **Now:** the free stack, already implemented.
- **Next (owner decision):** a sector-ETF fundamentals feed at about $50–$100/month (EODHD first, then FMP), but only with written public-display rights.

## M4 — Human-first interface (`scripts/v7_site.py`)
**Five experiences, one home per feature:**
- **Home:** where we are (cycle visual), where we may be heading (3/6/12 months), what supports and challenges the view, what would change it, sectors worth researching, reliability. It summarises and links.
- **Forecast:** all 12 outlooks with status and reasons; inputs explained in plain English.
- **Sectors:** 11 cards by priority, a relative-strength chart and the method. Plus **11 sector pages**: support versus challenge, behaviour chart, "Is it attractively priced?" (gated), what would change the view, contrary case.
- **Track Record:** the labor-12-month forecast timeline against outcomes, calibration, every outlook's pass/fail, honest notes and the CSV archive.
- **Research & Data:** methods, sources and attribution, limitations, pre-registration.

**Design and verification:**
- Mobile-first, with a bottom tab bar on phones and top navigation on desktop; dark mode.
- Inline SVG and HTML charts, each with a text alternative.
- Dependency-free static HTML, consistent with the existing pipeline.
- **Verified on the actual build:**
  - axe-core WCAG 2.0/2.1/2.2 A/AA: **0 violations** on all 16 pages at 1280, 640 (≈200% zoom) and 320 px (≈400%), light and dark (96 page checks);
  - no horizontal overflow;
  - full keyboard reach on Home, Sectors and a sector page.
- Two issues found and fixed in the process: a non-focusable scroll region at 320 px, and copy that read wrongly in dark mode.
- **Screenshots:** `docs/evidence/v7-passb-screenshots/` (13 images: 6 pages × 390/1280 px, plus Home in dark mode).

## Tests
- `python -m unittest discover -s tests`: **508 tests OK** (Pass A: 492). The new `tests/test_v7_sectors_and_site.py` covers:
  - 11 sectors with gated attractiveness;
  - relative strength uses only past months;
  - the pre-registered rule;
  - relative strength is ignored when not informative;
  - onset scoring from expansion months only;
  - first-release series feed only features;
  - committed evidence reproduces;
  - five destinations, link integrity, `main`/`h1`/labels, and that only the gated outlook shows a number.
- The CI research workflow now also rebuilds sectors and the site and checks the committed evidence reproduces.

## Not yet done (Pass C)
- Integrate the V7 site into the production monthly and daily pipelines (M5): page set, publisher acceptance, manifest, rollback.
- Owner decision on a licensed valuation and earnings source.
- Human accessibility evaluation (screen readers, real devices, plain-language review).

## Pass C — mobile-first UX acceptance (2026-11-18)
Presentation only. The data, publication gate, Insufficient-evidence states, attractiveness fail-close and disclaimers are unchanged; tests still assert that only the gated 12-month labour outlook shows a number.

**Changes (`scripts/v7_site.py`)**
- **Home:** conclusions first. A compact condition card, then three one-line horizon rows with mini bars, then a sector preview listing only "Worth researching now" sectors. Drivers, counterevidence and reversal conditions moved into three collapsed sections, followed by a one-line reliability link. The long lede now shows on desktop only, and there are no tables.
- **Forecast:** the published outlook, with its inputs behind a disclosure. All 12 outlooks are grouped by target with horizon badges and one plain reason. Skill and ranking figures were removed because they live on Track Record (one feature, one location).
- **Sectors:** one compact list per priority group, with the 12-month strength bar inline. The duplicate relative-strength chart was removed, and the method is behind a disclosure.
- **Sector detail:** the conclusions stay visible (why, against, what would change). Behaviour, valuation, contrary case and method are in collapsible sections.
- **Track Record:** the timeline and headline metrics come first, and calibration sits behind a disclosure. The per-outlook list has ✓/✗ marks with screen-reader text. The notes are collapsed.
- **Research & Data:** one card of collapsible sections, and long file paths wrap.
- Touch targets are at least 48 px for rows and summaries and 32 px for header links (inline sentence links are exempt under WCAG 2.5.8). `overflow-wrap` and `min-width:0` were added so 200% text reflows, and bottom padding accounts for the tab bar and the safe-area inset.

**Mobile height at 390×844 (screens = page height ÷ 844)**
| Page | Before | After |
|---|---|---|
| Home | 3225 (3.8) | 2026 (2.4) |
| Forecast | 3105 | 1686 |
| Sectors | 3305 | 1771 |
| Track Record | 3092 | 1712 |
| Research & Data | 1257 | 1240 |
| Sector (Energy) | 2434 | 1459 |

On Home, the condition card ends at 424 px, the outlook at 874 px and the sector preview at 1406 px (1558 px at 320 wide), so all three conclusions fit within two screen heights (1688 px) at 320, 375, 390 and 430 px.

**Verification**
- `docs/evidence/v7_passc_mobile_measurements_2026-11-18.txt` covers 320/375/390/430 px × light/dark × 100%/200% text × 6 pages, with all disclosures expanded. It found no horizontal overflow, and the bottom navigation never covers the last content.
- axe-core 4.10.2 (WCAG 2.0/2.1/2.2 A/AA): 16 pages × 3 widths × 2 schemes, **0 violations**. Full keyboard reach on Home, Sectors and a sector page.
- `docs/evidence/v7-passc-screenshots/`:
  - all five experiences at 390 px, both initial-viewport and full-page;
  - Home with all sections expanded and a full-page sector page;
  - Home and Sectors in dark mode;
  - Home at 320 and 430 px;
  - desktop at 1280 px.
- Tests: 509 OK. Site tests were updated for the new structure, and new tests check:
  - no tables on Home;
  - three disclosures on Home;
  - previews link to the canonical pages;
  - each sector is listed once, with no duplicate chart;
  - there are no skill/ranking metrics on Forecast.

**30-second test (390 px, first screen and one scroll)**
1. *What is the economy doing?* "Expanding" and the gauge are visible on the first screen without scrolling.
2. *Where is it heading?* The first screen shows the three horizon rows: two say "Not enough evidence" and one says "About 30%, typical vs 28% average". The third row sits at the fold.
3. *Where should I research?* Four named sectors, each with recent strength, appear after one scroll and end at 1.7 screens.
4. *Can I trust it?* "1 of 12 outlooks pass our reliability test" links to Track Record.

Limits: automated checks and a self-evaluation only. Real-device and screen-reader testing by a person is still outstanding.

## Pass C — M5 integration and M6 release preparation (2026-11-18)
- **M5:** `scripts/v7_release.py` is wired into the Monthly assessment (build, gate, manifest) and the Milestone 1 daily publisher (promote, preserve or leave V6, then verify live). Tests: `tests/test_v7_release.py` (14). The new `V7 Release Rehearsal` workflow exercises the whole path on real data and never deploys.
- **Real-data evidence:**
  - monthly run 44307600691 at code commit `d57358d` gave `NEW_QUALIFIED`;
  - rehearsal run 44307784658 passed every stage: promote, contract, live verify, preserve, old-bundle notice, fail-closed, rollback bundle.
- **Defects found and fixed in M6:** Pages 503 handling (bounded retries); tab labels clipped at 200% text; the wrapped tab bar covering content (now sticky); focus clearance (scroll padding).
- **Release candidate:** `docs/V7_RELEASE_CANDIDATE.md`; screenshots in `docs/evidence/v7-rc-screenshots/` (31, from the actual pipeline output); runbook and owner checklist.
- **Unverified (needs a person):** real devices and safe area; VoiceOver and TalkBack; plain-language review.
- **Not merged, not deployed.**

## Market-vulnerability correction (2026-11-18)
- **Research:** see `docs/V7_CRASH_RESEARCH_REPORT_2026-11-18.md`. The study was pre-registered and run in CI (44314037141). Single warning signals have modest records (1.3–2.3×, with many misses), and every combined model failed the gate, so it is unpublished.
- **Implementation (P1–P4):**
  - Home leads with "How vulnerable is the stock market to a major decline?": six tested warnings with dates, status and records; what is concerning and reassuring; what would change the view; what cannot be predicted.
  - A new Market Risk page and data-driven charts.
  - Economy becomes supporting context.
  - Market data enter the monthly V7 gate, which checks freshness and writes the manifest.
  - Invalid candidate bundles are now rejected without blocking deployment.
- **Evidence:**
  - monthly run 44326670757 (`NEW_QUALIFIED`, code `c70d48a`);
  - rehearsal 44326671926 (all stages pass);
  - research run 44326671198;
  - 532 tests;
  - layout sweep 0 problems;
  - axe: only position-dependent `target-size` findings;
  - 38 screenshots in `docs/evidence/v7-rc-screenshots/`.
- **Not merged, not deployed.**
