"""V7 forward-looking economic engine (M1 foundation + M2 evaluation).

Transparent, dependency-free probability forecasts for 3-, 6- and 12-month
horizons, evaluated chronologically out of sample against simple benchmarks.
Only targets/horizons that pass a pre-declared evidence gate may be published;
everything else is reported as "Insufficient evidence".

Point-in-time rules (forecast made at the end of month t):
* Market data (GS10, TB3MS, BAA) for month t are known and never revised.
* UNRATE, PAYEMS, CPIAUCSL and INDPRO are used only through month t-1.
* USREC (NBER) is never an input. As a training label it counts as known only
  RECESSION_LABEL_DELAY months after the outcome window closes.
Inputs are current-vintage FRED data: macro series may have been revised since
first publication (documented limitation); market inputs are not revised.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date
from pathlib import Path

HORIZONS = (3, 6, 12)
SERIES = ("GS10", "TB3MS", "BAA", "USREC", "UNRATE", "CPIAUCSL", "INDPRO", "PAYEMS")
LAG = {"GS10": 0, "TB3MS": 0, "BAA": 0, "UNRATE": 1, "PAYEMS": 1, "CPIAUCSL": 1, "INDPRO": 1}
RECESSION_LABEL_DELAY = 12   # NBER announcements typically lag 6-21 months.
MACRO_LABEL_DELAY = 1        # Monthly macro outcomes known about a month later.
REFIT_EVERY = 12             # Re-estimate once a year (expanding window).
MIN_TRAIN = 120              # Months of labelled history before the first forecast.
EVAL_START = "1972-01"
PANDEMIC = ("2019-03", "2020-12")  # Origins whose window touches the 2020 shock.
L2 = 1.0

GATE = {"bss_vs_base_rate": 0.05, "auc": 0.70, "min_episodes": 3, "max_overconfidence": 0.20}

FEATURES = {
    "recession": ("term_spread", "term_spread_min12", "credit_spread", "unemp_rise", "payrolls_6m"),
    "labor_deterioration": ("term_spread", "term_spread_min12", "credit_spread", "unemp_rise", "payrolls_6m"),
    "inflation_rising": ("cpi_momentum", "cpi_12m", "unemp_rise", "term_spread"),
}
BENCH_FEATURES = {"recession": ("term_spread_min12",), "labor_deterioration": ("term_spread_min12",),
                  "inflation_rising": ("cpi_momentum",)}
TARGET_TEXT = {
    "recession": "The economy is in an NBER-dated recession at some point in the next {h} months",
    "labor_deterioration": "Unemployment rises 0.5 points or more above its latest known level within {h} months",
    "inflation_rising": "The 12-month inflation rate is higher in {h} months than its latest known level",
}


# --------------------------------------------------------------------------
# Calendar helpers and data
# --------------------------------------------------------------------------
def shift(month: str, k: int) -> str:
    y, m = int(month[:4]), int(month[5:7])
    i = y * 12 + m - 1 + k
    return f"{i // 12:04d}-{i % 12 + 1:02d}"


def month_range(start: str, end: str):
    m = start
    while m <= end:
        yield m
        m = shift(m, 1)


def load(data_dir: Path) -> dict:
    data = {}
    for name in SERIES:
        path = Path(data_dir) / f"{name}_monthly.csv"
        with path.open(newline="") as handle:
            data[name] = {row["date"][:7]: float(row["value"]) for row in csv.DictReader(handle)}
    return data


def visible(data: dict, t: str) -> dict:
    """Only observations available at the end of month t (publication lags)."""
    return {name: {m: v for m, v in data[name].items() if m <= shift(t, -LAG[name])}
            for name in LAG}


# --------------------------------------------------------------------------
# Point-in-time features
# --------------------------------------------------------------------------
def _avg3(series, m):
    vals = [series.get(shift(m, -k)) for k in range(3)]
    return None if None in vals else sum(vals) / 3


def features_at(data: dict, t: str) -> dict | None:
    """Features known at the end of month t, or None if any is unavailable."""
    v = visible(data, t)
    g, tb, baa, u, pay, cpi = (v["GS10"], v["TB3MS"], v["BAA"], v["UNRATE"], v["PAYEMS"], v["CPIAUCSL"])
    m1 = shift(t, -1)
    try:
        spreads = [g[shift(t, -k)] - tb[shift(t, -k)] for k in range(12)]
        now = _avg3(u, m1)
        prior = [_avg3(u, shift(m1, -k)) for k in range(1, 13)]
        if now is None or None in prior:
            return None
        cpi12 = 100 * math.log(cpi[m1] / cpi[shift(m1, -12)])
        cpi3 = 400 * math.log(cpi[m1] / cpi[shift(m1, -3)])
        return {
            "term_spread": spreads[0],
            "term_spread_min12": min(spreads),
            "credit_spread": baa[t] - g[t],
            "unemp_rise": now - min(prior),
            "payrolls_6m": 100 * math.log(pay[m1] / pay[shift(m1, -6)]),
            "cpi_12m": cpi12,
            "cpi_momentum": cpi3 - cpi12,
        }
    except KeyError:
        return None


# --------------------------------------------------------------------------
# Targets (outcomes) — only for scoring and as lagged training labels
# --------------------------------------------------------------------------
def outcome(data: dict, target: str, t: str, h: int):
    future = [shift(t, k) for k in range(1, h + 1)]
    if target == "recession":
        rec = data["USREC"]
        if any(m not in rec for m in future):
            return None
        return int(any(rec[m] >= 0.5 for m in future))
    u = data["UNRATE"]
    known = u.get(shift(t, -1))
    if target == "labor_deterioration":
        if known is None or any(m not in u for m in future):
            return None
        return int(max(u[m] for m in future) - known >= 0.5)
    if target == "inflation_rising":
        cpi = data["CPIAUCSL"]
        a, b = shift(t, -1), shift(t, h)
        try:
            now = math.log(cpi[a] / cpi[shift(a, -12)])
            later = math.log(cpi[b] / cpi[shift(b, -12)])
        except KeyError:
            return None
        return int(later > now)
    raise ValueError(target)


def label_known_by(target: str, origin: str, h: int) -> str:
    delay = RECESSION_LABEL_DELAY if target == "recession" else MACRO_LABEL_DELAY
    return shift(origin, h + delay)


# --------------------------------------------------------------------------
# Regularised logistic regression (pure Python, Newton/IRLS)
# --------------------------------------------------------------------------
def _solve(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        if abs(m[c][c]) < 1e-12:
            raise ValueError("Singular system")
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                for k in range(c, n + 1):
                    m[r][k] -= f * m[c][k]
    return [m[i][n] / m[i][i] for i in range(n)]


def fit_logistic(x, y, l2=L2, iters=25):
    """Return (weights, means, sds); features standardised on training data."""
    k = len(x[0])
    means = [sum(r[j] for r in x) / len(x) for j in range(k)]
    sds = [max(1e-9, math.sqrt(sum((r[j] - means[j]) ** 2 for r in x) / len(x))) for j in range(k)]
    z = [[1.0] + [(r[j] - means[j]) / sds[j] for j in range(k)] for r in x]
    w = [0.0] * (k + 1)
    for _ in range(iters):
        grad = [0.0] * (k + 1)
        hess = [[0.0] * (k + 1) for _ in range(k + 1)]
        for row, yi in zip(z, y):
            s = sum(wi * xi for wi, xi in zip(w, row))
            p = 1 / (1 + math.exp(-max(-35, min(35, s))))
            for a in range(k + 1):
                grad[a] += (yi - p) * row[a]
                pa = p * (1 - p) * row[a]
                for b in range(a, k + 1):
                    hess[a][b] += pa * row[b]
        for a in range(k + 1):
            for b in range(a):
                hess[a][b] = hess[b][a]
            if a:  # do not penalise the intercept
                grad[a] -= l2 * w[a]
                hess[a][a] += l2
        step = _solve(hess, grad)
        w = [wi + si for wi, si in zip(w, step)]
        if max(abs(s) for s in step) < 1e-8:
            break
    return w, means, sds


def predict(model, row):
    w, means, sds = model
    s = w[0] + sum(wj * (v - m) / sd for wj, v, m, sd in zip(w[1:], row, means, sds))
    return 1 / (1 + math.exp(-max(-35, min(35, s))))


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------
def brier(p, y):
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(y)


def auc(p, y):
    pos = sum(y)
    neg = len(y) - pos
    if not pos or not neg:
        return None
    order = sorted(range(len(p)), key=lambda i: p[i])
    ranks = [0.0] * len(p)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and p[order[j + 1]] == p[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    rsum = sum(r for r, yy in zip(ranks, y) if yy)
    return (rsum - pos * (pos + 1) / 2) / (pos * neg)


def episodes(rows):
    """Count runs of consecutive positive outcomes (independent events)."""
    count, prev = 0, 0
    for r in rows:
        if r["y"] and not prev:
            count += 1
        prev = r["y"]
    return count


def calibration(p, y):
    edges = (0, 0.1, 0.3, 0.5, 0.7, 1.0001)
    out = []
    for lo, hi in zip(edges, edges[1:]):
        idx = [i for i, v in enumerate(p) if lo <= v < hi]
        if idx:
            out.append({"bucket": f"{lo:.1f}-{min(hi, 1):.1f}", "n": len(idx),
                        "mean_forecast": round(sum(p[i] for i in idx) / len(idx), 3),
                        "observed": round(sum(y[i] for i in idx) / len(idx), 3)})
    return out


def overconfidence(cal):
    """Largest forecast-minus-observed gap among buckets with p >= 0.3 and n >= 10."""
    gaps = [c["mean_forecast"] - c["observed"] for c in cal
            if c["n"] >= 10 and c["mean_forecast"] >= 0.3]
    return round(max(gaps), 3) if gaps else 0.0


def summarise(rows, key):
    p = [r[key] for r in rows]
    y = [r["y"] for r in rows]
    base = [r["base"] for r in rows]
    b, b0 = brier(p, y), brier(base, y)
    return {"n": len(rows), "events": sum(y), "episodes": episodes(rows),
            "brier": round(b, 4), "brier_base_rate": round(b0, 4),
            "bss_vs_base_rate": round(1 - b / b0, 3) if b0 else None,
            "auc": None if auc(p, y) is None else round(auc(p, y), 3)}


# --------------------------------------------------------------------------
# V6.3 descriptive rubric as a benchmark (is "Deteriorating" predictive?)
# --------------------------------------------------------------------------
def rubric_flag(data, t):
    try:
        from .v63_historical_replay import assessment_at
        from .v63_interpretation import interpret
    except ImportError:
        from v63_historical_replay import assessment_at
        from v63_interpretation import interpret
    sub = {"INDPRO": data["INDPRO"], "UNRATE": data["UNRATE"], "CPIAUCSL": data["CPIAUCSL"]}
    a = assessment_at(sub, t)  # macro observations through month t-1, as published
    if a is None or any(a.get(k) is None for k in ("industrial_production_growth_12m_log_pct",
                                                    "cpi_inflation_12m_log_pct", "unemployment_change_3m_pp")):
        return None
    view = interpret(a, "PASS", date.fromisoformat(a["assessment_date"]))
    return None if view["condition"] == "Insufficient evidence" else int(view["condition"] == "Deteriorating")


# --------------------------------------------------------------------------
# Out-of-sample evaluation
# --------------------------------------------------------------------------
def evaluate(data: dict, target: str, h: int, end: str | None = None):
    feats = FEATURES[target]
    bench = BENCH_FEATURES[target]
    months = sorted(set(data["GS10"]) & set(data["TB3MS"]) & set(data["BAA"]) & set(data["UNRATE"]))
    last = end or months[-1]
    panel = {}
    for t in month_range(months[0], last):
        f = features_at(data, t)
        if f is not None:
            panel[t] = f
    rubric_cache = data.setdefault("_rubric_cache", {})
    rows, model, bmodel, rubric_rates, fitted_at = [], None, None, None, None
    for t in sorted(panel):
        if t < EVAL_START:
            continue
        y = outcome(data, target, t, h)
        if y is None:
            continue
        if fitted_at is None or t >= shift(fitted_at, REFIT_EVERY):
            train = [(s, panel[s]) for s in sorted(panel)
                     if label_known_by(target, s, h) <= t and outcome(data, target, s, h) is not None]
            if len(train) < MIN_TRAIN:
                continue
            ys = [outcome(data, target, s, h) for s, _ in train]
            if 0 < sum(ys) < len(ys):
                model = fit_logistic([[f[k] for k in feats] for _, f in train], ys)
                bmodel = fit_logistic([[f[k] for k in bench] for _, f in train], ys)
            base_rate = sum(ys) / len(ys)
            # Benchmark: frequency of the outcome when the V6.3 rubric said
            # Deteriorating vs not, estimated on the same past-only data.
            flags = []
            for s, _ in train:
                if s not in rubric_cache:
                    rubric_cache[s] = rubric_flag(data, s)
                if rubric_cache[s] is not None:
                    flags.append((rubric_cache[s], outcome(data, target, s, h)))
            on = [o for fl, o in flags if fl == 1]
            off = [o for fl, o in flags if fl == 0]
            rubric_rates = ((sum(on) + base_rate) / (len(on) + 1), (sum(off) + base_rate) / (len(off) + 1))
            fitted_at = t
        if model is None:
            continue
        f = panel[t]
        if t not in rubric_cache:
            rubric_cache[t] = rubric_flag(data, t)
        rf = rubric_cache[t]
        rows.append({"origin": t, "y": y, "base": base_rate,
                     "model": predict(model, [f[k] for k in feats]),
                     "curve": predict(bmodel, [f[k] for k in bench]),
                     "rubric": base_rate if rf is None else rubric_rates[0 if rf == 1 else 1]})
    return rows, panel


def assess(rows, target, h):
    general = [r for r in rows if not PANDEMIC[0] <= r["origin"] <= PANDEMIC[1]]
    full = {k: summarise(rows, k) for k in ("model", "curve", "rubric")}
    ex = {k: summarise(general, k) for k in ("model", "curve", "rubric")}
    cal = calibration([r["model"] for r in rows], [r["y"] for r in rows])
    oc = overconfidence(cal)
    m = full["model"]
    checks = {
        "bss_vs_base_rate": m["bss_vs_base_rate"] is not None and m["bss_vs_base_rate"] >= GATE["bss_vs_base_rate"],
        "auc": m["auc"] is not None and m["auc"] >= GATE["auc"],
        "episodes": m["episodes"] >= GATE["min_episodes"],
        "calibration": oc <= GATE["max_overconfidence"],
    }
    return {"target": target, "horizon_months": h, "definition": TARGET_TEXT[target].format(h=h),
            "features": list(FEATURES[target]), "evaluation_start": rows[0]["origin"] if rows else None,
            "evaluation_end": rows[-1]["origin"] if rows else None,
            "full_sample": full, "excluding_pandemic_window": ex,
            "calibration": cal, "overconfidence": oc,
            "gate_checks": checks, "publishable": all(checks.values())}


def band(p, base):
    if p >= 0.5:
        return "High"
    if p >= 2 * base:
        return "Elevated"
    if p <= 0.5 * base:
        return "Low"
    return "Typical"


def current_outlook(data, panel, target, h, verdict):
    t = max(panel)
    known_by = t
    train = [(s, panel[s]) for s in sorted(panel)
             if label_known_by(target, s, h) <= known_by and outcome(data, target, s, h) is not None]
    ys = [outcome(data, target, s, h) for s, _ in train]
    feats = FEATURES[target]
    base = sum(ys) / len(ys)
    out = {"target": target, "horizon_months": h, "forecast_origin": t,
           "definition": TARGET_TEXT[target].format(h=h), "historical_base_rate": round(base, 3),
           "training_months": len(train)}
    if not verdict["publishable"]:
        out.update({"state": "Insufficient evidence", "probability": None, "band": None,
                    "reason": "Out-of-sample evidence gate not passed: " +
                              ", ".join(k for k, ok in verdict["gate_checks"].items() if not ok)})
        return out
    p = predict(fit_logistic([[f[k] for k in feats] for _, f in train], ys), [panel[t][k] for k in feats])
    shown = min(0.95, max(0.05, round(p * 20) / 20))
    text = ("under 5%" if p < 0.05 else "over 95%" if p > 0.95 else f"about {round(shown * 100)}%")
    out.update({"state": "Published", "probability": round(shown, 2), "probability_text": text, "band": band(p, base),
                "inputs": {k: round(panel[t][k], 3) for k in feats}})
    return out


def run(data: dict, end: str | None = None) -> dict:
    results, outlooks, archive = [], [], []
    for target in FEATURES:
        for h in HORIZONS:
            rows, panel = evaluate(data, target, h, end)
            if not rows:
                continue
            verdict = assess(rows, target, h)
            results.append(verdict)
            outlooks.append(current_outlook(data, panel, target, h, verdict))
            archive.extend({"target": target, "horizon_months": h, "origin": r["origin"],
                            "probability": round(r["model"], 4), "outcome": r["y"]} for r in rows)
    return {"status": "V7_FORECAST_EVALUATION_RESEARCH", "generated": date.today().isoformat(),
            "point_in_time": {"publication_lags_months": LAG, "recession_label_delay_months": RECESSION_LABEL_DELAY,
                              "refit_every_months": REFIT_EVERY, "vintage": "current-vintage FRED; market inputs unrevised, macro inputs may be revised"},
            "gate": GATE, "evaluations": results, "current_outlooks": outlooks,
            "forecast_archive": archive}


def markdown(report: dict) -> str:
    lines = ["# V7 forecast evaluation (out-of-sample, chronological)", "",
             "| Target | h | n | episodes | Brier | BSS vs base | AUC | curve-only BSS | rubric BSS | publishable |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for e in report["evaluations"]:
        m, c, r = e["full_sample"]["model"], e["full_sample"]["curve"], e["full_sample"]["rubric"]
        lines.append(f"| {e['target']} | {e['horizon_months']} | {m['n']} | {m['episodes']} | {m['brier']} | "
                     f"{m['bss_vs_base_rate']} | {m['auc']} | {c['bss_vs_base_rate']} | {r['bss_vs_base_rate']} | "
                     f"{'YES' if e['publishable'] else 'no'} |")
    lines += ["", "Excluding pandemic window (model BSS / AUC):"]
    for e in report["evaluations"]:
        m = e["excluding_pandemic_window"]["model"]
        lines.append(f"- {e['target']} {e['horizon_months']}m: {m['bss_vs_base_rate']} / {m['auc']}")
    lines += ["", "Current outlooks:"]
    for o in report["current_outlooks"]:
        lines.append(f"- {o['target']} {o['horizon_months']}m (origin {o['forecast_origin']}): {o['state']}"
                     + (f", {o['probability_text']}, {o['band']} (base rate {o['historical_base_rate']})"
                        if o["state"] == "Published" else f" — {o.get('reason', '')}"))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data/v7"))
    parser.add_argument("--output", type=Path, default=Path("audit-output/v7_forecast_evaluation.json"))
    parser.add_argument("--end")
    args = parser.parse_args()
    report = run(load(args.data_dir), args.end)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    args.output.with_suffix(".md").write_text(markdown(report))
    print(markdown(report))


if __name__ == "__main__":
    main()
