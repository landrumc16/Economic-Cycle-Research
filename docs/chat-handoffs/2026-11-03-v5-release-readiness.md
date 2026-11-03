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
