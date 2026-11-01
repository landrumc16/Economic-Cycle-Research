# Equity valuation data requirements

## Scope
The equity valuation-gap transform is implemented but **not yet populated with verified historical earnings-yield observations**. Do not manufacture a Nasdaq earnings-yield series or infer earnings yield from price alone.

## Input contract
- Two monthly CSVs, each with `date,value`, dated YYYY-MM-01.
- Earnings yield and benchmark Treasury yield both in percentage points.
- Source URL, publisher, observation coverage, universe, adjustment and earnings definition.
- Whether earnings are trailing, forward consensus, or cyclically adjusted.
- Publication lag, revisions and vintage availability, separately from observation dates.
- Treasury maturity and month aggregation method.
- Clear alignment of equity index universe with the index being analyzed.

## Output
`scripts/derive_equity_valuation_gap.py earnings_yield.csv treasury_yield.csv --output data/industry_observations/equity_earnings_yield_gap.csv`

Higher values represent Treasury yields exceeding earnings yields by a larger margin. This is a **relative valuation proxy**, not an estimated equity risk premium and not evidence of a bubble by itself.

## Research gate
Before using in the automated Nasdaq comparison, document the earnings-yield data license and verify the series covers relevant pre-crash and non-crash episodes. For reproducibility, the pipeline should fail rather than quietly substitute a different index, synthetic values, or a price-only metric.

## Broader thesis
Historical valuation must be analyzed alongside credit conditions, industry acceleration, investor behavior and counterexamples. Retrospective full-sample thresholds are descriptive only. Chronological, point-in-time holdout evaluation is necessary before claiming forecasting usefulness.
