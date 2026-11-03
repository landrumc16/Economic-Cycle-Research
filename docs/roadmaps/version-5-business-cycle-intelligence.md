# Version 5 — Business-Cycle Intelligence & Forecasting Dashboard

Status: V5 DESCRIPTIVE/HISTORICAL RELEASE VERIFIED — CURRENT-DATA AND FORECAST APPROVAL WITHHELD
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

## November 3, 2026 release checkpoint
- Existing monthly pipeline includes historical phase estimation, retrospective episode and 3/6/12-month diagnostics, an explicitly blocked numerical forecast gate, executive brief, descriptive dashboard and unified landing page.
- A separate integrated acceptance gate now checks artifact presence, agreement between release statuses, stale-data handling and forecast restrictions.
- Monthly workflow retains its day-20 schedule and is configured to run on relevant pushes to main, reducing manual dispatches.
- **Not yet accepted:** GitHub Actions success and artifact rendering have not been verified. A commit alone is not release evidence.
- The Google Sheets promotion snapshot remains dated/unreviewed; automated authenticated workbook synchronization and daily/weekly cadence verification remain limitations. No live macro approval or numeric recession forecast may be inferred.
- Next action: inspect an actual run and artifacts, repair only release-blocking failures, then record the verified run and formal closeout.

## Verified release evidence — 2026-11-03
- GitHub Actions: https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41686229400 — descriptive job completed successfully on main at commit fd44328c62f1e6fbfb1990d4a0c5ec22c69ca023. All reported unit/regression, historical analysis, monthly assessment, dashboard, and acceptance steps succeeded.
- Artifact ID 13253584340, `industry-deviation-descriptive-evidence`, 86 files, SHA-256 `5b6b9074cf1d465a5ffeab187d69c1a38530a99fcbb7d082674ee86e97443f62`; downloaded and inspected.
- `v5_integrated_acceptance.json`: `V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED`; `weekly_release_acceptance.json`: `STALE_RESEARCH_ONLY`; 546 historical months and 9 dashboard metrics. HTML/JSON dashboards, brief, portal, forecast gate and status files exist.
- Common observation month 2026-08, assessment date 2026-11-03. Source workbook snapshot 2026-11-01 is unreviewed, workbook reconciliation `NOT_RECONCILED`, and UNRATE/CPIAUCSL/GDPC1 promotion `BLOCKED`. This release is descriptive/historical only; it does not certify a current cycle state or numerical crash/recession probabilities.
- Monthly workflow is automated on relevant main pushes and day-20 schedule. Daily refresh status `NOT_RECONCILED` and weekly outlook `DESCRIPTIVE_ONLY` are recorded operational limitations; their separate schedules, fresh workbook reconciliation, and independent live end-to-end runs have not been verified here. Do not claim these cadences operational from this monthly run.
- The artifact HTML was inspected for presence and structure, but browser visual rendering and a public hosted dashboard URL are not independently certified. The workflow artifact is the verified distribution channel.
- **Disposition:** V5 research-only artifact release verified; full operational acceptance remains open pending daily/weekly cadence verification, current workbook source-promotion reconciliation where applicable, and browser/deployment verification. Forecast approval is a separate future gate, not a prerequisite to publishing explicitly research-only outputs.

## Final integration safeguards — 2026-11-03
- The portal now surfaces separate daily, weekly, and monthly evidence states, rather than implying the verified monthly workflow proves the other schedules ran.
- Workbook snapshot review state is displayed beside its date and source-promotion status, with a collapsible methodology panel. Regression coverage checks the cadence disclosures and responsive markup.
- These changes postdate the verified monthly run 41686229400. A fresh run on the latest main commit is necessary to verify this exact revision; prior CI evidence must not be reused as proof of later changes.
- Full operational closure is not asserted. Remaining limitations are explicit: separate daily/weekly executions not independently evidenced, no live authenticated Sheets synchronization, unreviewed macro promotion snapshot, stale common observation month, no certified numeric forecasts, and no independent hosted/mobile browser test.
