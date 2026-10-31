# Version 5 — Descriptive Release Candidate and Verification Checklist

Date: 2026-10-31
Status: **RELEASE CANDIDATE — NOT YET VERIFIED**
Branch: main

## What is implemented
- Dated FRED history and standardized descriptive macro transformations.
- Temporal provenance and publisher-original vintage contract checks.
- Historical episode/negative-control research, objective outcome coverage and PIT replay reports.
- Six mechanism evidence-readiness pathways; missing PIT and outcome evidence stays explicit.
- Integrated weekly JSON research readout and offline HTML dashboard.
- Fail-closed descriptive acceptance script, integration tests and scheduled workflow integration.
- V3/V4 existing descriptive dashboards retained as fallback.

## Required before declaring the descriptive release complete
1. GitHub Actions milestone1.yml must complete successfully on current main HEAD.
2. Confirm the artifact contains v5_weekly_research_readout.json,
   dashboard/weekly-v5.html, v5_release_acceptance.json,
   v5_objective_outcomes.json, v5_pit_replay.json and
   v5_mechanism_evidence_gate.json.
3. Confirm v5_release_acceptance.json status PASS_DESCRIPTIVE_ONLY,
   no omitted steps, and inspect the rendered HTML for readability.
4. Verify current observation dates and source freshness; do not confuse a
   passing build with current economic data.
5. Preserve the exact verified run ID, commit SHA, evidence date and
   release limitations in a final closeout.

## Research still blocked
- Independent objective event onset/end and complete non-event coverage.
- Verified publisher-original vintages across historical replay periods.
- Chronological, embargoed, event-parent-independent holdouts.
- Mechanism baseline/ablation results, falsification, calibration and
  independent review.
- Two genuinely distinct dated weekly snapshots for weekly continuity.

A passing descriptive release **does not** approve crash forecasts,
calibrated probabilities or claims that the research predicts market turns.

## Operating principle
Do not delay the descriptive release solely for inaccessible historical
publisher vintages. Publish transparent coverage gaps and keep the
predictive gate blocked. Do not mark this document as closed until the
current GitHub Actions run and artifacts are independently verified.
