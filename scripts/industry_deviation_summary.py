"""Consolidate industry deviation comparisons into a readable descriptive report."""
import argparse
import csv
import json
from pathlib import Path

SERIES = ("NASDAQCOM", "CSUSHPINSA")
HORIZONS = (6, 12, 24)


def build(root):
    report = {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY", "predictive_claims": "BLOCKED",
              "series": {}, "limitations": [
                  "Overlapping monthly windows are not independent",
                  "NASDAQCOM is a broad equity proxy, not an isolated internet or AI industry",
                  "CSUSHPINSA measures national home prices, not housing equity",
                  "Current-vintage data are not point-in-time certified",
                  "20 percent housing drawdowns are not directly comparable with equity drawdowns"]}
    for series in SERIES:
        results = []
        for horizon in HORIZONS:
            suffix = "" if horizon == 12 else f"_{horizon}m"
            path = root / "audit-output" / f"{series}_comparison{suffix}.json"
            data = json.loads(path.read_text())
            assert data["horizon_months"] == horizon
            assert data["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
            groups = data["groups"]
            for group in groups.values():
                assert group["eligible"] == group["drawdown"] + group["no_drawdown"]
            results.append({
                "horizon_months": horizon,
                "high": groups["high_deviation"],
                "other": groups["other"],
                "fraction_difference": data["observed_fraction_difference_high_minus_other"],
                "excluded_no_baseline": data["excluded_no_baseline"],
                "excluded_incomplete_horizon": data["excluded_incomplete_horizon"],
            })
        report["series"][series] = results
    return report


def markdown(report):
    lines = ["# Industry Deviation Historical Comparison", "",
             "**Retrospective descriptive evidence only; not a crash forecast.**", "",
             "| Series | Horizon | High months | High drawdowns | High no-drawdowns | Other months | Other drawdowns | Difference (pp) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for series, horizons in report["series"].items():
        for item in horizons:
            high, other = item["high"], item["other"]
            difference = item["fraction_difference"]
            pp = "N/A" if difference is None else f"{difference * 100:+.1f}"
            lines.append(f"| {series} | {item['horizon_months']} | {high['eligible']} | {high['drawdown']} | {high['no_drawdown']} | {other['eligible']} | {other['drawdown']} | {pp} |")
    lines += ["", "## Interpretation limits", ""]
    lines += [f"- {limitation}" for limitation in report["limitations"]]
    lines += ["", "A positive difference is an observed association, not validated forecasting ability or evidence of causation.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    result = build(root)
    output = root / "audit-output"
    output.mkdir(exist_ok=True)
    (output / "industry_deviation_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "industry_deviation_summary.md").write_text(markdown(result))
    print(markdown(result))


if __name__ == "__main__":
    main()
