"""Summarize credit/acceleration joint historical comparisons without predictive claims."""
import json
from pathlib import Path


def build(root):
    output = {"status": "RETROSPECTIVE_DESCRIPTIVE_ONLY", "results": [],
              "limitations": [
                  "Consumer and business credit are economy-wide, not industry-specific leverage",
                  "Median thresholds use the full retrospective sample",
                  "The 20 percent drawdown threshold is equity-oriented and may be unsuitable for national housing prices",
                  "Month labels are not source publication dates; these are not point-in-time signals",
                  "Overlapping observation windows cannot be treated as independent observations",
                  "Joint associations are not causal estimates or validated forecasts",
              ]}
    for asset in ("NASDAQCOM", "CSUSHPINSA"):
        for horizon in (6, 12, 24):
            path = root / "audit-output" / f"{asset}_credit_joint_{horizon}m.json"
            data = json.loads(path.read_text())
            assert data["status"] == "RETROSPECTIVE_DESCRIPTIVE_ONLY"
            assert data["horizon_months"] == horizon
            for indicator in ("consumer_credit_growth", "business_credit_growth"):
                comparison = data["joint_comparisons"][indicator]
                if comparison["status"] == "NO_OVERLAP":
                    output["results"].append({"asset": asset, "horizon": horizon,
                                               "indicator": indicator, "status": "NO_OVERLAP"})
                    continue
                cells = comparison["cells"]
                assert sum(c["months"] for c in cells.values()) == comparison["eligible_months"]
                assert all(c["declines"] + c["no_decline"] == c["months"] for c in cells.values())
                output["results"].append({
                    "asset": asset, "horizon": horizon, "indicator": indicator,
                    "eligible_months": comparison["eligible_months"],
                    "missing_months": comparison["missing_months"],
                    "retrospective_median": comparison["retrospective_indicator_median"],
                    "cells": cells,
                })
    return output


def render(report):
    lines = ["# Acceleration and credit: historical joint comparisons", "",
             "**Retrospective descriptive only — not a market warning or forecast.**", "",
             "| Asset | Months forward | Credit indicator | Acceleration | Credit above retrospective median | Observations | Subsequent declines | Decline fraction |",
             "|---|---:|---|---|---|---:|---:|---:|"]
    for item in report["results"]:
        if item.get("status") == "NO_OVERLAP":
            lines.append(f"| {item['asset']} | {item['horizon']} | {item['indicator']} | N/A | N/A | 0 | N/A | N/A |")
            continue
        for acceleration in (0, 1):
            for credit in (0, 1):
                cell = item["cells"][f"acceleration_{acceleration}_indicator_{credit}"]
                fraction = "N/A" if cell["fraction"] is None else f"{cell['fraction'] * 100:.1f}%"
                lines.append(f"| {item['asset']} | {item['horizon']} | {item['indicator']} | {acceleration} | {credit} | {cell['months']} | {cell['declines']} | {fraction} |")
    lines += ["", "## Limitations", ""]
    lines += [f"- {note}" for note in report["limitations"]]
    lines.append("")
    return "\n".join(lines)


def main():
    root = Path(".")
    result = build(root)
    folder = root / "audit-output"
    folder.mkdir(exist_ok=True)
    (folder / "industry_credit_joint_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    (folder / "industry_credit_joint_summary.md").write_text(render(result))
    print(render(result))


if __name__ == "__main__":
    main()
