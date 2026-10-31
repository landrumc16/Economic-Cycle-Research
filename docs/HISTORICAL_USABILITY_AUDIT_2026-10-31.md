# Historical usability audit — initial evidence inventory

Date: 2026-10-31
Status: INITIAL AUDIT COMPLETE; HISTORICAL PERFORMANCE TEST NOT YET RUN
Decision: Enough source material for a descriptive usability pilot; insufficient verified point-in-time evidence for predictive backtest claims.

## Existing repository evidence inspected

| Source | What it contains | Restriction |
| --- | --- | --- |
| `data/workbook_historical_research_snapshot_2026-10-30.json` | Eight crash pathway parent clusters and monthly noncrash comparison rows (source tab A4:L448, 1987 onward) | `point_in_time_certified: false`; retrospective workbook extraction |
| `data/v2_canonical_lead_window_summary_2026-10-31.json` | Eight historical drawdown pathways with financial warning flags and retrospective lead windows | `point_in_time_certified: false`; warnings are not validated prospective signals |
| `scripts/v5_historical_episode_research.py` | Event-parent and negative-control research contracts | Does not certify historical positive labels or independent non-events |
| `scripts/v5_objective_outcomes.py` | Outcome window labeling logic | Workflow currently supplies no independent events or outcome windows |
| `scripts/v5_pit_replay.py` | Publisher-original release/vintage chronology checks | Workflow currently supplies no original historical vintage records |
| `scripts/v5_mechanism_evidence.py` | Six distinct downturn mechanism evidence gates | No calibrated comparative performance without audited PIT inputs and outcomes |

## Ground-truth reference

Use the NBER US business-cycle chronology for recession peak/trough labels, keeping recession outcomes distinct from market drawdowns. NBER labels are retrospective, and cannot be used as contemporaneously known features.

- https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions
- https://www.nber.org/research/business-cycle-dating

## Minimum historical pilot (no forecast claims)

1. Build a dated evaluation panel from existing workbook monthly rows; record exact field mapping, missingness, period coverage and duplicated parent clusters.
2. Define independent outcomes separately: NBER recession onset, 20% equity drawdown, and no-event windows. Avoid treating recession overlap as a crash label.
3. Select pre-event evaluation origins for 1973–75, 1980–82, 2000–02, 2007–09 and 2020, plus non-event controls including 2022–23. Mark missing pre-1987 source coverage explicitly.
4. Generate a retrospective *descriptive* scorecard: available indicators, mechanism coverage, explanation, lead time, false alarms, missing observations and uncertainty.
5. Only run a genuine no-lookahead test on dates with verified publisher-original releases/vintages. Separate this cohort from revised-data retrospective demonstrations.
6. Compare against transparent baselines (unemployment change, yield curve, credit spread) on the same origin dates. Report denominators and confidence limitations; do not publish prediction accuracy without independent holdout.

## Initial findings

- **Sufficient to demonstrate usability:** yes, a limited descriptive historical pilot can be built from the existing dated monthly comparison rows and crash-pathway inventory.
- **Sufficient to claim validated warning performance:** no. Existing extracts explicitly lack point-in-time certification; event outcome inputs and independent negative labels are not populated in the V5 weekly workflow.
- **Important coverage gap:** workbook monthly comparison begins in 1987, so 1970s and early 1980s episodes need additional historical series before a comparable pilot.
- **Practical acceptance target:** a reader can select a historical date, see what the available evidence suggested, understand the mechanism and data limitations, and compare with later outcomes without hidden hindsight.

## Next implementation pass

Create an automated `historical_usability_inventory.json` with counts, dates, coverage gaps and PIT flags from the two existing snapshots. Then build a small, deterministic historical assessment table using only defensible descriptive rules, with a separate no-lookahead eligibility field. Do not build another generic dashboard first.
