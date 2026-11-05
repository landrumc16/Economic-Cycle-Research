"""Verify the shared public-site template discloses nonpersonalized scope."""
import unittest
from scripts.v6_public_site import page


class DisclosureTests(unittest.TestCase):
    def test_every_generated_page_inherits_disclosure(self):
        for title in ("Overview", "Sectors", "Sector Detail", "Research Library"):
            with self.subTest(title=title):
                markup = page(title, "<p>Research</p>")
                self.assertIn("not personalized financial advice", markup)
                self.assertIn("not recommendations tailored to any individual", markup)
                self.assertIn("past performance does not guarantee future results", markup)
                self.assertIn("loss of principal", markup)
                self.assertIn("Numeric crash forecasts are not certified", markup)


if __name__ == "__main__":
    unittest.main()
