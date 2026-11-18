# Economic Cycle Research — Version 7 Release Candidate

**Status:** RELEASE CANDIDATE. **Not merged into `main`. Not deployed.** It awaits owner visual and technical evaluation and explicit approval.
**Candidate code commit (`v7-development`):** `d57358d87990998345ae5f44366f63f2fbd5718c`. Later commits on the branch add only this report and evidence files; there are no code changes. The exact branch head to merge is given in the owner's approval request.
**Production baseline (unchanged):** V6.3, `main` at `7dfc811e765fd8ca927f082c2fa0c63948799bb3`. It remains production and the rollback target.

## 1. Recommendation
**Ready for owner evaluation.** M5 integration and M6 release preparation are complete and verified. The outstanding items are testing by a person:
- real-device checks (iOS and Android, including the safe area);
- screen readers (VoiceOver and TalkBack);
- a plain-language review.

None of these could be performed by the development agent, so they are listed as **unverified**, not passed. There are no technical release blockers. A licensed valuation-data subscription is **not** a blocker.

## 2. What the application currently shows (actual pipeline output of the candidate commit)
Real data from FRED, the French Data Library and Damodaran were fetched in CI on 2026-11-18. The pipeline is monthly assessment run `44307600691`, published through the rehearsal of the daily publisher.

| Question | Answer shown |
|---|---|
| Where is the economy? | **Expanding**, direction **Firming**, evidence **Moderate**. Assessment dated 2026-10-20, using data through 2026-09. |
| Where may it be heading? | **Job market weakens within 12 months: about 30%**. That is *Typical* against the 28% historical average (origin 2026-10). This is the only published number. |
| What is not published | 3- and 6-month job-market outlooks, all recession-under-way and new-recession outlooks, and all inflation outlooks. Each shows **"Not enough evidence"** with a plain reason: *too confident*, *no better than the long-run average* or *weak at ranking risk*. 11 of 12 outlooks are unpublished. |
| Sectors worth researching now | **Energy** (+31 pts vs market over 12 months, cyclical, supportive backdrop), **Information Technology** (+26), **Materials** (+6), **Industrials** (+2). |
| Monitor | **Real Estate** (−21 pts, cyclical, supportive backdrop). |
| Lower priority for now | Financials (−6), Health Care (−3), Consumer Staples (−12), Utilities (−12), Consumer Discretionary (−17), Communication Services (−27). |
| Investment attractiveness | **Insufficient evidence** for all 11 sectors. Only an annual Damodaran valuation vintage is available; a licensed current source is required. |
| Track record | The 12-month job-market outlook since 1972: skill +0.33, ranking 0.83, 15 episodes. On data as first published: +0.31 / 0.82. Failures are shown with ✗. |

"Worth researching" is research guidance, never a recommendation. Every page carries "not personalized financial advice".

## 3. M5 — production integration (complete)
| Requirement | Evidence |
|---|---|
| Connected to the monthly assessment | The `Monthly Economic Cycle Assessment` workflow fetches V7 inputs and runs `scripts/v7_release.py monthly`. The steps are `continue-on-error`, so a V7 failure never blocks V6. |
| Connected to the daily publisher | The `Milestone 1` workflow's publish step promotes a qualified bundle, preserves the accepted one, or leaves V6 as home. A new post-deploy check (`verify_live`) compares every V7 file byte for byte. |
| DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD. | Conclusions change only when a monthly bundle qualifies. Daily runs republish the accepted bundle, and V7 owns `index.html` (one home page). |
| Forecasts and sectors update only when appropriate | The manifest is `NEW_QUALIFIED` only if: the V6 monthly gate is PASS; unemployment data are ≤3 months old; French data are ≤4 months old; 11 sectors are covered with no rating; and the site contract passes. Otherwise it is `FAILED`. An older bundle never replaces a newer one. |
| Approved-outlook allowlist | Only job market at 12 months may show a number. A newly passing outlook is **held for owner review** (tested). |
| Stale-data handling | A preserved bundle accepted more than 45 days ago carries a visible notice on every page. The notice is never stacked, and is removed by the next qualified bundle (tested). |
| Provenance and manifest | `v7_release_manifest.json` records the build commit, build time, assessment date, observation cutoff, source months, gate reasons, published and held outlooks, and SHA-256 hashes of every page. See `docs/evidence/v7_rc_release_manifest_2026-11-18.json`. |
| Acceptance checks | The V7 site contract checks: 16 pages; doctype, viewport, `lang`, `main` and one `h1` on each; the disclaimer; exactly five nav destinations; every internal link; no recession percentage on Home; published badges equal to the manifest; and an unrated attractiveness. |
| Fail closed | An unreachable, incomplete, tampered or unqualified live V7 bundle means **deployment refused**. Transient 5xx and network errors are retried a bounded number of times. This change came from a real Pages 503 seen during the rehearsal. |
| V6.3 not broken | The V6 steps are unchanged. The V6 post-deploy checks are relaxed only for `index.html == overview.html` when a V7 manifest is present. All V6, V6.2 and V6.3 tests pass. |
| Actual data, whole process | The real monthly run on `v7-development` was `44307600691`, followed by **V7 Release Rehearsal** run `44307784658`. The rehearsal took the actual last-deployed production bundle from `main` and showed: `NEW_QUALIFIED`, then `V7_SITE_CONTRACT_PASS` (16 pages), then `V7_LIVE_VERIFIED` (17 files served), then `PRESERVED_PREVIOUS` (identical bytes), then the old-bundle notice, then unreachable site → deployment blocked, then the rollback bundle valid (V6.2 manifest `7dfc811`, 2026-11-17). |

