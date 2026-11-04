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

## Build-to-completion sequence (execute in order)

The steps below are the **implementation order**, not seven separate development programs. Each step produces a user-visible or operational deliverable, passes its acceptance checks, and is committed before the next step. Reuse accepted V5 systems; do not start over.

| Step | Implement | Deliverable | Completion evidence |
| --- | --- | --- | --- |
| 1. Foundation | Inventory only live daily, monthly and Pages entry points; eliminate redundant weekly production; consolidate FRED/BLS/BEA acquisition and source-qualified persistence; verify revision/missing-data handling. | One daily acquisition process and one official monthly research workflow. | Automated source tests, workflow logs, dated acquisition artifacts, and preservation of last valid data on source failure. |
| 2. Economic intelligence | Reuse existing growth, labor, inflation, credit, financial stress and historical research; reconcile individual observation dates and source lags; generate concise narrative, monthly changes and uncertainty. | Structured monthly assessment with plain-English executive findings and detailed evidence. | Regression tests with fresh, lagged, missing and revised inputs; no unsupported forecasts. |
| 3. Sector intelligence | Establish a qualified data inventory for 11 GICS sectors; add relative total-return history, earnings/valuation where sourced, economic sensitivity, industry distinctions, and evidence-gated outlooks. Start with sectors having verifiable coverage; label gaps explicitly. | Sector overview and 11 sector detail entries, each either evidence-backed or marked insufficient evidence. | Source-date and benchmark checks, historical bias controls, and tests that missing data never create favorable ratings. |
| 4. Public experience | Adapt existing GitHub Pages design into a mobile-first overview: monthly executive summary, growth/jobs/prices/stress cards, what changed, sector opportunities, and drill-down links. | One polished public home page understandable without economics training. | Mobile and desktop smoke tests; all headline statements link to evidence; accessible labels and dates. |
| 5. Research deep dives | Reuse existing episode and crash-mechanism studies; expose historical comparison charts, indicator histories, sector detail, methodology, revisions, source links and archives as organized pages/expandable sections. | Navigable research library behind the plain-language home page. | Every major conclusion is traceable; navigation and source links verified; historical limitations visible. |
| 6. Expansion interfaces | Keep acquisition, calculations, report data and HTML separate; document a minimal series/sector registration convention and implement one tested example. Avoid a plugin framework or new runtime unless required. | Small, documented extension points for new indicators, sectors and historical studies. | Demonstrated addition without modifying unrelated workflows or pages. |
| 7. Operational release | Run complete tests; exercise failed acquisition and rejected monthly publication; deploy GitHub Pages; check live URLs, report dates, monthly archives, and scheduling. Update README and close out. | Publicly deployed Version 6 with a first qualified monthly report and release evidence. | Green relevant CI, verified live pages, last-good preservation test, commit IDs, manual and actual scheduled run evidence distinguished. |

### Execution rules and dependencies

- Step 1 is a prerequisite for publication, but Steps 2–5 may reuse accepted historical data while live-source issues are being resolved. Do not stall all UI work on a missing provider key.
- Do not invent valuation or sector return data to complete Step 3. Publish an explicit **Insufficient Evidence** state for gaps; record gaps as limitations rather than silently manufacturing ratings.
- Implement a thin end-to-end slice early: qualified observation → monthly assessment → public summary → linked evidence. Then fill out remaining sectors and research pages.
- Maintain a single monthly publication decision. Stage candidate output, validate, then publish atomically; on failure, retain the last accepted report and expose the reason.
- Record each milestone as **Implemented / Tested / Deployed / Verified**, with links to commits and runs. Do not count a green CI run as proof of published research, or a manual run as scheduled execution.
- Avoid new roadmap files or process layers. Update this roadmap's evidence and the README only.

## Finished product specification

**Public site navigation:** Overview · Economic Indicators · Sectors & Industries · Historical Comparisons · Monthly Reports · Research & Methodology.

**Overview page:** The top of the page answers four questions in ordinary language: *Where is the economy now? What changed since the last assessment? Which vulnerabilities deserve attention? What is uncertain?* It includes a visible assessment publication date, underlying observation dates, four explanatory panels (growth, jobs, inflation, financial stress), and a short sector opportunities/risks preview. Every panel links to a detailed evidence page.

**Indicators page:** Interactive or accessible static time-series charts, definitions, units, changes over time, source links, observation/retrieval dates, revision flags and missing-data notices. Show source-specific freshness, not a misleading common-month current label.

**Sectors & Industries page:** All 11 GICS sectors with an evidence-qualified outlook (**Favorable / Mixed / Caution / Insufficient Evidence**), rationale, valuation versus fundamentals, relative performance against a broad-market benchmark, economic sensitivity and links to industry-level research. Separate observed historical relationships from forward-looking hypotheses. Never infer a stock purchase from sector growth alone.

**Historical Comparisons page:** Different recession/crash mechanisms, comparable historical episodes, contrasting non-crash periods, timelines and charts. State where the analogy breaks down and whether the underlying data are retrospective rather than point-in-time.

**Monthly Reports page:** Latest accepted official assessment first; previous accepted reports accessible; explicit change since last report, observed strengths, weaknesses, risks, and unknowns. A failed or unqualified candidate must not replace an accepted publication.

**Research & Methodology page:** Expandable technical research, full indicator definitions, transformations, original sources, historical vintages, release dates, revisions, sample sizes, backtest limitations, predictive safeguards and archived weekly studies. Make detailed research available without cluttering the overview.

**Visual and usability requirements:** Mobile-first, readable typography, clear labels and charts, sensible color contrast, plain-English summaries, expandable technical detail, fast static-page loading, keyboard-accessible navigation, and no unexplained confidence scores.

**What Version 6 is not:** An automated trading service, personalized investment adviser, guaranteed sector rotation strategy, or certified crash prediction model. Qualified research findings are publishable without claiming predictive validation.

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
