# Weekly Economic Assessment and Dashboard

## Production path

The Industry Deviation Descriptive Data GitHub Actions workflow runs each Monday at 13:20 UTC and on manual dispatch or relevant pushes. It fetches public FRED current-vintage observations, derives credit growth and housing/income divergence, runs historical comparisons and release gates, then builds the weekly economic assessment and portable HTML dashboard.

Open the workflow run's **industry-deviation-descriptive-evidence** artifact. Inside `audit-output/`:
- `weekly_economic_assessment.md`: concise human-readable economic research assessment.
- `weekly_economic_assessment.json`: dated and source-labelled machine-readable observations.
- `economic_dashboard.html`: standalone responsive dashboard; open locally in a browser.
- `economic_dashboard.json`: normalized dashboard and optional comparison data.
- `industry_credit_joint_summary.md`: historical acceleration/credit comparison.
- `CSUSHPINSA_fundamentals_credit_{6,12,24}m.json`: housing acceleration/income/credit three-factor comparisons.
- `industry_multifactor_acceptance.json`: evidence gate result.

## Week-over-week comparison

The dashboard generator accepts `--previous path/to/prior/weekly_economic_assessment.json`. Download a prior run's assessment JSON and supply it when regenerating. The scheduled workflow currently builds without a prior-run input; therefore, it does **not** yet claim automatic week-over-week deltas. This is an explicit outstanding integration item, not a hidden zero change.

## Interpretation safeguards

The dashboard uses a common month across all five source series; this favors comparable dates over apparent recency. It shows the lag and flags stale observations. It describes observed expansion-related conditions but does not assign a calibrated economic-cycle phase or crash probability. The weekly schedule is a reporting cadence; source data are primarily monthly. Current-vintage data are not point-in-time certified.

## Operational verification still required

Confirm a successful GitHub Actions run, validate source ingestion and resulting numerical output, and check artifact availability. A commit alone does not establish execution success.