## 4. M6 — release readiness (complete, except testing by a person)
| Check | Result |
|---|---|
| Forecast evidence integrity | The CI `V7 Forecast Research` run `44307784651` (code identical to the candidate) runs the full suite and reproduces the committed forecast and sector evidence from the dated snapshot. The monthly pipeline re-evaluates on fresh data with the same gate. |
| Daily and monthly publication | Rehearsed as above. Daily source acquisition is unchanged. |
| Data freshness and failure recovery | Freshness gate, preserve-previous, old-bundle notice and blocked deployment are tested, and rehearsed on real infrastructure. |
| Navigation and generated pages | Site contract plus tests: 16 pages and every internal link. |
| Mobile and desktop layout | 320/375/390/430 px × light/dark × 100%/200% text × 6 pages, with all sections expanded: **0 problems** (`docs/evidence/v7_rc_layout_sweep_2026-11-18.txt`). Home conclusions end at 1406 px at 390×844, within two screens. |
| Accessibility | axe-core 4.10.2 (WCAG 2.0/2.1/2.2 A/AA), 16 pages × 3 widths × 2 schemes = 96 page checks: **0 violations** in every rule except `target-size`. That rule shows 3 position-dependent findings (dark, 640 px: two sector pages; 320 px: Research). In each, a 56 px-tall, full-width section heading sits under the sticky tab bar at the initial scroll position. Re-tested with the element scrolled clear of the bar, each passes. These are disclosed rather than suppressed. Keyboard: every link and section reachable. Focus is never hidden behind the tab bar (474 focus checks). |
| Security and dependencies | Pages contain no JavaScript, forms, iframes or external resources. Generators use the standard library only. Content is HTML-escaped. Workflows use pinned major versions of GitHub-owned actions only. The rehearsal workflow has read-only permissions and never deploys. |
| Build reproducibility | Deterministic generators; the committed evidence is reproduced in CI. The real-data pages matched the snapshot build except for one revised FRED value (industrial production growth 2.22% → 2.12%), which is a current-vintage revision as expected. |
| Rollback readiness | `docs/V7_RELEASE_RUNBOOK.md`. The pre-V7 production bundle is preserved as a Milestone 1 artifact, and the rehearsal validated it. |
| Tests | `python -m unittest discover -s tests`: **524 OK**. |

Defects found and fixed during M6:
1. Pages 503 handling: added bounded retries.
2. Bottom-tab labels clipped at 200% text: labels now wrap and hyphenate.
3. The wrapped tab bar covered the last content at 200% text: the bar is now sticky instead of fixed.
4. Focus visibility next to the sticky bar: added scroll padding.

## 5. Visual acceptance package — actual pipeline output
Screenshots: [`docs/evidence/v7-rc-screenshots/`](evidence/v7-rc-screenshots/) (rendered with Chromium; phone captures at 2× pixel density).
- **Five experiences at 390 px, first screen and full page:**
  - Home: [first](evidence/v7-rc-screenshots/390-light-index-first-screen.png) · [full](evidence/v7-rc-screenshots/390-light-index-full-page.png)
  - Forecast: [first](evidence/v7-rc-screenshots/390-light-forecast-first-screen.png) · [full](evidence/v7-rc-screenshots/390-light-forecast-full-page.png)
  - Sectors: [first](evidence/v7-rc-screenshots/390-light-sectors-first-screen.png) · [full](evidence/v7-rc-screenshots/390-light-sectors-full-page.png)
  - Track Record: [first](evidence/v7-rc-screenshots/390-light-track-record-first-screen.png) · [full](evidence/v7-rc-screenshots/390-light-track-record-full-page.png)
  - Research & Data: [first](evidence/v7-rc-screenshots/390-light-research-first-screen.png) · [full](evidence/v7-rc-screenshots/390-light-research-full-page.png)
