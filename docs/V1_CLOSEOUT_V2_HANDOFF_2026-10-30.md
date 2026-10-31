# Version 1.0 descriptive dashboard closeout — 2026-10-30

## Acceptance evidence
- GitHub Actions manual workflow run **#169** on main, commit `abca1c8`: successful (user-supplied run summary).
- Job summary explicitly reported `RESEARCH_DASHBOARD_CANDIDATE` and `Predictive model: NOT_VALIDATED`.
- Evidence artifact: `milestone1-audit-evidence`, including `dashboard/index.html`, `dashboard/state.json`, and `dashboard/v1_acceptance.json`.
- This is **acceptance of the descriptive research-dashboard candidate only**. It does not certify point-in-time historical observations, crash prediction, live financial advice, or investment decisions.
- Run #169 also displayed two error annotations (`Process completed with exit code 1`) and platform deprecation notices despite overall job success. Inspect corresponding steps/logs and distinguish tolerated upstream failures from mandatory checks; preserve the warnings as open operational debt.

## Scope preserved
- Workbook `SEM_Historical_Crash_Research_v1` is the canonical historical research record.
- Reuse existing crash pathway taxonomy, 24-month trajectories, non-crash controls, curve/credit studies, housing and mortgage research, social context, and release verification.
- Five famous macro anchors are **exploratory examples**, not the full crash universe.
- Retrospective current-revised data and hindsight-selected anchors cannot support forward probabilities or cycle-stage certainty.

## Version 2 implementation boundary
1. Build a **read-only canonical evidence bridge** from existing workbook outputs to versioned machine-readable research data. Record workbook tab, source range, extraction timestamp, row count, checksums and per-row source status. No fresh historical research.
2. Assemble historical **pathway-specific feature panels** across business-cycle, inflation, labor, curve, credit, housing, policy, valuations, and contextual social observations, explicitly representing missing values.
3. Compare pathway trajectories with **genuine non-crash control episodes** and preserve sample/overlap diagnostics. Do not treat overlapping lead windows as independent observations.
4. Add release-aware vintage timestamps and no-lookahead checks before any model evaluation. Unverified rows remain descriptive-only.
5. Only after source approval, run walk-forward and untouched holdout validation. Keep separate: cycle-stage classification, crash mechanism, drawdown vulnerability, and sector opportunity. No composite score without demonstrated incremental value.

## Next deliverable
A canonical workbook-to-code mapping and first multi-pathway comparison built from existing approved research exports, with regression tests and a fail-closed source manifest. Do not duplicate historical research or introduce unsupported forecasts.
