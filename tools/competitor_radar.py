#!/usr/bin/env python3
"""
Competitor Radar -- Behike Competitive Intelligence Tool
Monitors Gumroad sellers, tracks pricing changes, new products, and content velocity.

Usage:
    python competitor_radar.py --setup          # First-time setup
    python competitor_radar.py                  # Run a check
    python competitor_radar.py --report         # Generate markdown report
    python competitor_radar.py --dry-run        # Preview without making requests
"""

import argparse
import json
import logging
import os
import random
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path.home() / ".competitor_radar"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
CONFIG_FILE = BASE_DIR / "config.json"
OUR_PRODUCTS_FILE = BASE_DIR / "our_products.json"
ALERTS_LOG = BASE_DIR / "alerts.log"

DEFAULT_CONFIG = {
    "competitors": [
        {
            "name": "Competitor A",
            "gumroad": "competitor-a",
            "twitter": "@competitora"
        },
        {
            "name": "Competitor B",
            "gumroad": "competitor-b",
            "twitter": "@competitorb"
        }
    ],
    "check_interval_hours": 24,
    "alert_on_price_change": True,
    "alert_on_new_product": True
}

DEFAULT_OUR_PRODUCTS = {
    "brand": "Behike",
    "gumroad": "behike",
    "products": [
        {"name": "Solopreneur OS", "price": 12.99},
        {"name": "AI Employee Guide", "price": 19.99},
        {"name": "Behike Method v2", "price": 19.99},
        {"name": "AI Security Guide", "price": 14.99},
        {"name": "Niche Sniper", "price": 14.99}
    ]
}

