# V7 market-crash research correction — findings and plan

**Date:** 2026-11-18 · **Branch:** `v7-development` · **Status:** research report for the owner's decision. Nothing on the site was changed. V7 is not merged and not deployed.
**Evidence:**
- Pre-registration: `docs/V7_PREREGISTRATION_CRASH_RESEARCH.md`, committed before the results existed.
- CI run `44314037141`: full suite, fetch and analysis.
- Results: `docs/evidence/v7_crash_research_2026-11-18.json`.
- Dated data snapshot (54 files, SHA-256 verified from the CI log): `data/v7_crash/`.
- The analysis reproduces exactly from that snapshot (`scripts/v7_crash_research.py analyze --data data/v7_crash`).

## Answer in brief
1. **"Expanding" is correct about the economy, but it answers a different question.** It is computed from two economic readings (industrial-production growth and the 3-month change in unemployment). No market, valuation, credit or liquidity data enter it, so it cannot speak to stock-market vulnerability.
2. **Current market evidence complicates the picture.**
   - Since mid-October the Nasdaq Composite has fallen 7% and is 12% below its high. The Nasdaq-100 is 13.5% below its high, and both are now below their 10-month averages.
   - The VIX volatility index is 22.9, up 51% in 3 months.
   - Small companies have lagged large ones over 3 months (−5.5% vs +3.2%, to September), and leadership is narrow: the hardware industry is up 88% in 12 months.
   - The equity value of non-financial companies relative to GDP is at its highest level since 1947.
   - Commodities are up 33% in a year, energy 63% and copper 45%.
   - Consumer sentiment is at the 0.3rd percentile of its history.
3. **Historical crash research:**
   - **Several individual signals have modest, real historical value.** A recent yield-curve inversion, a market trend break, weak industry breadth and tight financial conditions each raised the frequency of a later 20% decline 1.5–2.3×.
   - **Every signal missed many bear markets.**
   - **A combined probability model fails the out-of-sample test decisively**, with negative skill and AUC 0.48–0.59.
   - A published crash probability is therefore not supported. A transparent "vulnerability" view built from individually tested warnings, with their track records, is supported.
4. **Recommendation:** correct the product hierarchy within the existing V7 architecture, as P1–P4 below, before the owner approves V7. The headline becomes market vulnerability, with economic conditions as supporting context.

---

## Pass 1 — Why the model says "Expanding / Firming"
**Code:** `scripts/v63_interpretation.py` (`interpret`, `classify_*`), called by `scripts/v7_site.py:current_assessment`, with data assembled by `scripts/v63_historical_replay.py:assessment_at`.

| Input | Series | Latest used | Value | Rule | Result |
|---|---|---|---|---|---|
| Growth level | INDPRO, 12-month log change | 2026-09 | **+2.12%** (fresh data; +2.22% before revision) | ≥ +0.5% means expanding | expanding |
| Labour | UNRATE, 3-month change | 2026-09 | **0.00 pp** (4.2%) | ≥ +0.3 deteriorating; ≤ −0.2 improving | stable |
| Condition | (growth, labour) lookup table | | | expanding + stable | **Expanding** |
| Direction | INDPRO 12-month growth now minus 3 months earlier | 2026-09 | **+0.66 pp** (fresh; +0.77 before revision) | ≥ +0.5 means strengthening | **Firming** |
| Inflation | CPI 12-month change | 2026-09 | 3.65%, +0.24 over 3 months | commentary only | "elevated, stable" |
| Unemployment rise from 12-month low | UNRATE, 3-month average | — | **unavailable** | ≥ 0.5 is a warning | cannot run: October 2025 was never published (federal shutdown) |

- **Weighting:** none. The rubric uses fixed thresholds and a lookup table. Growth and labour decide the condition; production momentum decides the direction.
- **Revisions and staleness:**
  - INDPRO was revised between the snapshot and today's fetch. "Firming" now rests on +0.66 against a 0.5 threshold, so it is fragile.
  - With October production (+2.13%, momentum +0.89) the call is still Expanding/Firming. However, the site cannot use October at all: October 2025 CPI was never published, so October 2026's 12-month inflation is uncomputable and the whole assessment falls back to September.
- **What it does not represent:** stock prices, drawdowns, breadth, concentration, valuations, earnings, commodities, credit spreads, lending, financial conditions and liquidity. None are inputs.
- **What it establishes:** U.S. production is growing and unemployment is stable. That is *economic activity*.
- **What it does not establish:** anything about stock-market vulnerability. Historically, markets have fallen 20% or more during expansions (1987, 1998, 2018 and 2022 began with production growing).

