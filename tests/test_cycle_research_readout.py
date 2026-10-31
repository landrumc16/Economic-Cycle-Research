"""Research readout is descriptive and fails closed for missing inputs."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from cycle_research_readout import interpret

class CycleReadoutTests(unittest.TestCase):
    def test_complete_descriptive_readout(self):
        data = {"metrics": {"real_gdp_yoy_pct": {"value": 2.1},
                            "unemployment_3m_change_pp": {"value": 0.2},
                            "cpi_yoy_pct": {"value": 3.4}}}
        result = interpret(data)
        self.assertEqual(result["domains"]["growth"]["description"], "POSITIVE_REAL_GROWTH")
        self.assertEqual(result["domains"]["labor"]["description"], "UNEMPLOYMENT_RISING")
        self.assertEqual(result["domains"]["inflation"]["description"], "PRICES_RISING")
        self.assertIsNone(result["validated_cycle_stage"])
        self.assertEqual(result["publication"], "BLOCKED")

    def test_missing_data_blocks_cross_domain_interpretation(self):
        result = interpret({"metrics": {"real_gdp_yoy_pct": {"value": 1.2}}})
        self.assertEqual(result["cross_domain"], "INSUFFICIENT_DATA")
        self.assertIsNone(result["crash_probability"])

    def test_zero_change_is_not_missing(self):
        data = {"metrics": {"real_gdp_yoy_pct": {"value": 0},
                            "unemployment_3m_change_pp": {"value": 0},
                            "cpi_yoy_pct": {"value": 0}}}
        result = interpret(data)
        self.assertEqual(result["domains"]["labor"]["description"], "UNCHANGED")
        self.assertEqual(result["domains"]["growth"]["description"], "FLAT_REAL_GROWTH")

if __name__ == "__main__":
    unittest.main()