# User-Agent pool -- rotated per request
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("competitor_radar")


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def cmd_setup():
    """Create directory structure and write template config files."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        log.info("Config already exists at %s -- skipping", CONFIG_FILE)
    else:
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        log.info("Created config: %s", CONFIG_FILE)

    if OUR_PRODUCTS_FILE.exists():
        log.info("our_products.json already exists at %s -- skipping", OUR_PRODUCTS_FILE)
    else:
        OUR_PRODUCTS_FILE.write_text(json.dumps(DEFAULT_OUR_PRODUCTS, indent=2))
        log.info("Created our_products template: %s", OUR_PRODUCTS_FILE)

    ALERTS_LOG.touch(exist_ok=True)
    log.info("Alerts log: %s", ALERTS_LOG)
    print("\nSetup complete. Edit the config files before running your first check:")
    print(f"  {CONFIG_FILE}")
    print(f"  {OUR_PRODUCTS_FILE}")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _random_ua() -> str:
    return random.choice(USER_AGENTS)


def _polite_sleep():
    """Sleep 2-5 seconds between requests to avoid rate limiting."""
    delay = random.uniform(2.0, 5.0)
    log.debug("Sleeping %.1fs", delay)
    time.sleep(delay)


def fetch_page(url: str, dry_run: bool = False) -> str | None:
    """Fetch a URL and return the response text. Returns None on failure."""
    if dry_run:
        log.info("[dry-run] Would fetch: %s", url)
        return None

    headers = {
        "User-Agent": _random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 404:
            log.warning("404 for %s -- seller may not exist or URL changed", url)
            return None
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.ConnectionError:
        log.error("Connection error fetching %s", url)
        return None
    except requests.exceptions.Timeout:
        log.error("Timeout fetching %s", url)
        return None
    except requests.exceptions.HTTPError as exc:
        log.error("HTTP error fetching %s: %s", url, exc)
        return None
    except Exception as exc:
        log.error("Unexpected error fetching %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Gumroad scraping
# ---------------------------------------------------------------------------

def scrape_gumroad_profile(username: str, dry_run: bool = False) -> list[dict]:
    """
    Scrape a Gumroad seller profile page and return a list of product dicts.

    Each dict has keys: name, url, price, currency, is_pay_what_you_want, bestseller.
    Returns empty list if the page cannot be fetched or parsed.
    """
    url = f"https://app.gumroad.com/{username}"
    log.info("Scraping Gumroad profile: %s", url)

    html = fetch_page(url, dry_run=dry_run)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    products = []

    # Gumroad product cards -- structure may change; update selectors if needed.
    # Primary approach: look for product list items with data attributes or known classes.
    product_items = (
        soup.find_all("li", class_=lambda c: c and "product" in c.lower())
        or soup.find_all("div", attrs={"data-type": "product"})
        or soup.select(".js-product")
        or soup.select("[class*='ProductCard']")
        or soup.select("[class*='product-card']")
    )

    if not product_items:
        # Fallback: scan all anchor tags that link to gumroad.com/l/
        product_items = [
            a for a in soup.find_all("a", href=True)
            if "/l/" in a.get("href", "")
        ]

    seen_urls = set()
    for item in product_items:
        try:
            # Extract link
            link_tag = item if item.name == "a" else item.find("a", href=True)
            if not link_tag:
                continue
            href = link_tag.get("href", "")
            if not href or "/l/" not in href:
                continue
            full_url = href if href.startswith("http") else f"https://gumroad.com{href}"
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            # Extract name
            name_tag = (
                item.find(["h2", "h3", "h4", "strong"])
                or item.find(class_=lambda c: c and "name" in c.lower())
                or item.find(class_=lambda c: c and "title" in c.lower())
                or link_tag
            )
            name = name_tag.get_text(strip=True) if name_tag else "Unknown"

            # Extract price
            price_tag = item.find(
                lambda tag: tag.name in ["span", "div", "p"]
                and tag.get_text(strip=True).startswith("$")
            )
            raw_price = price_tag.get_text(strip=True) if price_tag else ""
            price = _parse_price(raw_price)
            is_pwyw = "+" in raw_price or "pay what you want" in raw_price.lower()

            # Bestseller badge
            bestseller_tag = item.find(
                lambda tag: "bestseller" in tag.get_text(strip=True).lower()
                or (tag.get("class") and any("bestseller" in c.lower() for c in tag["class"]))
            )
            is_bestseller = bestseller_tag is not None

            products.append({
                "name": name[:120],
                "url": full_url,
                "price": price,
                "currency": "USD",
                "is_pay_what_you_want": is_pwyw,
                "bestseller": is_bestseller,
            })
        except Exception as exc:
            log.debug("Failed to parse product item: %s", exc)
            continue

    log.info("Found %d products for @%s", len(products), username)
    return products


def _parse_price(raw: str) -> float | None:
    """Convert '$14.99' or '14.99' to float. Returns None if unparseable."""
    if not raw:
        return None
    cleaned = raw.replace("$", "").replace(",", "").strip()
    # Handle "14.99+" or "14.99 USD"
    cleaned = cleaned.split()[0].rstrip("+")
    try:
        return float(cleaned)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Snapshot persistence
# ---------------------------------------------------------------------------

def today_snapshot_dir() -> Path:
    return SNAPSHOTS_DIR / date.today().isoformat()


def yesterday_snapshot_dir() -> Path:
    return SNAPSHOTS_DIR / (date.today() - timedelta(days=1)).isoformat()


def save_snapshot(username: str, products: list[dict]):
    """Save today's product list for a competitor."""
    snap_dir = today_snapshot_dir()
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap_file = snap_dir / f"{username}.json"
    data = {
        "username": username,
        "scraped_at": datetime.now().isoformat(),
        "product_count": len(products),
        "products": products,
    }
    snap_file.write_text(json.dumps(data, indent=2))
    log.info("Snapshot saved: %s", snap_file)


