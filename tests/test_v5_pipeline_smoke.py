"""End-to-end V5 descriptive artifact smoke test without external economic data."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class V5PipelineSmokeTests(unittest.TestCase):
    def test_full_descriptive_pipeline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = {
                "standardized": {"report_type": "V5_STANDARDIZED_MACRO_METRICS",
                                 "as_of": "2026-10-31", "metrics": []},
                "mechanisms": {"report_type": "V5_MECHANISM_EVIDENCE_GATE",
                               "mechanisms": {"monetary": {"required_features": [],
                                                          "pit_features_verified": []}},
                               "prediction_status": "BLOCKED"},
                "outcomes": {"event_count": 0,
                             "coverage_status": "NO_VERIFIED_OUTCOME_INPUTS"},
                "replay": {"report_type": "V5_PIT_REPLAY",
                           "publisher_original_coverage": 0,
                           "predictive_publication": "BLOCKED"},
            }
            for name, value in inputs.items():
                (root / (name + ".json")).write_text(json.dumps(value))
            repo = Path(__file__).resolve().parents[1]
            def run(script, *args):
                subprocess.run([sys.executable, str(repo / "scripts" / script), *map(str, args)],
                               check=True, cwd=repo, capture_output=True, text=True)
            readout = root / "v5_weekly_research_readout.json"
            dashboard = root / "dashboard" / "weekly-v5.html"
            run("v5_weekly_research_readout.py",
                "--standardized", root / "standardized.json",
                "--mechanisms", root / "mechanisms.json",
                "--outcomes", root / "outcomes.json",
                "--replay", root / "replay.json", "--output", readout)
            run("v5_weekly_dashboard.py", "--readout", readout, "--output", dashboard)
            for name, target in [("mechanisms", "v5_mechanism_evidence_gate.json"),
                                 ("outcomes", "v5_objective_outcomes.json"),
                                 ("replay", "v5_pit_replay.json")]:
                (root / target).write_text((root / (name + ".json")).read_text())
            run("v5_release_acceptance.py", "--directory", root,
                "--output", root / "v5_release_acceptance.json")
            report = json.loads((root / "v5_release_acceptance.json").read_text())
            self.assertEqual(report["status"], "PASS_DESCRIPTIVE_ONLY")
            self.assertEqual(report["predictive_publication"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
