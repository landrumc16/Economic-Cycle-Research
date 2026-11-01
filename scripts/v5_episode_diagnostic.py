"""Evaluate phase heuristics as episode-level signals, not independent monthly samples."""
import argparse
import json
from pathlib import Path

from scripts.v5_cycle_evaluation import REFERENCE_INTERVALS


def shift(month, n):
    year, m = map(int, month.split("-"))
    index = year * 12 + m - 1 + n
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def analyze(estimates):
    if estimates.get("status") != "HISTORICAL_RESEARCH_ONLY":
        raise ValueError("Expected historical estimates")
    rows = {r["month"]: r for r in estimates["timeline"]}
    episodes = []
    for start, end in REFERENCE_INTERVALS:
        pre = [shift(start, -k) for k in range(1, 13)]
        before = [m for m in pre if m in rows and rows[m]["phase"] in ("LATE_CYCLE", "CONTRACTION")]
        during = []
        m = start
        while m <= end:
            if m in rows and rows[m]["phase"] == "CONTRACTION":
                during.append(m)
            m = shift(m, 1)
        episodes.append({
            "reference_start": start, "reference_end": end,
            "pre_recession_12m_warning": bool(before),
            "first_warning_month": min(before) if before else None,
            "contraction_detected_during_episode": bool(during),
            "first_contraction_month": min(during) if during else None,
        })
    return {
        "status": "RETROSPECTIVE_EPISODE_DIAGNOSTIC_ONLY",
        "episodes": episodes,
        "episode_count": len(episodes),
        "pre_recession_warning_episodes": sum(e["pre_recession_12m_warning"] for e in episodes),
        "contraction_detected_episodes": sum(e["contraction_detected_during_episode"] for e in episodes),
        "limitations": [
            "Warnings use a broad late-cycle OR contraction heuristic and are not calibrated",
            "No control for warning prevalence in non-recession periods",
            "Revised data and ex-post recession chronology; no release-vintage reconstruction",
            "Four episodes are too few to establish reliable predictive skill",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("estimates")
    parser.add_argument("--output", default="audit-output/v5_episode_diagnostic.json")
    args = parser.parse_args()
    result = analyze(json.loads(Path(args.estimates).read_text()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"episodes": result["episode_count"],
                      "warnings": result["pre_recession_warning_episodes"],
                      "detected": result["contraction_detected_episodes"]}))


if __name__ == "__main__":
    main()
