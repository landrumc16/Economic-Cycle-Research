"""Browser smoke checks against the *deployed* V6.2 GitHub Pages site.

Run: python scripts/v62_browser_acceptance.py --url https://.../Economic-Cycle-Research/
Requires: playwright and an installed Chromium browser.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

WIDTHS = (360, 768, 1440)
PAGES = ("", "research.html", "sectors.html", "monthly-research.html")
SECTORS = (
    "communication-services", "consumer-discretionary", "consumer-staples",
    "energy", "financials", "health-care", "industrials",
    "information-technology", "materials", "real-estate", "utilities",
)


def inspect(base_url: str, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for width in WIDTHS:
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            for path in PAGES:
                url = urljoin(base_url, path)
                response = page.goto(url, wait_until="networkidle", timeout=30000)
                assert response and response.status == 200, f"{url}: HTTP {response.status if response else 'none'}"
                assert page.locator("h1").count() >= 1, f"{url}: missing primary heading"
                sizes = page.evaluate("""() => ({
                    document: document.documentElement.scrollWidth,
                    viewport: document.documentElement.clientWidth,
                    body: document.body.scrollWidth
                })""")
                assert max(sizes["document"], sizes["body"]) <= sizes["viewport"] + 2, (
                    f"{url} at {width}px: horizontal overflow {sizes}"
                )
                page.screenshot(path=str(output / f"{width}-{path.replace('/', '-') or 'index.html'}.png"), full_page=True)
                results.append({"width": width, "page": path or "index.html", "http": response.status, "overflow": False})
            page.goto(base_url, wait_until="networkidle")
            page.keyboard.press("Tab")
            focused = page.evaluate("() => document.activeElement?.tagName")
            assert focused not in (None, "BODY", "HTML"), f"Keyboard focus absent at {width}px"
            page.close()
        page = browser.new_page()
        response = page.goto(urljoin(base_url, "sectors.html"), wait_until="networkidle")
        assert response and response.status == 200
        links = page.locator("a[href]").evaluate_all("(items) => items.map(a => a.getAttribute('href'))")
        for sector in SECTORS:
            assert any(sector in href for href in links), f"Missing sector navigation: {sector}"
        browser.close()
    assert not errors, f"Uncaught browser errors: {errors}"
    (output / "results.json").write_text(json.dumps({"passed": True, "checks": results, "uncaught_errors": errors}, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", default="v62-browser-evidence")
    args = parser.parse_args()
    inspect(args.url.rstrip("/") + "/", Path(args.output))
