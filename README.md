# Economic Cycle Research

**Operating model: DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.**

- **Daily source evidence:** `.github/workflows/daily-economic-source-acquisition.yml` acquires FRED, BLS and BEA observations each calendar day, checks acquisition status, and archives evidence. Acquisition alone does not authorize source promotion or predictive claims.
- **Monthly descriptive assessment:** `.github/workflows/industry-deviation-descriptive.yml` runs on the 20th of each month (13:20 UTC), with manual and change-triggered verification available. Each observation retains its own release and freshness limitations. Only an accepted, non-stale assessment qualifies for current publication.
- **One GitHub Pages dashboard:** `.github/workflows/milestone1.yml` validates and deploys the dashboard after relevant changes and completed monthly assessments. It no longer runs the comprehensive historical/weekly research suite on a daily timer. Accepted monthly reporting is primary; older weekly research remains archival.
- **Publication safety:** A failed or unqualified monthly update must not replace a previously accepted monthly report. If a prior report cannot be recovered reliably, publication fails closed.

The historical research and Version 5 descriptive safeguards are retained. Historical publisher-original point-in-time certification, independent predictive validation, and model forecasts remain **BLOCKED** unless explicitly qualified by their existing evidence gates. Successful acquisition is not equivalent to approved current economic conclusions.

**Release evidence:** Review the GitHub Actions run logs and artifacts for each of the three workflows. A manually dispatched success is not proof of a scheduled execution. Do not claim full operational completion until daily and monthly scheduled executions and the public dashboard have been independently verified.

## Version 6 implementation handoff (2026-11-04)

Version 6 work has started on main. The existing V5 monthly research and Pages workflows remain the source of truth. Added `scripts/v6_sector_intelligence.py` and its tests for evidence-gated 11-sector coverage, plus `scripts/v6_public_site.py` and its tests for accessible overview, sector, monthly and research pages. The monthly workflow now generates V6 pages only after V5 integrated acceptance; the existing Pages workflow copies sector and methodology pages only from a qualified PASS monthly artifact.

**Not yet released:** The new pages have not been verified live. Run `python -m unittest discover -s tests -p 'test_v6_*.py' -v`, inspect the triggered monthly Actions run and its uploaded artifact, then verify the Pages run and public links. Monthly PASS artifacts may be unavailable or stale; in that case preserve the existing dashboard and do not claim a current assessment. The sector evidence registry is intentionally empty until verifiable point-in-time total returns, earnings, valuation, benchmark and economic data have been integrated. Do not infer favorable investment ratings from macro data alone.

**Next implementation batch:** Connect sourced sector/industry datasets and histories to the existing acquisition/assessment process; ensure last-good public pages survive failed retrieval; expand indicator provenance and monthly changes; complete end-to-end release checks, actual schedule evidence, and final V6 acceptance. No new roadmap or parallel research workflow is needed.
