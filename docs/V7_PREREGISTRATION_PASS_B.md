# V7 Pass B — Pre-registration (written before the new data or results were examined)

**Committed:** 2026-11-18, before any recession-onset or first-release evaluation was run.
**Purpose:** control data-snooping risk. Pass A added recalibration after seeing results. Pass B fixes its new analyses in advance, and no model is promoted on the strength of already-examined history.

## A. Recession-onset target (new, never examined)
- **Definition:** at forecast origin *t* (end of month), the target is 1 if an NBER business-cycle **peak-to-recession transition** begins in months *t*+1 … *t*+*h*, meaning some month *m* in that window has USREC=1 while USREC=0 in month *m*−1. *h* = 3, 6, 12.
- **Evaluation population:** origins where the economy was **in expansion** at *t* (USREC[*t*] = 0, as later dated). This is the standard conditional framing, and it removes Pass A's "recession still under way" misses. Because the NBER state at *t* is not known in real time, results are labelled as conditional on expansion.
- **Features, model, recalibration, refit schedule, label delay (12 months) and evaluation start (1972-01):** identical to the Pass A `recession` target. No feature search.
- **Gate:** identical to the roadmap (BSS vs base rate ≥ 0.05, AUC ≥ 0.70, ≥ 3 episodes, overconfidence ≤ 0.20), on the full sample including 2020.
- **Decision rule:**
  - If the onset target passes, it may be published as "recession *start* risk", with its own track record.
  - If it fails, recession remains **Insufficient evidence**.
  - The Pass A `recession` result is not re-tuned either way.

## B. First-release (ALFRED) robustness check
- **Data:** FRED API `output_type=4` (initial release only) for **UNRATE** and **PAYEMS**: each month's value as first published.
- **Test:** re-run the Pass A `labor_deterioration` model at 3, 6 and 12 months with first-release UNRATE and PAYEMS as **inputs**. Outcomes stay on current-vintage UNRATE, as published history is the yardstick.
- **Interpretation:** a **robustness check, not a promotion route.**
  - If the 12-month labor outlook still passes the gate on first-release inputs, revision bias is shown not to drive the result.
  - If it fails, the outlook is downgraded to Insufficient evidence until resolved.
  - Better first-release results do **not** promote any other target.
- **Coverage:** first-release data begin only when ALFRED vintages start for each series. Any shorter evaluation window is reported, and the gate is applied as is.

## C. Sector research tests (M3)
- **Relative-strength persistence:** does a sector proxy's trailing 12-month return relative to the market (skipping the latest month) predict its next 6-month relative return?
  - **Method:** chronological evaluation from 1960 using only past returns.
  - **Metrics:** hit rate of the sign, the average spread of top-third minus bottom-third sectors, and a t-statistic on non-overlapping 6-month periods.
  - **Publish condition:** relative strength may be described as a *historically informative* signal only if the spread is positive with t ≥ 2.0 on non-overlapping periods, and positive in both halves of the sample. Otherwise it is shown as descriptive only.
- **Cycle, rate and inflation sensitivities:** computed descriptively over full history. No forecasting claim is made from them.
- **Investment attractiveness:** requires valuation and earnings evidence no older than the V6 gate allows (valuation ≤ 3 months, earnings ≤ 6 months) from a qualified source. Annual-vintage data can be shown as dated context but cannot qualify a rating.
