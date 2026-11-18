# V7 pre-registration — market-crash vulnerability research

**Registered:** 2026-11-18, before any results were computed. **Code:** `scripts/v7_crash_research.py`. **Run:** CI only (`V7 Forecast Research` workflow), because the data sources are not reachable from the development container.
**Purpose:** answer the project's original question — *how vulnerable is the U.S. stock market to a major decline?* — with historically tested evidence. This is research: nothing here is published on the site until it passes the gate below and the owner approves.

## Market and targets
- **Market:** Kenneth R. French Data Library U.S. total market (Mkt-RF + RF), **daily** total-return index from 1926-07 (monthly origins use month-end levels). It is consistent over the whole history and freely licensed for research with attribution. FRED S&P 500 and Nasdaq series are used for *current* conditions only (S&P 500 history on FRED covers about 10 years).
- **Bear market (episode list):** a peak-to-trough decline of **20% or more** on the daily index before the previous peak is regained. **Crash** = a bear market of 30% or more.
- **Primary target (T12):** from the month-end at origin *t*, the daily index falls **20% or more below the origin level at any time within the next 12 months.** Label known 12 months later.
- **Secondary target (T6):** the same within 6 months.

## Signals (point-in-time; thresholds fixed in advance, not fitted)
| Signal | Rule (warning when true) | Lag | History |
|---|---|---|---|
| Yield curve | 10-year minus 3-month Treasury (GS10 − TB3MS) below 0 in any of the past 12 months | 0 | 1953– |
| Credit stress | BAA − GS10 spread ≥ 2.5 points, or widened ≥ 0.5 points over 6 months | 0 | 1953– |
| Labour | 3-month average unemployment ≥ 0.5 points above its prior-12-month low | 1 | 1948– |
| Valuation | Shiller CAPE at or above the 80th percentile of its own history to date | 1 | 1881– (if the source is available) |
| Trend break | Market below its 10-month moving average | 0 | 1926– |
| Weak breadth | Fewer than 40% of the 49 French industries above their own 10-month averages | 0 | 1926– |
| Euphoria | Trailing 12-month market return ≥ 30% | 0 | 1926– |
| Rate shock | 3-month Treasury bill up ≥ 2 points over 12 months | 0 | 1934– |
| Financial conditions | Chicago Fed NFCI above 0 (tighter than average) | 0 | 1971– (descriptive only; too short for the main model) |

## Model
- Logistic regression (the existing V7 engine code: `fit_logistic`, L2 = 1) on: curve minimum over 12 months, BAA − GS10 level, its 6-month change, unemployment rise from 12-month low, CAPE percentile (to date), trend gap (market ÷ 10-month average − 1), breadth share, 12-month bill change.
- Expanding window, re-fitted every 12 months, trained only on origins whose 12-month outcome was known at the forecast date. First forecast after 120 labelled months; evaluation origins 1965-01 onward. No recalibration step in this first test.
- **Gate (unchanged from V7):** Brier skill vs base rate ≥ 0.05, AUC ≥ 0.70, at least 3 independent episodes, overconfidence ≤ 0.20. If it fails, the result is "not enough evidence" and is reported as such.

## Reporting (whatever the result)
- Every bear market since 1926 with peak, trough, depth and duration.
- For each signal: warning frequency, hit rate when warning vs base rate (lift), bear markets with a warning in the 12 months before the peak (caught vs missed), share of warning months not followed by a 20% decline (false alarms), and median lead from first warning to the peak.
- Model: out-of-sample skill, AUC, calibration table, overconfidence; full sample and excluding the 2020 shock window.
- Current values of every signal with observation dates. Missing or delayed data are named, never filled.

## Known limitations (stated in advance)
- About 15–20 bear markets since 1926 means wide uncertainty; monthly origins overlap, so they are not independent.
- Macro series are current-vintage (revisions); market prices are not revised.
- CAPE comes from Robert Shiller's public data; if it cannot be fetched reproducibly, valuation is reported as missing rather than substituted.
- No earnings-revision, margin-debt or market-breadth (advance/decline) data are freely licensed for redistribution; they are reported as gaps.
