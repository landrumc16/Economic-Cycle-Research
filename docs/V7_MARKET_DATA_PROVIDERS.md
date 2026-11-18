# V7 Market-Data Provider Research and Recommendation

**Prepared:** 2026-11-18 · **Decision owner:** repository owner (licensing and cost).

## What the sector framework needs
| Need | Frequency | Status today |
|---|---|---|
| Sector / industry returns (relative strength, cycle sensitivity) | Monthly | **Covered free:** Kenneth R. French Data Library (1926–present, about 1–2 month lag) |
| Valuation (forward P/E, P/B) by sector | Monthly or better | **Annual only:** Damodaran (January vintage), shown as dated context |
| Earnings trends and expectations by sector | Monthly or quarterly | **Annual only:** Damodaran expected 5-year growth |
| Display on a public website | — | **Licensing is the binding constraint** |

The existing V6 gate requires valuation no older than 3 months and earnings no older than 6 months before any investment-attractiveness rating. The free sources cover exposure and relative strength, but not current valuation.

## Providers reviewed (prices as published; verify before purchase)
| Provider | Relevant data | Indicative price | Public-display / redistribution terms | Fit |
|---|---|---|---|---|
| **Kenneth R. French Data Library** | Industry portfolio returns, market factor | Free | Free research data with attribution | **In use** (returns) |
| **Damodaran (NYU Stern)** | Industry P/E, forward P/E, expected growth, margins | Free | Free with attribution; annual | **In use** (dated context) |
| **FRED / ALFRED** | Macro, yields, first releases | Free | Public; attribution | **In use** |
| **EODHD** | Fundamentals feed (company and ETF fundamentals, P/E) | Fundamentals $59.99/mo ($49.99/mo billed annually); All-in-One $99.99/mo | Personal plans are for personal use; display or redistribution needs a commercial agreement | Strong candidate if a display licence is affordable |
| **Financial Modeling Prep (FMP)** | Ratios, key metrics, sector P/E endpoints | Free tier 250 calls/day; paid tiers quoted up to about $99–$139/mo, with real-time on $49+ plans (sources conflict) | Separate commercial plans for display; verify sector-P/E endpoint tier | Candidate; verify endpoint and licence |
| **Tiingo** | EOD prices; fundamentals (Power $9.99–$49.99/mo by history depth) | Commercial: about $100–$200/mo (fundamentals), $250–$500/mo (EOD+IEX) | Free and Power tiers are individual/internal; redistribution is a separate line item | Good data; commercial cost higher |
| **Alpha Vantage** | Prices, fundamentals, sector performance | $49.99–$249.99/mo (75–1,200 req/min); free 25 req/day | Commercial display needs a separate licence | Usable; licence unclear for display |

Sources: [FMP pricing](https://site.financialmodelingprep.com/pricing-plans?planType=commercial), [EODHD pricing](https://eodhd.com/pricing), [Tiingo fundamentals](https://api.tiingo.com/products/fundamental-data-api), [Tiingo IEX/EOD](https://api.tiingo.com/products/iex-api), [Tiingo docs (licensing)](https://api.tiingo.com/documentation), [Alpha Vantage premium](https://alphavantage.co/premium), [FMP alternatives comparison](https://multiples.vc/compare/fmp-api-alternatives). Third-party price snapshots conflict in places (notably FMP), so treat every figure as indicative.

## Recommendation
1. **Now ($0, implemented):** French Data Library for returns, relative strength and cycle, rate and inflation sensitivity; Damodaran annual valuation and growth as dated context; FRED/ALFRED for macro. Investment attractiveness stays **Insufficient evidence**, which is honest and fail-closed.
2. **Next (owner decision, about $50–$100/month):** one provider for **monthly sector valuation and earnings using sector-ETF fundamentals** (for example the 11 Select Sector SPDR funds). This needs only about 11 symbols a month, which fits the smallest paid tiers.
   - **Preferred to evaluate first:** EODHD Fundamentals (about $50–60/month). Then compare FMP for a sector-P/E endpoint.
   - **Before buying:** obtain written confirmation that **derived figures** (for example sector forward P/E and P/E versus market) **may be displayed on a public website**, as was done with CFBD for the college-football project.
   - If display rights cost materially more than about $100/month, keep the free stack and Insufficient evidence for attractiveness.
3. **Not recommended:** scraping unofficial sources (for example Yahoo or Stooq) or any provider whose terms forbid public display.

## What changes once a licensed source exists
- `scripts/v6_sector_intelligence.py`'s existing evidence gate already accepts dated valuation, earnings and relative-return records with source URLs and methodology. A monthly fetch would populate it, and attractiveness ratings would then appear only where the gate passes.
- Before any attractiveness rating is published, a pre-registered historical test of the valuation signal against benchmark-relative returns is required (roadmap M3).
