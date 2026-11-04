# Economic Cycle Research

**Operating model: DAILY DATA. MONTHLY CONCLUSIONS. ONE DASHBOARD.**

- **Daily source evidence:** `.github/workflows/daily-economic-source-acquisition.yml` acquires FRED, BLS and BEA observations each calendar day, checks acquisition status, and archives evidence. Acquisition alone does not authorize source promotion or predictive claims.
- **Monthly descriptive assessment:** `.github/workflows/industry-deviation-descriptive.yml` runs on the 20th of each month (13:20 UTC), with manual and change-triggered verification available. Each observation retains its own release and freshness limitations. Only an accepted, non-stale assessment qualifies for current publication.
- **One GitHub Pages dashboard:** `.github/workflows/milestone1.yml` validates and deploys the dashboard after relevant changes and completed monthly assessments. It no longer runs the comprehensive historical/weekly research suite on a daily timer. Accepted monthly reporting is primary; older weekly research remains archival.
- **Publication safety:** A failed or unqualified monthly update must not replace a previously accepted monthly report. If a prior report cannot be recovered reliably, publication fails closed.

The historical research and Version 5 descriptive safeguards are retained. Historical publisher-original point-in-time certification, independent predictive validation, and model forecasts remain **BLOCKED** unless explicitly qualified by their existing evidence gates. Successful acquisition is not equivalent to approved current economic conclusions.

**Release evidence:** Review the GitHub Actions run logs and artifacts for each of the three workflows. A manually dispatched success is not proof of a scheduled execution. Do not claim full operational completion until daily and monthly scheduled executions and the public dashboard have been independently verified.
