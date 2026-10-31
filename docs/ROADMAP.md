# Economic Cycle Research — Implementation Roadmap
**Updated:** 2026-10-30. **Authority:** canonical Google workbook; see [reconciliation](EXISTING_RESEARCH_RECONCILIATION.md).

## Destination
A transparent, reproducible assessment of economic conditions, with **separate** views for (1) cycle conditions, (2) crash mechanisms, (3) equity drawdown vulnerability, (4) sector opportunities and (5) interpretive social/generational context. Do not conflate a recession with a crash or a sector thesis with a validated forecast. One existing workbook dashboard is the eventual user view.

## Phases and exit criteria
| Phase | State | Required exit evidence |
|---|---|---|
| 0. Recover canonical research and authority | DONE | Workbook mapped; existing research reconciliation recorded; no duplicate crash study |
| 1. Data acquisition and descriptive baseline | SUBSTANTIALLY IMPLEMENTED, VALIDATION OPEN | BLS/BEA/FRED ingestion, revised-data crosschecks, provenance-aware macro/financial reports, dated source snapshots; release vintage still uncertified |
| 2. Historical research integration | IN PROGRESS | Consume complete canonical crash-pathway and noncrash observation exports; validate schema, row counts, completeness, time boundaries, and original workbook provenance; no independent-prediction claim |
| 3. Release-vintage and point-in-time evidence | NOT COMPLETE | Original publisher release files/timestamps/hashes, vintage correctness and no-lookahead certification per input; explicit approval gate |
| 4. Read-only operational cycle and pathway assessment | PARTIAL SCAFFOLD | Consume approved evidence, separate domain outputs, explicit missing/blocked states, no unsupported composite score |
| 5. False-alarm, holdout and calibration validation | NOT COMPLETE | Noncrash controls, nonoverlapping event denominators, genuinely untouched holdout, base rates, calibration and stability audits; reject weak signals |
| 6. Sector/social interpretation | RESEARCH EXISTS; VALIDATION OPEN | Sector analysis distinct from forecasts; social/“Fourth Turning” context not asserted as predictor without incremental evidence |
| 7. Controlled dashboard and refresh | BLOCKED | Authorized automated workbook synchronization, freshness and QA gates, human signoff; publish only approved results |

## Current critical path
1. **Finish Phase 2**: historical snapshot already contains eight parent clusters and 444 monthly baseline observations. Make workflow enforce expected coverage and evidence completeness, not just parse schema. Keep manual snapshot labeled dated.
2. **Advance Phase 3 in parallel**: map source release dates, original vintages, hashes, and evidence status for UNRATE, CPIAUCSL, GDPC1 and other canonical inputs; never substitute revised FRED series for original publisher vintage.
3. **Build Phase 4 read-only outputs** against source gates; distinguish missing, staged and approved observations.
4. **Run Phase 5 validation** against existing workbook controls; do not treat overlapping 12-month windows as independent events.
5. **Only then** consider approved sector signals and publication to existing dashboard.

## Stop-work / scope control
- No duplicate research into five famous crashes or replacement of the workbook's parent-cluster universe.
- No additional workbook tabs, new taxonomies or thresholds without a documented gap.
- No unverified risk percentages, cycle-stage forecasts, causal crash classifications or sector recommendations.
- Do not equate successful GitHub Actions with original-vintage certification or predictive validation.
- Prefer substantial increments with tests and real workflow verification; do not get stuck indefinitely in Milestone 1.
- At every milestone: update PROJECT_STATUS.md with verified HEAD/run, deliverables, blockers and next chunk; keep roadmap aligned.

## Source links
- [Canonical workbook](https://docs.google.com/spreadsheets/d/1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE/edit)
- [Implementation reconciliation](EXISTING_RESEARCH_RECONCILIATION.md)
- [Prior closeout](chat-handoffs/2026-10-30-economic-cycle-closeout.md)
