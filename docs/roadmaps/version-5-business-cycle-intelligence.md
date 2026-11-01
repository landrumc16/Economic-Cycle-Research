# Version 5 — Business-Cycle Intelligence & Forecasting Dashboard

Status: APPROVED ROADMAP / IMPLEMENTATION PENDING
Date: 2026-11-01

## Objective
Extend the technically validated V4 monthly research pipeline to estimate business-cycle conditions, evaluate 3/6/12-month outcomes, and publish a transparent executive summary and integrated dashboard. Do not rebuild V4 or wait for new monthly releases to test the product.

## Scope and principles
- Monthly U.S. assessment, run on the existing day-20 workflow.
- Develop using latest complete historical common-month observations (currently 2026-08 in the verified 2026-11-01 run); support an explicit historical as-of date.
- Preserve strict distinction between retrospective research, model estimates, and approved current assessments.
- Never present current-vintage revised FRED data as point-in-time backtesting. Historical simulation must avoid future-row leakage; where release-time vintages are unavailable, label limitations and do not claim live predictive validity.
- Avoid causal claims, unsupported crash probabilities, investment advice, and uncalibrated numeric confidence.
- Keep model simple, interpretable, testable, and modular. Reuse existing data acquisition, historical timeline, dashboard and acceptance gates.
- Avoid feature creep, cosmetic refactors, and mass renaming legacy weekly filenames.

## Milestones
1. **Reference and label specification**: Define observable cycle states and outcomes. Establish reference chronology (e.g., NBER recession intervals), turning-point conventions, indicator availability, historical coverage, and non-overlapping evaluation windows. Explicitly distinguish an ex-post reference label from an observable real-time phase estimate.
2. **Current-state estimator**: Transparent growth/labor/inflation/credit/housing/markets features and deterministic phase mapping (recovery, expansion, late-cycle, contraction, or uncertain). Explain supporting/conflicting indicators and missingness. Validate on historical periods without future-row leakage.
3. **Forward outlook**: Separate 3-, 6-, and 12-month outcome definitions (e.g., contraction/recession occurrence or state transition); establish base-rate benchmark; train/evaluate using expanding-window temporal splits with embargo where labels overlap. Publish probabilities only if calibrated and sufficiently supported; otherwise use qualitative outlook and disclose insufficient validation.
4. **Historical validation**: Check recession/expansion episodes, false positives, misses, lead times, Brier/log loss and calibration against baseline where applicable, sensitivity to threshold choices, source revisions, and small event counts. Produce machine-readable validation report and fail-closed acceptance gate.
5. **Executive summary**: Deterministic evidence-grounded narrative: assessment month, estimated phase and uncertainty, outlook at three horizons, principal drivers, disagreements, month-over-month change, and methodological caveats.
6. **Integrated dashboard**: Extend existing self-contained HTML dashboard with phase/outlook, indicator explanations, historical performance, executive summary, freshness and research-only status. No fabricated values. Continue to produce portable JSON/HTML artifacts.
7. **CI and acceptance**: Add unit/integration/regression tests, historical-as-of fixtures, missing/stale-data cases, reproducibility checks, artifact checks, and workflow integration. Verify a real Actions run and inspect generated evidence before formal V5 closure.

## Release rules
- **HISTORICAL_RESEARCH_ONLY**: valid retrospective model output, never an approved current estimate.
- **STALE_RESEARCH_ONLY**: current run with stale common-month observations; dashboard may display explicitly dated historical estimates but not represent them as current.
- **INSUFFICIENT_MODEL_VALIDATION**: uncalibrated/unsupported phase or probability outputs must not be presented as validated forecasts.
- **PASS**: all tests, artifact checks, freshness, completeness and relevant model validation gates pass. Current-vintage data limitations remain clearly disclosed.

## Definition of done
- One reproducible CLI path from source data through classification, outlook, narrative, and dashboard.
- Working historical as-of example using existing data; no new release dependency.
- Explicit 3/6/12-month results, with numerical probabilities gated by calibration and historical event sufficiency.
- Backtest and limitations published; deterministic fixtures and automated regression tests pass.
- Monthly workflow produces JSON/HTML/summary artifacts and accurately reports its gate.
- Completed CI run and artifact contents independently inspected; closeout committed to GitHub.

## Work order
Implement milestones 1–4 before styling the dashboard; then 5–7. Prefer substantial vertical slices and avoid repeated approval requests for minor decisions.
