"""
Web Scraper Skill — Cobo executor module for URL scraping.

Supports two modes:
  1. Simple HTTP (requests) — fast, no JS rendering
  2. Browser (Playwright) — full JS rendering, slower

Falls back gracefully: Playwright → requests → error

Usage via Kernel:
    dispatcher.add_task(
        skill="skills.web_scraper",
        params={"url": "https://ebay.com/trending", "mode": "simple"},
        priority=TaskPriority.MEDIUM,
    )
"""

import json
from datetime import datetime, timezone
from urllib.parse import urlparse


def _scrape_simple(url: str, max_chars: int = 10000) -> dict:
    """Simple HTTP scrape using requests + BeautifulSoup."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return {"error": "Missing dependencies: pip install requests beautifulsoup4"}

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script/style tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)[:max_chars]

        # Extract links
        links = []
        for a in soup.find_all("a", href=True)[:50]:
            links.append({"text": a.get_text(strip=True)[:80], "href": a["href"]})

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        return {
            "url": url,
            "status_code": resp.status_code,
            "title": title,
            "text_length": len(text),
            "text": text,
            "links_count": len(links),
            "links": links[:20],
            "mode": "simple",
        }
    except requests.RequestException as e:
        return {"error": f"HTTP error: {str(e)}", "url": url}


def _scrape_browser(url: str, max_chars: int = 10000) -> dict:
    """Browser scrape using Playwright (JS rendering)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"error": "Playwright not installed. Run: pip install playwright && playwright install chromium"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle", timeout=10000)

            title = page.title()
            text = page.inner_text("body")[:max_chars]

            # Extract structured data
            links = page.eval_on_selector_all(
                "a[href]",
                """els => els.slice(0, 50).map(a => ({
                    text: a.innerText.trim().substring(0, 80),
                    href: a.href
                }))"""
            )

            browser.close()

            return {
                "url": url,
                "title": title,
                "text_length": len(text),
                "text": text,
                "links_count": len(links),
                "links": links[:20],
                "mode": "browser",
            }
    except Exception as e:
        return {"error": f"Playwright error: {str(e)}", "url": url}


# ============ Skill Entry Point ============
def run(url: str = "", mode: str = "simple", max_chars: str = "10000", **kwargs) -> dict:
    """
    Scrape a URL and return structured content.

    Args:
        url: The URL to scrape
        mode: "simple" (requests) or "browser" (Playwright)
        max_chars: Max characters of text to return
    """
    if not url:
        return {"error": "url parameter is required"}

    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {"error": f"Invalid URL: {url}"}

    max_c = int(max_chars) if max_chars else 10000

    if mode == "browser":
        result = _scrape_browser(url, max_c)
        # Fallback to simple if browser fails
        if "error" in result and "not installed" in result["error"]:
            result = _scrape_simple(url, max_c)
            result["fallback"] = True
    else:
        result = _scrape_simple(url, max_c)

    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return result


# ============ CLI ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web Scraper Skill")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--mode", default="simple", choices=["simple", "browser"])
    parser.add_argument("--max-chars", type=int, default=10000)
    args = parser.parse_args()

    result = run(url=args.url, mode=args.mode, max_chars=str(args.max_chars))
    print(json.dumps(result, indent=2))
