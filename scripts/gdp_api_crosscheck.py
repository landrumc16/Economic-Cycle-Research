"""Reconcile BEA original quarterly real GDP against FRED GDPC1 API observations."""
import argparse
import json
from pathlib import Path
from api_crosscheck import compare

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bea", default="audit-output/bea-api/bea_gdpc1_normalized.json")
    p.add_argument("--fred", default="audit-output/fred-api/GDPC1_normalized.json")
    p.add_argument("--output", default="audit-output/gdp_api_crosscheck.json")
    args = p.parse_args()
    report = {"series": "GDPC1", "promotion": "BLOCKED", "vintage_status": "NOT VERIFIED"}
    try:
        publisher = json.loads(Path(args.bea).read_text())
        fred = json.loads(Path(args.fred).read_text())
        report.update(compare(publisher, fred, 0.005, 250))
    except (OSError, ValueError) as exc:
        report.update({"revised_series_pass": False, "error": f"{type(exc).__name__}: {exc}"})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["revised_series_pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
