# Economic Cycle Research — Version 2.0 master roadmap

Status: ACTIVE / milestone 1 ACCEPTANCE PENDING CI; milestone 2 IN PROGRESS
Authority: SEM_Historical_Crash_Research_v1 (canonical research), GitHub implementation and tests.
Scope: Historical-pattern intelligence, including global transmission; no invented crash probability or investment recommendation.

## Delivery rules
- Deliver in substantial passes, not repeated planning cycles. Reuse existing workbook research, source registry and V1 dashboard.
- Every milestone must have a code/evidence artifact, automated checks, explicit limitations, and an acceptance record.
- Green GitHub Actions does not imply complete acquisition or model validation: inspect continue-on-error failures and source gates.
- Current-revised observations are not historical point-in-time observations; missing or unapproved data stay missing.
- Preserve four separate questions: economic-cycle stage, crash mechanism, drawdown vulnerability, and sector implications.
- No release of probabilities, rankings or actionable predictions until publisher-original vintages, genuine controls, and untouched out-of-sample validation pass.

## Milestone 1 — Canonical evidence foundation (IN PROGRESS)
Existing: V1 dashboard accepted as descriptive candidate; canonical snapshot comparison module, prior-month matching, dashboard table, regression tests and workflow integration committed.
Exit:
- Run full CI suite and inspect annotations; all required tests pass.
- Confirm Version 2 table appears in artifact and source metadata/quality warnings persist.
- Document all snapshot source tabs, ranges, checksum and extraction timestamp status.
- Confirm monthly observations are not mislabeled verified non-crash controls.
Deliverable: v2_canonical_comparison.json + Version 2 dashboard panel + CI evidence.

## Milestone 2 — Multi-pathway historical intelligence (IN PROGRESS)
Reuse CRASH EVENTS, CRASH PATHWAY TYPOLOGY, CRASH 24M LEAD TRAJECTORIES, CYCLE EPISODE SEQUENCES, WARNING NONCRASH BASELINES, WALK FORWARD RULE AUDIT and related existing workbook tabs.
Exit:
- Explicit mapping of canonical pathway labels to events; no numeric-feature invented labels.
- Separate lead trajectories and baseline outcomes, with correct denominator and episode clustering.
- Coverage matrix for GDP, inflation, labor, policy, curve, credit, housing, valuation and social context; missingness visible.
- Confirmed negative-control definitions or explicit BLOCKED status if not verifiable.
Implemented: initial 8-cluster feature-coverage matrix with explicit absent domains, regression tests and CI artifact; canonical mechanism labels and verified controls still pending.
Deliverable: canonical pathway evidence dataset, comparison panels, regression tests.

## Milestone 3 — International and global transmission (PLANNED)
Exit:
- Source registry and coverage map for international rates, currency, trade, capital flows and cross-market contagion.
- Historical global channels linked to pathways only where evidence exists; no post-hoc causal claims.
- Vintage, publication lag, geography, unit and currency transformations audited.
Deliverable: global context layer with coverage and evidence quality.

## Milestone 4 — Current-cycle interpretation (PLANNED)
Exit:
- Reuse growth, labor, inflation, housing, credit and policy research domains with timestamped freshness.
- Display separate mechanism lenses and global context; explicitly distinguish observable conditions from inferred stage.
- No missing-value-to-zero substitutions; no composite score without validation.
Deliverable: current-to-historical comparison view with source gating.

## Milestone 5 — Validation and falsification (PLANNED)
Exit:
- Publisher-original releases/vintages and no-lookahead checks for every candidate predictive input.
- True non-crash forward-outcome controls, base rates, clustered episode-level analysis, untouched era holdouts.
- Report sensitivity, false positives, calibration and failure cases; fail closed if inadequate.
Deliverable: independent validation report, or explicit NOT VALIDATED status.

## Milestone 6 — Integrated dashboard and V2 acceptance (PLANNED)
Exit:
- One dashboard, not a separate parallel product; reproducible offline artifact and release notes.
- CI tests, data contracts, accessibility and regression smoke tests.
- Source status, research limitations and predictive approval displayed clearly.
- Formal milestone evidence and final audit; release only descriptive features if predictive gate remains closed.
Deliverable: Version 2.0 research dashboard candidate and acceptance record.

## Current next action
Verify CI after dependency-order fix (90eeec0), then accept Milestone 1 only with passing evidence. Continue Milestone 2 by mapping authoritative workbook mechanism labels and lead trajectories; do not infer labels or redo research.

## Progress protocol
Track each milestone as PLANNED / IN PROGRESS / BLOCKED / ACCEPTED with commit, test run, artifact and remaining blocker. Update this file only on meaningful milestone changes.
