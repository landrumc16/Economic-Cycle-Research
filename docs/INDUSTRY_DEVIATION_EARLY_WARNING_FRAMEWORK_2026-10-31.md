# Industry deviation and emerging-industry surveillance framework

Status: hypothesis and implementation specification; not a validated crash signal.

## Two discovery tracks
**Emerging industry:** a newly investable technology or industry with insufficient own-history baseline. Compare price growth, financing, issuance, valuation-implied adoption and realized delivery with *predeclared analogous cohorts* (railroads, electrification, internet, AI). Do not invent a 20-year baseline for a five-year sector.

**Established industry:** compare housing, banking, commodities and other mature industries against their own long-run real-price growth, valuations relative to cash flow/rent/income, credit expansion, turnover, supply and investment. Normalize for structural changes and inflation.

## Common signal dimensions (separate, not a single unvalidated score)
1. Acceleration: 12/24/36-month real price or industry-index growth against pre-event rolling historical distribution; robust percentile and z-score, calculated without look-ahead.
2. Fundamental divergence: prices/valuation relative to realized revenue, earnings, rent, income or production, with original vintage and unit conventions.
3. Capital inflow: sector fund flows, new issuance, IPO share, private financing and market-cap concentration.
4. Financial amplification: leverage, margin debt, credit creation, collateral dependence and refinancing sensitivity.
5. Expectation-delivery: contemporaneous forecasts and valuation-implied growth compared with subsequent measurable delivery; never use future realization in a real-time signal.
6. Reversal: declining breadth, earnings revisions, funding spreads and realized drawdown, explicitly distinguished from precursor indicators.

## Explicit comparisons
- **Positive historical cases:** railway booms, late-1990s internet, 2000s U.S. housing; use consistent outcome dates and evidence-quality labels.
- **Research analogue:** 1636–37 tulip contracts. Sparse/inconsistent price records, atypical contract structure, and contested systemic effects make it unsuitable for mechanical modern z-score calibration. Use qualitative case analysis.
- **Current candidate, not predetermined bubble:** AI industry. Classify using observed valuations, financing, revenues, adoption, margins and expectations; do not assert that rapid growth alone is a bubble.
- **Counterexamples:** industry acceleration followed by normalization without a qualifying drawdown. Define and collect prospectively from a complete industry universe, not handpicked survivors.

## Event/outcome protocol
- Universe and industry definitions fixed before outcome review; address survivorship bias and sector reclassifications.
- Track first 10%, 20%, and 30% industry-index drawdown from prior high with specified observation horizons; separately track broad-market drawdowns and NBER recessions.
- Use 3/6/12/24/36-month precursor windows and separate timing from eventual occurrence.
- All qualifying episodes remain in master record. Mechanism cohorts (external shock, endogenous, mixed) are labeled by documented criteria, with full-sample sensitivity.
- Compare high-deviation episodes with matched non-crash episodes and report false alarms, coverage, lead times and missing data.
- No inevitability claims, crash probabilities or causal policy attribution until full outcomes, original point-in-time vintages and chronological holdouts exist.

## Initial product design
Industry deviation monitor: industry, cohort type, baseline coverage, acceleration percentile, fundamental gap, capital inflow, leverage, breadth, data quality, dated observation and links to source releases. Show 'insufficient data' rather than substituting subjective risk grades.

## Source starting points
- FDIC, Crisis and Response (2008–2013), Chapter 1: https://www.fdic.gov/sites/default/files/2024-03/chap1_0.pdf
- Cleveland Fed, Comparing Two House-Price Booms: https://www.clevelandfed.org/publications/economic-commentary/ec-202404-comparing-two-house-price-booms
- Cambridge Financial History Review, Tulipmania's timing: https://www.cambridge.org/core/journals/financial-history-review/article/explaining-the-timing-of-tulipmanias-boom-and-bust-historical-context-sequestered-capital-and-market-signals/20BEB345A7BB4BF2E84C07F9077361A1
- Anne Goldgar, Tulipmania: https://doi.org/10.7208/chicago/9780226301303.001.0001
