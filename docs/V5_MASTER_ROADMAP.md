# Economic Cycle Research — Version 5 Master Roadmap

Date: 2026-10-31
Status: DESCRIPTIVE RELEASE ACCEPTED — FULL OPERATIONAL CERTIFICATION PENDING
Predecessor: [V4 descriptive closeout](V4_DESCRIPTIVE_RELEASE_CLOSEOUT_2026-10-31.md)

## Mission
Turn Version 4's explainable descriptive economic intelligence into a historically grounded, release-aware weekly research platform. Preserve the working V4 weekly product and its explicit predictive gate. Do not promise a crash forecast or validated cycle stage until prospective information availability, negative controls, out-of-sample results and independent calibration pass.

## Priorities and release milestones

### M1 — Operational weekly continuity and provenance
- Confirm two distinct dated scheduled weekly snapshots with an actual previous-run artifact, not just two builds on the same date.
- Preserve observation date, release/available-at timestamp, retrieval timestamp, source geography, units and vintage where supported.
- Validate weekly comparisons against release cadence; carry-forward is not a new economic observation.
- Exit: reproducible archived consecutive-week linkage and explicit freshness/coverage report.

### M2 — Genuine standardized macroeconomic measures
- Build transformations from dated observations: CPI 12-month inflation, real GDP quarterly growth (annualized and nonannualized), unemployment change, claims averages, yield curve, credit spread and financial stress.
- Add consumer spending, housing, business investment and international financial signals only with sourced, dated measurements.
- Exit: deterministic tests for unit conversions, revisions, missing months, quarterly boundaries and publication lags.

### M3 — Historical event labels and negative controls
- Establish objective event definitions, onset/end and independent parent episodes.
- Separate crash outcomes, recessions, drawdowns and non-events. Select true non-event windows by a documented prospective outcome horizon.
- Record label provenance, overlapping windows, embargoes and cluster-level splits.
- Exit: versioned positive/negative research registry with reproducible tests; publish gaps where incomplete.

### M4 — Point-in-time replay
- Reconstruct publisher-original vintages and actual release availability where possible; track irrecoverable periods.
- Prevent future-revised values, future labels and hindsight regime definitions from entering features.
- Exit: automated no-lookahead checks, provenance manifest and replay coverage report.

### M5 — Mechanism-specific baselines and global/social ablations
- Test monetary, credit/banking, labor/growth, housing, speculative and external-shock pathways separately.
- Compare interpretable baselines against richer models. Test global/social variables only when sourced and contemporaneously available.
- Exit: evidence tables with contradictory findings and ablation results.

### M6 — Falsification, calibration and independent review
- Use untouched chronological/era holdouts, event-cluster separation, explicit horizons, base-rate comparators, false positives, missed events, lead times, sensitivity and confidence intervals.
- Publish negative results and independent audit findings.
- Exit: independent validation report. Otherwise remain descriptive.

### M7 — Integrated V5 weekly release
- Preserve V4 fallback and weekly cadence; publish provenance, standardized metrics, historical analog limitations, mechanism evidence and validation coverage in offline HTML and JSON.
- Keep monthly deep dives and quarterly reviews optional to the weekly primary product.
- Exit: automated acceptance, live scheduled run, archived evidence, closeout and explicit prediction status.

## Execution order and scope discipline
- Pass A: M1–M2; Pass B: M3–M4; Pass C: M5–M6; Pass D: M7.
- Do not wait indefinitely for inaccessible original vintages: ship descriptive improvements with predictive gate blocked.
- No architecture rewrite or repetition of accepted V4 work.

## Completion-focused execution protocol (2026-10-31)
- Execute coherent implementation/testing/release passes, without routine approval requests.
- Do not expand predictive research as a prerequisite to descriptive V5 release.
- Resolve blockers, inspect artifacts, and record exact evidence before declaring completion.
- Release boundary: weekly descriptive JSON/HTML, macro coverage, mechanism readiness, historical/PIT coverage, explicit BLOCKED predictive gate, reproducible acceptance.
- After passing verification and recorded closeout, scope Version 6 separately.

## Verification addendum — 2026-11-03
- Monthly descriptive run 41720710428 succeeded; accepted historical/descriptive release is preserved.
- Milestone 1 run 41720903373 succeeded at commit 23d7af81.
- Hardened daily run 41720903411 succeeded at commit 23d7af81, with all six regression tests passing and FRED, BLS and BEA acquisition steps successful.
- Inspected artifact 13272566362 (daily-economic-source-evidence): 60 files, including daily_acquisition_status.json and source reports. Status records acquisition_complete=true, all reports_present=true, all reports_valid=true.
- Source promotion remains BLOCKED; workbook_reconciled=false; current_assessment_approved=false; numeric_forecasts_approved=false. Acquisition does not certify historical vintages or authorize forecasts.
- Remaining operational release checks: certify distinct-date weekly continuity and artifact linkage, confirm daily/weekly/monthly reliability together, and verify hosted/mobile dashboard against release artifacts. Full operational Version 5 is not yet certified.

## Release hardening update — 2026-11-03
- Monthly integrated acceptance now requires explicit cadence/review evidence, rejects mismatched observation months, stale-current claims, and unauthorized workbook macro promotion. Regression tests were added; **post-change CI is not yet certified**.
- Weekly artifact 13271024721 generated descriptive output, but standardized macro availability was **0 of 4**, and original-vintage replay coverage was **0**. Descriptive release success must not be interpreted as current economic coverage.
- Fixed prior weekly artifact recovery JSON serialization in `.github/workflows/milestone1.yml` (commit `08b16fc`). The original literal escaped newline could invalidate the recovered snapshot; the new code reads it back to verify parseability.
- **Open M1:** two separate scheduled weekly dates with valid prior-artifact linkage remain unverified.
- **Open M7:** latest code revision needs successful CI, artifact inspection, and hosted/mobile dashboard verification. Current workbook source promotion remains blocked.
- Do not close V5 until those checks pass; do not expand the release into new forecasting research.
