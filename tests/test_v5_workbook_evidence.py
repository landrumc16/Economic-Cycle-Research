import unittest
from scripts.v5_workbook_evidence import convert

URL = "https://docs.google.com/spreadsheets/d/1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE/edit"


def rows(status="BLOCKED", check="PARTIAL", vintage="PENDING"):
    return [[s, "BLS" if s != "GDPC1" else "BEA", "", "", "", check, vintage, status]
            for s in ("UNRATE", "CPIAUCSL", "GDPC1")]


class WorkbookEvidenceTests(unittest.TestCase):
    def test_blocked_inputs_remain_blocked(self):
        result = convert(rows(), URL, reviewed=True)
        self.assertEqual(set(result["macro_promotion"].values()), {"BLOCKED"})

    def test_unreviewed_apparent_approval_fails_closed(self):
        result = convert(rows("APPROVED", "PASS", "PASS"), URL)
        self.assertEqual(set(result["macro_promotion"].values()), {"BLOCKED"})

    def test_approval_requires_all_three_gates(self):
        result = convert(rows("APPROVED", "PASS", "PASS"), URL, reviewed=True)
        self.assertEqual(set(result["macro_promotion"].values()), {"APPROVED"})

    def test_incomplete_rows_rejected(self):
        with self.assertRaises(ValueError):
            convert(rows()[:2], URL, reviewed=True)


if __name__ == "__main__":
    unittest.main()
