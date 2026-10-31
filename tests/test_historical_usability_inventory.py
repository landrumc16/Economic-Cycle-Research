import unittest
from scripts.historical_usability_inventory import inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "source_workbook": "example",
            "pathways": {"rows": [["parent", "date"], ["1", "2000-01-01"]]},
            "noncrash": {"rows": [["month", "curve"], ["1999-01", "1"], ["1999-02", "2"]]},
        }
        self.leads = {"rows": [["id"], ["1"]]}

    def test_descriptive_inventory(self):
        result = inventory(self.snapshot, self.leads)
        self.assertEqual(result["monthly_rows"], 2)
        self.assertEqual(result["first_month"], "1999-01")
        self.assertEqual(result["crash_parent_clusters"], 1)
        self.assertFalse(result["point_in_time_certified"])
        self.assertEqual(result["predictive_publication"], "BLOCKED")

    def test_duplicate_months_rejected(self):
        self.snapshot["noncrash"]["rows"].append(["1999-02", "3"])
        with self.assertRaises(ValueError):
            inventory(self.snapshot, self.leads)

    def test_duplicate_parent_clusters_rejected(self):
        self.snapshot["pathways"]["rows"].append(["1", "2001-01-01"])
        with self.assertRaises(ValueError):
            inventory(self.snapshot, self.leads)


if __name__ == "__main__":
    unittest.main()
