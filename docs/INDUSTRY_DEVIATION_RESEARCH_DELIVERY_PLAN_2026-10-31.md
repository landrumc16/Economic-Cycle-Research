# Industry deviation: delivery and expansion plan

Status: implementation plan, not validated findings.

## Immediate delivery
1. Run the existing descriptive pipeline and publish an evidence summary with actual counts, event rates, and missing-data limitations. A failing run is a repair task, not a reason to stop other research.
2. Compare 6-, 12-, and 24-month subsequent declines for NASDAQCOM and CSUSHPINSA. Keep the asset definitions separate: broad Nasdaq equities versus national housing prices.
3. Report the number of high-deviation months with **no** subsequent 20% drawdown. Explicitly report denominators and missing group results. Do not present overlapping months as independent samples.
4. Check whether a 20% drawdown is appropriate for housing prices. Run a separate housing-relevant threshold sensitivity; do not interpret a zero-event housing result as proof of safety.
5. Compare episodes rather than just months: collapse overlapping alerts into independent alert clusters, report lead times and misses.

## Next model expansion
Add valuations, credit creation/leverage, industry capital investment, adoption/earnings delivery, and narrative/sentiment proxies only when sources and observation timing are documented. Compare incremental information beyond industry acceleration using chronological holdouts. Include non-crash episodes and all observed drawdowns, not selected successes.

## Delivery definition
A complete descriptive release contains source manifests, coverage dates, denominators, raw and grouped outcomes, 6/12/24-month sensitivity, non-crash counterexamples, tests, and an explicit retrospective-only warning. A predictive warning system requires separate point-in-time data and out-of-sample validation.

## Program management
Do not block broader economic-cycle development on one data source or GitHub Actions issue. Advance independent workstreams while repairing failed checks. Avoid additional speculative indicators until the initial evidence is inspected.
