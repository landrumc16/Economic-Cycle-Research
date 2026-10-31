# Economic Cycle Research — Version 5 Master Roadmap

Date: 2026-10-31
Status: IMPLEMENTATION AUTHORIZED — RESEARCH HARDENING
Predecessor: [V4 descriptive closeout](V4_DESCRIPTIVE_RELEASE_CLOSEOUT_2026-10-31.md)

## Mission
Turn Version 4's explainable descriptive economic intelligence into a historically grounded, release-aware weekly research platform. Preserve the working V4 weekly product and its explicit predictive gate. **Do not promise a crash forecast or a validated cycle stage until prospective information availability, negative controls, out-of-sample results and independent calibration pass.**

## Priorities and release milestones

### M1 — Operational weekly continuity and provenance
- Confirm **two distinct dated** scheduled weekly snapshots with an actual previous-run artifact, not just two builds on the same date.
- Preserve observation date, release/available-at timestamp, retrieval timestamp, source geography, units and vintage where supported.
- Validate weekly comparisons against release cadence; carry-forward is not a new economic observation.
- Exit: reproducible archived consecutive-week linkage and explicit freshness/coverage report.

### M2 — Genuine standardized macroeconomic measures
- Build transformations from dated observations: CPI 12-month inflation, real GDP quarterly growth (annualized and nonannualized), unemployment change, claims averages, yield curve, credit spread and financial stress.
- Add consumer spending, housing, business investment and international financial signals only with sourced, dated measurements.
- Exit: deterministic tests for unit conversions, revisions, missing months, quarterly boundaries and publication lags.

### M3 — Historical event labels and negative controls
- Establish objective event definitions, onset/end and independent parent episodes.
- Separate crash outcomes, recessions, drawdowns and non-events. Select true non-event windows by a documented prospective outcome horizon, not by retrospectively excluding crash neighborhoods alone.
- Record label provenance, overlapping windows, embargoes and cluster-level splits.
- Exit: versioned positive/negative research registry with reproducible tests; if historical coverage is incomplete, publish gaps.

### M4 — Point-in-time replay
- Reconstruct publisher-original vintages and actual release availability where possible; track irrecoverable periods.
- Prevent future-revised values, future labels and hindsight regime definitions from entering features.
- Exit: automated no-lookahead checks, provenance manifest and replay coverage report.

### M5 — Mechanism-specific baselines and global/social ablations
- Test monetary, credit/banking, labor/growth, housing, speculative and external-shock pathways separately.
- Compare simple interpretable baselines against richer models. Evaluate global/social variables only if sourced and available at the time; test generational/fourth-turning proxies as falsifiable optional features.
- Exit: evidence tables with contradictory findings and ablation results; do not force one universal crash signature.

### M6 — Falsification, calibration and independent review
- Use untouched chronological/era holdouts, event-cluster separation, explicit prediction horizons, base-rate comparators, false positives, missed events, lead-time distributions, sensitivity and confidence intervals.
- Publish negative results and independent audit findings.
- Exit: independent validation report. Any predictive release is strictly target-, horizon-, vintage- and population-specific; otherwise remain descriptive.

### M7 — Integrated V5 weekly release
- Preserve V4 fallback and weekly cadence; publish provenance, standardized metrics, historical analogs with clear comparability limitations, mechanism evidence and validation coverage in offline HTML and JSON.
- Keep monthly deep dives and quarterly structural reviews optional to the weekly primary product.
- Exit: automated acceptance, live scheduled run, archived evidence, closeout and explicit prediction status.

## Execution order and scope discipline
- Pass A: M1–M2. Make weekly observations and transformations genuinely reliable.
- Pass B: M3–M4. Establish trustworthy historical labels and no-lookahead replay.
- Pass C: M5–M6. Falsify mechanism hypotheses and calibrate only if evidence supports it.
- Pass D: M7. Integrate, test, release.

Do not spend months waiting for inaccessible original vintages: ship useful **V5 descriptive** improvements with the predictive gate blocked if necessary. No architecture rewrite, no repetition of accepted V4 work.

## First implementation chunk
Create an auditable V5 provenance and temporal-integrity report from the V4 weekly evidence, with tests that fail on future-dated observations, stale/missing source metadata and false claims of week-over-week changes. Then build dated historical transformation primitives and connect them to the existing workflow.
