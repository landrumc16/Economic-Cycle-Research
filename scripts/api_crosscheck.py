"""Reconcile normalized publisher API outputs with independent FRED API outputs.

Run only after both API acquisition jobs complete. Never approves point-in-time
vintages or Google Sheets promotion. The report is evidence, not a release gate.
"""
import argparse
import json
from pathlib import Path

SERIES = {
    "UNRATE": ("LNS14000000", 1e-6, 600),
    "CPIAUCSL": ("CUSR0000SA0", 0.005, 600),
}

def compare(bls, fred, tolerance, min_overlap):
    dates = sorted(set(bls) & set(fred))
    diffs = [{"date": d, "publisher": bls[d], "fred": fred[d]}
             for d in dates if abs(bls[d] - fred[d]) > tolerance]
    return {"overlap": len(dates), "first": dates[0] if dates else None,
            "last": dates[-1] if dates else None,
            "missing_publisher_count": len(set(fred) - set(bls)),
            "missing_fred_count": len(set(bls) - set(fred)),
            "mismatch_count": len(diffs), "mismatches": diffs[:100],
            "revised_series_pass": len(dates) >= min_overlap and not diffs}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bls", default="audit-output/bls-api")
    p.add_argument("--fred", default="audit-output/fred-api")
    p.add_argument("--output", default="audit-output/api_crosscheck.json")
    args = p.parse_args()
    report = {"series": {}, "errors": [], "vintage_status": "NOT VERIFIED",
              "promotion": "BLOCKED"}
    for series, (bls_id, tolerance, minimum) in SERIES.items():
        try:
            publisher = json.loads((Path(args.bls) / f"{bls_id}_normalized.json").read_text())
            fred = json.loads((Path(args.fred) / f"{series}_normalized.json").read_text())
            report["series"][series] = compare(publisher, fred, tolerance, minimum)
        except (OSError, ValueError) as exc:
            report["errors"].append(f"{series}: {type(exc).__name__}: {exc}")
            report["series"][series] = {"revised_series_pass": False}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if report["errors"] or not all(s["revised_series_pass"] for s in report["series"].values()):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