## Pass 2 — Current market conditions (CI fetch on 2026-11-18)
All figures come from the snapshot. "Pctile" is the percentile of the series' own history on FRED; for short histories it means little and is flagged.

| Area | Evidence (date) |
|---|---|
| **Stock prices** | **Nasdaq Composite** (11-17): 1 month −6.9%, 3 months −7.5%, 6 months −6.0%, 12 months +7.1%; **−11.9% from its high**; −3.0% vs its 10-month average. **Nasdaq-100**: 1 month −7.5%, 12 months +8.9%; **−13.5% from its high**; −3.7% vs its 10-month average. **Dow** (11-17): 1 month −2.4%, 12 months +9.0%, −6.6% from its high, at its 10-month average. **S&P 500** (11-16): 1 month −3.2%, 3 months −4.2%, 6 months +0.2%, −5.2% from its 52-week high. (FRED now provides only about one year of S&P 500 history, so no 12-month change.) **U.S. total market** (French, to 09-30): 12 months +14.7%, −2.3% from its high. |
| **Volatility** | VIX 22.9 (11-16), up 51% in 3 months; 76th percentile since 1990 |
| **Small vs large** | Russell 2000 is not available on FRED. French size deciles (to 2026-09): smallest 10% −5.5% over 3 months vs largest 10% +3.2%; over 12 months, +19.0% vs +14.7% |
| **Breadth and leadership** | 40.8% of the 49 industries are above their 10-month averages (warning threshold 40%). 67% have positive 12-month returns. Leaders over 12 months: Hardware +88%, Machinery +58%, Lab equipment +48%, Oil +44%, Chips +43%. Laggards: Entertainment −33%, Apparel −24%, Medical equipment −16%. Advance/decline breadth and index concentration data are not freely licensed. |
| **Valuation** | Equity value of non-financial corporations ÷ GDP = **2.55, the highest since 1947** (2026-Q2; Federal Reserve Z.1). **Shiller CAPE: not current.** The public mirror stops at 2023-09 (30.8, 95th percentile then). Damodaran's January vintage gives a market forward P/E of 27.7. |
| **Earnings** | Corporate profits after tax (NIPA) +26.6% year on year, a record (2026-Q2). S&P earnings and analyst revisions are not freely licensed, so they are unavailable. |
| **Credit** | BAA − 10-year spread 1.50 (11-16), very tight (6th percentile since 1986). High-yield spread 3.34, **up 24% in 3 months** (FRED holds only 3 years of history). Chicago Fed NFCI −0.46 (loose); credit and leverage subindexes near average. Banks' lending standards for business loans: slight net tightening (1.7%). Business loans +11% year on year. |
| **Rates and liquidity** | 10-year Treasury 5.12%, +1.0 points in a year. Yield curve: 10-year minus 3-month +0.77, 10-year minus 2-year +0.30 (not inverted in the past 12 months). Fed funds 3.88%. M2 +5.7% year on year. Fed overnight reverse repo near zero (drained). Reserves +3.4%. |
| **Commodities** | IMF all-commodities +32.8% year on year (98.6th percentile since 1992); energy +62.8%; metals +23.5% (99.8th percentile); copper +44.8% (record). WTI $89.6 (11-11), +47% year on year. |
| **Economy** | Industrial production +2.1% year on year (Oct). Payrolls +0.6% year on year. Unemployment 4.1% (Oct). Initial claims 200k (3rd percentile, very low). Chicago Fed activity index +0.07. Sahm real-time indicator 0.0. Real GDP +2.1% year on year. Consumer sentiment **48.1 (0.3rd percentile)**. Building permits −3% year on year. |

**Delayed or unavailable:**
- French data end 2026-09, so they miss the October–November selloff.
- CAPE is stale (2023-09).
- S&P earnings and revisions, margin debt, advance/decline breadth, current Russell 2000 data and a licensed equal-weight S&P 500 are unavailable.
- The high-yield spread has only a short FRED history.
- October 2025 CPI and unemployment were never published.

**Reading.** The economic data say "expanding". The market data show a technology-led correction under way (Nasdaq about −12%), rising volatility, narrowing breadth and small-cap lag, alongside record valuation by the equity/GDP measure. Credit spreads remain tight and financial conditions loose, though high-yield spreads are starting to widen. That divergence is exactly what the current homepage cannot show.

