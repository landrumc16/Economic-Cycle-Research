# Version 5 — Descriptive Release Candidate and Verification Checklist

Date: 2026-10-31
Status: **SMOKE AND FULL WORKFLOW VERIFIED — ARTIFACT INSPECTION PENDING**
Branch: main

## What is implemented
- Dated FRED history and standardized descriptive macro transformations.
- Temporal provenance and publisher-original vintage contract checks.
- Historical episode/negative-control research, objective outcome coverage and PIT replay reports.
- Six mechanism evidence-readiness pathways; missing PIT and outcome evidence stays explicit.
- Integrated weekly JSON research readout and offline HTML dashboard.
- Fail-closed descriptive acceptance script, integration tests and scheduled workflow integration.
- Machine-readable `v5_release_evidence_manifest.json` now checks required output files, acceptance result, report dates and predictive gate. It explicitly does not certify live freshness.
- V3/V4 existing descriptive dashboards retained as fallback.

## Fast independent code verification
- Workflow: `.github/workflows/v5-descriptive-smoke.yml` (pushes to main and manual dispatch).
- Runs Python compilation and `python -m unittest discover -s tests -p 'test_v5_*.py' -v`.
- A passing smoke test establishes code integrity, **not** source freshness or full weekly release acceptance.
- Full scheduled evidence and acceptance remain in `.github/workflows/milestone1.yml`.

## Verified smoke evidence
- User-supplied GitHub Actions screenshots show **Version 5 Descriptive Release Smoke #16**, commit `b320010` on `main`, status **Success** (10 seconds), with one uploaded artifact.
- The job screenshot shows successful compilation, regression tests, isolated descriptive artifact-chain build and validation, and artifact preservation.
- This is screenshot-based confirmation of the smoke run, not independent inspection of the artifact bytes or full weekly pipeline.
- Subsequent commits on `main` still require their own verification; run #16 must not be described as validation of later commits.

## Full workflow evidence
- User-supplied GitHub Actions screenshots show **Milestone 1 — Economic Data Acquisition and QA #374**, commit `7e0a60f` on `main`, status **Success** (21 seconds), `audit` job passed, one artifact uploaded.
- Some external-data acquisition steps were skipped; a passing workflow does not certify a live-source refresh.
- Screenshot confirms workflow success, not the contents of `v5_release_evidence_manifest.json`, the dashboard, or source dates. Those artifacts still require inspection.

## Required before declaring the descriptive release complete
1. GitHub Actions milestone1.yml must complete successfully on current main HEAD.
2. Confirm the artifact contains v5_weekly_research_readout.json,
   dashboard/weekly-v5.html, v5_release_acceptance.json,
   v5_objective_outcomes.json, v5_pit_replay.json and
   v5_mechanism_evidence_gate.json.
3. Confirm v5_release_evidence_manifest.json status DESCRIPTIVE_ARTIFACTS_VERIFIED and v5_release_acceptance.json status PASS_DESCRIPTIVE_ONLY,
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
