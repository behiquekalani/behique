#!/usr/bin/env python3
"""
BIOS Revenue & Analytics Tracker
Tracks sales, views, and generates reports across all platforms.

Usage:
    python3 tracker.py sale "Behike OS" 97 gumroad
    python3 tracker.py sale "Behike OS" 97 gumroad --email customer@example.com
    python3 tracker.py view "Behike OS" gumroad
    python3 tracker.py report daily
    python3 tracker.py report weekly
    python3 tracker.py report monthly
    python3 tracker.py export csv
"""

import json
import os
import sys
import csv
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SALES_FILE = DATA_DIR / "sales.json"
VIEWS_FILE = DATA_DIR / "views.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path):
    if not path.exists():
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Core logging functions
# ---------------------------------------------------------------------------

def log_sale(product, price, platform, customer_email=None):
    """Append a sale record to sales.json."""
    sales = _load_json(SALES_FILE)
    record = {
        "id": str(uuid.uuid4())[:8],
        "product": product,
        "price": float(price),
        "platform": platform.lower(),
        "customer_email": customer_email,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    sales.append(record)
    _save_json(SALES_FILE, sales)
    print(f"Logged sale: {product} - ${price} on {platform}")
    return record


def log_view(product, platform):
    """Append a view record to views.json."""
    views = _load_json(VIEWS_FILE)
    record = {
        "product": product,
        "platform": platform.lower(),
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    views.append(record)
    _save_json(VIEWS_FILE, views)
    print(f"Logged view: {product} on {platform}")
    return record


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------

def _sales_in_range(sales, start_date):
    """Filter sales from start_date to now."""
    return [s for s in sales if s.get("date", "") >= start_date.strftime("%Y-%m-%d")]


def _views_in_range(views, start_date):
    return [v for v in views if v.get("date", "") >= start_date.strftime("%Y-%m-%d")]


def daily_report():
    """Today's revenue, total revenue, top products, sales by platform."""
    sales = _load_json(SALES_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    today_sales = [s for s in sales if s.get("date") == today]

    today_revenue = sum(s["price"] for s in today_sales)
    total_revenue = sum(s["price"] for s in sales)

    product_rev = defaultdict(float)
    for s in sales:
        product_rev[s["product"]] += s["price"]
    top_products = sorted(product_rev.items(), key=lambda x: x[1], reverse=True)[:5]

    platform_rev = defaultdict(float)
    for s in today_sales:
        platform_rev[s["platform"]] += s["price"]

    report = {
        "period": "daily",
        "date": today,
        "today_revenue": today_revenue,
        "today_sales_count": len(today_sales),
        "total_revenue": total_revenue,
        "total_sales_count": len(sales),
        "top_products": [{"product": p, "revenue": r} for p, r in top_products],
        "platform_breakdown": dict(platform_rev),
    }

    _print_report("DAILY REPORT", report)
    return report


def weekly_report():
    """Week's revenue, growth %, top 5 products, conversion rate."""
    sales = _load_json(SALES_FILE)
    views = _load_json(VIEWS_FILE)

    now = datetime.now()
    week_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)

    this_week = _sales_in_range(sales, week_start)
    prev_week = [s for s in sales
                 if prev_week_start.strftime("%Y-%m-%d") <= s.get("date", "") < week_start.strftime("%Y-%m-%d")]

    week_revenue = sum(s["price"] for s in this_week)
    prev_revenue = sum(s["price"] for s in prev_week)
    growth = ((week_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0

    product_rev = defaultdict(float)
    for s in this_week:
        product_rev[s["product"]] += s["price"]
    top_products = sorted(product_rev.items(), key=lambda x: x[1], reverse=True)[:5]

    week_views = _views_in_range(views, week_start)
    conversion = (len(this_week) / len(week_views) * 100) if week_views else 0

    report = {
        "period": "weekly",
        "start": week_start.strftime("%Y-%m-%d"),
        "end": now.strftime("%Y-%m-%d"),
        "week_revenue": week_revenue,
        "week_sales_count": len(this_week),
        "growth_pct": round(growth, 1),
        "conversion_rate": round(conversion, 2),
        "top_products": [{"product": p, "revenue": r} for p, r in top_products],
    }

    _print_report("WEEKLY REPORT", report)
    return report


def monthly_report():
    """MRR, total customers, avg order value, revenue by category."""
    sales = _load_json(SALES_FILE)

    now = datetime.now()
    month_start = now.replace(day=1)
    this_month = _sales_in_range(sales, month_start)

    month_revenue = sum(s["price"] for s in this_month)
    unique_customers = len(set(s.get("customer_email") for s in this_month if s.get("customer_email")))
    avg_order = (month_revenue / len(this_month)) if this_month else 0

    platform_rev = defaultdict(float)
    for s in this_month:
        platform_rev[s["platform"]] += s["price"]

    # Revenue by product as category proxy
    product_rev = defaultdict(float)
    for s in this_month:
        product_rev[s["product"]] += s["price"]

    report = {
        "period": "monthly",
        "month": now.strftime("%Y-%m"),
        "mrr": month_revenue,
        "month_sales_count": len(this_month),
        "total_customers": unique_customers,
        "avg_order_value": round(avg_order, 2),
        "revenue_by_platform": dict(platform_rev),
        "revenue_by_product": dict(product_rev),
    }

    _print_report("MONTHLY REPORT", report)
    return report


def _print_report(title, report):
    """Pretty-print a report to the terminal."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

    for key, value in report.items():
        if key == "period":
            continue
        if isinstance(value, list):
            print(f"\n  {key}:")
            for item in value:
                if isinstance(item, dict):
                    print(f"    - {item.get('product', '?')}: ${item.get('revenue', 0):.2f}")
                else:
                    print(f"    - {item}")
        elif isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: ${v:.2f}" if isinstance(v, (int, float)) else f"    {k}: {v}")
        elif isinstance(value, float):
            if "pct" in key or "rate" in key:
                print(f"  {key}: {value}%")
            else:
                print(f"  {key}: ${value:.2f}")
        else:
            print(f"  {key}: {value}")

    print(f"{'=' * 50}\n")


def export_csv():
    """Export all sales to analytics/data/sales_export.csv."""
    sales = _load_json(SALES_FILE)
    if not sales:
        print("No sales data to export.")
        return

    output_path = DATA_DIR / "sales_export.csv"
    fieldnames = ["id", "product", "price", "platform", "customer_email", "timestamp", "date"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sale in sales:
            writer.writerow({k: sale.get(k, "") for k in fieldnames})

    print(f"Exported {len(sales)} sales to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "sale":
        if len(sys.argv) < 5:
            print("Usage: python3 tracker.py sale <product> <price> <platform> [--email <email>]")
            return
        product = sys.argv[2]
        price = float(sys.argv[3])
        platform = sys.argv[4]
        email = None
        if "--email" in sys.argv:
            idx = sys.argv.index("--email")
            if idx + 1 < len(sys.argv):
                email = sys.argv[idx + 1]
        log_sale(product, price, platform, email)

    elif cmd == "view":
        if len(sys.argv) < 4:
            print("Usage: python3 tracker.py view <product> <platform>")
            return
        log_view(sys.argv[2], sys.argv[3])

    elif cmd == "report":
        if len(sys.argv) < 3:
            print("Usage: python3 tracker.py report <daily|weekly|monthly>")
            return
        period = sys.argv[2].lower()
        if period == "daily":
            daily_report()
        elif period == "weekly":
            weekly_report()
        elif period == "monthly":
            monthly_report()
        else:
            print(f"Unknown report type: {period}")

    elif cmd == "export":
        fmt = sys.argv[2].lower() if len(sys.argv) > 2 else "csv"
        if fmt == "csv":
            export_csv()
        else:
            print(f"Unknown export format: {fmt}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