## Pass 3 — Historical crash research
**Existing repository research (reviewed):**
- `ENDOGENOUS_CRASH_THRESHOLD_RESEARCH` (design: targets, mechanisms, counterexamples).
- A workbook snapshot of 8 crashes with yield-curve, credit, CPI and labour values at each (retrospective, not point-in-time).
- The endogenous/external event classification.
- Nasdaq and housing deviation, credit-growth and multifactor comparisons (descriptive).
- The valuation-gap transform (built, but unpopulated for lack of licensed earnings yields).
- The earlier usability test, which scored the wrong target (future market *peaks*) and found no discrimination.

None of this was an out-of-sample test of crash warnings. The new work below closes that gap.

**Target:** the French daily U.S. total market (1926–2026). **16 bear markets of 20% or more**, of which **7 were 30% or more**: 1929, 1946, 1957, 1962, 1966, 1968–70, 1973–74, 1981–82, 1987, 1990, 1998, 2000–02, 2007–09, 2018, 2020 and 2022. A 20% decline within 12 months followed **15.4%** of month-ends; within 6 months, 9.3%.

**Individual signals:** thresholds were fixed in advance and computed point in time. Lift is the hit rate when warning ÷ the base rate.

| Signal (history) | Warning share | 20% decline within 12 months: warning vs not | Lift (12m / 6m) | Bear markets caught / missed | Median lead |
|---|---|---|---|---|---|
| Yield curve inverted, past 12m (1954–) | 24% | 27% vs 7% | **2.3 / 2.0** | 5 / 9 | 12 months |
| Trend break, below 10-month average (1927–) | 28% | 29% vs 10% | **1.9 / 2.2** | 8 / 8 | 9 months |
| Weak breadth, <40% of industries above trend (1927–) | 23% | 27% vs 12% | **1.7 / 2.1** | 8 / 8 | 8 months |
| Financial conditions tight, NFCI > 0 (1971–) | 30% | 19% vs 10% | **1.5 / 1.6** | 5 / 5 | 12 months |
| Credit stress (1953–) | 26% | 17% vs 10% | 1.4 / 1.8 | 3 / 11 | 12 months |
| Valuation extreme, CAPE ≥ 80th percentile (1927–2023) | 45% | 20% vs 12% | 1.3 / 1.1 | 11 / 5 | 12 months |
| Unemployment rising (1949–) | 24% | 12% vs 11% | 1.1 / 1.4 | 3 / 11 | 12 months |
| Rate shock (1935–) | 6% | 13% vs 13% | 1.0 / 0.2 | 3 / 12 | 6 months |
| Euphoria, 12-month return ≥ 30% (1927–) | 17% | 14% vs 16% | 0.9 / 0.9 | 10 / 6 | 10 months |

- **Lead times.** The yield curve and credit signals warn about a year ahead, with many misses and long false alarms. Trend and breadth warn later; they partly describe a decline already starting.
- **Valuation** is high in many decades; it says "fragile", not "when".
- **False alarms** are the norm: 71–83% of warning months were not followed by a 20% decline within 12 months.

**Combined model (pre-registered logistic regression, evaluated out of sample 1965–2025):**

| Model | Evaluation | Skill vs base rate | AUC | Overconfidence | Gate |
|---|---|---|---|---|---|
| 12 months, core signals | 1965–2025, 728 months, 14 episodes | **−0.35** | 0.53 | 0.73 | **Fail** |
| 6 months, core signals | 1965–2025 | −0.23 | 0.54 | 0.39 | Fail |
| 12 months, with CAPE | 1965–2023 | −0.31 | 0.59 | 0.77 | Fail |
| 6 months, with CAPE | 1965–2023 | −0.20 | 0.52 | 0.34 | Fail |

- Excluding the 2020 window makes the results worse, not better.
- Forecasts of 70% or more came true 11–17% of the time.
- The CAPE model said 82% in October 2023, and the market then rose.
- **Conclusion:** the data support neither a crash probability nor timing. They do support describing *how many historically informative warnings are active*, each with its record.

**Current values of the tested signals:**

