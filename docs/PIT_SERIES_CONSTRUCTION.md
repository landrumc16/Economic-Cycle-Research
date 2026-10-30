# Point-in-time series construction contract

The `scripts/build_pit_series.py` transformation chooses the most recently published vintage **available on each decision date**, separately for each economic observation. It rejects future publication dates, future vintage dates, ambiguous latest revisions, missing values and non-finite values.

Example:
```bash
python scripts/build_pit_series.py --ledger verified_release_ledger.csv --output audit-output/pit_series.json
```

**Critical boundary:** A syntactically valid release ledger is not independently verified evidence. This transformation does not retrieve or authenticate publisher release archives, does not establish the exact intraday release time, and does not certify ALFRED/BEA historical coverage. The input ledger must first be independently verified against archived releases, with UTC time and timezone documented where decisions are intraday.

No dashboard promotion or 0/3 certification change is authorized by this script. A future milestone increment must acquire and reconcile the original release evidence, not infer it from present-day revised values.
