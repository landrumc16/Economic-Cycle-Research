# Existing-research reconciliation and implementation authority — 2026-10-30

## Canonical research system
Google Sheet: SEM_Historical_Crash_Research_v1
https://docs.google.com/spreadsheets/d/1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE/edit

**The workbook is the authoritative research and model design record.** GitHub supplies executable ingestion, reproducible QA, and implementation. Do not recreate existing crash taxonomies, historical case studies, thresholds, or tests as if the research were absent.

## Verified workbook-to-code inventory

| Research capability | Existing canonical workbook tabs | State / action |
|---|---|---|
| Crash events, distinct pathways and parent clusters | CRASH EVENTS; CRASH PATHWAY TYPOLOGY; NASDAQ PARENT CRASH CLUSTERS | REUSE. Five-event GitHub demo is a subset, NOT the authoritative event universe. |
| Pre-crash leads, cycle sequences and controls | CRASH 24M LEAD TRAJECTORIES; CRASH LEAD WINDOW SUMMARY; CYCLE EPISODE SEQUENCES; WARNING NONCRASH BASELINES | REUSE. Do not re-research five famous crashes. |
| Signal false positives and walk-forward | WALK FORWARD RULE AUDIT; CLEAN SIGNAL RULE SUMMARY; SIGNAL EPISODE COUNTS; ERA HOLDOUT DIAGNOSTIC | REUSE; existing workbook explicitly says selected rules/holdout are not truly untouched OOS. |
| Credit, curve, policy and funding pathways | CURVE CREDIT MONTHLY AUDIT; POLICY REGIME INTERACTION AUDIT; STRESS FIRST PATHWAY AUDIT; FUNDING INDICATOR BRIDGE QA | REUSE. Validate vintages before treating as predictive. |
| Housing and household credit | HOUSING MACRO TEST DESIGN; HOUSING SUPPLY REGIME CHECK; MORTGAGE 142Q SIGNAL BACKTEST | REUSE, unresolved source/validation gates remain. |
| International reserve crisis | RESERVE CRISIS COMPARATIVE MATRIX; RESERVE CRISIS SEQUENCE TEST; RESERVE PRIMARY SOURCE AUDIT | REUSE; primary-source and negative-control gates still open. |
| Social and generational context | SOCIAL CONTEXT | Framework exists, observations and incremental validation do not. Fourth Turning is interpretive, not established predictor. |
| Current economic cycle / risk | CURRENT RISK INPUTS; INTEGRATED CYCLE; ECONOMY AT A GLANCE | REUSE, dashboard still blocked for publication. No fabricated crash probability. |
| Source approval | SOURCE VERIFICATION LEDGER; DATA PROMOTION GATE; BUILD CHECKLIST | KEEP authoritative, currently blocked for historical vintage certification. |
| Implementation | GitHub scripts/fred_api.py, bls_api.py, bea_api.py and comparison tests | Current-revised reconciliation complete, 35 tests passed and 2,219 overlaps matched in successful run 41122452284. |

## Reconciliation correction
The newly created scripts/retrospective_event_panel.py and scripts/compare_crash_events.py are **smoke-test/exploratory implementation fixtures**, not new research or a replacement for workbook's broader event universe. Their five windows are not representative; do not infer universal mechanisms or publish probabilities from them. The Phase 2 plan must defer to the already established workbook methods and case studies.

## Actual remaining critical path
1. **Inventory and map** existing workbook output definitions, formulas and QA to one GitHub implementation specification; reuse existing source registry, event universe and tests.
2. **Complete publisher vintage/release-time certification** for UNRATE, CPIAUCSL, GDPC1 and other model inputs; retain original files/hashes, prevent look-ahead, and seek human approval. Current revised-series reconciliation is not PIT approval.
3. **Implement a read-only operational model** that consumes only approved canonical inputs and emits explicit missing/blocked states. Preserve separate outputs for cycle stage, crash mechanism, drawdown vulnerability and sector opportunity.
4. **Verify actual historical predictive performance** using noncrash controls, genuinely untouched holdouts, base rates and calibration; reuse existing workbook research as discovery, not independent validation.
5. **Publish one existing dashboard** only after source, freshness and validation gates pass. Keep social factors as context until incremental explanatory value is established.

## Stop-work rules
- No new crash-category brainstorming, duplicate historical-event panels, extra workbook tabs or additional indicator catalogs without a documented gap.
- No redesign of approved source definitions or source gates.
- No claim that 10 accepted research/structure items imply end-to-end model validation; BUILD CHECKLIST records 0/10 workstreams validated end-to-end.
- No promotion of GitHub retrospective fixtures into canonical workbook or live scores.
