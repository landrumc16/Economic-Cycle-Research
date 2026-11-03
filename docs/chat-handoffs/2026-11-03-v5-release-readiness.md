# Version 5 — Release readiness and execution checklist (2026-11-03)

## Scope
Ship the existing descriptive/historical research system, not unvalidated crash forecasts. The canonical workbook continues to control source promotion; the GitHub pipeline may consume dated evidence without claiming a live sync.

## Implemented in main
- Monthly GitHub Actions workflow with historical data acquisition, economic assessment, historical cycle estimates, evaluation, 3/6/12-month retrospective outcomes, baseline tests, blocked forecast gate, executive brief and HTML dashboards.
- Unified research status and dated workbook promotion snapshot. Snapshot remains unreviewed and must not be interpreted as current approval.
- Integrated `index.html` landing page linking the monthly economic dashboard, V5 diagnostics and brief.
- `v5_integrated_acceptance.py` checks required outputs, status agreement, stale-data disclosure and forecast blocking.
- Unit tests for integrated release and workbook evidence.

## Release blockers — must verify, not assume
1. Trigger **Monthly Economic Cycle Assessment** via GitHub Actions workflow_dispatch, or wait for its day-20 schedule. Confirm the run's full job succeeds and examine `industry-deviation-descriptive-evidence` artifact.
2. Confirm `audit-output/index.html`, `v5_integrated_acceptance.json`, `v5_dashboard.html`, `economic_dashboard.html`, `v5_executive_brief.md`, `unified_research_status.json` exist and render correctly on mobile.
3. Inspect release freshness: `STALE_RESEARCH_ONLY` is an acceptable research-only artifact, **not** a current economic assessment.
4. Confirm the daily workbook refresh and weekly outlook scheduling/ownership independently; the monthly workflow alone does not prove these cadences run. Do not claim live Sheets sync: the November 1 snapshot is fixed.
5. Fix only reproducible release-blocking failures. Publish a final closeout with the verified run URL, commit SHA, artifact inspection, known limits and any next-version deferrals.

## Explicitly deferred
- Point-in-time validated numerical recession/crash probabilities.
- Automatic source promotion, licensed market breadth/earnings/sector feeds.
- Additional model complexity and dashboard cosmetics.

## Acceptance rule
No formal Version 5 completion declaration until the Actions run and generated artifacts are independently verified. A passing test suite cannot certify original-release vintage accuracy or authorize predictive publication.


## Additional release work — November 3
- Main monthly workflow triggers on relevant main-branch pushes and retains its day-20 schedule.
- Lightweight V5 smoke CI now includes unified portal and integrated acceptance regression tests.
- Full workflow summary reports the integrated artifact gate; its status is not inferred from a successful commit.
- Unified portal places methodology and source promotion behind a collapsible disclosure and includes mobile navigation improvements.
- Historical heuristic remains explicitly research-only; no current-cycle approval or numerical forecasts are asserted.
- **Outstanding external evidence:** No completed monthly run ID, CI log, downloaded artifact, or deployed page inspection has been obtained in this session. The available GitHub connector can inspect a run by ID but does not list recent runs or dispatch new ones. A run URL or ID is needed for direct inspection, unless independently discoverable through the public Actions page.
- Do not mark V5 released until workflow and artifacts are verified. Dated workbook snapshot is not a live workbook connection.

## Verified monthly execution (supersedes earlier missing-run note)
- Run https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41686229400, commit fd44328c62f1e6fbfb1990d4a0c5ec22c69ca023, job 126092587842: completed successfully.
- Downloaded artifact 13253584340, 86 files; inspected portal JSON, unified status, integrated acceptance and monthly release acceptance. Integrated release accepted, monthly status STALE_RESEARCH_ONLY, 2026-08 observation month, 546 historical months, 9 economic indicators.
- The canonical workbook snapshot remains UNREVIEWED_AUTOMATED_SNAPSHOT, macro promotion blocked, and daily refresh NOT_RECONCILED. Weekly outlook is descriptive only. Numerical forecasting remains blocked. None of these facts is overridden by passing CI.
- The tested artifact includes the mobile HTML portal and companion dashboards; browser visual inspection and hosted publication are not yet verified.
- Remaining operational verification: inspect separate daily and weekly workflow schedules/runs, reconcile source promotion with the canonical Sheet, and verify hosted/mobile rendering if hosting is part of the desired deployment. Do not describe V5 as fully operational until these are resolved or explicitly accepted as release limitations.