def load_snapshot(username: str, snapshot_dir: Path) -> dict | None:
    """Load a snapshot from a given day directory. Returns None if missing."""
    snap_file = snapshot_dir / f"{username}.json"
    if not snap_file.exists():
        return None
    try:
        return json.loads(snap_file.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Could not load snapshot %s: %s", snap_file, exc)
        return None


# ---------------------------------------------------------------------------
# Change detection
# ---------------------------------------------------------------------------

def detect_changes(username: str, today_products: list[dict], yesterday_snap: dict | None) -> list[str]:
    """
    Compare today's product list against yesterday's snapshot.
    Returns a list of human-readable change strings.
    """
    changes = []
    if yesterday_snap is None:
        return []

    yesterday_products = yesterday_snap.get("products", [])
    yesterday_by_url = {p["url"]: p for p in yesterday_products}
    today_by_url = {p["url"]: p for p in today_products}

    # New products
    new_urls = set(today_by_url) - set(yesterday_by_url)
    for url in new_urls:
        p = today_by_url[url]
        price_str = f"${p['price']:.2f}" if p["price"] is not None else "unknown price"
        changes.append(f"NEW PRODUCT: {p['name']} ({price_str}) -- {url}")

    # Removed products
    removed_urls = set(yesterday_by_url) - set(today_by_url)
    for url in removed_urls:
        p = yesterday_by_url[url]
        changes.append(f"REMOVED PRODUCT: {p['name']} -- {url}")

    # Price changes
    for url in set(today_by_url) & set(yesterday_by_url):
        old_price = yesterday_by_url[url].get("price")
        new_price = today_by_url[url].get("price")
        if old_price is not None and new_price is not None and old_price != new_price:
            name = today_by_url[url]["name"]
            direction = "UP" if new_price > old_price else "DOWN"
            changes.append(
                f"PRICE {direction}: {name} ${old_price:.2f} -> ${new_price:.2f} -- {url}"
            )

    return changes


def write_alert(competitor_name: str, changes: list[str]):
    """Append changes to the alerts log."""
    if not changes:
        return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"[{ts}] {competitor_name}"]
    for change in changes:
        lines.append(f"  {change}")
    lines.append("")
    with ALERTS_LOG.open("a") as f:
        f.write("\n".join(lines) + "\n")
    log.info("Wrote %d alert(s) for %s to %s", len(changes), competitor_name, ALERTS_LOG)


# ---------------------------------------------------------------------------
# Main check loop
# ---------------------------------------------------------------------------

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        log.error("Config not found. Run: python competitor_radar.py --setup")
        raise SystemExit(1)
    return json.loads(CONFIG_FILE.read_text())


def cmd_check(dry_run: bool = False):
    """Run a full check cycle: scrape, compare, alert."""
    config = load_config()
    competitors = config.get("competitors", [])

    if not competitors:
        log.warning("No competitors configured in %s", CONFIG_FILE)
        return

    log.info("Starting check for %d competitor(s)", len(competitors))

    for idx, comp in enumerate(competitors):
        name = comp.get("name", comp.get("gumroad", "unknown"))
        username = comp.get("gumroad", "").strip()

        if not username:
            log.warning("Competitor '%s' has no gumroad username -- skipping", name)
            continue

        log.info("[%d/%d] Checking %s (@%s)", idx + 1, len(competitors), name, username)

        # Load yesterday for comparison
        yesterday_snap = load_snapshot(username, yesterday_snapshot_dir())

        # Scrape today
        products = scrape_gumroad_profile(username, dry_run=dry_run)

        if not dry_run:
            save_snapshot(username, products)

            # Detect changes
            if config.get("alert_on_new_product") or config.get("alert_on_price_change"):
                changes = detect_changes(username, products, yesterday_snap)
                if changes:
                    write_alert(name, changes)
                    for c in changes:
                        log.warning("CHANGE: %s", c)
                else:
                    log.info("No changes detected for %s", name)

        # Polite delay between competitors
        if idx < len(competitors) - 1:
            _polite_sleep()

    log.info("Check complete.")


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _load_week_snapshots(username: str) -> list[dict]:
    """Load all snapshots from the past 7 days for a competitor."""
    snaps = []
    for days_back in range(7):
        day = date.today() - timedelta(days=days_back)
        snap_dir = SNAPSHOTS_DIR / day.isoformat()
        snap = load_snapshot(username, snap_dir)
        if snap:
            snaps.append(snap)
    return snaps


