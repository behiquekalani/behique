#!/usr/bin/env python3
"""
Gumroad Sales Sync
Pulls sales data from Gumroad API and syncs to analytics/data/sales.json.

Usage:
    python3 gumroad_sync.py --sync
    python3 gumroad_sync.py --sync --after 2026-03-01

Requires:
    GUMROAD_ACCESS_TOKEN environment variable

To get your token:
    1. Go to https://app.gumroad.com/settings/advanced#application-form
    2. Create an application (any name)
    3. Go to https://api.gumroad.com/oauth/authorize?client_id=YOUR_APP_ID&redirect_uri=YOUR_REDIRECT&scope=view_sales
    4. Or use the personal access token from Settings > Advanced > Access Token
    5. Set: export GUMROAD_ACCESS_TOKEN="your_token_here"
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import urllib.request
    import urllib.parse
    import urllib.error
except ImportError:
    pass

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SALES_FILE = DATA_DIR / "sales.json"

GUMROAD_API = "https://api.gumroad.com/v2"


def _load_sales():
    if not SALES_FILE.exists():
        return []
    with open(SALES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_sales(sales):
    with open(SALES_FILE, "w") as f:
        json.dump(sales, f, indent=2)


def _gumroad_request(endpoint, params=None):
    """Make a GET request to the Gumroad API."""
    token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    if not token:
        return None

    url = f"{GUMROAD_API}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None


def fetch_gumroad_sales(after_date=None):
    """Fetch sales from Gumroad API."""
    token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    if not token:
        print("\n" + "=" * 50)
        print("  GUMROAD_ACCESS_TOKEN not set")
        print("=" * 50)
        print()
        print("To get your Gumroad API token:")
        print()
        print("  1. Log in to Gumroad")
        print("  2. Go to Settings > Advanced")
        print("  3. Scroll to 'Access Token' section")
        print("  4. Generate or copy your token")
        print("  5. Run:")
        print()
        print("     export GUMROAD_ACCESS_TOKEN='your_token_here'")
        print("     python3 gumroad_sync.py --sync")
        print()
        return []

    all_sales = []
    page = 1
    params = {}
    if after_date:
        params["after"] = after_date

    while True:
        params["page"] = page
        data = _gumroad_request("sales", params)
        if not data or not data.get("success"):
            if data:
                print(f"API returned error: {data.get('message', 'unknown')}")
            break

        sales = data.get("sales", [])
        if not sales:
            break

        all_sales.extend(sales)
        print(f"  Fetched page {page}: {len(sales)} sales")

        if not data.get("next_page_url"):
            break
        page += 1

    return all_sales


def convert_gumroad_sale(gs):
    """Convert a Gumroad sale record to our format."""
    # Parse Gumroad timestamp
    ts = gs.get("created_at", "")
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")
        ts_str = dt.isoformat()
    except (ValueError, AttributeError):
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts_str = datetime.now().isoformat()

    # Price is in cents from Gumroad
    price_cents = gs.get("price", 0)
    price = price_cents / 100.0 if isinstance(price_cents, int) and price_cents > 100 else float(price_cents)

    return {
        "id": gs.get("id", ""),
        "product": gs.get("product_name", "Unknown"),
        "price": price,
        "platform": "gumroad",
        "customer_email": gs.get("email"),
        "timestamp": ts_str,
        "date": date_str,
        "gumroad_id": gs.get("id"),
    }


def sync_sales(after_date=None):
    """Pull from Gumroad and merge into local sales.json."""
    print("Syncing sales from Gumroad...")

    gumroad_sales = fetch_gumroad_sales(after_date)
    if not gumroad_sales:
        print("No new sales found (or API not configured).")
        return

    existing = _load_sales()
    existing_ids = set()
    for s in existing:
        if s.get("gumroad_id"):
            existing_ids.add(s["gumroad_id"])
        existing_ids.add(s.get("id", ""))

    new_count = 0
    for gs in gumroad_sales:
        gid = gs.get("id", "")
        if gid in existing_ids:
            continue
        converted = convert_gumroad_sale(gs)
        existing.append(converted)
        existing_ids.add(gid)
        new_count += 1

    _save_sales(existing)
    print(f"\nSync complete: {new_count} new sales added, {len(existing)} total.")


def main():
    if len(sys.argv) < 2 or "--sync" not in sys.argv:
        print(__doc__)
        return

    after_date = None
    if "--after" in sys.argv:
        idx = sys.argv.index("--after")
        if idx + 1 < len(sys.argv):
            after_date = sys.argv[idx + 1]

    sync_sales(after_date)


if __name__ == "__main__":
    main()
