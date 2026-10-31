# Binding Project Laws — Canonical Workbook Mirror

**Authority:** [SEM_Historical_Crash_Research_v1 — PROJECT LAWS & RESTART](https://docs.google.com/spreadsheets/d/1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE/edit#gid=1742037650), cells A7:D25. This GitHub document is an implementation mirror, not a replacement for the workbook's binding research laws. If there is a discrepancy, stop and reconcile with the workbook; do not silently weaken a law.

**Source snapshot:** 2026-10-30. Re-read the live workbook before changing research rules or publishing standards.

| ID | Non-negotiable principle | Required practice | Failure response |
|---|---|---|---|
| L01 | Never invent a number | Only use actual verifiable observations; distinguish reported values, calculations and model estimates. | Leave missing; label UNVERIFIED. |
| L02 | Trace every value | Record original publisher, series/ticker, source URL or identifier, retrieval date and methodology. | Do not publish unsupported value. |
| L03 | Corroborate independently | Cross-check with credible second source or independently reproduce from documented primary records; investigate discrepancies. | Quarantine conflicting value. |
| L04 | Match exact measurement | Verify price basis, corporate actions, total return, units, geography, seasonal adjustment, frequency and denominator. | Reject incompatible comparisons. |
| L05 | Respect dates and revisions | Keep observation, publication, retrieval and historical-vintage dates distinct; record revisions and method breaks. | Exclude unverified vintage from backtests. |
| L06 | No look-ahead bias | Historical forecasts may use only information actually released at the forecast date, including historical index constituents. | Invalidate leaking test. |
| L07 | Never convert missing into zero | No silent forward-fills, interpolations, assumptions or substitution; explicitly document modeled imputations. | Mark missing and block score. |
| L08 | Audit equations | Check formula logic, units, denominators, compounding, lag structure and spot-check derived values. | Hold affected outputs. |
| L09 | Separate prediction targets | Recession stage, recession probability, equity drawdown vulnerability, crash event, and sector returns are different outcomes. | Never combine labels without definition. |
| L10 | No fake precision | Never claim exact future crash date; publish probability ranges only after calibration and out-of-sample tests. | Show NOT VALIDATED. |
| L11 | Test false alarms | Include non-crash periods, base rates, walk-forward tests, sensitivity, calibration and simple benchmarks. | Keep signal experimental. |
| L12 | Avoid cherry-picking | Predefine hypotheses where possible; test unconventional signals against simpler models and multiple regimes. | Reject spurious signals. |
| L13 | Sector rigor | Use verified sector total returns, valuation and earnings data; consider risk, turnover and sector composition changes. | Do not rank with missing inputs. |
| L14 | Track source disagreement | Log discrepancies and explain resolution, never select the number that fits a narrative. | Flag CONFLICT. |
| L15 | Freshness matters | Check release schedules and revisions; record last checked and last observed dates; clearly flag inaccessible/stale feeds. | Do not claim updated. |
| L16 | Preserve originals and audit trail | Keep raw source values separate from formulas; log edits and verify changed ranges by reading back. | Stop on unexpected overwrite. |
| L17 | Use legal/accessible sources | Respect source access, licensing and terms; do not pretend to access restricted feeds. | Document blocker. |
| L18 | Communicate uncertainty | Separate observations, hypotheses, model estimates and investment judgments; report limitations. | Withhold unsupported recommendation. |

## Additional binding operational constraints
- The user approves material changes to research purpose and publishing standards; routine verified implementation may proceed.
- Research covers U.S. economic cycles, recessions, equity crashes and sector opportunities; targets remain distinct.
- Original publisher evidence, release date, vintage, retrieval time, revision and corroboration must be tracked separately.
- Research staging is not canonical approval. Current-revised reconciliation does not certify point-in-time release eligibility.
- Historical controls must include false alarms, base rates, walk-forward tests, nonoverlapping event denominators, untouched holdouts and calibration before predictions.
- Preserve original research, raw values, formulas, audit history and workbook dependencies; do not add or delete tabs without a documented need.
- Maintain one canonical dashboard; publication stays BLOCKED until explicit evidence and approval gates pass.
- The workbook's PROJECT LAWS & RESTART restart checklist R01–R10 is also binding. GitHub startup must additionally read START-HERE.md, PROJECT_STATUS.md and docs/ROADMAP.md.
- Existing workbook operations call for daily ~8 AM Central checks and Sunday ~8 AM Central outlook; **do not create duplicate schedules** or assume a scheduled job succeeded.
- On every substantial milestone update PROJECT_STATUS.md, retain actual commit and Actions verification, and record the next authorized implementation chunk.

## Enforcement
All scripts, workflows, readouts and future documentation must conform to L01–L18. Fail closed on missing, conflicting, unreleased or unapproved inputs. CI success demonstrates execution, not research or predictive validity.
