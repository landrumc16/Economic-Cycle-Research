# Version 7 release, operation and rollback runbook

**Rule:** DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.
**Code:** `scripts/v7_release.py` (monthly gate and manifest, daily publication, verification); tests are in `tests/test_v7_release.py`.

## How V7 runs in production (after owner-approved merge only)
1. **Monthly: Monthly Economic Cycle Assessment** (`industry-deviation-descriptive.yml`, on the 20th and on pushes to `main`).
   - **V6 chain:** runs unchanged and produces the monthly gate (`weekly_release_acceptance.json`) and the V6.2 bundle.
   - **V7 inputs:** fetches eight FRED series from 1948 into `data/v7_fresh/`, plus French industry and factor returns, Damodaran annual P/E and ALFRED first releases into `data/v7_research_fresh/`.
   - **Build:** `v7_release.py monthly` reruns the V7 tests, re-evaluates every outlook out of sample, builds the sector research and the site into `audit-output/v7-site/`, and writes `v7_release_manifest.json`.
   - **The manifest is `NEW_QUALIFIED` only if all of the following hold:**
     - the V6 monthly gate is `PASS`;
     - unemployment data are no more than 3 months old;
     - French returns are no more than 4 months old;
     - all 11 sectors are covered and none shows an attractiveness rating;
     - the V7 site contract passes.

     Otherwise the manifest is `FAILED`, with its reasons.
   - **Allowlist:** only `labor_deterioration` at 12 months may show a number. Any other outlook that newly passes the gate is withheld as "not enough evidence" and listed under `held_for_review` for the owner.
   - **Isolation:** the V7 steps are `continue-on-error`, so a V7 failure never blocks the V6 monthly artifact.
2. **Daily: Milestone 1 Pages workflow** (`milestone1.yml`, daily at 12:15 UTC, and after each monthly run).
   - The existing V6 steps run unchanged first.
   - `v7_release.py publish` then decides the V7 outcome:
     - **`NEW_QUALIFIED`:** a qualified monthly V7 bundle, no older than the live one, becomes the home page and owns `index.html`, `forecast.html`, `sectors.html`, `track-record.html`, `research.html`, the 11 `sector-<name>.html` pages, `forecast_archive.csv` and `v7_release_manifest.json`.
     - **`PRESERVED_PREVIOUS`:** with no qualified bundle, the live V7 bundle is recovered and each page is checked against the SHA-256 hashes in its manifest. If it was accepted more than 45 days ago, every page gets a visible notice: "A newer monthly assessment has not yet passed our checks".
     - **`NOT_PUBLISHED`:** V7 has never been live and there is no qualified bundle, so the V6 dashboard stays home.
     - **Blocked:** if the live V7 bundle is unreachable, incomplete, tampered with or unqualified, the deployment is refused.
   - After deployment, every V7 file and the manifest are compared byte for byte with the accepted publication (`verify_live`, with retries).
   - The non-colliding V6.2 pages (`overview.html`, `historical.html`, `monthly-research.html`, `sector-01…11.html`, `v62_release_manifest.json`) and the V5 archive stay published as unlinked archives. The V6.2 manifest and preserve logic are unchanged.

## Release procedure (owner approval required)
1. The owner reviews `docs/V7_RELEASE_CANDIDATE.md`, the screenshots and `docs/V7_OWNER_EVALUATION_CHECKLIST.md`.
2. The owner explicitly approves a merge of `v7-development` into `main`. **Nothing is merged or deployed without this.**
3. The merge push to `main` triggers the Monthly assessment, because `scripts/**` changed. When it finishes, Milestone 1 runs through `workflow_run`. Confirm that:
   - the monthly summary shows `V7 promotion: NEW_QUALIFIED`;
   - the Milestone 1 log shows `{"outcome": "NEW_QUALIFIED", ...}` and `PUBLIC VERIFIED: {'status': 'V7_LIVE_VERIFIED', ...}`;
   - the live `v7_release_manifest.json` `build_commit` equals the merge commit.

   The push also starts an immediate Milestone 1 run. It will report `NOT_PUBLISHED`, because no monthly V7 bundle exists yet, and it leaves V6 as home. This is expected.
4. Inspect the live site at 390 px and on desktop. Record the run IDs and live URL in the closeout.

## Rollback
- **Fast (no code change):** restore the last pre-V7 Pages bundle. Every successful Milestone 1 run uploads `milestone1-audit-evidence` (30 days). Its `dashboard/` folder is the deployed site, and the V7 Release Rehearsal checks that this bundle is valid. To restore it, revert the merge commit on `main`, as below.
- **Revert:** `git revert -m 1 <merge>` on `main`, with owner approval.
  - The revert push triggers the Monthly assessment, which produces a fresh qualified V6.2 bundle. The following Milestone 1 run publishes V6 with `index.html` equal to `overview.html`.
  - Caveat: the Milestone 1 run started immediately by the revert push may recover `sectors.html` and `research.html` from the live V7 site, because V7 and V6 share those file names. The V6 site is fully clean once the monthly-triggered run completes, normally within about 20 minutes.
  - If the monthly gate is not `PASS` at that moment, re-run the Monthly assessment manually, or redeploy the archived pre-V7 bundle.
- **Verify the restored site:**
  - `v62_release_manifest.json` matches the restored bundle;
  - `index.html` equals `overview.html`;
  - there are 11 sector pages;
  - the source dates are as before.

## Stale or failed data
- A failed monthly gate or stale V7 inputs never promote new V7 conclusions; the accepted bundle is kept and later carries a visible notice.
- A V7 bundle is never edited to look current.
- Daily runs republish the accepted monthly conclusions; daily source acquisition continues unchanged.

## Known limitations
- Most history uses current-vintage data. Only the labour outlook was re-checked on data as first published.
- Sector figures use industry proxies, not GICS indices.
- Valuations are an annual Damodaran vintage, so attractiveness stays unrated.
- This is educational research, not personalized financial advice.
