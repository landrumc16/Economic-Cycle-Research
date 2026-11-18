# V7 market monitoring

**Rule:** DAILY MARKET MONITORING. WEEKLY INTERPRETATION. MONTHLY ECONOMIC RESEARCH.
**Code:** `scripts/v7_market_monitor.py`, plus `refresh_market` in `scripts/v7_release.py`.
**Tests:** `tests/test_v7_market_monitor.py`, `tests/test_v7_release.py`.

## Cadence
| Layer | When | Source data | What changes |
|---|---|---|---|
| Daily market assessment | Daily production Pages workflow, 12:15 UTC: after each U.S. session's FRED closes are posted. Runs on other days do nothing. | S&P 500, Nasdaq, Dow and VIX (daily); high-yield and BAA spreads (daily); NFCI (weekly); French industries and breadth (monthly, 1–2 month lag) | Market observations, warning statuses, the change summary, event reviews |
| Weekly interpretation | Generated on the first assessment after a trading week (Mon–Fri) completes | The same data, over the completed week | A deeper summary; it says plainly when nothing meaningful changed |
| Monthly economic research | Monthly Economic Cycle Assessment (20th) | Economic data and V6 gate | Economic condition, outlooks, sectors. **These never change because of daily prices**; the refresh refuses to alter them. |

## Assessments
- **Dates:** each observation keeps its own observation date and frequency (daily, weekly or monthly).
- **When an assessment is made:** only when at least one observation is newer than in the previous assessment; otherwise the result is `NO_NEW_DATA` and nothing is rewritten. Repeat runs are safe.
- **Slower indicators:** an unchanged weekly or monthly reading is carried forward with its original date. It is never compared again as if it were new.
- **History:** `v7_market_history.json` holds the latest 90 assessments and 12 weekly reports. It is published with the site, SHA-256 hashed in `v7_release_manifest.json` (`data_files`) and verified whenever it is recovered from the live site.

## Change detection (deterministic)
**Tested** (historically tested warning signs; see `docs/V7_PREREGISTRATION_CRASH_RESEARCH.md`):
- any change of state among clear, near trigger, warning on and not current, in both directions, including signals returning to normal.

**Monitoring** (descriptive thresholds; not tested predictors, and never converted to probabilities):
| Measure | Reported when |
|---|---|
| S&P 500 or Nasdaq decline from its 1-year high | crosses 5, 10, 15, 20 or 30%, in either direction |
| One-day move | S&P 500 ±2%; Nasdaq ±2.5% |
| VIX | crosses 20, 30 or 40, or changes 4 points or more since the previous reading |
| High-yield spread | crosses 4.0 or 5.0, or changes 0.30 points or more |
| BAA − 10-year spread | changes 0.15 points or more |
| Chicago Fed NFCI (weekly) | crosses 0, or changes 0.10 or more |
| Breadth (monthly) | crosses 40% or 50%, or changes 10 points or more |

**Event review** is opened when any of these occurs:
- a new tested warning switches on;
- the S&P 500 or Nasdaq falls 10% or more below its 1-year high;
- the VIX rises above 30;
- the high-yield spread widens 0.5 points or more.

An event review rechecks every warning sign. It is a review, not a prediction.

## Freshness and reliability
- **Freshness gate:** daily market data must be no more than 7 days old, with no gaps in the series the warnings use; otherwise the result is `SKIPPED`.
- **Writes:** nothing is written unless every check passes. On any failure the previous valid assessment stays published.
- **Monitoring:** a skipped or failed refresh is annotated on the workflow run (`::warning`) and written to the run summary.
- **Display:** the homepage shows the assessment time, the date the market data run through, and the previous data date. If the market data are more than four days old on the viewer's own clock, a stale-data notice appears automatically.
- **Additional runs:** further scheduled runs can be added safely. Without new data they do nothing.
