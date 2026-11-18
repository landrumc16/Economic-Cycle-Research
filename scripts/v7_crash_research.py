"""V7 market-crash vulnerability research (pre-registered: docs/V7_PREREGISTRATION_CRASH_RESEARCH.md).

    fetch    --out DIR            # CI only: FRED, French Data Library, Shiller (public mirror)
    analyze  --data DIR --out F   # current conditions, bear-market history, signal tests, OOS model

Research only: nothing here is published on the site. Standard library only. Missing data stay
missing and are reported as gaps.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
import urllib.parse
import zipfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v7_forecast_engine as eng  # noqa: E402
from v7_fetch_research_data import FRENCH, french_monthly, get  # noqa: E402

FRED_DAILY = ("SP500", "NASDAQCOM", "NASDAQ100", "DJIA", "VIXCLS", "DCOILWTICO", "DCOILBRENTEU",
              "BAA10Y", "AAA10Y", "BAMLH0A0HYM2", "BAMLC0A0CM", "T10Y3M", "T10Y2Y", "DGS10", "DFF")
FRED_OTHER = ("GS10", "TB3MS", "BAA", "UNRATE", "CPIAUCSL", "INDPRO", "PAYEMS", "ICSA", "CFNAI",
              "SAHMREALTIME", "PERMIT", "UMCSENT", "GDPC1", "CP", "NCBEILQ027S", "GDP", "M2SL", "WALCL",
              "RRPONTSYD", "WRESBAL", "NFCI", "ANFCI", "NFCICREDIT", "NFCILEVERAGE", "NFCIRISK", "STLFSI4",
              "DRTSCILM", "BUSLOANS", "PALLFNFINDEXM", "PNRGINDEXM", "PMETAINDEXM", "PCOPPUSDM", "USREC")
FRENCH_FILES = {"factors_daily": "F-F_Research_Data_Factors_daily_CSV.zip",
                "factors": "F-F_Research_Data_Factors_CSV.zip",
                "size": "Portfolios_Formed_on_ME_CSV.zip",
                "industries": "49_Industry_Portfolios_CSV.zip"}
SHILLER_MIRROR = "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"


# ---------------------------------------------------------------------------
# Fetch (CI)
# ---------------------------------------------------------------------------
def fred(series, key):
    q = urllib.parse.urlencode({"series_id": series, "api_key": key, "file_type": "json"})
    obs = json.loads(get("https://api.stlouisfed.org/fred/series/observations?" + q))["observations"]
    return [(o["date"], float(o["value"])) for o in obs if o["value"] not in ("", ".")]


def french_daily(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0]).decode("latin-1")
    out = []
    for line in text.splitlines():
        c = [x.strip() for x in line.split(",")]
        if len(c) >= 5 and len(c[0]) == 8 and c[0].isdigit():
            d = f"{c[0][:4]}-{c[0][4:6]}-{c[0][6:]}"
            out.append((d, float(c[1]) + float(c[4])))  # Mkt-RF + RF, percent
    return out


def fetch(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("FRED_API_KEY", "").strip()
    manifest = {"retrieved": date.today().isoformat(), "fred": {}, "french": {}, "gaps": []}
    for s in FRED_DAILY + FRED_OTHER:
        try:
            rows = fred(s, key)
            with (out / f"fred_{s}.csv").open("w", newline="") as f:
                csv.writer(f).writerows([("date", "value")] + rows)
            manifest["fred"][s] = {"first": rows[0][0], "last": rows[-1][0], "n": len(rows)}
        except Exception as exc:  # report, never substitute
            manifest["gaps"].append(f"FRED {s}: {type(exc).__name__}: {exc}"[:200])
    for name, fn in FRENCH_FILES.items():
        try:
            raw = get(FRENCH + fn)
            if name == "factors_daily":
                rows = french_daily(raw)
                with (out / "french_market_daily.csv").open("w", newline="") as f:
                    csv.writer(f).writerows([("date", "ret_pct")] + rows)
                manifest["french"][name] = {"first": rows[0][0], "last": rows[-1][0]}
            else:
                header, rows = french_monthly(raw)
                with (out / f"french_{name}.csv").open("w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["month"] + header)
                    for m in sorted(rows):
                        w.writerow([m] + [rows[m].get(h, "") for h in header])
                manifest["french"][name] = {"first": min(rows), "last": max(rows)}
        except Exception as exc:
            manifest["gaps"].append(f"French {name}: {type(exc).__name__}: {exc}"[:200])
    try:
        raw = get(SHILLER_MIRROR).decode()
        (out / "shiller_mirror.csv").write_text(raw)
        rows = list(csv.DictReader(io.StringIO(raw)))
        manifest["shiller"] = {"url": SHILLER_MIRROR, "first": rows[0]["Date"], "last": rows[-1]["Date"],
                               "note": "Public mirror of Robert Shiller's U.S. stock market data (datasets/s-and-p-500)."}
    except Exception as exc:
        manifest["gaps"].append(f"Shiller mirror: {type(exc).__name__}: {exc}"[:200])
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps(manifest, indent=1))


# ---------------------------------------------------------------------------
# Load helpers
# ---------------------------------------------------------------------------
def read_series(path):
    if not path.is_file():
        return {}
    with path.open() as f:
        return {r["date"]: float(r["value"]) for r in csv.DictReader(f)}


def monthly_last(daily):
    out = {}
    for d in sorted(daily):
        out[d[:7]] = daily[d]
    return out


def monthly_mean(daily):
    acc = {}
    for d, v in daily.items():
        acc.setdefault(d[:7], []).append(v)
    return {m: sum(v) / len(v) for m, v in acc.items()}


def table(path):
    if not path.is_file():
        return {}
    with path.open() as f:
        out = {}
        for r in csv.DictReader(f):
            out[r["month"]] = {k: float(v) for k, v in r.items() if k != "month" and v not in ("", None)}
        return out


def load(data: Path):
    D = {"fred": {p.stem[5:]: read_series(p) for p in data.glob("fred_*.csv")}}
    daily = []
    if (data / "french_market_daily.csv").is_file():
        with (data / "french_market_daily.csv").open() as f:
            daily = [(r["date"], float(r["ret_pct"])) for r in csv.DictReader(f)]
    level, idx = 1.0, {}
    for d, r in daily:
        level *= 1 + r / 100
        idx[d] = level
    D["mkt_daily"] = idx
    D["mkt_m"] = monthly_last(idx)
    D["size"] = table(data / "french_size.csv")
    D["ind"] = table(data / "french_industries.csv")
    D["cape"] = {}
    D["earn"] = {}
    if (data / "shiller_mirror.csv").is_file():
        for r in csv.DictReader((data / "shiller_mirror.csv").open()):
            m = r["Date"][:7]
            try:
                if r.get("PE10") not in ("", "0", "0.0", None):
                    D["cape"][m] = float(r["PE10"])
                if r.get("Earnings") not in ("", None) and float(r["Earnings"]) > 0:  # 0.0 = placeholder
                    D["earn"][m] = float(r["Earnings"])
            except ValueError:
                pass
    D["manifest"] = json.loads((data / "MANIFEST.json").read_text()) if (data / "MANIFEST.json").is_file() else {}
    return D


def sh(month, k):
    """The month k months BEFORE `month` (negative k moves forward)."""
    return eng.shift(month, -k)


def mdiff(a, b):
    """Whole months from a to b (YYYY-MM...)."""
    return (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])


def pct(cur, prev):
    return None if cur is None or not prev else round(100 * (cur / prev - 1), 2)


def pctile(hist, v):
    hist = [h for h in hist if h is not None]
    if v is None or len(hist) < 24:
        return None
    return round(100 * sum(h <= v for h in hist) / len(hist), 1)


# ---------------------------------------------------------------------------
# Bear markets and targets (French daily total market)
# ---------------------------------------------------------------------------
def bear_markets(idx, threshold=0.20):
    ds = sorted(idx)
    out, peak_d, peak, trough_d, trough, in_bear = [], ds[0], idx[ds[0]], None, None, False
    for d in ds:
        v = idx[d]
        if v >= peak:
            if in_bear:
                out.append({"peak": peak_d, "trough": trough_d, "depth_pct": round(100 * (trough / peak - 1), 1),
                            "recovered": d})
                in_bear = False
            peak_d, peak, trough_d, trough = d, v, d, v
        else:
            if trough is None or v < trough:
                trough_d, trough = d, v
            if v <= peak * (1 - threshold):
                in_bear = True
    if in_bear:
        out.append({"peak": peak_d, "trough": trough_d, "depth_pct": round(100 * (trough / peak - 1), 1),
                    "recovered": None})
    for b in out:
        b["months_peak_to_trough"] = mdiff(b["peak"], b["trough"])
    return out


def forward_target(idx, mkt_m, h, drop=0.20):
    """{origin month: 1/0} — daily level falls >= drop below the origin month-end within h months."""
    ds = sorted(idx)
    last = ds[-1][:7]
    y = {}
    pos = {d: i for i, d in enumerate(ds)}
    month_end_day = {}
    for d in ds:
        month_end_day[d[:7]] = d
    for m, lvl in mkt_m.items():
        end_m = sh(m, -h)
        if end_m > last or m == last:
            continue
        i = pos[month_end_day[m]] + 1
        lo = math.inf
        while i < len(ds) and ds[i][:7] <= end_m:
            lo = min(lo, idx[ds[i]])
            i += 1
        y[m] = int(lo <= lvl * (1 - drop))
    return y


# ---------------------------------------------------------------------------
# Point-in-time monthly features
# ---------------------------------------------------------------------------
def feature_panel(D):
    F = D["fred"]
    gs10, tb3, baa, ur = ({k[:7]: v for k, v in F.get(s, {}).items()} for s in ("GS10", "TB3MS", "BAA", "UNRATE"))
    mkt = D["mkt_m"]
    ind = D["ind"]
    ind_names = sorted({k for r in ind.values() for k in r})
    # Industry cumulative indexes for breadth.
    ind_lvl, lv = {}, {n: 1.0 for n in ind_names}
    for m in sorted(ind):
        for n in ind_names:
            if n in ind[m]:
                lv[n] *= 1 + ind[m][n] / 100
        ind_lvl[m] = dict(lv)
    cape_hist = sorted(D["cape"].items())
    panel = {}
    for m in sorted(mkt):
        row = {}
        spread = {k: gs10[k] - tb3[k] for k in (sh(m, j) for j in range(12)) if k in gs10 and k in tb3}
        if len(spread) == 12:
            row["curve"] = round(gs10[m] - tb3[m], 3)
            row["curve_min12"] = round(min(spread.values()), 3)
        if m in baa and m in gs10:
            row["credit"] = round(baa[m] - gs10[m], 3)
            p6 = sh(m, 6)
            if p6 in baa and p6 in gs10:
                row["credit_chg6"] = round(row["credit"] - (baa[p6] - gs10[p6]), 3)
        um = sh(m, 1)  # unemployment published with a one-month lag
        a3 = [ur.get(sh(um, k)) for k in range(3)]
        prior = [[ur.get(sh(um, k + j)) for k in range(3)] for j in range(1, 13)]
        if None not in a3 and all(None not in p for p in prior):
            row["unemp_rise"] = round(sum(a3) / 3 - min(sum(p) / 3 for p in prior), 3)
        tm = sh(m, 12)
        if m in tb3 and tm in tb3:
            row["rate_chg12"] = round(tb3[m] - tb3[tm], 3)
        last10 = [mkt.get(sh(m, k)) for k in range(10)]
        if None not in last10:
            row["trend_gap"] = round(mkt[m] / (sum(last10) / 10) - 1, 4)
        if sh(m, 12) in mkt:
            row["ret12"] = round(100 * (mkt[m] / mkt[sh(m, 12)] - 1), 2)
        if m in ind_lvl and sh(m, 9) in ind_lvl:
            above = tot = 0
            for n in ind_names:
                hist = [ind_lvl.get(sh(m, k), {}).get(n) for k in range(10)]
                if None not in hist and n in ind.get(m, {}):
                    tot += 1
                    above += ind_lvl[m][n] > sum(hist) / 10
            if tot >= 20:
                row["breadth"] = round(above / tot, 3)
        cm = sh(m, 1)  # CAPE known with a one-month lag
        hist = [v for k, v in cape_hist if k <= cm]
        if cm in D["cape"] and len(hist) >= 240:
            row["cape"] = D["cape"][cm]
            row["cape_pct"] = pctile(hist, D["cape"][cm])
        nf = monthly_mean(F.get("NFCI", {}))
        if m in nf:
            row["nfci"] = round(nf[m], 3)
        panel[m] = row
    return panel


RULES = {
    "Yield curve inverted (past 12m)": lambda r: None if "curve_min12" not in r else r["curve_min12"] < 0,
    "Credit stress": lambda r: None if "credit" not in r else (r["credit"] >= 2.5 or r.get("credit_chg6", 0) >= 0.5),
    "Unemployment rising": lambda r: None if "unemp_rise" not in r else r["unemp_rise"] >= 0.5,
    "Valuation extreme (CAPE >= 80th pct)": lambda r: None if "cape_pct" not in r else r["cape_pct"] >= 80,
    "Trend break (below 10m average)": lambda r: None if "trend_gap" not in r else r["trend_gap"] < 0,
    "Weak breadth (<40% industries above 10m avg)": lambda r: None if "breadth" not in r else r["breadth"] < 0.40,
    "Euphoria (12m return >= 30%)": lambda r: None if "ret12" not in r else r["ret12"] >= 30,
    "Rate shock (bill +2pp in 12m)": lambda r: None if "rate_chg12" not in r else r["rate_chg12"] >= 2,
    "Financial conditions tight (NFCI > 0)": lambda r: None if "nfci" not in r else r["nfci"] > 0,
}
MODEL_FEATURES = ("curve_min12", "credit", "credit_chg6", "unemp_rise", "cape_pct", "trend_gap", "breadth", "rate_chg12")
CORE_FEATURES = tuple(f for f in MODEL_FEATURES if f != "cape_pct")  # variant if CAPE is unavailable or short


def signal_tests(panel, y, bears, start="1927-01"):
    out = {}
    origins = [m for m in sorted(y) if m >= start]
    base_all = sum(y[m] for m in origins) / len(origins)
    for name, rule in RULES.items():
        flags = {m: rule(panel[m]) for m in origins if m in panel and rule(panel[m]) is not None}
        if len(flags) < 120:
            out[name] = {"status": "insufficient history", "months": len(flags)}
            continue
        ms = sorted(flags)
        on = [m for m in ms if flags[m]]
        off = [m for m in ms if not flags[m]]
        base = sum(y[m] for m in ms) / len(ms)
        hit = sum(y[m] for m in on) / len(on) if on else None
        caught, missed, leads = [], [], []
        for b in bears:
            pk = b["peak"][:7]
            if pk < ms[0] or pk > ms[-1]:
                continue
            window = [sh(pk, k) for k in range(0, 13)]
            warn = [w for w in window if flags.get(w)]
            (caught if warn else missed).append(pk)
            if warn:
                first = min(warn)
                leads.append(mdiff(first, pk))
        out[name] = {"from": ms[0], "months": len(ms), "warning_share": round(len(on) / len(ms), 3),
                     "base_rate": round(base, 3), "hit_rate_when_warning": None if hit is None else round(hit, 3),
                     "rate_when_no_warning": round(sum(y[m] for m in off) / len(off), 3) if off else None,
                     "lift": None if hit is None or not base else round(hit / base, 2),
                     "false_alarm_share": None if hit is None else round(1 - hit, 3),
                     "bears_caught": len(caught), "bears_missed": len(missed), "missed": missed,
                     "median_lead_months": sorted(leads)[len(leads) // 2] if leads else None}
    return {"base_rate_all": round(base_all, 3), "signals": out}


def oos_model(panel, y, h, feats=MODEL_FEATURES, eval_start="1965-01", min_train=120):
    origins = [m for m in sorted(y) if m >= "1953-01" and all(k in panel.get(m, {}) for k in feats)]
    rows, model, fitted = [], None, None
    for m in origins:
        if m < eval_start:
            continue
        known = sh(m, h)  # outcomes known by origin m are those with origin <= m - h
        train = [o for o in origins if o <= known]
        if len(train) < min_train:
            continue
        if model is None or mdiff(fitted, m) >= eng.REFIT_EVERY:
            ys = [y[o] for o in train]
            if 0 < sum(ys) < len(ys):
                model = eng.fit_logistic([[panel[o][k] for k in feats] for o in train], ys)
                fitted = m
        if model is None:
            continue
        base = sum(y[o] for o in train) / len(train)
        p = eng.predict(model, [panel[m][k] for k in feats])
        rows.append({"origin": m, "model": p, "base": base, "y": y[m]})
    if not rows:
        return {"status": "no evaluable origins"}

    def summ(rs):
        p, yy, b = [r["model"] for r in rs], [r["y"] for r in rs], [r["base"] for r in rs]
        bs, b0 = eng.brier(p, yy), eng.brier(b, yy)
        a = eng.auc(p, yy)
        return {"n": len(rs), "events": sum(yy), "episodes": eng.episodes(rs), "brier": round(bs, 4),
                "brier_base": round(b0, 4), "bss_vs_base_rate": round(1 - bs / b0, 3) if b0 else None,
                "auc": None if a is None else round(a, 3)}
    full = summ(rows)
    ex = summ([r for r in rows if not eng.PANDEMIC[0] <= r["origin"] <= eng.PANDEMIC[1]])
    cal = eng.calibration([r["model"] for r in rows], [r["y"] for r in rows])
    oc = eng.overconfidence(cal)
    g = eng.GATE
    checks = {"bss_vs_base_rate": (full["bss_vs_base_rate"] or -9) >= g["bss_vs_base_rate"],
              "auc": (full["auc"] or 0) >= g["auc"], "episodes": full["episodes"] >= g["min_episodes"],
              "calibration": oc <= g["max_overconfidence"]}
    final = eng.fit_logistic([[panel[o][k] for k in feats] for o in origins], [y[o] for o in origins])
    return {"horizon_months": h, "features": list(feats), "evaluation": [rows[0]["origin"], rows[-1]["origin"]],
            "full_sample": full, "excluding_2020_window": ex, "calibration": cal, "overconfidence": oc,
            "gate_checks": checks, "passes_gate": all(checks.values()),
            "full_sample_weights_standardised": dict(zip(["intercept"] + list(feats),
                                                         [round(w, 3) for w in final[0]])),
            "last_forecasts": [{"origin": r["origin"], "p": round(r["model"], 3), "y": r["y"]} for r in rows[-6:]]}


# ---------------------------------------------------------------------------
# Current conditions
# ---------------------------------------------------------------------------
def by_offset(series, days):
    ds = sorted(series)
    if not ds:
        return None, None, None
    last = ds[-1]
    target = (date.fromisoformat(last) - timedelta(days=days)).isoformat()
    prior = max((d for d in ds if d <= target), default=None)
    return last, series[last], (series[prior] if prior else None)


def current(D, panel):
    F, out = D["fred"], {}
    for s in ("SP500", "NASDAQCOM", "NASDAQ100", "DJIA"):
        ser = F.get(s, {})
        if not ser:
            out[s] = "unavailable"
            continue
        last, v, _ = by_offset(ser, 0)
        r = {"date": last, "level": v}
        for lab, dd in (("1m", 30), ("3m", 91), ("6m", 182), ("12m", 365)):
            r[lab] = pct(v, by_offset(ser, dd)[2])
        yr = [x for d, x in ser.items() if d > (date.fromisoformat(last) - timedelta(days=365)).isoformat()]
        r["from_52w_high"] = pct(v, max(yr))
        r["from_high_in_history"] = pct(v, max(ser.values()))
        r["history_from"] = min(ser)
        out[s] = r
    mk = D["mkt_daily"]
    if mk:
        last, v, _ = by_offset(mk, 0)
        out["US_total_market_French"] = {"date": last, **{lab: pct(v, by_offset(mk, dd)[2]) for lab, dd in
                                                          (("1m", 30), ("3m", 91), ("6m", 182), ("12m", 365))},
                                         "from_high": pct(v, max(mk.values()))}
    size = D["size"]
    if size:
        lm = max(size)
        def cum(col, n):
            x = 1.0
            for k in range(n):
                r = size.get(sh(lm, k), {}).get(col)
                if r is None:
                    return None
                x *= 1 + r / 100
            return round(100 * (x - 1), 2)
        out["size_deciles_French"] = {"month": lm, **{f"{lab}_{c}": cum(c, n) for lab, n in (("3m", 3), ("12m", 12))
                                                     for c in ("Lo 10", "Lo 20", "Hi 20", "Hi 10")}}
    ind = D["ind"]
    if ind:
        lm = max(ind)
        r12 = {}
        for n in ind[lm]:
            x = 1.0
            ok = True
            for k in range(12):
                v = ind.get(sh(lm, k), {}).get(n)
                if v is None:
                    ok = False
                    break
                x *= 1 + v / 100
            if ok:
                r12[n] = round(100 * (x - 1), 1)
        srt = sorted(r12.items(), key=lambda t: -t[1])
        out["industries_French"] = {"month": lm, "share_positive_12m": round(sum(v > 0 for v in r12.values()) / len(r12), 3),
                                    "breadth_above_10m_avg": panel.get(lm, {}).get("breadth"),
                                    "leaders_12m": srt[:5], "laggards_12m": srt[-5:]}
    def latest(s, chg=None, monthly=True):
        ser = F.get(s, {})
        if not ser:
            return "unavailable"
        ds = sorted(ser)
        r = {"date": ds[-1], "value": ser[ds[-1]], "history_pctile": pctile(list(ser.values()), ser[ds[-1]]),
             "history_from": ds[0]}
        if chg:
            for lab, dd in chg:
                r[f"chg_{lab}"] = pct(ser[ds[-1]], by_offset(ser, dd)[2])
        return r
    grp = {"credit": ("BAA10Y", "AAA10Y", "BAMLH0A0HYM2", "BAMLC0A0CM", "NFCI", "ANFCI", "NFCICREDIT",
                      "NFCILEVERAGE", "NFCIRISK", "STLFSI4", "DRTSCILM"),
           "rates": ("T10Y3M", "T10Y2Y", "DGS10", "DFF"),
           "volatility": ("VIXCLS",),
           "liquidity": ("M2SL", "WALCL", "RRPONTSYD", "WRESBAL", "BUSLOANS"),
           "commodities": ("PALLFNFINDEXM", "PNRGINDEXM", "PMETAINDEXM", "PCOPPUSDM", "DCOILWTICO", "DCOILBRENTEU"),
           "economy": ("INDPRO", "PAYEMS", "UNRATE", "ICSA", "CFNAI", "SAHMREALTIME", "PERMIT", "UMCSENT", "GDPC1"),
           "earnings_valuation": ("CP", "NCBEILQ027S", "GDP")}
    chg = (("3m", 91), ("6m", 182), ("12m", 365))
    for g, ss in grp.items():
        out[g] = {s: latest(s, chg) for s in ss}
    eq, gdp = F.get("NCBEILQ027S", {}), F.get("GDP", {})
    common = sorted(set(eq) & set(gdp))
    if common:
        ratio = {d: eq[d] / 1000 / gdp[d] for d in common}  # equities in $M, GDP in $B
        out["earnings_valuation"]["equity_value_to_GDP"] = {"date": common[-1], "value": round(ratio[common[-1]], 3),
                                                           "history_pctile": pctile(list(ratio.values()), ratio[common[-1]]),
                                                           "history_from": common[0]}
    if D["cape"]:
        cm = max(D["cape"])
        out["earnings_valuation"]["CAPE_Shiller"] = {"month": cm, "value": D["cape"][cm],
                                                    "age_months": mdiff(cm, max(D["mkt_m"])) if D["mkt_m"] else None,
                                                    "current": bool(D["mkt_m"]) and mdiff(cm, max(D["mkt_m"])) <= 2,
                                                    "history_pctile": pctile(list(D["cape"].values()), D["cape"][cm]),
                                                    "history_from": min(D["cape"])}
        em = max(D["earn"]) if D["earn"] else None
        if em:
            out["earnings_valuation"]["SP_composite_trailing_earnings"] = {
                "month": em, "value": D["earn"][em], "chg_12m_pct": pct(D["earn"][em], D["earn"].get(sh(em, 12)))}
    lm = max(panel)
    out["signals_now"] = {"month": lm, "features": panel[lm],
                          "warnings": {n: rule(panel[lm]) for n, rule in RULES.items()}}
    return out


def analyze(data: Path, out_path: Path):
    D = load(data)
    panel = feature_panel(D)
    bears = bear_markets(D["mkt_daily"])
    crashes = [b for b in bears if b["depth_pct"] <= -30]
    y12 = forward_target(D["mkt_daily"], D["mkt_m"], 12)
    y6 = forward_target(D["mkt_daily"], D["mkt_m"], 6)
    rep = {"status": "V7_CRASH_RESEARCH_PREREGISTERED", "generated": date.today().isoformat(),
           "sources": D["manifest"], "bear_markets": bears, "crash_count": len(crashes),
           "target_base_rates": {"T12_all": round(sum(y12.values()) / len(y12), 3),
                                 "T6_all": round(sum(y6.values()) / len(y6), 3)},
           "signals_T12": signal_tests(panel, y12, bears), "signals_T6": signal_tests(panel, y6, bears),
           "model_T12_core": oos_model(panel, y12, 12, CORE_FEATURES),
           "model_T6_core": oos_model(panel, y6, 6, CORE_FEATURES),
           "model_T12_with_cape": oos_model(panel, y12, 12, MODEL_FEATURES),
           "model_T6_with_cape": oos_model(panel, y6, 6, MODEL_FEATURES),
           "current": current(D, panel)}
    # Signal values at each bear-market peak since 1953: 12, 6, 3, 0 months before.
    rep["at_peaks"] = [{"peak": b["peak"], "depth": b["depth_pct"],
                        **{f"t-{k}": {f: panel.get(sh(b["peak"][:7], k), {}).get(f) for f in
                                      ("curve_min12", "credit", "unemp_rise", "cape_pct", "trend_gap", "breadth", "ret12")}
                           for k in (12, 6, 3, 0)}} for b in bears if b["peak"] >= "1953"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rep, indent=1, default=str) + "\n")
    print(json.dumps(rep, default=str))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("analyze")
    a.add_argument("--data", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    x = ap.parse_args()
    fetch(x.out) if x.cmd == "fetch" else analyze(x.data, x.out)


if __name__ == "__main__":
    main()
