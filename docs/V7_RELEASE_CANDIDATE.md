# Economic Cycle Research — Version 7 Release Candidate (market-vulnerability edition)

**Status:** RELEASE CANDIDATE. **Not merged into `main`. Not deployed.** It awaits owner visual and technical evaluation and explicit approval.
**Candidate code commit (`v7-development`):** `c70d48aa7cab650964f374eb34b6eb78f282aa63` (later commits add only documents and evidence; no code changes)
**Production baseline (unchanged):** V6.3, `main` at `7dfc811e765fd8ca927f082c2fa0c63948799bb3`. It remains production and the rollback target.
**Research basis:** `docs/V7_CRASH_RESEARCH_REPORT_2026-11-18.md` and the pre-registration `docs/V7_PREREGISTRATION_CRASH_RESEARCH.md`. This release implements P1–P4 of that report.

## 1. What the application now answers (actual pipeline output)
The homepage leads with **"How vulnerable is the stock market to a major decline?"**

| Question | What the site shows (monthly run `44326670757`, real data fetched 2026-11-18) |
|---|---|
| Are historical warning conditions present? | **0 of 5 tested warning signs are on, and 2 are close to their trigger.** Market trend: the S&P 500 is +0.9% above its 10-month average (Nov 16); the Nasdaq is −3.0% below its own. Market breadth: 41% of industries are above trend against a 40% trigger (Sep). Clear: yield curve +1.08 (12-month low +0.31, Oct); financial conditions −0.48 (Nov 13); credit spread 1.46 points (Oct). Valuation: **not current** (the latest CAPE is from 2023-09), so it is not counted. |
| Why they matter | Each warning shows its record since 1927–1971: how much more often a 20% fall followed (1.3–2.3×), the bear markets it missed, and the share of false alarms. |
| How today compares with past pre-crash environments | A table of the median at 14 past bear-market peaks against today. Breadth is far weaker (41% vs 69%). The yield curve and credit spreads look calmer. The market trend is weaker than at a typical peak. |
| What would raise or ease concern | Each warning's trigger, plus what would reverse the near-trigger readings. |
| What the evidence cannot predict | Timing, depth, or whether a decline happens at all. The combined model failed out of sample, so no crash probability or overall score is published. Sudden shocks (1987, 2020) gave little warning. |
| Supporting context | The economy is "Expanding" (data through Sep 2026) on its own Economy page, with a real production chart. The 12-month job-market outlook remains the only published number: about 30%, typical. Sector research is unchanged. |

Concerns listed on Home:
- the S&P 500 is near its trend line and the Nasdaq is below its own;
- the Nasdaq is 11.8% below its high;
- breadth is near its trigger;
- small companies are lagging large ones;
- VIX is 22.9, up 51% in 3 months;
- stock value relative to GDP is at a record (labelled as not yet a tested warning).

Reassurances listed: the yield curve is not inverted, credit spreads are narrow, financial conditions are loose, and the economy is expanding.

## 2. Charts (all data-driven, dated, with text alternatives)
- **A century of market declines** (1926–2026): U.S. total market drawdown, with recessions shaded and the deepest declines labelled. A compact version since 1950 appears on Home.
- **Index performance:** S&P 500, Nasdaq, Nasdaq-100 and Dow returns and distance from high (daily closes). A one-year chart is rebased to 100.
- **Breadth and leadership:** the share of industries above trend since 2000, with its 40% trigger; leaders and laggards over 12 months; small versus large companies.
- **Credit and financial conditions:** the BAA − 10-year spread since 1960 with its stress threshold; the Chicago Fed NFCI since 1971.
- **Warnings before past bear markets:** which of the six warnings were on in the 12 months before each bear-market peak since 1954.
- **Economy versus market:** production growth against market drawdown since 1985. Markets fell 20% or more in 1987, 1998, 2018 and 2022 while production was growing.
- **The decorative cycle gauge was removed.** No hypothetical forecast is drawn anywhere.

