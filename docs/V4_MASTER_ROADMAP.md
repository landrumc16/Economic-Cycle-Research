# Economic Cycle Research — Version 4 Master Roadmap

Date: 2026-10-31
Status: PROPOSED IMPLEMENTATION BASELINE
Product: **Economic Cycle Intelligence & Historical Validation**
Predecessor: `docs/V3_DESCRIPTIVE_RELEASE_CLOSEOUT_2026-10-31.md` (V3 descriptive release accepted).

## Mission
Advance the existing weekly economic intelligence system from dated observations and descriptive pathway inventories to **interpretable, historically testable economic-cycle and risk assessments**. Distinguish economic-cycle condition, recession vulnerability, market drawdown mechanisms, and sector exposure. Do not collapse them into one unvalidated crash score.

## Delivery principles
1. Extend V3; preserve its stable weekly HTML dashboard, JSON/Markdown reports, schedule, and accepted descriptive contract. No rewrite of V1–V3.
2. Ship in substantial, tested increments; avoid repetitive audits, approval loops, and low-value micro-milestones.
3. Weekly is the primary product. Daily collection and release-event refresh support it; monthly and quarterly reviews add depth.
4. All signals identify source, geography, units, observation date, available-at/publication date when known, retrieval time, vintage, lag, transformation, and missingness. Never silently fill unavailable evidence with zero.
5. Distinguish **observed facts**, **interpreted directional evidence**, **hypotheses**, **historical associations**, and **validated predictive results**. Predictions remain disabled until independently validated.
6. Prefer interpretable rule-based baselines over complex models. Add machine learning only if it beats honest, simple baselines on untouched historical holdouts.
7. No investment recommendations or fabricated crash probabilities. Generational/fourth-turning ideas are optional falsifiable hypotheses, not assumed causes.

## Milestone 1 — Operational hardening and trustworthy weekly comparisons
**Build:** verify two distinct dated V3 snapshots; fix retrieval of earlier weekly artifact; test missing/revised/new observations; separate source acquisition success from actual observation coverage and freshness; archive stable weekly history and quality summaries.
**Exit:** two dated end-to-end runs with verified prior snapshot linkage, correct comparisons and an auditable data-freshness summary. Continue publishing V3 if later V4 work fails.

## Milestone 2 — Standardized economic-cycle signal library
**Build:** common time-aware transformations for labor, growth, inflation, interest rates/curve, credit/liquidity, housing, consumer demand, business investment and financial conditions. Include 3/6/12-month changes where statistically appropriate, levels vs rates, recession-sensitive directional rules, counter-signals, release lags, and revision flags. Avoid false weekly movements for monthly/quarterly series.
**Exit:** deterministic, unit-tested signal contracts and explainable domain readouts with uncertainty and missingness; no unvalidated composite cycle-stage labels.

## Milestone 3 — Historical episodes, genuine controls and vintage reconstruction
**Build:** reuse eight canonical crash-parent clusters, existing 444 monthly historical rows, lead-window work, V2 workbook and V3 cohort audit. Build episode-level labels with explicit onset/end and drawdown definition; independently identify non-event outcome windows and overlapping samples; reconstruct source-release availability and publisher-original vintages where obtainable. Record unrecoverable evidence honestly.
**Exit:** reproducible positive/negative episode registry, provenance and no-lookahead checks, independent cohort accounting and blocked predictive publication when critical evidence is missing.

## Milestone 4 — Multi-mechanism cycle and crash-risk assessment
**Build:** distinct lenses for monetary tightening/inflation, credit and banking stress, speculative valuation unwind, growth/labor recession, housing and leverage, external/global shocks, and supply shocks. Each lens reports observed evidence, directional changes, disconfirming signals, confidence in *evidence quality*, and unknowns. Distinguish macro recession from equity market drawdown.
**Exit:** coherent weekly pathway-by-pathway assessment, historically traceable mechanism definitions, and tested cases where mixed evidence prevents a confident conclusion.

## Milestone 5 — Global transmission, social behavior and generational hypotheses
**Build:** prioritized international USD funding, FX, sovereign yields, trade, commodities, foreign credit, cross-border stress and global equities; measurable consumer/business sentiment, household balance sheets and behavior. Optional generational/fourth-turning variables require a documented measurable proxy, plausible mechanism, and incremental-value test against a baseline without them.
**Exit:** source-qualified global/social context and an ablation-ready research dataset; no speculative narrative promoted to established causal evidence.

## Milestone 6 — Backtesting, falsification and calibration
**Build:** chronological point-in-time replay, event-cluster splits, untouched era holdouts, genuine non-event controls, base-rate benchmarks, false alarms, missed events, lead-time distributions, calibration, robustness across vintage revisions and sensitivity to regime changes. Independently audit results. Publish null/negative findings.
**Exit:** reproducible validation report. Any quantitative recession/crash probability or named cycle-stage classifier is enabled **only** for its specifically validated target, horizon, population and data vintage. Otherwise keep descriptive labels and publication blocked.

## Milestone 7 — Integrated V4 weekly product and release
**Build:** evolve the existing dashboard to present (1) current economic conditions, (2) weekly changes and releases, (3) evidence by cycle domain, (4) distinct mechanism lenses and counterevidence, (5) historical context, (6) data coverage/uncertainty, and (7) validation status. Offer weekly primary report, monthly deeper analysis, quarterly structural review, and clearly labeled event-driven updates. Preserve downloadable offline HTML, JSON and Markdown.
**Exit:** full tests, end-to-end live run, reproducible evidence artifact, versioned release acceptance, written closeout, and no unsupported claims.

## Suggested execution sequence and scope discipline
- **Pass A (M1–M2):** reliable weekly historical comparisons plus substantive domain signals; deliver a visibly better descriptive dashboard quickly.
- **Pass B (M3–M4):** episode-aware history and mechanism analysis, with gaps clearly flagged.
- **Pass C (M5–M6):** global/social enrichment and rigorous falsification; predictive features stay optional and gated.
- **Pass D (M7):** product integration, release testing and closeout.

Do not hold the improved descriptive V4 product hostage to an impossible historical-vintage recovery. If M6 cannot meet predictive standards, ship V4 **descriptive intelligence** with the predictive gate closed and document the unresolved research separately.

## Definition of done
- Weekly production pipeline remains healthy and archived.
- Domain-level interpretations are meaningful, sourced and reproducible.
- Historical comparisons do not conflate crash periods with verified negative controls.
- Separate risk mechanisms and contradictory evidence are visible.
- No-lookahead and validation status are explicit.
- Automated tests and one live operational run pass.
- Final dashboard and closeout are committed to GitHub.

## First authorized implementation chunk (once roadmap approved)
Harden previous-week artifact retrieval and source freshness; build standardized economic domain signal contracts and tests; integrate into the existing V3 weekly report without breaking it. Then advance in large passes.
