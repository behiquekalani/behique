#!/usr/bin/env python3
"""
Daily sales digest - sends a Telegram summary of today's sales.

Run via cron at 9 PM daily:
    0 21 * * * cd /Users/kalani/behique/bios/sales && python3 daily_digest.py

Or run manually:
    python3 daily_digest.py
    python3 daily_digest.py --dry-run
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Import analytics tracker
ANALYTICS_DIR = Path(__file__).parent.parent / "analytics"
sys.path.insert(0, str(ANALYTICS_DIR))

try:
    from tracker import _load_json, SALES_FILE
except ImportError:
    SALES_FILE = ANALYTICS_DIR / "data" / "sales.json"

    def _load_json(path):
        if not path.exists():
            return []
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

# Import notifier
sys.path.insert(0, str(Path(__file__).parent))
from notifier import send_daily_summary, send_custom


def build_digest() -> dict:
    """Build today's sales digest data."""
    sales = _load_json(SALES_FILE)
    today = datetime.now().strftime("%Y-%m-%d")

    today_sales = [s for s in sales if s.get("date") == today]
    total_revenue_all_time = sum(s.get("price", 0) for s in sales)
    today_revenue = sum(s.get("price", 0) for s in today_sales)

    # Find top product today
    product_rev = defaultdict(float)
    for s in today_sales:
        product_rev[s.get("product", "Unknown")] += s.get("price", 0)

    top_product = "N/A"
    if product_rev:
        top_product = max(product_rev, key=product_rev.get)

    return {
        "date": today,
        "total_sales": len(today_sales),
        "total_revenue": today_revenue,
        "top_product": top_product,
        "all_time_revenue": total_revenue_all_time,
        "all_time_sales": len(sales),
    }


def run_digest(dry_run: bool = False):
    """Build and send the daily digest."""
    digest = build_digest()

    print(f"Date: {digest['date']}")
    print(f"Today: {digest['total_sales']} sales, ${digest['total_revenue']:.2f}")
    print(f"Top: {digest['top_product']}")
    print(f"All-time: {digest['all_time_sales']} sales, ${digest['all_time_revenue']:.2f}")

    if dry_run:
        print("\n[dry-run] Skipping Telegram send.")
        return digest

    send_daily_summary(
        total_sales=digest["total_sales"],
        total_revenue=digest["total_revenue"],
        top_product=digest["top_product"],
        all_time_revenue=digest["all_time_revenue"],
    )

    return digest


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run_digest(dry_run=dry)