## 3. Daily data versus monthly conclusions
- Every warning shows its own date and frequency: daily (S&P 500 trend), weekly (NFCI) or monthly (curve, credit, breadth).
- Economic conclusions remain monthly.
- Market data are refreshed in each monthly build. The build gate requires daily market data no more than 7 days old and no fetch gaps, and records the warnings in `v7_release_manifest.json` (`market_warnings`).
- **Limitation:** the published market readings are as of the monthly build. They are not refreshed every day; daily refresh of the market panel is a possible follow-up.

## 4. Scientific integrity (preserved)
- The failed combined crash model is unpublished. Its out-of-sample results are disclosed on the Market Risk page (skill −0.20 to −0.35).
- No historical frequency is presented as today's odds. Records are shown as "about N× as often as usual", together with misses and false alarms.
- The site contract requires both market-risk pages to state that no crash probability is published, and rejects "chance/probability of a crash … %".
- Unchanged:
  - the job-market outlook gate;
  - the approved-outlook allowlist;
  - unrated sector attractiveness;
  - all disclaimers.

## 5. Production integration and release safety
- **Monthly assessment:** fetches market data (`v7_crash_research.py fetch`), runs the analysis inside `v7_release.py monthly` and gates on freshness.
- **Daily publisher:** unchanged in design: promote, preserve or leave V6 as home; verify live; rollback.
- **New during this pass:** an invalid candidate bundle is now rejected and the accepted publication kept, instead of aborting the whole deployment. This was found when the rehearsal met a pre-change bundle.
- **Rehearsal** `44326671926` on the real monthly artifact:
  - `NEW_QUALIFIED`;
  - `V7_SITE_CONTRACT_PASS` (17 pages);
  - `V7_LIVE_VERIFIED` (18 files);
  - `PRESERVED_PREVIOUS`;
  - old-bundle notice added;
  - unreachable live site → deployment blocked;
  - rollback bundle valid (V6.2 manifest `7dfc811`).

## 6. Verification
| Check | Result |
|---|---|
| Tests | `python -m unittest discover -s tests`: **532 OK** |
| Historical evidence | Crash research reproduces exactly from `data/v7_crash/`. Forecast and sector evidence reproduce in CI run `44326671198`. |
| Layout | 7 pages × 320/375/390/430 px × light/dark × 100%/200% text, all sections expanded: **0 problems** (`docs/evidence/v7_rc_layout_sweep_2026-11-18.txt`) |
| Accessibility | axe-core 4.10.2, WCAG 2.2 A/AA, 17 pages × 3 widths × 2 schemes: **0 violations** apart from position-dependent `target-size` findings. These are 56 px section headings sitting under the sticky tab bar at load, and each passes when scrolled clear. |
| Keyboard | Every link and section is reachable. Focus is never hidden behind the tab bar, except the bear-market matrix scroll region, which is taller than a phone screen and so only partly visible when focused (allowed by WCAG 2.4.11). |
| Security | No JavaScript, forms or external resources; standard-library generators; read-only rehearsal workflow |

## 7. Screenshots (actual pipeline output)
Folder: [`docs/evidence/v7-rc-screenshots/`](evidence/v7-rc-screenshots/). Captures at 390 px are at 2× (first screen) and 1× (full page); desktop is 1280 px.
- **Home:**
  - [390 first screen](evidence/v7-rc-screenshots/390-light-index-first-screen.png) · [390 full page](evidence/v7-rc-screenshots/390-light-index-full-page.png)
  - [390 dark first screen](evidence/v7-rc-screenshots/390-dark-index-first-screen.png) · [390 dark full page](evidence/v7-rc-screenshots/390-dark-index-full-page.png)
  - [1280 first screen](evidence/v7-rc-screenshots/1280-index-first-screen.png) · [1280 light full page](evidence/v7-rc-screenshots/1280-light-index-full-page.png) · [1280 dark full page](evidence/v7-rc-screenshots/1280-dark-index-full-page.png)
