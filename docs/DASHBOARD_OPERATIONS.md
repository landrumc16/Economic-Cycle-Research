# Dashboard operations (implementation checkpoint)

The canonical dashboard generator is `scripts/build_dashboard.py`. GitHub Actions workflow `.github/workflows/milestone1.yml` builds `audit-output/dashboard/index.html` and `state.json` and uploads them in `milestone1-audit-evidence`.

## How to use it today

Open the latest successful [GitHub Actions run](https://github.com/landrumc16/Economic-Cycle-Research/actions), open the `milestone1-audit-evidence` artifact, and open `dashboard/index.html` locally. This is an offline HTML dashboard, not a publicly hosted site. The repository may be private; do not turn on public GitHub Pages or publish research data without explicit authorization.

## Refresh and evidence

Pull-request CI uses the dated workbook export and can have missing macro data. Scheduled/manual workflows attempt FRED, BLS, and BEA data acquisition. API quotas and source failures can prevent refresh; a green offline CI run **does not** mean fresh source acquisition succeeded. Dashboard freshness is relative to the dated snapshot, not wall-clock live freshness. The `--strict-macro` option requires the macro readout file; `--require-macro-values` additionally requires nonmissing growth, labor, and inflation observations. Neither option certifies publisher-original point-in-time vintages.

## Release conditions

Do not claim a current economic cycle stage, crash probability, or investment recommendation until separate release-vintage, holdout, calibration, and human-approval gates pass. Historical cluster and stress-window data are exploratory, with overlapping observations. Preserve workbook laws L01–L18 and the roadmap in `docs/ROADMAP.md`.

## Next engineering work

Implement a controlled source-refresh manifest with per-series timestamps and status; then add a **private**, access-controlled hosted view only after the owner selects a hosting destination and approves the data visibility. Do not create duplicate dashboard implementations or scheduled jobs.