| Signal | Status |
|---|---|
| Yield curve | **Off**: minimum +0.24 over 12 months |
| Credit stress | **Off**: 1.48, narrowing |
| Financial conditions | **Off**: NFCI −0.53 |
| Unemployment rising | **Unavailable**: shutdown gap; Sahm real-time 0.0 |
| Trend break | **Off on the total market to September (+5.7%). On for the Nasdaq and Nasdaq-100 in November (−3.0%, −3.7%).** Dow at its average |
| Weak breadth | **Borderline**: 40.8% vs the 40% threshold (September) |
| Valuation | CAPE **stale**; equity/GDP at a record. The equity/GDP measure is not yet back-tested |
| Euphoria | Off (+14.7%) |
| Rate shock | Off |

## Missing signals, in priority order
1. **A current, licensed valuation series with history.** Options are an official Shiller CAPE conversion, or the equity/GDP ratio (Z.1, 1945–) tested point in time with a roughly 3-month publication lag.
2. **Market breadth and concentration from a licensed source.** These are advance/decline, the share of stocks above trend, and the top-10 weight. Interim proxies are the French industries and size deciles.
3. **Earnings growth and revisions** (licensed; S&P or FactSet). Interim proxy: NIPA corporate profits.
4. **Leverage:** margin debt (FINRA, monthly) and the household and corporate leverage in Z.1.
5. **High-yield spread history.** FRED now truncates the ICE data, so BAA − 10-year is the long-history substitute.
6. **Daily, current-market inputs in the pipeline** (Nasdaq, Dow, VIX), so trend and drawdown are not delayed 1–2 months by the French release lag.
7. **Episode-level evaluation and a warning-count composite.** These should be pre-registered before testing.

## Pass 4 — Implementation plan (existing V7 architecture, no V8)
These are ordered by value and risk. Each step keeps the evidence gates: no crash probability unless one passes the gate.

| # | Change | Where | Effort |
|---|---|---|---|
| **P1** | **Correct the homepage hierarchy.** The lead question becomes "How vulnerable is the stock market to a major decline?". Answer it with **N of 6 tested warnings active** (curve, trend break, breadth, credit stress, financial conditions, valuation). Each shows its current value and date, its historical lift and its misses. Plain status words ("few / several / many warnings") are used, with no probability. Below it sit "What would raise vulnerability" (each warning's trigger) and "What would reduce it". The economic cycle moves to a supporting card. | `v7_site.py` (Home and a new "Market risk" section), evidence JSON | Medium |
| **P2** | **Stock-market, credit and liquidity panels.** Index returns and drawdowns (Nasdaq, Dow, S&P 500), VIX, size and industry breadth, leadership, credit spreads, NFCI, lending and liquidity, each dated. Descriptive daily data, labelled as such. | `v7_site.py`, data from `v7_crash_research.py` | Medium |
| **P3** | **Pipeline integration.** Add the crash-research fetch and analysis to the monthly assessment, and gate it like V7: fresh inputs, plus manifest fields for the warnings. Daily runs refresh only the market panel data, keeping monthly conclusions. Fix the shutdown artefact by letting each pillar use its own latest month, never imputing. | `v7_release.py`, monthly workflow | Medium |
| **P4** | **Historical charts.** A 1926–2026 drawdown chart with bear markets and recessions marked; a warning timeline (which signals were on before each bear market); and a divergence chart of production growth against market drawdown. | `v7_site.py` (inline SVG) | Small–medium |
| **P5** | **Research stage 2 (pre-register first).** A warning-count composite tested out of sample at episode level; equity/GDP valuation tested point in time; Nasdaq-specific targets; a licensed CAPE or breadth source if the owner approves. Publish only what passes. | `v7_crash_research.py` | Medium |
| **P6** | **Owner decisions.** Licensing for valuation, breadth and earnings data (also listed in `V7_MARKET_DATA_PROVIDERS.md`); whether V7 approval waits for P1–P4 (recommended) or ships now and corrects afterwards. | — | — |

**What stays unchanged:**
- The economic outlook gate. The 12-month job-market outlook remains the only published number.
- Sector research (attractiveness stays unrated).
- The release, preserve and rollback machinery from M5.

## Limitations
- There are 16 bear markets in 100 years, and overlapping monthly origins are not independent, so uncertainty is wide.
- Macro data are current-vintage.
- The CAPE source is a third-party mirror, stale after 2023-09.
- The French market data lag by 1–2 months.
- Signal thresholds were set in advance but by convention, not optimised. That is deliberate, but other reasonable thresholds would give somewhat different numbers.
