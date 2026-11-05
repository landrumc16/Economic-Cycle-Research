"""Fast V6.2 site checks with no network or live research dependency."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.v62_site_contract import PAGES, validate


def fixture(root):
    for name in PAGES:
        content = ('<!doctype html><html><main><h1>Research</h1>'
                   '<p>Educational research — not personalized financial advice.</p>')
        if name == "overview.html":
            content += ("1. Where is the economy right now? | 2. Where do we think it is going? | "
                        "3. Where should investors look?")
        if name == "research.html":
            content += "<details><summary>Evidence</summary>Sources</details>"
        if name.startswith("sector-"):
            content += "Economic sensitivity | Investment evidence"
        content += '<a href="overview.html">Home</a></main></html>'
        (root / name).write_text(content)
    (root / "v6_sector_report.json").write_text(json.dumps(
        {"sectors": [{"sector": str(i)} for i in range(11)]}))


class SiteContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fixture(self.root)
        self.patch = patch("scripts.v62_site_contract.validate_v61",
                           return_value={"monthly_gate": "PASS"})
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_complete_site(self):
        self.assertEqual(validate(self.root)["pages_checked"], 16)

    def test_missing_disclaimer(self):
        p = self.root / "sector-01.html"
        p.write_text(p.read_text().replace("not personalized financial advice", ""))
        with self.assertRaisesRegex(ValueError, "disclaimer"):
            validate(self.root)

    def test_broken_internal_link(self):
        p = self.root / "overview.html"
        p.write_text(p.read_text().replace('href="overview.html"', 'href="missing.html"'))
        with self.assertRaisesRegex(ValueError, "Broken internal link"):
            validate(self.root)

    def test_rejects_path_traversal(self):
        p = self.root / "overview.html"
        p.write_text(p.read_text().replace('href="overview.html"', 'href="../secret.html"'))
        with self.assertRaisesRegex(ValueError, "Unsafe internal link"):
            validate(self.root)

    def test_broken_anchor(self):
        p = self.root / "overview.html"
        p.write_text(p.read_text().replace('href="overview.html"', 'href="overview.html#absent"'))
        with self.assertRaisesRegex(ValueError, "Broken internal anchor"):
            validate(self.root)

    def test_missing_sector_research_distinction(self):
        p = self.root / "sector-02.html"
        p.write_text(p.read_text().replace("Investment evidence", ""))
        with self.assertRaisesRegex(ValueError, "distinction"):
            validate(self.root)

    def test_missing_research_library(self):
        p = self.root / "research.html"
        p.write_text(p.read_text().replace("<details>", "<div>").replace("<summary>", "<p>"))
        with self.assertRaisesRegex(ValueError, "collapsible"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
