# Version 6 — Complete, Expandable Economic Research Platform

**Status:** Approved product direction; implementation and release verification pending.
**Operating model:** DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.
**Primary outcome:** A finished, reliable product that a layperson can understand immediately, with detailed, traceable research behind every major conclusion.

## Product definition

Version 6 is the next major improvement, not a rebuild of accepted Version 5 research. The public home page answers: **Where does the economy stand, what changed, why does it matter, and what is uncertain?** Readers can drill down into economic indicators, historical comparisons, source data, revisions, methodology, and the research archive. Build for mobile first. Use plain English, with precise terms available in deeper pages.

## Finished experience

1. **Overview (default):** A dated monthly assessment with an executive summary; growth, jobs, inflation, and financial stress sections; direction of change; clear strength/weakness explanations; data freshness notices; links to supporting evidence. No invented composite score.
2. **Indicators:** Chartable current and historical series, units, definitions, latest observation dates, release lags, revisions, source links, and missing-data disclosures.
3. **Historical context:** Distinct crash/downturn mechanisms, episode timelines, comparable and non-comparable conditions, counterexamples, and limitations. Similarity is not a probability.
4. **Monthly assessment:** What changed since the previous accepted report, observed conditions, vulnerabilities, competing explanations, and explicit uncertainty.
5. **Research library:** Expandable, navigable detailed studies, calculations, provenance, source-vintage qualifications, historical methods, and prior reports. Keep historical weekly reports as archives, not competing current conclusions.

## Sector & industry investment intelligence (required V6 feature)

Add a **Sector & Industry Intelligence** section for readers who ask where investments may be more or less attractive given the observed economy. Cover all 11 GICS sectors, with expandable industry-level analysis where reliable data exist. The public summary uses plain-English **Favorable / Mixed / Caution / Insufficient Evidence** research outlooks only when the evidence supports them, never as automatic buy/sell instructions.

- **Economic fit:** Explain how labor, growth, inflation, interest rates, credit conditions, commodity prices and financial stress may help or hurt each sector.
- **Investment fit:** Separately assess earnings trends, valuation relative to history and peers, profitability, balance-sheet resilience, and recent price performance. A strong industry is not necessarily an attractively priced investment.
- **Historical evidence:** Compare relative sector returns versus a broad-market benchmark in comparable conditions, including weak periods and counterexamples. Report observation dates, sample sizes, uncertainty, transaction-cost assumptions, and survivorship/look-ahead caveats.
- **Industry drilldowns:** Highlight subindustries with materially different exposures; distinguish sector-wide trends from company-specific opportunities.
- **Reader experience:** A concise sector overview with evidence-based explanations and a link to a detailed research page per sector; show what would change the assessment.
- **Data integrity:** Source-qualified price/total-return, classification, valuation, earnings and macro datasets are prerequisites. If missing, mark **INSUFFICIENT EVIDENCE**, not a fabricated rating. No investment allocations, model portfolios, target prices, or claims of validated predictive alpha without independently tested evidence.
- **Update cadence:** Refresh dated market data through the existing acquisition architecture where supported; publish sector conclusions with the official monthly assessment. Do not add a competing weekly research pipeline.

**Acceptance:** All 11 sectors are covered or explicitly flagged for missing evidence; research conclusions link to dated source data; sector and industry history can be inspected; current economic fit and valuation are distinct; backtests guard against look-ahead/survivorship bias; failed updates retain the last accepted report; unsupported recommendations are blocked.

## Milestones and acceptance gates

### M1 — Stabilize one operating pipeline
- Preserve Version 5 data, research, and predictive safeguards.
- Consolidate daily FRED/BLS/BEA acquisition and source validation; record missing values, observation dates, revisions, failures, and provenance.
- Keep one official monthly analysis schedule (20th) and stop generating competing weekly conclusions.
- Fail closed on invalid inputs; preserve previously verified observations.
**Gate:** Relevant tests pass; daily and monthly workflows work; source failures do not corrupt prior evidence; scheduled-run evidence is recorded separately from manual-run evidence.

### M2 — Plain-language public dashboard
- Lead with a concise executive answer, then growth, labor, inflation, and financial stress.
- Explain what each movement means, what changed, and why readers should care.
- Mobile-first navigation, accessible charts, no unexplained jargon, source-date labels.
**Gate:** The live home page works on phone and desktop, shows the latest accepted assessment and its underlying observation dates, and links to detailed evidence.

### M3 — Deep research pages
- Reuse existing historical episode and mechanism research rather than recalculating or duplicating it.
- Organize indicator history, methodology, original sources, vintage/revision disclosures, limitations, and archival reports.
- Provide navigation from each major dashboard conclusion to supporting research.
**Gate:** Every substantive headline conclusion has traceable supporting evidence; research pages render and are navigable on mobile.

### M4 — Coherent monthly economic and sector intelligence
- Synthesize growth, employment, prices, credit, asset prices, and financial stress.
- Integrate the Sector & Industry Intelligence section: economic sensitivity, valuation, relative performance, sector-level outlooks, and deep research pages.
- Compare to prior accepted assessment and relevant historical mechanisms; disclose conflicting indicators.
- Use latest individually dated, source-qualified observations; do not force a common observation month for current metrics.
- Preserve descriptive-only release gates; no unvalidated recession/crash probabilities or inevitable-crash claims.
**Gate:** Monthly report is useful and readable, all observations are dated, historical comparison limitations are explicit, and unqualified forecasts remain blocked.

### M5 — Expandable architecture
- Define small, documented interfaces for series definitions, data transformations, research modules, and presentation sections.
- Separate acquisition, validation, assessment, and display. Prefer readable Python and static GitHub Pages outputs; avoid new dependencies unless essential.
- Include one documented example of adding an indicator and its test.
**Gate:** A new indicator can be added without editing unrelated pipelines or rebuilding the dashboard.

### M6 — Release and closeout
- Run relevant automated and regression tests; verify daily acquisition, monthly synthesis, source freshness, missing-data behavior, and predictive safeguards.
- Verify failed or unqualified monthly updates cannot replace the previous accepted report.
- Deploy GitHub Pages and verify actual public URLs, mobile navigation, report links, and artifacts.
- Confirm real scheduled daily and monthly Actions executions (manual success is insufficient); distinguish future scheduled evidence if not yet due.
- Update README with final architecture, operations, recovery, and expansion instructions.
**Gate:** All applicable checks pass with concrete commit IDs, Actions runs, deployment evidence, and a dated official monthly report. Otherwise report exact remaining blockers, not a false completion claim.

## Engineering guardrails

- **Preserve completed research.** No Version 5 reimplementation or speculative forecasting.
- **Build the product, not the process.** No new parallel workflows, dashboards, or endless audits.
- **One source of truth per concern.** Source dates and qualifications travel with every derived observation.
- **Separate current and historical timing.** Retrospective current-vintage history is not a certified point-in-time replay.
- **Publish qualified descriptive findings.** Forecast certification must not block trustworthy descriptive reporting.
- **Safe publication.** Stage, validate, then replace; if validation or retrieval fails, retain the last accepted assessment.
- **Future-proof through simplicity.** Small modules and tests, not a general-purpose plugin framework.

## Release definition

**Version 6 is complete when:** daily data acquisition and monthly assessment operate reliably; sector and industry investment research is source-qualified and clearly explained; one mobile-friendly public dashboard serves clear explanations and linked research pages; source and revision provenance are visible; a qualified official monthly assessment is live; failures preserve previous accepted research; tests and deployment checks pass; scheduled execution evidence is verified or explicitly identified as the sole pending time-dependent check. Future expansion should not require revisiting this foundation.
