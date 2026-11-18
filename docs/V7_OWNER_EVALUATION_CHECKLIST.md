# Version 7 owner evaluation checklist

Tick each item before approving a merge of `v7-development` into `main`. Items marked **(human)** cannot be verified automatically and were not verified by the development agent.

## 1. Understanding in 30 seconds (phone, 390 px)
- [ ] The home page shows where the economy is ("Expanding") without scrolling.
- [ ] The three outlook rows are clear: two say "Not enough evidence"; the 12-month job-market row says "About 30% — typical vs the 28% historical average".
- [ ] "Sectors worth researching" lists named sectors and is reached with one scroll.
- [ ] "1 of 12 outlooks pass our reliability test" makes the evidence standard clear.
- [ ] **(human)** A person unfamiliar with the project can explain the three answers after 30 seconds.

## 2. Visual quality (screenshots in `docs/evidence/v7-rc-screenshots/`)
- [ ] It looks like a polished financial app, not a textbook: compact cards, readable type and clear hierarchy.
- [ ] Light and dark modes both look correct (Home, Forecast, Sectors).
- [ ] The bottom navigation never hides content; expanded sections and charts display correctly.
- [ ] Desktop (1280 px) uses the width sensibly.
- [ ] **(human)** Looks right on a real iPhone and a real Android phone, including the safe area or notch.

## 3. Integrity of what is published
- [ ] Only the 12-month job-market outlook shows a number.
- [ ] Recession and inflation outlooks say "not enough evidence", with plain reasons.
- [ ] Every sector shows investment attractiveness as "Insufficient evidence".
- [ ] "Worth researching" is described as research guidance, never a recommendation.
- [ ] The track record shows failures (✗) and the honest notes.

## 4. Accessibility
- [x] Automated axe-core WCAG 2.2 AA: 0 violations except 3 position-dependent `target-size` findings next to the sticky tab bar, each passing once scrolled clear of it (details in the release candidate report).
- [x] Keyboard reach and 200% text reflow (automated).
- [ ] **(human)** VoiceOver (iOS) and TalkBack (Android) read the cycle gauge, outlook rows and sector rows sensibly.
- [ ] **(human)** Plain-language review by a non-expert.

## 5. Production integration and rollback
- [ ] `docs/V7_RELEASE_RUNBOOK.md` is understood: monthly conclusions, daily republication, preserve-previous, and the visible notice on old bundles.
- [ ] The release rehearsal run succeeded (link in the release candidate report).
- [ ] The rollback route is accepted: revert the merge, then the monthly-triggered V6 republication or the archived pre-V7 bundle.

## 6. Decision
- [ ] Approve merging `v7-development` into `main` at commit `__________`.
- [ ] Or list the changes required before approval.

The licensed valuation data provider is a separate owner decision. It is not a release blocker.
