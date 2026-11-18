"""V7 M3: evidence-based research framework for the 11 GICS sectors.

Distinguishes *economic exposure* (how a sector has behaved across the cycle,
rates and inflation) from *investment attractiveness* (which needs current,
qualified valuation and earnings evidence and stays "Insufficient evidence"
until it exists). Nothing here is a recommendation.

Sources (free, attributable):
* Kenneth R. French Data Library: 49 industry value-weighted monthly returns and
  market return (Mkt-RF + RF). GICS sectors are approximated by equal-weighting
  mapped industries — a documented proxy, not an official sector index.
* Aswath Damodaran (NYU Stern) US industry P/E and expected growth: annual
  vintage, shown as dated context only.
* FRED (data/v7): NBER recession indicator, 10-year yield, CPI.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

try:
    from .v7_forecast_engine import shift
    from .v6_sector_intelligence import SENSITIVITY as V6_PROFILES, SECTORS
except ImportError:
    from v7_forecast_engine import shift
    from v6_sector_intelligence import SENSITIVITY as V6_PROFILES, SECTORS

FRENCH_MAP = {  # GICS sector -> French 49-industry proxies
    "Communication Services": ("Telcm", "Fun", "Books"),
    "Consumer Discretionary": ("Autos", "Toys", "Clths", "Txtls", "Rtail", "Meals", "PerSv"),
    "Consumer Staples": ("Food", "Soda", "Beer", "Smoke", "Hshld", "Agric"),
    "Energy": ("Oil", "Coal"),
    "Financials": ("Banks", "Insur", "Fin"),
    "Health Care": ("Hlth", "MedEq", "Drugs"),
    "Industrials": ("Mach", "ElcEq", "Aero", "Ships", "Guns", "Trans", "BusSv", "Cnstr", "FabPr", "Whlsl"),
    "Information Technology": ("Hardw", "Softw", "Chips", "LabEq"),
    "Materials": ("Chems", "Steel", "Mines", "Gold", "Paper", "Boxes", "BldMt", "Rubbr"),
    "Real Estate": ("RlEst",),
    "Utilities": ("Util",),
}
DAMODARAN_MAP = {
    "Communication Services": ("Advertising", "Broadcasting", "Cable TV", "Entertainment", "Publishing & Newspapers",
                               "Software (Entertainment)", "Software (Internet)", "Telecom (Wireless)", "Telecom. Services"),
    "Consumer Discretionary": ("Apparel", "Auto & Truck", "Auto Parts", "Furn/Home Furnishings", "Homebuilding", "Hotel/Gaming",
                               "Recreation", "Restaurant/Dining", "Retail (Automotive)", "Retail (Building Supply)",
                               "Retail (Distributors)", "Retail (General)", "Retail (Special Lines)", "Rubber& Tires", "Shoe",
                               "Education", "Electronics (Consumer & Office)"),
    "Consumer Staples": ("Beverage (Alcoholic)", "Beverage (Soft)", "Food Processing", "Food Wholesalers", "Household Products",
                         "Retail (Grocery and Food)", "Tobacco", "Farming/Agriculture"),
    "Energy": ("Coal & Related Energy", "Oil/Gas (Integrated)", "Oil/Gas (Production and Exploration)", "Oil/Gas Distribution",
               "Oilfield Svcs/Equip.", "Green & Renewable Energy"),
    "Financials": ("Bank (Money Center)", "Banks (Regional)", "Brokerage & Investment Banking", "Financial Svcs. (Non-bank & Insurance)",
                   "Insurance (General)", "Insurance (Life)", "Insurance (Prop/Cas.)", "Investments & Asset Management", "Reinsurance"),
    "Health Care": ("Drugs (Biotechnology)", "Drugs (Pharmaceutical)", "Healthcare Products", "Healthcare Support Services",
                    "Heathcare Information and Technology", "Hospitals/Healthcare Facilities"),
    "Industrials": ("Aerospace/Defense", "Air Transport", "Business & Consumer Services", "Electrical Equipment",
                    "Engineering/Construction", "Environmental & Waste Services", "Machinery", "Office Equipment & Services",
                    "Shipbuilding & Marine", "Transportation", "Transportation (Railroads)", "Trucking"),
    "Information Technology": ("Computer Services", "Computers/Peripherals", "Electronics (General)", "Information Services",
                               "Semiconductor", "Semiconductor Equip", "Software (System & Application)", "Telecom. Equipment"),
    "Materials": ("Building Materials", "Chemical (Basic)", "Chemical (Diversified)", "Chemical (Specialty)", "Construction Supplies",
                  "Metals & Mining", "Packaging & Container", "Paper/Forest Products", "Precious Metals", "Steel"),
    "Real Estate": ("R.E.I.T.", "Real Estate (Development)", "Real Estate (General/Diversified)",
                    "Real Estate (Operations & Services)", "Retail (REITs)"),
    "Utilities": ("Power", "Utility (General)", "Utility (Water)"),
}
CYCLE_BAND = 5.0          # pp/year: recession-minus-expansion excess return to call a sector Defensive/Cyclical.
HIGH_INFLATION = 4.0      # CPI 12-month % above which a month is "high inflation".
RS_TEST_START = "1960-01"
RS_HOLD = 6
RS_TOP = 4                # top/bottom third of 11 sectors (rounded)
VALUATION_PREMIUM = 0.25  # forward P/E more than 25% above the market is flagged (annual vintage).


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def _csv_table(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    key = "month" if "month" in rows[0] else "date"
    return {r[key][:7]: {k: float(v) for k, v in r.items() if k != key and v not in ("", None)} for r in rows}


def load(research_dir: Path, fred_dir: Path) -> dict:
    research_dir, fred_dir = Path(research_dir), Path(fred_dir)
    fred = {}
    for name in ("USREC", "GS10", "CPIAUCSL"):
        with open(fred_dir / f"{name}_monthly.csv", newline="") as f:
            fred[name] = {r["date"][:7]: float(r["value"]) for r in csv.DictReader(f)}
    factors = _csv_table(research_dir / "french_factors_monthly.csv")
    return {
        "industries": _csv_table(research_dir / "french_49_industries_vw_monthly.csv"),
        "market": {m: v["Mkt-RF"] + v["RF"] for m, v in factors.items() if "Mkt-RF" in v and "RF" in v},
        "damodaran": json.loads((research_dir / "damodaran_pe_us.json").read_text()),
        "manifest": json.loads((research_dir / "MANIFEST.json").read_text()),
        **fred,
    }


# --------------------------------------------------------------------------
# Returns and sensitivities
# --------------------------------------------------------------------------
def sector_returns(industries: dict, mapping=FRENCH_MAP) -> dict:
    """Equal-weight of available mapped industries; requires at least half present."""
    out = {s: {} for s in mapping}
    for month, row in industries.items():
        for sector, names in mapping.items():
            vals = [row[n] for n in names if n in row]
            if vals and len(vals) * 2 >= len(names):
                out[sector][month] = sum(vals) / len(vals)
    return out


def _compound(returns):
    g = 1.0
    for r in returns:
        g *= 1 + r / 100
    return 100 * (g - 1)


def relative_strength(sec: dict, mkt: dict, latest: str, months=12, skip=1):
    """Pre-registered: sector minus market compounded return over the `months`
    ending `skip` months before `latest` (the latest available month is skipped)."""
    window = [shift(latest, -k) for k in range(skip, skip + months)]
    if any(m not in sec or m not in mkt for m in window):
        return None
    return _compound(sec[m] for m in window) - _compound(mkt[m] for m in window)


def _ols_beta(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxx = sum((a - mx) ** 2 for a in x)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx if sxx else None


def sensitivities(sec: dict, data: dict) -> dict:
    mkt, rec, g10, cpi = data["market"], data["USREC"], data["GS10"], data["CPIAUCSL"]
    months = sorted(m for m in sec if m in mkt and m in rec and m >= "1953-05")
    ex = {m: sec[m] - mkt[m] for m in months}
    in_rec = [ex[m] for m in months if rec[m] >= 0.5]
    in_exp = [ex[m] for m in months if rec[m] < 0.5]
    dy = [(g10[m] - g10[shift(m, -1)], ex[m]) for m in months if m in g10 and shift(m, -1) in g10]
    infl = {}
    for m in months:
        a, b = cpi.get(m), cpi.get(shift(m, -12))
        if a and b:
            infl[m] = 100 * (a / b - 1)
    hi = [ex[m] for m in months if m in infl and infl[m] > HIGH_INFLATION]
    lo = [ex[m] for m in months if m in infl and infl[m] <= HIGH_INFLATION]
    recession_ex, expansion_ex = 12 * statistics.mean(in_rec), 12 * statistics.mean(in_exp)
    beta = _ols_beta([a for a, _ in dy], [b for _, b in dy])
    return {
        "period": f"{months[0]} to {months[-1]}", "months": len(months),
        "recession_excess_pct_per_year": round(recession_ex, 1),
        "expansion_excess_pct_per_year": round(expansion_ex, 1),
        "cycle_gap_pp": round(recession_ex - expansion_ex, 1),
        "rate_beta_pct_per_pp": round(beta, 2) if beta is not None else None,
        "high_inflation_excess_pct_per_year": round(12 * statistics.mean(hi), 1) if hi else None,
        "low_inflation_excess_pct_per_year": round(12 * statistics.mean(lo), 1) if lo else None,
    }


def cycle_class(sens: dict) -> str:
    gap = sens["cycle_gap_pp"]
    return "Defensive" if gap >= CYCLE_BAND else "Cyclical" if gap <= -CYCLE_BAND else "Neutral"


def persistence_test(secs: dict, mkt: dict) -> dict:
    """Pre-registered: does trailing 12-month relative strength (skip 1) predict
    the next 6-month relative return? Non-overlapping 6-month periods."""
    common = sorted(set.intersection(*(set(s) for s in secs.values())) & set(mkt))
    last = common[-1]
    spreads, hits, total, t = [], 0, 0, RS_TEST_START
    while shift(t, RS_HOLD - 1) <= last:
        rs = {s: relative_strength(v, mkt, shift(t, -1)) for s, v in secs.items()}
        nxt_window = [shift(t, k) for k in range(RS_HOLD)]
        if all(x is not None for x in rs.values()) and all(m in mkt for m in nxt_window):
            nxt = {s: _compound(v[m] for m in nxt_window) - _compound(mkt[m] for m in nxt_window) for s, v in secs.items()}
            ranked = sorted(rs, key=rs.get, reverse=True)
            spreads.append((t, statistics.mean(nxt[s] for s in ranked[:RS_TOP]) - statistics.mean(nxt[s] for s in ranked[-RS_TOP:])))
            for s in secs:
                if rs[s] != 0 and nxt[s] != 0:
                    total += 1
                    hits += (rs[s] > 0) == (nxt[s] > 0)
        t = shift(t, RS_HOLD)
    vals = [v for _, v in spreads]
    n = len(vals)
    mean = statistics.mean(vals)
    tstat = mean / (statistics.stdev(vals) / math.sqrt(n))
    half = n // 2
    first, second = statistics.mean(vals[:half]), statistics.mean(vals[half:])
    informative = tstat >= 2.0 and first > 0 and second > 0
    return {"periods": n, "first_period": spreads[0][0], "last_period": spreads[-1][0],
            "mean_spread_pp_per_6m": round(mean, 2), "t_stat": round(tstat, 2),
            "first_half_mean": round(first, 2), "second_half_mean": round(second, 2),
            "sign_hit_rate": round(hits / total, 3), "historically_informative": informative,
            "rule": "Informative only if mean top-minus-bottom spread has t >= 2.0 and is positive in both halves (pre-registered)."}


# --------------------------------------------------------------------------
# Valuation context (annual vintage; never qualifies a rating)
# --------------------------------------------------------------------------
def _num(v):
    try:
        return float(str(v).replace("%", "").replace(",", "").strip())
    except ValueError:
        return None


def valuation_context(rows: list, sector: str) -> dict:
    by = {r["Industry Name"]: r for r in rows}
    market = by.get("Total Market", {})
    picks = [by[n] for n in DAMODARAN_MAP[sector] if n in by]
    fpe = [x for x in (_num(r.get("Forward PE")) for r in picks) if x and 0 < x < 200]
    gr = [x for x in (_num(r.get("Expected growth - next 5 years")) for r in picks) if x is not None]
    mfpe = _num(market.get("Forward PE"))
    sector_fpe = statistics.median(fpe) if fpe else None
    return {"industries_matched": len(picks), "forward_pe_median": round(sector_fpe, 1) if sector_fpe else None,
            "market_forward_pe": mfpe,
            "forward_pe_vs_market": round(sector_fpe / mfpe - 1, 3) if sector_fpe and mfpe else None,
            "expected_growth_5y_median_pct": round(statistics.median(gr), 1) if gr else None,
            "vintage": "Damodaran annual US industry dataset (January vintage); dated context only",
            "qualifies_rating": False}


# --------------------------------------------------------------------------
# Backdrop, priority and narrative
# --------------------------------------------------------------------------
BACKDROP = {
    "Expanding": {"Cyclical": "Supportive", "Neutral": "Neutral", "Defensive": "Less favored"},
    "Slowing": {"Cyclical": "Mixed", "Neutral": "Neutral", "Defensive": "Relatively resilient"},
    "Deteriorating": {"Cyclical": "Headwind", "Neutral": "Mixed", "Defensive": "Relatively resilient"},
    "Mixed": {"Cyclical": "Mixed", "Neutral": "Mixed", "Defensive": "Mixed"},
}
BACKDROP_SCORE = {"Supportive": 1, "Relatively resilient": 1, "Neutral": 0, "Mixed": 0, "Less favored": 0, "Headwind": -1}


def assess_sector(name, sec, data, condition, labor_band, rs_test, latest, rates_up):
    sens = sensitivities(sec, data)
    klass = cycle_class(sens)
    backdrop = BACKDROP.get(condition, {}).get(klass, "Not assessed")
    if labor_band in ("Elevated", "High") and klass == "Cyclical" and backdrop == "Supportive":
        backdrop = "Mixed"  # published labor-risk outlook tempers a cyclical tailwind
    rs = relative_strength(sec, data["market"], latest, months=12, skip=1)
    val = valuation_context(data["damodaran"], name)
    score = BACKDROP_SCORE.get(backdrop, 0)
    if rs_test["historically_informative"] and rs is not None:
        score += 1 if rs > 0 else -1
    priority = ("Worth researching now" if score >= 1 else "Lower priority for now" if score <= -1 else "Monitor")
    supports, challenges = [], []
    word = {"Cyclical": "has historically lagged the market in recessions and led in expansions",
            "Defensive": "has historically held up better than the market in recessions",
            "Neutral": "has historically moved with the market across the cycle"}[klass]
    (supports if score > 0 else challenges if backdrop == "Headwind" else supports).append(
        f"{name} {word} (recessions {sens['recession_excess_pct_per_year']:+.1f}%/yr vs market, "
        f"expansions {sens['expansion_excess_pct_per_year']:+.1f}%/yr, since {sens['period'][:4]}).")
    if rs is not None:
        txt = f"Past 12 months: {rs:+.1f} percentage points versus the market."
        if rs_test["historically_informative"]:
            (supports if rs > 0 else challenges).append(txt + " Relative strength has historically persisted.")
        else:
            challenges.append(txt + " Relative strength has not reliably persisted in our test, so it is context only.")
    if val["forward_pe_vs_market"] is not None and val["forward_pe_vs_market"] > VALUATION_PREMIUM:
        challenges.append(f"Forward P/E about {val['forward_pe_vs_market']:.0%} above the market (annual vintage) — "
                          "a strong economy may already be priced in.")
    beta = sens["rate_beta_pct_per_pp"]
    if rates_up and beta is not None and beta <= -1.0:
        challenges.append(f"Rising 10-year yields have historically hurt this sector "
                          f"({beta:+.1f}% relative return per 1-point rise); yields rose over the past 6 months.")
    if sens["high_inflation_excess_pct_per_year"] is not None and sens["high_inflation_excess_pct_per_year"] <= -3:
        challenges.append(f"Historically lagged in high-inflation periods ({sens['high_inflation_excess_pct_per_year']:+.1f}%/yr).")
    changes = {
        "Cyclical": "A turn toward slowing or deteriorating conditions, or a rise in labor-market risk, would weaken this view.",
        "Defensive": "A clear, broad expansion would reduce the relative appeal of this sector's resilience.",
        "Neutral": "This sector's view depends more on its own fundamentals than on the economic cycle.",
    }[klass]
    return {
        "sector": name, "slug": name.lower().replace(" ", "-"),
        "proxy_industries": list(FRENCH_MAP[name]), "cycle_class": klass, "economic_backdrop": backdrop,
        "relative_strength_12m_pp": None if rs is None else round(rs, 1), "relative_strength_as_of": latest,
        "sensitivities": sens, "valuation_context": val, "research_priority": priority,
        "supports": supports, "challenges": challenges,
        "what_would_change": [changes, "Qualified, current valuation and earnings data could change the investment view."],
        "contrary_case": V6_PROFILES[name]["contrary"], "watch": V6_PROFILES[name]["watch"],
        "investment_attractiveness": "Insufficient evidence",
        "attractiveness_reason": ("Requires valuation no older than 3 months and earnings no older than 6 months from a "
                                  "qualified licensed source; only annual-vintage context is available."),
        "is_recommendation": False,
    }


def build(data: dict, condition: str, labor_band: str | None) -> dict:
    secs = sector_returns(data["industries"])
    latest = min(max(v) for v in secs.values())
    latest = min(latest, max(data["market"]))
    test = persistence_test(secs, data["market"])
    g = data["GS10"]
    last_g = max(g)
    rates_up = g[last_g] - g.get(shift(last_g, -6), g[last_g]) > 0.25
    items = [assess_sector(n, secs[n], data, condition, labor_band, test, latest, rates_up) for n in SECTORS]
    return {"status": "V7_SECTOR_RESEARCH_DESCRIPTIVE", "as_of_month": latest, "condition_used": condition,
            "labor_outlook_band_used": labor_band, "relative_strength_test": test, "rates_rose_6m": rates_up,
            "sectors": items,
            "sources": {"french": data["manifest"]["sources"].get("french_49_industries"),
                        "damodaran": data["manifest"]["sources"].get("damodaran_pe"),
                        "attribution": ["Kenneth R. French Data Library (Dartmouth)", "Aswath Damodaran, NYU Stern"]},
            "disclaimer": "Educational research, not personalized investment advice. Sector proxies are equal-weighted "
                          "French industry portfolios, not official GICS indices."}


def current_inputs(fred_dir, forecast_path):
    """Condition from the V6.3 rubric on the latest data; labor band from the published outlook."""
    try:
        from .v7_site import current_assessment
        from .v7_forecast_engine import load as load_fred
    except ImportError:
        from v7_site import current_assessment
        from v7_forecast_engine import load as load_fred
    _, view = current_assessment(load_fred(Path(fred_dir)))
    band = None
    ev = json.loads(Path(forecast_path).read_text())
    for o in ev.get("current_outlooks", []):
        if o["target"] == "labor_deterioration" and o["horizon_months"] == 12 and o["state"] == "Published":
            band = o["band"]
    return view["condition"], band


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--research-dir", default="data/v7_research")
    ap.add_argument("--fred-dir", default="data/v7")
    ap.add_argument("--forecast", default="docs/evidence/v7_forecast_evaluation_2026-11-17.json")
    ap.add_argument("--output", default="audit-output/v7_sectors.json")
    a = ap.parse_args()
    condition, band = current_inputs(a.fred_dir, a.forecast)
    report = build(load(a.research_dir, a.fred_dir), condition, band)
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(json.dumps(report, indent=1) + "\n")
    print("condition:", condition, "| labor band:", band)
    print(json.dumps(report["relative_strength_test"], indent=1))
    for s in report["sectors"]:
        print(f"{s['sector']:24s} {s['cycle_class']:9s} {s['economic_backdrop']:20s} RS {s['relative_strength_12m_pp']!s:>6} -> {s['research_priority']}")
