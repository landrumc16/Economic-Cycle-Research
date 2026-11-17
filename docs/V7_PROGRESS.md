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
