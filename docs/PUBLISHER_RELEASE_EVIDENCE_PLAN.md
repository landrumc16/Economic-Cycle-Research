# Publisher-original release evidence: bounded acquisition plan

Status: **OPEN — no PIT certification, no predictive promotion**.

## Authority and scope
The canonical Google workbook's `PROJECT LAWS & RESTART` governs. GitHub is the implementation mirror. Preserve original raw files, source URLs, publisher, observation period, release timestamp/timezone, retrieval time, SHA-256, contemporaneous reported values, methodology/seasonal-adjustment basis, and independent crosschecks. Do not infer a historical vintage from a current API observation.

## Acquisition sequence
1. **BLS unemployment (UNRATE / LNS14000000)**: identify original Employment Situation release archives for selected decision-date case studies already in the workbook. Record the exact report's U-3 seasonally adjusted value and published release date. A present-day BLS time-series response is not sufficient evidence of the originally reported value.
2. **BLS CPI (CPIAUCSL / CUSR0000SA0)**: identify original CPI news releases and archived seasonally adjusted tables for the same case-study windows. Preserve the actual release value and note seasonal revisions and rebasing/methodology differences.
3. **BEA real GDP (GDPC1)**: identify original GDP news releases, release estimate number (advance/second/third), original chained-dollar reference year, publication timestamp, and any benchmark revisions. Do not compare nominal or differently based real-GDP levels as equivalent.
4. **Crosscheck and decision-date eligibility**: verify source authenticity and hash of the downloaded raw bytes; confirm release timestamp precedes the decision timestamp. Crosscheck independent archive or reproduce from the original publisher file.
5. **Only then populate** `data/publisher_original_release_records.json` with actual evidence, preserving raw artifacts separately and marking all entries unverified until independent review. Existing `scripts/validate_release_evidence.py` checks metadata plausibility only, not publisher authenticity.
6. **Expansion**: move from a few previously researched case studies to representative crash and noncrash decision dates. Require chronological holdout, false-alarm evaluation and human approval before any model use.

## Operational safeguards
- No bulk re-download on each PR; scheduled/manual live-source acquisition only.
- BLS daily quota exhaustion must stop further calls, not trigger retry storms.
- No silent interpolation, backfill, or conversion of missing evidence to zero.
- Keep historical parent clusters separate from overlapping monthly warning windows.
- A passing offline CI run is a code-quality checkpoint, **not** source verification.
- Original publisher documents may establish a release date but not necessarily the precise intraday timestamp; if unavailable, record uncertainty rather than guessing.

## Current gate
`publication = BLOCKED`; `point_in_time_certified = false`; `forecast_authorized = false`.
