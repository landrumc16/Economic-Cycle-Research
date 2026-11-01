# Unified Economic Research Pipeline — V5 Integration Contract

Status: APPROVED IMPLEMENTATION BOUNDARY (not evidence of data validation)
Date: 2026-11-01

## Systems and authority

- **Google Sheets research workbook:** `SEM_Historical_Crash_Research_v1` (Drive ID `1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE`). Owns manually reviewed source-verification, vintage, and promotion evidence. Relevant tabs: `SOURCE REGISTRY`, `SOURCE VERIFICATION LEDGER`, `DATA PROMOTION GATE`, `DATA REFRESH STATUS`, `CURRENT RISK INPUTS`, `INTEGRATED CYCLE`.
- **GitHub Economic-Cycle-Research:** owns reproducible ingestion, transformation, tests, retrospective diagnostics, release artifacts, and the V5 HTML dashboard.
- Neither system may silently overwrite the other's eligibility decisions. A GitHub successful run does **not** imply that the Sheet's source-promotion gate passed. A staged or verified observation does **not** imply a vintage-certified predictive input.

## Three distinct cadences

1. **Daily source refresh:** Check official release dates, ingestion success, source timestamps, missing observations, revisions, and pending feeds. Append an auditable change record; zero new observations is a valid result. No forecast release.
2. **Weekly outlook:** Summarize verified economic observations and upcoming official releases. Explicitly distinguish descriptive commentary from the unvalidated model. No manufactured probabilities, crash dates, or sector rankings.
3. **Monthly cycle assessment (20th):** Run the GitHub workflow, historical phase diagnostics, 3/6/12-month benchmark, release gates, executive brief, and dashboards. Current-cycle claims remain blocked if data freshness or source eligibility fails.

## Eligibility and schema

Each series must retain: `series_id`, `publisher`, `source_url`, `observation_date`, `release_date` (if known), `retrieval_date`, `value`, `unit`, `revision_or_vintage_id` (if known), `publisher_crosscheck_status`, `vintage_review_status`, `promotion_status`, and `evidence_reference`.

Promotion requires publisher verification, historical-vintage review, documented gaps, and passing transformation QA. Preserve original missingness; do not interpolate missing October 2025 unemployment/CPI observations. For point-in-time tests, use only releases available at each historical decision date. Revised series remain labeled `RETROSPECTIVE_ONLY`.

## Current reconciliation (2026-11-01)

| Dimension | Google Sheet | GitHub | Unified policy |
| --- | --- | --- | --- |
| UNRATE / CPIAUCSL / GDPC1 canonical promotion | All 3 BLOCKED in `DATA PROMOTION GATE` | Retrospective FRED-derived indicators available for some series | Keep canonical promotion blocked until evidence reviewed |
| Daily refresh | 12 registry feeds, 9 categories reviewed Nov 1; no new imports | Scheduled monthly workflow, not daily | Keep daily status distinct from monthly CI |
| Current cycle | `INTEGRATED CYCLE` says expansion-like heuristic, NOT PUBLISHED | V5 latest phase heuristic, historical research only | No approved current phase |
| Forecast probabilities | Unvalidated | V5 forecast gate BLOCKED | No published numeric probabilities |
| Financial risk inputs | 3/6 validated in `CURRENT RISK INPUTS` | Different historical indicators | Do not merge without date, units, vintage, and provenance reconciliation |

## Artifact contract

- `audit-output/historical_cycle_timeline.json`: revised historical timeline; not PIT certified.
- `audit-output/v5_cycle_estimates.json`: provisional heuristic phases.
- `audit-output/v5_baseline_validation.json`: retrospective benchmark.
- `audit-output/v5_forecast_release_gate.json`: numeric forecast approval status.
- `audit-output/v5_dashboard.html` and `.json`: research-only display.
- `audit-output/unified_research_status.json`: machine-readable reconciliation and reporting eligibility.

The status artifact must fail closed: unknown workbook approval status is `NOT_RECONCILED`, never `APPROVED`. No direct Sheet-to-GitHub live ingestion is implied by this contract.

## Completion criteria

1. Export or connect a source-evidence snapshot from the Sheet with stable provenance and retrieval timestamp.
2. Reconcile matching series by ID, observation month, units, and source release/vintage; report disagreements.
3. Keep canonical and forecast gates blocked until their respective checks pass.
4. Generate daily, weekly, and monthly summaries from the same evidence ledger with different cadence-specific sections.
5. CI tests prove stale, missing, and unverified inputs cannot silently become approved current assessments.
