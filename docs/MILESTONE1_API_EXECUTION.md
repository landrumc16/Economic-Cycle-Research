# Milestone 1 — Official API execution and promotion gates

## Implemented
- Original BLS bulk files and FRED graph CSV attempted with original-byte hashing.
- BLS official API fallback, ten-year windows; preserves each original JSON response.
- FRED observations API fallback, three date windows for UNRATE, CPIAUCSL and GDPC1.
- BEA official NIPA T10106 line 1 real GDP quarterly API acquisition; original JSON retained.
- Independent BLS/FRED 600+ month comparisons and BEA/FRED 250+ quarter comparisons.
- Point-in-time release-ledger metadata validator and unit tests.
- Workflow preserves audit evidence even when publisher endpoints fail.

## Required GitHub repository secrets
- `FRED_API_KEY`: obtain from the Federal Reserve Bank of St. Louis FRED API.
- `BEA_API_KEY`: obtain from BEA API.
Set in repository Settings > Secrets and variables > Actions > New repository secret.
Never paste credentials into chat, a spreadsheet, source code, issue or PR.

## Hard limitations
- A successful revised-series comparison is **not** historical point-in-time vintage certification.
- BLS public API can enforce strict quotas; failure or partial coverage is not approval.
- BEA and FRED GDP levels must match in series definition, units, seasonal adjustment, and rounding before reconciliation can pass.
- The BLS API and FRED API may be blocked from hosted runners too; observe logs and artifacts.
- No series is promoted to canonical Google Sheets inputs without source and vintage certification.
- Current certification remains 0/3 until evidence demonstrates otherwise.
