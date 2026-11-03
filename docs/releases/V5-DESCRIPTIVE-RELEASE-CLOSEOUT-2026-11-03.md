# Version 5 — Verified Descriptive Release Closeout

Date: 2026-11-03
Decision: **ACCEPTED — HISTORICAL/DESCRIPTIVE RELEASE; CURRENT-CYCLE CERTIFICATION WITHHELD**

## Shipped and independently verified

| Component | GitHub evidence | Release interpretation |
| --- | --- | --- |
| Daily official-source acquisition | [41718925304](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41718925304), artifact 13270758056 (60 files) | Manual dispatch passed; FRED, BLS and BEA acquisition steps succeeded. Data acquired, **not certified**. Weekday schedule configured but recurring execution not yet observed. |
| Weekly research | [41717373533](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41717373533), artifact 13269823787 (47 files) | Weekly V5 descriptive acceptance `PASS_DESCRIPTIVE_ONLY`; dashboard and readout generated. Source coverage 0/4 in that run, so **not** a certified current outlook. |
| Monthly historical assessment | [41695279177](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41695279177), artifact 13261995064 (86 files) | `V5_INTEGRATED_DESCRIPTIVE_RELEASE_ACCEPTED`; monthly gate `STALE_RESEARCH_ONLY`; common observation month 2026-08. |
| Integration regression checks | [41695279195](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41695279195) | Passed on functional head `85bf9cf`. |
| Descriptive smoke | [41695279185](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41695279185) | Passed on functional head `85bf9cf`. |
| Post-integration code and documentation CI | [41719108758](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41719108758) | Milestone 1 passed at `60c9cda`. |

The monthly artifact contains `index.html`, `economic_dashboard.html`, `v5_dashboard.html`, the executive brief, source/release status and validation reports. Its three HTML dashboards include mobile viewport metadata. The integrated acceptance gate rejects missing report links, unsafe paths, missing mobile viewport, inconsistent workbook claims and unsupported numeric/current-cycle approvals. Artifact inspection and CI checks do **not** substitute for interactive browser/device testing or a hosted deployment.

## Source governance and scientific boundaries

Canonical source-promotion authority: Google Sheet `SEM_Historical_Crash_Research_v1` (DATA PROMOTION GATE, SOURCE VERIFICATION LEDGER). Last repository snapshot `data/workbook_evidence/promotion_gate_2026-11-01.json` is **UNREVIEWED_AUTOMATED_SNAPSHOT**, with UNRATE, CPIAUCSL and GDPC1 **BLOCKED**. The downloaded daily artifact also explicitly records `source_promotion=BLOCKED`, `workbook_reconciled=false`, `current_assessment_approved=false`, `numeric_forecasts_approved=false`.

Historical recession/crash, credit/housing, bubble/pathway, negative-control, and forward-outcome research remains retrospective. Original-release vintage completeness and out-of-sample calibration are not certified. No present-tense phase classification, recession/crash probability, or investment recommendation is authorized by this release.

## Operational architecture

- Weekdays: `.github/workflows/daily-economic-source-acquisition.yml` gathers official source observations and uploads dated evidence without promotion.
- Mondays: `.github/workflows/milestone1.yml` runs source QA, historical analogues, financial/housing overlay and descriptive weekly readout/dashboard.
- Monthly day 20: `.github/workflows/industry-deviation-descriptive.yml` runs historical cycle, validation, source/workbook gate, unified portal and artifact publication.

These workflows reuse existing modules. **There is no automated cross-run artifact ingestion or authenticated write-back to the canonical Google Sheet**; the independent source-promotion gate prevents treating them as a single certified live-data pipeline.

## Remaining limitations and exact closure requirements

1. **Canonical workbook reconciliation:** review the authoritative Sheet's source ledger and vintage comparisons; update a dated reviewed snapshot with verified approval decisions. Do not set macro promotion to APPROVED until the sheet explicitly supports it. This is the blocker for a certified current-cycle assessment.
2. **Recurring schedule:** inspect at least one actual weekday scheduled daily run, a Monday weekly scheduled run and a day-20 monthly scheduled run. Manual dispatch proves executability, not future scheduler reliability.
3. **Dashboard delivery:** inspect `index.html` and companion pages in desktop and mobile browsers, and establish a supported hosting/deployment route if a public live URL is a requirement. Current verified distribution is via downloadable GitHub Actions artifacts.
4. **Forecasting:** retain numerical predictions blocked until original-vintage, negative-control, embargo and calibration gates independently pass. This is not a prerequisite for the **descriptive** release.

## Release declaration

**Version 5 historical/descriptive research artifact release is accepted and technically verified.** The broader goal of a fully live, source-promoted, continuously reconciled current economic assessment **is not certified or closed**. Do not call this a predictive release. Preserve existing V1–V4 behavior. Defer enhancements unrelated to these remaining operational checks to Version 6.

## Direct canonical Google Sheets review — 2026-11-03

The live connected native spreadsheet `SEM_Historical_Crash_Research_v1` (`1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE`) was read directly, not inferred from the repository's November 1 snapshot.

- `DATA PROMOTION GATE!A1:H9`: UNRATE, CPIAUCSL and GDPC1 all remain **BLOCKED**. UNRATE publisher cross-check partial and vintage review partial; CPIAUCSL cross-check partial and vintage pending; GDPC1 cross-check partial and vintage pending. Missing October 2025 BLS observations must remain missing.
- `DATA REFRESH STATUS!A1:H9`: November 3 08:11 CST source review reports 12/12 registry feeds and 9/9 refresh categories reviewed, with two numeric observations staged but **zero canonical promotions** and **0/3 primary macro approved**. Source scan and manual workbook notes are **not** proof of automated GitHub-to-Sheets synchronization.
- `SOURCE VERIFICATION LEDGER!A1:H12`: ledger retains publisher, series IDs, definitions, units, source URLs and observation dates; listing a source is explicitly not verification of fetched observations.

**Reconciliation result:** The live workbook agrees with the repository's fail-closed macro approval state. This is a verified **status reconciliation**, not a verified numerical point-by-point ingestion or authorized source promotion. Current-cycle certification remains blocked; do not mark it complete or replace missing data.

## Daily workflow reliability correction — 2026-11-03
- Commit `548281f` corrects the daily workflow's false-success failure mode. All official-source acquisition steps retain `continue-on-error` to allow subsequent sources to run and preserve their reports, but the final summary now exits nonzero when **any** FRED/BLS/BEA step outcome is not `success`. The artifact upload remains `if: always()` and retains the evidence even on a failed run.
- This change was committed **after** the successful manual run `41718925304`; that prior run cannot validate the new failure gate. A new manual or scheduled run is required before claiming the corrected daily workflow verified. GitHub connection presently has read/run-inspection and repository-edit tools but no workflow-dispatch action.
- Source-promotion restrictions and the authoritative workbook approval state remain unchanged.
