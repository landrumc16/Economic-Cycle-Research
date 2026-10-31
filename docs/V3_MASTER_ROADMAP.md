# Economic Cycle Research — Version 3 Master Roadmap
Status: APPROVED BASELINE / IMPLEMENTATION STARTED
Date: 2026-10-31
Authority: Version 2 descriptive acceptance at docs/V2_DESCRIPTIVE_RELEASE_CANDIDATE.md.
Product: **Weekly Economic Intelligence**, supported by daily refresh, monthly depth reviews, quarterly structural reviews and event-driven updates.

## Objective
Explain where the economy stands, what changed in the past week, which historically distinct crash and economic-cycle mechanisms have gained or lost evidence, and what evidence is missing. Keep **economic-cycle stage**, **crash mechanism**, **market drawdown vulnerability**, and **sector implications** separate. No fabricated probabilities, cycle stages, investment recommendations or point-in-time certification.

## Nonnegotiable engineering rules
- Extend the accepted V2 dashboard and canonical workbook research; do not rewrite, duplicate or redo completed historical work.
- Ship substantial tested increments with commits, CI artifacts, acceptance criteria and explicit limitations. No recurring approval loops.
- Preserve series observation date, release/publication date, retrieval time, units, frequency, revisions, vintage and source quality where available. Missing metadata must remain missing.
- Daily data collection does not mean daily GDP, inflation or unemployment measurements. Weekly reports carry forward latest released observations with visible freshness and stale/missing warnings.
- Weekly change tracking compares **two report snapshots** (including source availability and revisions), not two observations whose dates/frequencies differ.
- Treat generational/fourth-turning theories as optional falsifiable social-context hypotheses, not assumed causal predictors.
- Publisher-original historical vintages, genuine noncrash outcomes, untouched era holdouts and calibrated validation are required before publishing predictive claims.

## Reporting cadence
- **Daily:** source refresh and QA; record failures and publication lag.
- **Weekly:** primary evidence-based economic assessment, changes since previous report, data freshness, mechanism-by-mechanism evidence, uncertainty, and next consequential releases.
- **Monthly:** deep macro/labor/inflation/housing/credit review using released observations.
- **Quarterly:** GDP, earnings, structural trends, regime stability and model-failure review.
- **Event-driven:** material release or financial stress change; explicitly labeled outside the regular weekly cadence.

## Milestone 1 — Data acquisition, freshness and weekly snapshot contract (IN PROGRESS)
Reuse existing FRED/BLS/BEA clients, source manifest, daily refresh workflow and V2 dashboard. Build a weekly snapshot artifact with a report as-of date, latest source dates, statuses, quality, explicit missingness and deterministic serialization. No missing-to-zero conversion.
**Exit:** daily acquisition tested; weekly snapshot generated on schedule and on demand; source failures visible; tests for stale, missing, future and invalid observations; release-time vs observation-time distinguished.
**First increment:** implement fail-closed weekly snapshot builder and regression tests, integrate into existing CI evidence artifact.

## Milestone 2 — Historical cycle and noncrash reconstruction (PLANNED)
Reuse 8 parent crash clusters, 444 historical monthly observations, lead windows and existing workbook tabs. Recover publisher-original vintages, publication lags and true noncrash forward outcomes, not retrospective monthly rows mislabeled as independent controls.
**Exit:** provenance, cluster-aware positive and negative cohorts, evidence-coverage matrix and no-lookahead audit. Block predictive comparison when absent.

## Milestone 3 — Explainable multi-pathway weekly assessment (PLANNED)
Inflation/supply shocks; monetary tightening; speculative valuation; banking/credit/housing; external shocks and additional historically supported mechanisms. Track evidence changes since previous weekly snapshot. No single composite score without validation.
**Exit:** separate observed facts, interpretations, counterevidence, data gaps and changes for each pathway; deterministic tests.

## Milestone 4 — Global transmission and measurable social context (PLANNED)
Expand eight V2 global evidence channels with actual sourced observations where available; include foreign rates, FX, USD funding, trade, credit, equity contagion and commodities. Add measurable social indicators and explicitly test any generational hypothesis.
**Exit:** source coverage, dates, geography, units, lags and evidence quality; unknown stays unknown.

## Milestone 5 — Falsification and predictive validation (PLANNED; PUBLICATION BLOCKED)
No-lookahead point-in-time replay; episode clustering; true negative controls and base rates; untouched chronological/era holdouts; false alarms, missed events, calibration and sensitivity analysis.
**Exit:** independently reviewed validation report. Predictions remain disabled if evidence fails.

## Milestone 6 — Weekly Version 3 product and release (PLANNED)
Extend one V2 dashboard, add weekly economic summary, week-over-week change, mechanism evidence, freshness, monthly/quarterly context, and transparent limitations. Schedule weekly reports; archive dated outputs and provide reproducible offline evidence.
**Exit:** full CI, report contract, release artifact, formal acceptance and no unsupported claims.

## Execution order
Implement M1 immediately. Move through M2–M6 in substantial passes; do not hold descriptive reporting hostage to predictive evidence acquisition. Audit each milestone once, fix concrete defects, then advance.

## Status and decisions
- V2 descriptive dashboard: ACCEPTED; current macro data and historical macro analogues not fully populated in push-event CI.
- V3 weekly assessment: PRIMARY PRODUCT REQUIREMENT.
- Predictive publication: BLOCKED until M5 evidence and independent validation.
- Next implementation: weekly report snapshot contract, deterministic tests and workflow integration.
