# Economic Cycle Research — Approved Final Product Blueprint

**Approved by product owner:** 2026-11-04  
**Status:** Target vision; not a claim that all capabilities exist today.  
**Baseline:** Version 6.1; preserve accepted production releases while developing successors.

## Product mission

**Understand the Economy. Anticipate Change. Explore the Evidence.**

Build an accessible, source-grounded, research-driven economic and general investment intelligence platform. Serve everyday readers, individual investors, and financial professionals using one research foundation with progressively deeper presentation. The product explains current conditions, explores possible developments, and evaluates broad investment implications, without personalized investment advice.

## Product principles

1. Conclusions first: a readable mobile-first executive homepage; dated evidence, uncertainty, and deeper research on demand.
2. Research integrity: trace every material claim to dated sources, preserve source vintages and revisions, avoid lookahead, distinguish observation from inference and prediction.
3. Publish predictive forecasts or numerical probabilities **only** when reproducible out-of-sample validation, calibration, benchmark comparison, and release gates justify them.
4. Investigate competing theories, historical crash mechanisms, international transmission, negative controls, and false alarms. Never assume a downturn is inevitable.
5. Evaluate economic exposure separately from valuation and investment attractiveness. Track published theses and their subsequent outcomes against appropriate benchmarks, including failures.
6. Continuous monitoring of incoming data, one official comprehensive monthly assessment, and exceptional reviews under documented triggers.
7. Maintain a permanent, immutable-as-published archive of conclusions, evidence, model versions, and outcomes; disclose revisions transparently.
8. AI may explain, investigate, and propose hypotheses, but cannot bypass deterministic evidence validation, compliance rules, or publication approval.
9. Prefer a maintainable shared data and research engine, small testable modules, minimal duplication, and incremental, independently usable releases.
10. When evidence is missing or stale, show **Insufficient Evidence** rather than inventing conclusions.

## Eight product areas

1. **Executive Economic Dashboard:** current conditions, direction, risks, implications, uncertainty and sources; understandable in three minutes.
2. **Economic Forecasting Laboratory:** competing models, scenarios, historical validation, false alarms, calibration, forecast archive, benchmark comparisons.
3. **Historical Cycle Research:** expansions, recessions, credit crises, bubbles, overinvestment, inflationary contractions, shocks, recovery periods, negative controls and chronological episodes.
4. **Investment Intelligence:** eleven GICS sectors, industries, company fundamentals, ETFs, bonds, commodities, other asset classes, valuations, relative performance and illustrative nonpersonalized portfolio scenarios.
5. **Global Economic Intelligence:** developed/emerging economies, trade, currencies, monetary policy, sovereign/corporate debt, supply chains and cross-border shock transmission, with a U.S. primary lens.
6. **AI Research Assistant:** source-grounded explanation, comparison, hypothesis generation and constrained autonomous research proposals.
7. **Research Library:** collapsible methodology, dated observations, source provenance, datasets, model documentation, charts and accessible exports.
8. **Research Accountability Center:** original published forecasts and investment theses, subsequent realized outcomes, benchmarks, errors, changes and research lessons.

## Investment-research and legal safeguards — mandatory

**Scope:** general, broadly published educational and investment research, not advice personalized to any person's objectives, finances, risk tolerance or circumstances.

- Do not solicit personal financial profiles for recommendations, generate individualized buy/sell/hold instructions, personalized allocations, or suitability determinations.
- Clearly separate descriptive economic analysis, investment hypotheses, and validated forecasts. No claims of guaranteed performance or certainty.
- Label hypothetical portfolios and backtests prominently with methodology, assumptions, risk, fees, transaction costs, benchmark and survivorship/lookahead limitations.
- Publish dates, material assumptions, conflicts of interest, sources, and risk warnings with investment analysis. Keep editorial research independent of sponsors.
- AI research features must decline requests for personalized investment recommendations and instead provide general research and educational context.
- Require qualified U.S. securities counsel to review the actual product, business model, content, disclosures, registration/exemption issues, subscription arrangements, and relevant federal/state law **before commercial launch** of investment-related features. General publication and disclaimers alone do not guarantee exemption from investment-adviser rules.
- Require explicit human approval for any change to these compliance boundaries.

### Proposed public notice

> **Educational Research — Not Personalized Financial Advice.** Economic Cycle Research publishes general economic and investment research for informational and educational purposes. Analysis reflects dated evidence, historical trends, financial data, models, and assumptions that may be incomplete or incorrect. Past performance does not guarantee future results. Content is not tailored to any individual's objectives, finances, risk tolerance, or investment needs, and is not a personalized recommendation to buy, sell, or hold a security. Investing involves risk, including loss of principal. Conduct independent research and consult a qualified professional for advice about individual circumstances.

Show this notice in the site footer and more prominently on investment analysis, scenario, and AI research surfaces. Legal counsel must approve final wording and practices.

## Shared architecture

**Acquisition -> provenance and validation -> canonical observations and immutable research snapshots -> descriptive analysis and competing hypotheses -> independent backtesting -> publication and compliance gate -> executive and deep-research experiences -> archived outcomes and performance evaluation.**

No individual feature should invent a competing data pipeline, alternative source-of-truth, or unreviewed publication channel.

## Product release gates

- Data: provenance, observation date, vintage/availability date, freshness, source quality, completeness, reproducibility.
- Research: explicit methodology, contrary evidence, negative controls, independent episodes, chronological holdout, out-of-sample metrics and benchmarks where prediction is claimed.
- Investment: dated valuation and earnings, benchmarks, return basis, fees and limitations, separation of economic fit and investment attractiveness.
- Software: unit/integration/regression tests, accessibility/mobile checks, stable navigation, artifact contract, deploy verification and rollback/preservation.
- Compliance: approved general-research boundaries, disclosures, AI restrictions, counsel review before commercial release.
- Operations: monthly publication, change log, alert criteria, incident handling, audit trail and costs.

## Success criteria

- New visitors understand the current assessment within three minutes.
- Every material conclusion links to evidence and dates.
- Predictions are published only when validation qualifies them; historical claims never use future information.
- Archived research cannot be silently rewritten to improve perceived accuracy.
- Monthly publication and rollback operate reliably.
- Sector research separates business-cycle fit from valuations and expected returns.
- Responsive, accessible interface supports casual readers and deep researchers.
- Investment-related commercial release is legally reviewed.

## Governance

This blueprint is the approved **destination**, not permission to implement everything immediately. Future version roadmaps must explicitly map each milestone to this document, identify prerequisites, preserve stable V6.1 functionality, and keep unvalidated capabilities out of production claims. Material changes to product mission, research integrity or compliance require owner approval.