def cmd_report():
    """Generate a markdown competitive landscape report."""
    config = load_config()
    competitors = config.get("competitors", [])

    our_products = []
    our_brand = "Behike"
    our_price_range = (None, None)

    if OUR_PRODUCTS_FILE.exists():
        our_data = json.loads(OUR_PRODUCTS_FILE.read_text())
        our_brand = our_data.get("brand", "Behike")
        our_products = our_data.get("products", [])
        prices = [p["price"] for p in our_products if p.get("price")]
        if prices:
            our_price_range = (min(prices), max(prices))

    lines = [
        f"# Competitor Radar Report",
        f"",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"---",
        f"",
        f"## Your Position ({our_brand})",
        f"",
        f"- Products: {len(our_products)}",
    ]

    if our_price_range[0] is not None:
        lines.append(f"- Price range: ${our_price_range[0]:.2f} -- ${our_price_range[1]:.2f}")

    if our_products:
        lines.append(f"- Products listed:")
        for p in our_products:
            price_str = f"${p['price']:.2f}" if p.get("price") else "unknown"
            lines.append(f"  - {p['name']} ({price_str})")

    lines += ["", "---", "", "## Competitor Landscape", ""]

    for comp in competitors:
        name = comp.get("name", comp.get("gumroad", "unknown"))
        username = comp.get("gumroad", "").strip()
        twitter = comp.get("twitter", "")

        lines.append(f"### {name}")
        lines.append(f"")
        lines.append(f"- Gumroad: [{username}](https://app.gumroad.com/{username})")
        if twitter:
            lines.append(f"- Twitter: {twitter}")

        # Load today's snapshot
        today_snap = load_snapshot(username, today_snapshot_dir())
        if today_snap is None:
            lines.append(f"- Status: no snapshot found for today. Run a check first.")
            lines.append("")
            continue

        products = today_snap.get("products", [])
        prices = [p["price"] for p in products if p.get("price") is not None]

        lines.append(f"- Product count: {len(products)}")
        if prices:
            lines.append(f"- Price range: ${min(prices):.2f} -- ${max(prices):.2f}")

        bestsellers = [p for p in products if p.get("bestseller")]
        if bestsellers:
            lines.append(f"- Bestsellers ({len(bestsellers)}):")
            for p in bestsellers[:3]:
                price_str = f"${p['price']:.2f}" if p.get("price") is not None else "unknown"
                lines.append(f"  - {p['name']} ({price_str})")

        # Week changes
        week_snaps = _load_week_snapshots(username)
        new_this_week = []
        price_changes_this_week = []

        if len(week_snaps) >= 2:
            for i in range(len(week_snaps) - 1):
                newer = week_snaps[i]
                older = week_snaps[i + 1]
                changes = detect_changes(
                    username,
                    newer.get("products", []),
                    older,
                )
                for c in changes:
                    if c.startswith("NEW PRODUCT"):
                        new_this_week.append(c)
                    elif c.startswith("PRICE"):
                        price_changes_this_week.append(c)

        if new_this_week:
            lines.append(f"- New products this week:")
            for c in new_this_week[:5]:
                lines.append(f"  - {c.replace('NEW PRODUCT: ', '')}")
        else:
            lines.append(f"- New products this week: none detected")

        if price_changes_this_week:
            lines.append(f"- Price changes this week:")
            for c in price_changes_this_week[:5]:
                lines.append(f"  - {c.replace('PRICE UP: ', '').replace('PRICE DOWN: ', '')}")
        else:
            lines.append(f"- Price changes this week: none detected")

        lines.append("")

    # Alerts summary
    lines += ["---", "", "## Recent Alerts", ""]
    if ALERTS_LOG.exists():
        alert_text = ALERTS_LOG.read_text().strip()
        if alert_text:
            # Show last 20 lines of the alerts log
            alert_lines = alert_text.splitlines()[-20:]
            lines.append("```")
            lines.extend(alert_lines)
            lines.append("```")
        else:
            lines.append("No alerts logged yet.")
    else:
        lines.append("No alerts log found.")

    report = "\n".join(lines)
    report_file = BASE_DIR / f"report-{date.today().isoformat()}.md"
    report_file.write_text(report)
    print(report)
    print(f"\nReport saved to: {report_file}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Competitor Radar -- Behike Competitive Intelligence Tool"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Create ~/.competitor_radar/ directory structure and config templates",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a markdown summary of the competitive landscape",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be checked without making any HTTP requests",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.setup:
        cmd_setup()
    elif args.report:
        cmd_report()
    else:
        cmd_check(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
