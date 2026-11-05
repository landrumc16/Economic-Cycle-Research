"""Version 6.2 public-site contract: verify generated evidence before publication.

Read-only validation; never rewrites an accepted monthly assessment.
"""
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from scripts.v6_1_release_gate import validate as validate_v61

PAGES = ("overview.html", "historical.html", "sectors.html",
         "monthly-research.html", "research.html") + tuple(
             f"sector-{i:02d}.html" for i in range(1, 12))
DISCLAIMER = "not personalized financial advice"


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.headings = []
        self.has_main = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "main":
            self.has_main = True
        if tag in {"h1", "h2", "h3"}:
            self.headings.append(tag)


def validate(directory: Path) -> dict:
    root = Path(directory)
    baseline = validate_v61(root)
    parsed = {}
    for name in PAGES:
        content = (root / name).read_text(encoding="utf-8")
        if DISCLAIMER not in content.lower():
            raise ValueError(f"Missing educational disclaimer: {name}")
        parser = PageLinks()
        parser.feed(content)
        if not parser.has_main or "h1" not in parser.headings:
            raise ValueError(f"Missing accessible document structure: {name}")
        parsed[name] = parser
    for name, parser in parsed.items():
        for href in parser.links:
            url = urlsplit(href)
            if url.scheme or url.netloc or href.startswith(("mailto:", "tel:")):
                continue
            if url.path.startswith("/"):
                raise ValueError(f"Absolute local link cannot be checked: {name}: {href}")
            destination = url.path or name
            if ".." in Path(destination).parts:
                raise ValueError(f"Unsafe internal link: {name}: {href}")
            if not (root / destination).is_file():
                raise ValueError(f"Broken internal link: {name}: {href}")
            if url.fragment:
                target = parsed.get(destination)
                if target is None and destination.endswith(".html"):
                    target = PageLinks()
                    target.feed((root / destination).read_text(encoding="utf-8"))
                if target is not None and url.fragment not in target.ids:
                    raise ValueError(f"Broken internal anchor: {name}: {href}")
    overview = (root / "overview.html").read_text()
    for heading in ("Where We Are", "Where We Are Heading", "Where Investors Should Look"):
        if heading not in overview:
            raise ValueError(f"Missing executive answer: {heading}")
    research = (root / "research.html").read_text()
    if "<details>" not in research or "<summary>" not in research:
        raise ValueError("Research library must be collapsible")
    report = json.loads((root / "v6_sector_report.json").read_text())
    if len(report["sectors"]) != 11:
        raise ValueError("Missing sector coverage")
    for name in PAGES[5:]:
        page = (root / name).read_text()
        if "Economic sensitivity" not in page or "Investment evidence" not in page:
            raise ValueError(f"Missing economic/investment distinction: {name}")
    return {"status": "V6_2_SITE_CONTRACT_PASS", "pages_checked": len(PAGES),
            "sector_count": 11, "monthly_gate": baseline["monthly_gate"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("audit-output"))
    args = parser.parse_args()
    print(json.dumps(validate(args.directory), indent=2))


if __name__ == "__main__":
    main()