- **Market Risk:**
  - [390 first screen](evidence/v7-rc-screenshots/390-light-market-risk-first-screen.png) · [390 full page](evidence/v7-rc-screenshots/390-light-market-risk-full-page.png) · [390 all sections expanded](evidence/v7-rc-screenshots/390-light-market-risk-expanded.png)
  - [390 dark first screen](evidence/v7-rc-screenshots/390-dark-market-risk-first-screen.png) · [390 dark full page](evidence/v7-rc-screenshots/390-dark-market-risk-full-page.png)
  - [1280 first screen](evidence/v7-rc-screenshots/1280-market-risk-first-screen.png) · [1280 light full page](evidence/v7-rc-screenshots/1280-light-market-risk-full-page.png) · [1280 dark full page](evidence/v7-rc-screenshots/1280-dark-market-risk-full-page.png)
- **Economy:**
  - [390 first screen](evidence/v7-rc-screenshots/390-light-forecast-first-screen.png) · [390 full page](evidence/v7-rc-screenshots/390-light-forecast-full-page.png)
  - [390 dark first screen](evidence/v7-rc-screenshots/390-dark-forecast-first-screen.png) · [390 dark full page](evidence/v7-rc-screenshots/390-dark-forecast-full-page.png)
  - [1280](evidence/v7-rc-screenshots/1280-forecast-first-screen.png)
- **Sectors:**
  - [390 first screen](evidence/v7-rc-screenshots/390-light-sectors-first-screen.png) · [390 full page](evidence/v7-rc-screenshots/390-light-sectors-full-page.png)
  - [390 dark first screen](evidence/v7-rc-screenshots/390-dark-sectors-first-screen.png) · [390 dark full page](evidence/v7-rc-screenshots/390-dark-sectors-full-page.png)
  - [1280](evidence/v7-rc-screenshots/1280-sectors-first-screen.png)
  - Energy detail: [390 full page](evidence/v7-rc-screenshots/390-light-sector-energy-full-page.png) · [390 expanded](evidence/v7-rc-screenshots/390-light-sector-energy-expanded.png) · [1280](evidence/v7-rc-screenshots/1280-sector-energy-first-screen.png)
- **Research & Data:** [390 first screen](evidence/v7-rc-screenshots/390-light-research-first-screen.png) · [390 full page](evidence/v7-rc-screenshots/390-light-research-full-page.png) · [1280](evidence/v7-rc-screenshots/1280-research-first-screen.png)
- **Track Record:** [390 first screen](evidence/v7-rc-screenshots/390-light-track-record-first-screen.png) · [390 full page](evidence/v7-rc-screenshots/390-light-track-record-full-page.png)
- **Other:**
  - Home: [320 px](evidence/v7-rc-screenshots/320-light-index-first-screen.png) · [430 px](evidence/v7-rc-screenshots/430-light-index-first-screen.png) · [200% text](evidence/v7-rc-screenshots/390-light-index-200pct-text.png) · [expanded](evidence/v7-rc-screenshots/390-light-index-expanded.png)
  - [Bottom navigation at the end of a page](evidence/v7-rc-screenshots/390-light-sectors-scrolled-to-end.png)

## 8. Limitations and outstanding items
- **Unverified (needs a person):** real iOS and Android devices; VoiceOver and TalkBack; a plain-language review; the 30-second comprehension test with a real reader.
- **Data:**
  - CAPE is stale (2023-09), and equity/GDP is not yet back-tested.
  - Earnings revisions, margin debt, advance/decline breadth and Russell 2000 data are unlicensed.
  - French market data lag 1–2 months.
  - FRED keeps only about one year of S&P 500 and three years of high-yield spread history.
- **Method:** there are 16 bear markets in 100 years, and overlapping monthly origins are not independent. Warning thresholds are conventional, fixed in advance and not optimised.
- **Market readings** refresh with each monthly build, not daily.

## 9. CI and links
- Monthly assessment with V7 (candidate code): <https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/44326670757>
- V7 Release Rehearsal: <https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/44326671926>
- V7 Forecast Research (full suite, evidence reproduction, crash research): <https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/44326671198>
- Runbook: `docs/V7_RELEASE_RUNBOOK.md` · Owner checklist: `docs/V7_OWNER_EVALUATION_CHECKLIST.md`

## 10. Release authorization
`v7-development` has **not** been merged into `main`, and nothing has been deployed. Merge and deployment require explicit owner approval.
