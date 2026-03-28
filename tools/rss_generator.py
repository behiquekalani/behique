#!/usr/bin/env python3
"""
RSS Feed Generator for Behike.co
Reads products.json and generates a valid RSS 2.0 feed.

Usage:
    python rss_generator.py --generate    # Generate feed.xml
    python rss_generator.py --validate    # Validate existing feed.xml
    python rss_generator.py               # Generate by default

Designed to run on cron:
    */30 * * * * cd ~/behique && python tools/rss_generator.py --generate
"""

import json
import argparse
import hashlib
import sys
import os
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring, indent, parse
from xml.dom import minidom
from pathlib import Path

STOREFRONT_DIR = Path(__file__).resolve().parent.parent / "storefront"
PRODUCTS_FILE = STOREFRONT_DIR / "products.json"
FEED_FILE = STOREFRONT_DIR / "feed.xml"
SITE_URL = "https://behike.co"
MAX_ITEMS = 20


def load_products() -> list[dict]:
    """Load products from products.json."""
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)


def product_pub_date(product: dict, index: int) -> datetime:
    """Generate a deterministic pubDate for a product.

    Uses the product id to create a stable date so the feed
    stays consistent between regenerations. Products later
    in the list get newer dates (treated as added later).
    """
    if "pubDate" in product:
        return datetime.fromisoformat(product["pubDate"])
    # Spread products across the last 90 days, newest last in the list
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # Use index to space them out by ~1 day
    offset_hours = index * 24
    from datetime import timedelta
    return base + timedelta(hours=offset_hours)


def format_rfc822(dt: datetime) -> str:
    """Format datetime as RFC 822 for RSS."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return (f"{days[dt.weekday()]}, {dt.day:02d} {months[dt.month - 1]} "
            f"{dt.year} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} +0000")


def build_item_link(product: dict) -> str:
    """Build the product link. Uses gumroad_url if real, otherwise landing page."""
    gumroad = product.get("gumroad_url", "#")
    if gumroad and gumroad != "#":
        return gumroad
    # Fall back to the storefront landing page
    file_name = product.get("file", "")
    if file_name:
        return f"{SITE_URL}/storefront/{file_name}"
    return f"{SITE_URL}/storefront/products.html"


def generate_feed() -> str:
    """Generate RSS 2.0 XML feed string."""
    products = load_products()

    # Assign dates and sort by newest first
    dated_products = []
    for i, p in enumerate(products):
        pub_date = product_pub_date(p, i)
        dated_products.append((pub_date, p))

    dated_products.sort(key=lambda x: x[0], reverse=True)
    dated_products = dated_products[:MAX_ITEMS]

    # Build XML
    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Behike"
    SubElement(channel, "link").text = SITE_URL
    SubElement(channel, "description").text = "Systems for builders"
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "lastBuildDate").text = format_rfc822(
        datetime.now(timezone.utc)
    )
    SubElement(channel, "generator").text = "Behike RSS Generator"

    # Atom self-link for feed validators
    atom_link = SubElement(channel, "atom:link")
    atom_link.set("href", f"{SITE_URL}/storefront/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for pub_date, product in dated_products:
        item = SubElement(channel, "item")

        title = product.get("title", "Untitled")
        description = product.get("description", "")
        price = product.get("price", 0)
        category = product.get("category", "general")
        link = build_item_link(product)
        product_id = product.get("id", title.lower().replace(" ", "-"))

        # Build rich description with price
        price_str = "Free" if price == 0 else f"${price}"
        full_description = f"{description} | Price: {price_str}"

        SubElement(item, "title").text = title
        SubElement(item, "link").text = link
        SubElement(item, "description").text = full_description
        SubElement(item, "category").text = category
        SubElement(item, "pubDate").text = format_rfc822(pub_date)

        # GUID based on product id for stability
        guid = SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = f"behike-{product_id}"

    # Pretty print
    indent(rss, space="  ")
    xml_str = tostring(rss, encoding="unicode", xml_declaration=False)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}\n'


def write_feed():
    """Generate and write feed.xml."""
    xml = generate_feed()
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Feed generated: {FEED_FILE}")
    print(f"Items: {min(MAX_ITEMS, len(load_products()))}")


def validate_feed():
    """Validate the existing feed.xml for well-formed XML and RSS 2.0 structure."""
    if not FEED_FILE.exists():
        print(f"ERROR: {FEED_FILE} does not exist. Run --generate first.")
        sys.exit(1)

    errors = []

    # Check well-formed XML
    try:
        tree = parse(str(FEED_FILE))
        root = tree.getroot()
    except Exception as e:
        print(f"INVALID XML: {e}")
        sys.exit(1)

    # Check RSS 2.0 structure
    if root.tag != "rss":
        errors.append(f"Root element is '{root.tag}', expected 'rss'")

    version = root.get("version", "")
    if version != "2.0":
        errors.append(f"RSS version is '{version}', expected '2.0'")

    channel = root.find("channel")
    if channel is None:
        errors.append("Missing <channel> element")
    else:
        for required in ["title", "link", "description"]:
            el = channel.find(required)
            if el is None or not el.text:
                errors.append(f"Missing or empty <{required}> in channel")

        items = channel.findall("item")
        if not items:
            errors.append("No <item> elements found")
        else:
            for i, item in enumerate(items):
                for required in ["title", "link", "description", "pubDate"]:
                    el = item.find(required)
                    if el is None or not el.text:
                        errors.append(
                            f"Item {i + 1}: missing or empty <{required}>"
                        )

    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        items_count = len(channel.findall("item")) if channel is not None else 0
        print(f"VALID RSS 2.0 feed: {FEED_FILE}")
        print(f"Items: {items_count}")


def main():
    parser = argparse.ArgumentParser(description="Behike RSS Feed Generator")
    parser.add_argument(
        "--generate", action="store_true",
        help="Generate feed.xml from products.json"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate existing feed.xml"
    )
    args = parser.parse_args()

    if args.validate:
        validate_feed()
    elif args.generate:
        write_feed()
    else:
        # Default: generate
        write_feed()


if __name__ == "__main__":
    main()
