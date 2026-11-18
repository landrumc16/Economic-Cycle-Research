"""Fetch V7 Pass B research data from qualified free sources (runs in CI).

* Kenneth R. French Data Library (Dartmouth): 49 industry portfolios (value-
  weighted monthly returns) and the Fama/French market factors. Free for
  research use with attribution.
* Aswath Damodaran (NYU Stern) US industry P/E and expected-growth table
  (annual vintage, January). Free with attribution.
* ALFRED (FRED API, output_type=4): first-release UNRATE and PAYEMS.

Outputs go to data/v7_research/ with a provenance manifest. Nothing is
imputed; sentinel missing values (-99.99 / -999) are dropped.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

FRENCH = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
SOURCES = {
    "industries": FRENCH + "49_Industry_Portfolios_CSV.zip",
    "factors": FRENCH + "F-F_Research_Data_Factors_CSV.zip",
    "damodaran_pe": "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html",
}
UA = {"User-Agent": "economic-cycle-research/1.0 (research; contact via repository)"}


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def french_monthly(raw: bytes) -> tuple[list[str], dict]:
    """First monthly block of a French CSV zip: header + YYYYMM rows."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0]).decode("latin-1")
    header, rows = None, {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split(",")]
        if header is None:
            if len(cells) > 2 and cells[0] == "" and cells[1]:
                header = cells[1:]
            continue
        if len(cells[0]) == 6 and cells[0].isdigit():
            month = f"{cells[0][:4]}-{cells[0][4:]}"
            vals = {}
            for name, v in zip(header, cells[1:]):
                try:
                    x = float(v)
                except ValueError:
                    continue
                if x > -99:  # -99.99 / -999 are French's missing-value sentinels
                    vals[name] = x
            rows[month] = vals
        elif rows:
            break  # end of the first (monthly) block
    if not header or not rows:
        raise ValueError("Unexpected French CSV layout")
    return header, rows


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell, self._in = [], None, "", False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._in, self._cell = True, ""

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None:
            self._row.append(" ".join(self._cell.split()))
            self._in = False
        elif tag == "tr" and self._row:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._in:
            self._cell += data


def damodaran(raw: bytes) -> list[dict]:
    p = Tables()
    p.feed(raw.decode("latin-1"))
    header_idx = next(i for i, r in enumerate(p.rows) if r and r[0].lower().startswith("industry"))
    header = p.rows[header_idx]
    out = []
    for r in p.rows[header_idx + 1:]:
        if len(r) == len(header) and r[0]:
            out.append(dict(zip(header, r)))
    if len(out) < 50:
        raise ValueError("Unexpected Damodaran table layout")
    return out


def alfred_first_release(series: str, api_key: str) -> dict:
    q = urllib.parse.urlencode({"series_id": series, "api_key": api_key, "file_type": "json",
                                "realtime_start": "1776-07-04", "realtime_end": "9999-12-31",
                                "output_type": 4})
    data = json.loads(get("https://api.stlouisfed.org/fred/series/observations?" + q))
    out = {}
    for o in data.get("observations", []):
        if o.get("value") not in (None, "", "."):
            out[o["date"][:7]] = float(o["value"])
    if not out:
        raise ValueError("No first-release observations: " + series)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("data/v7_research"))
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"retrieved": date.today().isoformat(), "sources": {}, "notes": [
        "French industry returns are value-weighted monthly percent returns; Mkt-RF and RF are percent.",
        "Damodaran data are an annual vintage (published each January) and are context, not current valuation.",
        "ALFRED output_type=4 gives each observation's value as first released."]}
    header, ind = french_monthly(get(SOURCES["industries"]))
    with (a.output_dir / "french_49_industries_vw_monthly.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month"] + header)
        for m in sorted(ind):
            w.writerow([m] + [ind[m].get(h, "") for h in header])
    manifest["sources"]["french_49_industries"] = {"url": SOURCES["industries"], "first": min(ind), "last": max(ind)}
    fh, fac = french_monthly(get(SOURCES["factors"]))
    with (a.output_dir / "french_factors_monthly.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month"] + fh)
        for m in sorted(fac):
            w.writerow([m] + [fac[m].get(h, "") for h in fh])
    manifest["sources"]["french_factors"] = {"url": SOURCES["factors"], "first": min(fac), "last": max(fac)}
    pe = damodaran(get(SOURCES["damodaran_pe"]))
    (a.output_dir / "damodaran_pe_us.json").write_text(json.dumps(pe, indent=1) + "\n")
    manifest["sources"]["damodaran_pe"] = {"url": SOURCES["damodaran_pe"], "industries": len(pe),
                                           "columns": list(pe[0])}
    key = os.environ.get("FRED_API_KEY", "").strip()
    if key:
        for s in ("UNRATE", "PAYEMS"):
            fr = alfred_first_release(s, key)
            with (a.output_dir / f"{s}_first_release.csv").open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date", "value"])
                w.writerows((m + "-01", v) for m, v in sorted(fr.items()))
            manifest["sources"][f"alfred_{s}"] = {"url": "https://api.stlouisfed.org/fred/series/observations?series_id="
                                                  + s + "&output_type=4", "first": min(fr), "last": max(fr)}
    (a.output_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
