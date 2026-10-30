# Milestone 1 evidence gate

Run `python scripts/milestone1_gate.py --evidence reviewed_evidence.json` only after the acquisition, numerical crosschecks, historical vintage audit and release-time verification are complete.

Evidence JSON contains `series.UNRATE`, `series.CPIAUCSL`, and `series.GDPC1`. Each needs seven boolean checks: publisher_source_acquired, independent_source_acquired, numeric_reconciliation_pass, publisher_vintage_authenticated, release_timing_verified, point_in_time_no_lookahead_pass, coverage_pass.

**Evidence provenance rule:** These booleans are human-reviewed attestations, NOT automatically inferred from a successful download or a green test suite. Each affirmative assertion requires a source-artifact digest, source URL, dated verification record, and reviewer signoff stored in the source-verification ledger. This script does not validate the authenticity of assertions and cannot certify the series by itself.

Passing the manifest gate yields **eligible for human review**, never automatic approval or Google Sheets publication. Missing data and non-boolean truthy values fail closed.

API credentials should be stored only in GitHub Actions secrets:
- `BLS_API_KEY` (optional, but full-history unregistered BLS quotas may be insufficient)
- `FRED_API_KEY` (required for FRED API)
- `BEA_API_KEY` (required for BEA API)

Milestone remains 0/3 until real publisher evidence is acquired and authenticated.