- **Dark mode:**
  - Home: [first](evidence/v7-rc-screenshots/390-dark-index-first-screen.png) · [full](evidence/v7-rc-screenshots/390-dark-index-full-page.png)
  - Forecast: [first](evidence/v7-rc-screenshots/390-dark-forecast-first-screen.png) · [full](evidence/v7-rc-screenshots/390-dark-forecast-full-page.png)
  - Sectors: [first](evidence/v7-rc-screenshots/390-dark-sectors-first-screen.png) · [full](evidence/v7-rc-screenshots/390-dark-sectors-full-page.png)
- **Sector detail:** [Energy, full page](evidence/v7-rc-screenshots/390-light-sector-energy-full-page.png) · [all sections expanded](evidence/v7-rc-screenshots/390-light-sector-energy-expanded.png)
- **Expanded sections and charts:**
  - [Home expanded](evidence/v7-rc-screenshots/390-light-index-expanded.png)
  - [Track Record with the calibration chart](evidence/v7-rc-screenshots/390-light-track-record-expanded.png)
- **Bottom navigation:**
  - [Sectors scrolled to the end](evidence/v7-rc-screenshots/390-light-sectors-scrolled-to-end.png)
  - [200% text](evidence/v7-rc-screenshots/390-light-index-200pct-text.png)
- **Other widths:** [Home at 320 px](evidence/v7-rc-screenshots/320-light-index-first-screen.png) · [Home at 430 px](evidence/v7-rc-screenshots/430-light-index-first-screen.png)
- **Desktop 1280 px:**
  - [Home](evidence/v7-rc-screenshots/1280-index-first-screen.png) · [Home, full page](evidence/v7-rc-screenshots/1280-index-full-page.png)
  - [Forecast](evidence/v7-rc-screenshots/1280-forecast-first-screen.png) · [Sectors](evidence/v7-rc-screenshots/1280-sectors-first-screen.png)
  - [Track Record](evidence/v7-rc-screenshots/1280-track-record-first-screen.png) · [Research](evidence/v7-rc-screenshots/1280-research-first-screen.png)
  - [Energy](evidence/v7-rc-screenshots/1280-sector-energy-first-screen.png)

**30-second test (automated self-evaluation at 390 px, not a human usability test):**
1. "Expanding" with the cycle gauge appears on the first screen.
2. The three outlook rows are on the first screen (two say "Not enough evidence"; one says "About 30%, typical vs 28% average").
3. Four named sectors appear after one scroll.
4. "1 of 12 outlooks pass our reliability test" sits next to them.

Whether an ordinary person grasps all of this in 30 seconds is **unverified until a person tries it** (see the owner checklist).

## 6. Remaining limitations (disclosed, not blockers)
- **Unverified (human):**
  - real iOS and Android devices, including safe-area insets (headless Chromium cannot emulate them);
  - hyphenated tab labels at large text (Linux Chromium lacks hyphenation dictionaries, so labels break mid-word in the screenshots);
  - VoiceOver and TalkBack;
  - a plain-language review.
- Most history uses current-vintage data; only the labour outlook was re-checked on data as first published.
- Recessions since 1972 are few.
- Sector figures use French industry proxies, not GICS indices.
- Valuation is an annual vintage, so attractiveness stays unrated until a licensed current source is chosen (owner decision, optional).
- After merge, the first Milestone 1 run reports `NOT_PUBLISHED` (V6 stays home) until the merge-triggered monthly run qualifies V7. This is expected, and is described in the runbook.
- During a revert, the immediate Milestone 1 run may briefly carry the V7 `sectors.html` and `research.html` until the monthly-triggered V6 republication completes. See the runbook.

## 7. CI and links
- Real monthly assessment with V7, candidate code: <https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/44307600691>
- V7 Release Rehearsal: <https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/44307784658>
- V7 Forecast Research (tests and evidence reproduction): <https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/44307784651>
- Owner checklist: `docs/V7_OWNER_EVALUATION_CHECKLIST.md` · Runbook: `docs/V7_RELEASE_RUNBOOK.md`

## 8. Release authorization
`v7-development` has **not** been merged into `main`, and nothing has been deployed. Merge and deployment require explicit owner approval after visual and technical evaluation.
