# Historical usability evaluation — first observed results

Date: 2026-10-31
Evidence: user-provided historical-usability-evidence.zip from passing GitHub Actions historical evaluation.
Status: **BASELINE NOT VALIDATED — REVISE OUTCOMES BEFORE PRODUCTIZING**

## Actual run results
- Source monthly periods: 1987-01 through 2023-12 (444 months).
- Full 12-month follow-up: 432 months.
- Eight listed market pathway parent clusters.
- Elevated rule: yield curve < 0 or credit spread >= 2.5 percentage points, using retrospective workbook data.
- Elevated: 176 months; 16 followed by a listed **market peak** within 12 months; 160 did not.
- Not elevated: 256 months; 75 followed by a listed peak; 181 did not.
- Listed peak share: 16/176 = 9.1% in elevated months vs 75/256 = 29.3% in non-elevated months.
- **These are NOT crash probabilities, independently validated true/false positives, or independent event counts.**

## Interpretation
The current rule does not show useful discrimination against the selected **future market-peak** target. However, a market peak is not a crash onset, recession onset, or completed drawdown. The outcome is misaligned with the intended risk-warning question, so no performance conclusion about crash detection follows.

The workbook is retrospective and not certified publisher-original point-in-time. The eight peaks are a selected event inventory, not exhaustive outcomes; apparent negatives are not verified. Monthly samples are correlated and not an independent holdout. Historical coverage before 1987 is missing.

## Quality issue found
The lead-window snapshot stores eight data rows without a header, while the inventory and scorecard scripts subtract one as though it had a header. Their reported `lead_window_rows: 7` is wrong. Correct to eight and add a regression check.

## Required next pass
1. Fix lead-window count.
2. Replace market **peak** follow-up with independently documented drawdown-crossing and recession-onset outcomes, explicitly separating these targets.
3. Audit negative-event coverage before reporting false-alarm rates.
4. Score simple indicator baselines and mechanisms on identical evaluation origins; report cohort size and missingness.
5. Establish publisher-original vintage availability before claiming a genuine historical backtest.
6. Produce a small historical case-study readout that demonstrates useful explanations without claiming validated forecasting.

## Product decision
Proceed with a **descriptive, transparent historical case-study tool**, not a calibrated crash-risk predictor. No predictive publication or risk probabilities are authorized.
