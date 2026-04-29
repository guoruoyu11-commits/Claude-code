"""
Smoke tests for the EXVSDB Vue site.

Usage:
  py scripts/test_site.py
  py scripts/test_site.py --base-url http://127.0.0.1:5175
  py scripts/test_site.py --screenshots

The dev server should already be running, for example:
  npm run dev -- --host 127.0.0.1 --port 5175
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from playwright.sync_api import Page, sync_playwright


DEFAULT_BASE_URL = "http://127.0.0.1:5175"
VIEWPORTS = {
    "desktop": {"width": 1366, "height": 900},
    "mobile": {"width": 390, "height": 844},
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


class TestRun:
    def __init__(self) -> None:
        self.results: list[CheckResult] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.results.append(CheckResult(name, bool(condition), detail))

    def expect_text(self, name: str, actual: str, expected_part: str) -> None:
        self.check(name, expected_part in actual, actual.strip())

    def has_failures(self) -> bool:
        return any(not result.passed for result in self.results)

    def print_summary(self) -> None:
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            suffix = f" | {result.detail}" if result.detail else ""
            print(f"{status} | {result.name}{suffix}")

        passed = sum(1 for result in self.results if result.passed)
        total = len(self.results)
        print(f"\n{passed}/{total} checks passed")


def page_console_errors(page: Page) -> list[str]:
    errors: list[str] = []

    def on_console(message) -> None:
        if message.type == "error":
            errors.append(message.text)

    def on_page_error(error) -> None:
        errors.append(str(error))

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    return errors


def assert_no_horizontal_overflow(run: TestRun, page: Page, label: str) -> None:
    dims = page.evaluate(
        "() => ({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth })"
    )
    run.check(
        f"{label}: no horizontal page overflow",
        dims["scrollWidth"] <= dims["innerWidth"] + 1,
        f"scrollWidth={dims['scrollWidth']}, innerWidth={dims['innerWidth']}",
    )


def assert_header_controls(run: TestRun, page: Page, label: str) -> None:
    badge = page.locator(".header-badge").bounding_box()
    theme = page.locator(".theme-toggle").bounding_box()
    run.check(f"{label}: header controls measurable", badge is not None and theme is not None)
    if not badge or not theme:
        return

    run.check(
        f"{label}: header controls same height",
        abs(badge["height"] - theme["height"]) <= 1,
        f"badge={badge['height']:.1f}, theme={theme['height']:.1f}",
    )
    badge_mid = badge["y"] + badge["height"] / 2
    theme_mid = theme["y"] + theme["height"] / 2
    run.check(
        f"{label}: header controls vertically aligned",
        abs(badge_mid - theme_mid) <= 1,
        f"badgeY={badge['y']:.1f}, themeY={theme['y']:.1f}",
    )


def test_home(page: Page, run: TestRun, base_url: str, label: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    run.expect_text(f"{label}: home h1", page.locator("h1").inner_text(), "Tier")
    run.expect_text(f"{label}: initial cost heading", page.locator("h2").inner_text(), "3000 COST")
    run.check(f"{label}: tier table visible", page.locator(".tier-table").is_visible())
    run.check(f"{label}: removed info bar", page.locator(".info-bar").count() == 0)
    run.check(f"{label}: machine cards render", page.locator(".machine-card").count() > 0)
    assert_header_controls(run, page, label)
    assert_no_horizontal_overflow(run, page, label)

    cost_button = page.locator("button.cost-pill").filter(has_text="2500")
    run.check(f"{label}: 2500 quick filter unique", cost_button.count() == 1)
    if cost_button.count() == 1:
        cost_button.click()
        run.expect_text(f"{label}: 2500 heading after filter", page.locator("h2").inner_text(), "2500 COST")
        run.expect_text(f"{label}: 2500 active state", page.locator("button.cost-pill.active").inner_text(), "2500")
        run.check(f"{label}: filtered cards render", page.locator(".machine-card").count() > 0)

    before_theme = page.locator("html").get_attribute("data-theme")
    page.locator(".theme-toggle").click()
    after_theme = page.locator("html").get_attribute("data-theme")
    run.check(f"{label}: theme toggle changes theme", before_theme != after_theme, f"{before_theme}->{after_theme}")


def test_detail(page: Page, run: TestRun, base_url: str, label: str) -> None:
    page.goto(f"{base_url}/machine/m13501", wait_until="networkidle")

    run.check(f"{label}: detail content visible", page.locator(".content-section").is_visible())
    run.check(f"{label}: wiki content visible", page.locator(".wiki-content").count() > 0)
    run.check(f"{label}: language toggle visible", page.locator(".lang-toggle").is_visible())
    run.check(f"{label}: wiki tables render", page.locator(".wiki-content table").count() >= 20)
    assert_header_controls(run, page, label)

    first_table = page.locator(".wiki-content table").nth(0)
    run.check(f"{label}: first table scroll contained", table_scroll_is_contained(first_table))
    run.check(f"{label}: 弾数 header readable", cell_text_is_readable(first_table, "弾数"))

    # These are the two complex tables called out during visual review.
    table_10 = page.locator(".wiki-content table").nth(9)
    table_20 = page.locator(".wiki-content table").nth(19)
    run.check(f"{label}: table 10 uses contained horizontal scroll", table_scroll_is_contained(table_10))
    run.check(f"{label}: table 10 第1段 readable", cell_text_is_readable(table_10, "第1段"))
    run.check(f"{label}: table 20 uses contained horizontal scroll", table_scroll_is_contained(table_20))
    run.check(f"{label}: table 20 累计 readable", cell_text_is_readable(table_20, "累计"))


def table_scroll_is_contained(locator) -> bool:
    dims = locator.evaluate(
        """(el) => ({
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
          parentWidth: el.closest('.wiki-content')?.clientWidth || el.parentElement.clientWidth
        })"""
    )
    return dims["clientWidth"] <= dims["parentWidth"] + 1


def cell_text_is_readable(locator, target_text: str) -> bool:
    return locator.evaluate(
        """(table, targetText) => {
          const normalize = (value) => (value || '').replace(/\\s+/g, '');
          const target = normalize(targetText);
          const cells = Array.from(table.querySelectorAll('th, td'))
            .filter((cell) => normalize(cell.innerText).includes(target));
          if (!cells.length) return false;
          return cells.some((cell) => {
            const text = (cell.innerText || '').trim().replace(/\\s+/g, '');
            const rect = cell.getBoundingClientRect();
            if (rect.width >= 48) return true;
            return rect.width >= rect.height * 0.65;
          });
        }""",
        target_text,
    )


def run_viewport_tests(
    base_url: str,
    label: str,
    viewport: dict[str, int],
    run: TestRun,
    screenshots: bool,
    screenshot_dir: Path,
) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=viewport)
        errors = page_console_errors(page)

        test_home(page, run, base_url, label)
        if screenshots:
            page.screenshot(path=str(screenshot_dir / f"home-{label}.png"), full_page=True)

        test_detail(page, run, base_url, label)
        if screenshots:
            page.screenshot(path=str(screenshot_dir / f"detail-{label}.png"), full_page=True)

        run.check(f"{label}: no console errors", len(errors) == 0, "; ".join(errors[:3]))
        browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run browser smoke tests for the local EXVSDB site.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Site URL to test. Default: {DEFAULT_BASE_URL}")
    parser.add_argument("--screenshots", action="store_true", help="Save screenshots under test-artifacts/")
    parser.add_argument(
        "--viewport",
        choices=["desktop", "mobile", "all"],
        default="all",
        help="Viewport to test. Default: all",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run = TestRun()
    screenshot_dir = Path("test-artifacts")
    if args.screenshots:
        screenshot_dir.mkdir(exist_ok=True)

    viewports = VIEWPORTS.items() if args.viewport == "all" else [(args.viewport, VIEWPORTS[args.viewport])]

    try:
        for label, viewport in viewports:
            run_viewport_tests(args.base_url.rstrip("/"), label, viewport, run, args.screenshots, screenshot_dir)
    except Exception as error:
        run.check("test runner completed", False, str(error))

    run.print_summary()
    return 1 if run.has_failures() else 0


if __name__ == "__main__":
    sys.exit(main())
