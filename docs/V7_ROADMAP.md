# Economic Cycle Research — Version 7 Roadmap

**Status:** IN DEVELOPMENT on `v7-development`. Pass A (M1 + M2) complete; **Pass B (M3 + M4) complete** — see `docs/V7_PROGRESS.md`. Next: Pass C (M5 integration + M6 release preparation).
**Production baseline:** V6.3, `main` merge commit `7dfc811e765fd8ca927f082c2fa0c63948799bb3`. It stays production and the rollback target until the owner explicitly approves a V7 merge.
**Operating rule:** DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.

## Objective
Turn the descriptive V6.3 dashboard into an accessible, forward-looking economic and investment-sector intelligence application that an ordinary investor can understand. V7 serves two goals equally:
1. **Anticipate the direction of the economic cycle** at 3-, 6- and 12-month horizons, with honest uncertainty.
2. **Translate that outlook into evidence-based sector research** for all 11 GICS sectors, without unsupported rankings or advice.

## Non-negotiable safeguards (apply to every milestone)
- **No lookahead.** Every historical forecast uses only data that would have been available at the forecast date, with an emulated publication lag. Targets such as NBER dates are used to score, never as inputs.
- **No fabricated data or false precision.** Missing observations stay missing. Probabilities are published only where out-of-sample evaluation supports them, and they are rounded to a precision the evidence justifies.
- **Explicit insufficient-evidence state** for every outlook and sector rating that fails its evidence gate.
- **No unsupported recession probabilities or investment recommendations.** Investment attractiveness requires qualified valuation, earnings and relative-return sources.
- **Preserve V6.3 protections:** monthly gates, stale-data withholding, manifest stamping, last-accepted publication, `main`-only deployment and the rollback runbook.
- **Reproducibility:** dated data snapshots with source provenance; deterministic, dependency-free code (standard-library Python, like the existing pipeline); tests with every change.
- **Honest track record:** report failures, false alarms and missed turns alongside successes. Separate pandemic-type shocks.

## Milestones

### M1 — Research and forecasting foundation
**Deliverables**
- Inventory of existing data infrastructure and reuse decisions (FRED fetcher, monthly pipeline, V6.3 rubric and replay).
- Qualified historical inputs from the official FRED API: Treasury 10-year (GS10) and 3-month (TB3MS) yields, BAA corporate yield (market data, not revised), unemployment (UNRATE), CPI, industrial production, payrolls (PAYEMS), initial claims (ICSA), and the NBER recession indicator (USREC, target only).
- A dated, provenance-stamped data snapshot committed for offline reproducibility, refreshed by the V7 research workflow.
- Forecast-target definitions for 3, 6 and 12 months, with written rationale.
- A point-in-time panel builder with per-series publication lags and tests proving no future values enter a forecast.
- Baselines: historical base rate (climatology), current-state persistence, and the V6.3 descriptive rubric.

**Acceptance:** targets and lags documented; the panel builder passes lookahead tests; the snapshot carries source URLs and its retrieval run; baselines are computed by the same evaluation harness.

### M2 — Forward-looking economic engine
**Deliverables**
- A transparent, dependency-free probability model (regularised logistic regression on a small, pre-declared feature set) for each target and horizon.
- Expanding-window, chronological out-of-sample evaluation: re-fit each month using only past data, with a gap equal to the horizon so training outcomes are known at the forecast date.
- Metrics: Brier score, Brier skill score against the base rate and against persistence, AUC, calibration by bucket, hits and misses at the published threshold, per-episode lead and lag. The 2020 shock is reported separately.
- **Publication gate** per target and horizon. Publish only if, out of sample:
  - Brier skill score versus the base rate is at least 0.05;
  - AUC is at least 0.70;
  - at least 3 independent positive episodes were evaluated;
  - calibration does not show systematic overconfidence.
  Otherwise the published state is **Insufficient evidence**.
- A current outlook artefact (JSON) carrying the gated state, a plain-language band, the evidence behind it and the track-record summary.
- A historical forecast archive: the month-by-month out-of-sample forecasts, kept for future performance tracking.

**Acceptance:** results reproducible from the snapshot; real-data evaluation run in CI; every published claim traceable to gate evidence; failures documented.

### M3 — Investment sector intelligence
**Deliverables**
- A framework for all 11 GICS sectors scoring economic sensitivity (linked to the M2 outlook), valuation, earnings, relative strength and risk, each from qualified, dated sources.
- A strict distinction between **macro exposure** and **investment attractiveness**. Attractiveness stays **Insufficient evidence** unless valuation, earnings and relative-return evidence pass the gate.
- Historical testing of any sector-tilt claim against benchmark-relative returns, with transaction-cost and survivorship notes, before publication.

**Acceptance:** all 11 sectors covered; source links; fail-closed tests; no unsupported ranking.

### M4 — Human-first interface transformation
**Deliverables**
- A redesigned, mobile-first site built around:
  1. an economic-cycle visual ("where we are");
  2. the forward outlook with uncertainty ("where we're heading");
  3. sector discovery ("where to look");
  4. the track record ("how we've done");
  5. a Research & Data section holding all methodology and evidence.
- Plain language, clear graphics, one canonical location per feature, WCAG 2.2 AA.

**Acceptance:** responsive 320–1440 px; axe-core zero violations; plain-language review; each feature in exactly one place.

### M5 — Integration, accuracy and reliability
**Deliverables**
- Integration with the existing daily and monthly pipelines.
- Verification of data integrity, historical correctness, forecast evidence, sector research, accessibility, regression tests, deployment compatibility and rollback safeguards.

**Acceptance:** a full real-data monthly run and a daily-publisher compatibility check pass; the rollback procedure is verified.

### M6 — Release and evaluation
**Deliverables**
- A V7 release candidate with exact commit and workflow evidence.
- Documented outstanding human evaluation items.
- An owner evaluation checklist and explicit owner approval before merging into `main`.

## Dependencies
- M2 depends on the M1 data, targets and harness.
- M3's sensitivity component depends on the M2 outlook. Its attractiveness component depends on qualified market-data sources (owner decision on providers and licences).
- M4 depends on the M2 and M3 artefact contracts.
- M5 depends on M2–M4. M6 depends on M5.

## Execution passes
- **Pass A:** M1 + M2. Economic forecasting foundation and engine.
- **Pass B:** M3 + M4. Sector intelligence and the complete interface transformation.
- **Pass C:** M5 + M6 preparation. Integration, verification, release readiness.

## Definition of finished (V7)
1. A current economic-cycle assessment understandable to non-experts.
2. 3-, 6- and 12-month outlooks, each either evidence-supported with stated uncertainty or explicitly **Insufficient evidence**.
3. A tested, reproducible forecasting system with an honest historical track record.
4. Investment-sector intelligence covering all 11 sectors, with gated attractiveness.
5. A completely redesigned, mobile-first interface with a dedicated Research & Data area.
6. Historical forecast archives and future performance tracking.
7. V6.3 data-integrity, publishing and rollback protections preserved.
8. Passing automated tests and real-data verification.
9. A release-ready candidate with exact commit and workflow evidence, and owner approval before merge.

Any failed gate means V7 is IN PROGRESS.

## Progress log
See `docs/V7_PROGRESS.md`.
