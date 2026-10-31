## Release-evidence staging checkpoint — 2026-10-30
- Commits `1447c42`, `558c5cd`, `f2ce5c3`, `51595b5`: created empty original publisher release register, validator, no-lookahead tests, and CI step. No publisher observations or timestamps were fabricated.
- Validator rejects invalid source identifiers, missing timezone, malformed hashes, and releases after decision times; metadata plausibility never certifies source authenticity or authorizes prediction.
- Workflow #97 was cancelled by concurrency; not a passing result. Check the newest workflow before closure.
- Next: verify offline CI, then populate actual original BLS/BEA release artifacts with hashes, release timing and corroboration; resolve quota constraints without re-running full historical downloads unnecessarily.

## CI quota separation checkpoint — 2026-10-30
- Workflow #95 was in progress when checked. The BLS key's daily quota was exhausted on earlier runs.
- Commit `d0eab05` separates PR code checks from live BLS/FRED/BEA calls: live source acquisition and source reconciliation now run on scheduled or manually dispatched workflows, not on every PR commit. Source evidence remains blocked when absent; offline CI is **not** source certification.
- Next: verify new PR run, review remaining non-source failures, and prepare release evidence collection in bounded, non-duplicative batches. Do not force additional BLS calls until quota permits.

## Latest source acquisition diagnosis — 2026-10-30
- Workflow #90 failed specifically because the BLS API reported that the registered key's **daily request threshold was reached**. This is a quota limit, not evidence of bad macro observations. BLS/FRED reconciliation also failed because independent BLS evidence was unavailable.
- Added BLS quota circuit breaker in commit `614a9dc` to stop further calls immediately after the first quota rejection; the pipeline still fails closed and records the error.
- Workflow #93 was pending at check time; quota-fix commit has not been CI-verified. Do not repeatedly rerun acquisition while quota is exhausted.
- Next: verify quota reset / eligible source access, avoid redundant historical full-history requests, inspect latest CI, then build publisher-original release records with timestamps and hashes. Do not promote staging data.

## Checkpoint — publisher vintage contract automation (2026-10-30)
- Run #90 failed in BLS API fallback and BLS/FRED reconciliation; historical integrity step did not fail. Source pipeline remains unresolved; do not bypass.
- Historical Python syntax repaired in `9bc8ea1`; publisher evidence manifest in `cf787e8`.
- Added `scripts/validate_publisher_vintage_manifest.py`, tests and CI contract step in commits `aaf9685`, `7294fcb`, `155ede0`. The contract verifies required fields, publisher identity, expected series and explicitly blocks PIT certification and prediction. It does **not** prove original evidence exists.
- Next: inspect Actions for new commit; diagnose BLS source failures, then populate actual publisher-original release records and independently crosscheck decision-time eligibility.

# PROJECT STATUS — Economic Cycle Research
**Last updated:** 2026-10-30
**Active implementation branch:** `milestone-1-data-pipeline` (PR #1)
**Binding laws:** [docs/PROJECT_LAWS.md](docs/PROJECT_LAWS.md), mirrored from workbook PROJECT LAWS & RESTART (L01–L18)\n**Roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md)
**Canonical research:** [SEM_Historical_Crash_Research_v1](https://docs.google.com/spreadsheets/d/1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE/edit)
**Research authority and prior work:** [docs/EXISTING_RESEARCH_RECONCILIATION.md](docs/EXISTING_RESEARCH_RECONCILIATION.md)

## Where we are
**Phase 2: historical observation integration; Phase 3: release-vintage evidence remains the critical validation dependency.**
Do not restart historical crash research or spend another cycle on Milestone 1 ingestion infrastructure unless a concrete defect blocks progress.

## Verified checkpoint
- Most recent *verified successful* workflow at time of writing: GitHub Actions run **#78**, ID `41147875730`, associated with commit `73c4b68f6fd0ffde156cc36c6a93aa4c3bb7209a`.
- Subsequent commits: `34fe94c00c5dd1d6d193e5dbd541d567ad05c6d2` (complete historical snapshot), `1a51ebdbc3a0fe496fc24a69b708382d343ff332` (workflow reader integration). **Their workflow completion has not yet been verified in this status document.**
- Verify current branch HEAD and latest Actions before claiming new success. This status-file creation will also advance HEAD.

## Implemented and retained
- Official BLS, BEA and FRED acquisition, current-revised crosschecks and tests.
- Fail-closed operational status; macro observations, descriptive transformations and cycle-direction readout.
- Financial/housing overlay from dated workbook snapshot with per-series quality and approval gates.
- Integrated macro + financial readout with no crash probability or sector recommendation.
- Canonical historical research bridge: crash-pathway, noncrash, holdout and social/sector research provenance.
- `scripts/workbook_historical_observations.py`: schema-checking historical export reader and tests.
- `data/workbook_historical_research_snapshot_2026-10-30.json`: dated **manual** export of 8 parent clusters and 444 monthly baseline observations from canonical workbook; workflow runs reader and stores audit evidence.

## Not yet complete
- Historical reader checks schema but does **not** yet enforce full expected coverage, unique time keys, missing values, or release-date eligibility.
- Dated historical snapshot is **not** automatic Google Sheets sync.
- Publisher-original release vintages, hashes and no-lookahead certification incomplete.
- Truly untouched out-of-sample false-alarm validation and calibration incomplete.
- No approved predictive cycle stage, crash probability, composite score or sector recommendations.
- Dashboard publication remains blocked.

## Latest implementation checkpoint — 2026-10-30\n- Added coverage/time-integrity gate in `scripts/workbook_historical_observations.py` and focused tests. Commits `45d8c1f` and `1ce7679`.\n- Previous GitHub Actions run #83 was pending when checked; these newer commits are **not yet workflow-verified**.\n- Full historical snapshot remains dated research staging, not publisher-original point-in-time evidence.\n\n## NEXT AUTHORIZED IMPLEMENTATION CHUNK
**Verify historical integrity and advance original-release evidence**:
1. Check current branch HEAD and latest Actions result for the historical snapshot workflow.
2. Inspect the generated historical integrity report and repair only genuine schema/coverage defects; preserve missing data rather than filling it.
3. Add focused tests, wire the gate into the workflow, and verify resulting Actions run.
4. Then begin publisher-original release/vintage evidence manifest for UNRATE, CPIAUCSL and GDPC1 (without asserting certification).
5. Update this status file with actual commits, workflow results, remaining blockers and next authorized chunk.

## Rules for every session
Read START-HERE.md → this status → roadmap → reconciliation → latest handoff. Verify HEAD and workflow. Use workbook as research authority. Continue in substantial chunks; avoid repeated historical research and premature predictive publication. A green CI run proves code execution, not forecasting validity.
