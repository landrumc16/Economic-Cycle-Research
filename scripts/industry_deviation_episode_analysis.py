"""Collapse overlapping monthly alerts into episodes; descriptive research only."""
import argparse
import csv
import json
from pathlib import Path

try:
    from .industry_deviation_metrics import calculate
except ImportError:
    from industry_deviation_metrics import calculate


def episodes(rows, horizon=12, threshold=0.20, cutoff=90):
    if horizon < 1 or not 0 < threshold < 1 or not 0 < cutoff <= 100:
        raise ValueError("Invalid parameters")
    ordered = sorted(rows, key=lambda row: row["date"])
    metrics = {item["date"]: item for item in calculate(ordered)}
    signals = []
    for index, row in enumerate(ordered):
        metric = metrics.get(row["date"])
        if metric and metric["historical_percentile"] is not None and (
            metric["historical_percentile"] >= cutoff and
            metric["trailing_log_return"] > 0
        ):
            signals.append(index)
    clusters = []
    for index in signals:
        if not clusters or index > clusters[-1][-1] + 1:
            clusters.append([index])
        else:
            clusters[-1].append(index)
    results = []
    eligible = 0
    hits = 0
    for cluster in clusters:
        start, end = cluster[0], cluster[-1]
        # Require a full observation horizon from the FIRST signal.
        complete = start + horizon < len(ordered)
        event = False
        lead = None
        maximum = None
        if complete:
            eligible += 1
            high = float(ordered[start]["value"])
            maximum = 0.0
            for index in range(start + 1, start + horizon + 1):
                price = float(ordered[index]["value"])
                high = max(high, price)
                drawdown = 1 - price / high
                maximum = max(maximum, drawdown)
                if not event and drawdown >= threshold:
                    event = True
                    lead = index - start
            hits += int(event)
        results.append({
            "first_alert": ordered[start]["date"],
            "last_alert": ordered[end]["date"],
            "alert_months": len(cluster),
            "full_followup": complete,
            "threshold_crossed": event if complete else None,
            "first_crossing_months_after_alert": lead,
            "max_forward_path_drawdown": round(maximum, 6) if complete else None,
        })
    return {
        "status": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
        "unit": "consecutive alert clusters; first alert anchors followup",
        "horizon_months": horizon,
        "threshold": threshold,
        "alert_clusters": len(results),
        "eligible_clusters": eligible,
        "clusters_with_decline": hits,
        "clusters_without_decline": eligible - hits,
        "clusters_without_full_followup": len(results) - eligible,
        "observed_hit_fraction": round(hits / eligible, 6) if eligible else None,
        "episodes": results,
        "limitations": "Cluster followups can overlap; not independent trials or validated predictions.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--output", required=True)
    parser.add_argument("--horizon", type=int, default=12)
    parser.add_argument("--threshold", type=float, default=0.20)
    args = parser.parse_args()
    with open(args.csv_path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = episodes(rows, horizon=args.horizon, threshold=args.threshold)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "alert_clusters", "eligible_clusters", "clusters_with_decline",
        "clusters_without_decline", "observed_hit_fraction"
    )}))


if __name__ == "__main__":
    main()
