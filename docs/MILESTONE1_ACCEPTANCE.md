# Milestone 1 acceptance contract

The workbook is the system of record: `SEM_Historical_Crash_Research_v1`, tabs `DATA PROMOTION GATE` and `BUILD CHECKLIST`. This repository is an evidence-producing pipeline, not a substitute for the gate.

## Sources and strict acceptance

1. **UNRATE**: original BLS `LNS14000000` monthly file vs FRED `UNRATE`. At least 600 overlapping monthly dates, no unexplained mismatches, duplicates or missing observations; preserve both raw files and SHA-256.
2. **CPIAUCSL**: original BLS `CUSR0000SA0` vs FRED `CPIAUCSL`, same full-history coverage and discrepancy audit. Published decimal precision can differ; tolerance 0.005 index points is a provisional check, not approval of material differences.
3. **GDPC1**: BEA NIPA Table 1.1.6 line 1 (real GDP level, billions chained dollars SAAR) independently compared against FRED `GDPC1` by exact quarter. `scripts/gdp_reconcile.py` accepts a normalized, independently verified BEA export and an original FRED CSV. The workflow now acquires original BEA API JSON and normalizes the official million-dollar figures to FRED billion-dollar units; publisher-versus-FRED reconciliation is separately reported.
4. **Point-in-time**: reconstruct observation date, first publication timestamp, available-at-decision date, and revision vintage for the selected historical test panel. FRED current-revised values are not PIT evidence. Original BEA advance releases and BLS/ALFRED vintages must be independently verified.
5. **Promotion**: only after all required source, timing, unit, coverage, missingness and transformation checks PASS. No script in this repository writes canonical spreadsheet inputs or risk scores.

## Running

GitHub Actions workflow `Milestone 1 - Economic Data Acquisition and QA` runs on PRs, main, manual dispatch and weekly schedule. Download the `milestone1-audit-evidence` artifact after each run. A failed run is expected when the official publisher blocks the hosted runner, and is evidence of an acquisition problem, not evidence of data approval.

For GDP, after acquiring publisher CSVs with provenance:
```
python scripts/gdp_reconcile.py --bea bea_gdp_normalized.csv --fred fred_gdpc1.csv
```

The normalized BEA export must be traced to original BEA NIPA Table 1.1.6 line 1, with original download hash and an explicit unit/quarter normalization record. No manual fabricated values or spreadsheet copy-paste substitutes.

## Exit criteria

All three series independently reconciled, historical release-vintage audit complete, canonical input QA PASS, and spreadsheet approval 3/3. Until then **Milestone 1: NOT ACCEPTED**.
