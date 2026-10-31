# Historical point-in-time ledger

A machine-readable row is one observation as known on one decision date.

Required columns:

`series,observation_date,publication_date,decision_date,vintage_date,value,source_url`

Run `python scripts/validate_pit.py --csv evidence/pit_ledger.csv` after obtaining publisher-authenticated release/vintage records.

The validator checks dates, duplicates, values and HTTPS provenance references. It does not fetch original pages or prove that a recorded value was published on the stated date. Do not use a revised FRED observation to populate an earlier vintage. Keep every missing historical observation missing; do not interpolate.

## Acceptance boundary

- BLS U3/CPI current-revised full-series independent comparison: pending GitHub-hosted acquisition.
- BEA GDP original-publisher full-series comparison: original BEA file required.
- BLS/BEA original publication dates and historical ALFRED vintages: independently corroborated records required.
- Google Sheets promotion: explicitly blocked until all series and release-time checks pass.
