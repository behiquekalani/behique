#!/usr/bin/env python3
"""
Automated Review Request System

Checks for customers who purchased 7+ days ago and haven't left a review.
Sends review request via Telegram notification (email placeholder ready).

Usage:
    python3 review_request.py --check     # Show customers due for review requests
    python3 review_request.py --send      # Send review requests

Data sources:
    bios/analytics/data/sales.json   - purchase records
    bios/sales/data/reviews.json     - existing reviews

Env vars:
    TELEGRAM_BOT_TOKEN  - Bot token from @BotFather
    TELEGRAM_CHAT_ID    - Your chat/group ID
    REVIEW_FORM_URL     - URL to review form (default: http://localhost:8103/review_form.html)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
REVIEWS_FILE = SALES_DIR / "data" / "reviews.json"
SALES_FILE = SALES_DIR.parent / "analytics" / "data" / "sales.json"

REVIEW_FORM_URL = os.environ.get("REVIEW_FORM_URL", "http://localhost:8103/review_form.html")
REVIEW_DELAY_DAYS = 7

# Import notifier
sys.path.insert(0, str(SALES_DIR))
try:
    from notifier import send_custom
except ImportError:
    def send_custom(msg: str) -> bool:
        print(f"[review_request] No notifier. Message:\n{msg}")
        return False


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _parse_date(date_str: str) -> datetime | None:
    """Try common date formats."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str[:len(fmt.replace('%', 'X'))], fmt)
        except (ValueError, IndexError):
            continue
    # Fallback: try ISO parse
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00").replace("+00:00", ""))
    except Exception:
        return None


def find_due_customers() -> list[dict]:
    """
    Find customers who:
    1. Purchased 7+ days ago
    2. Have not already submitted a review for that product
    3. Have not already been sent a review request (tracked by flag)
    """
    sales = _load_json(SALES_FILE)
    reviews = _load_json(REVIEWS_FILE)

    if not sales:
        return []

    cutoff = datetime.utcnow() - timedelta(days=REVIEW_DELAY_DAYS)

    # Build set of (email, product) pairs that already have reviews
    reviewed = set()
    for r in reviews:
        email = r.get("email", "")
        product = r.get("product", "")
        if email and product:
            reviewed.add((email.lower(), product.lower()))

    due = []
    for sale in sales:
        email = sale.get("customer_email", sale.get("email", ""))
        product = sale.get("product", sale.get("product_name", ""))
        date_str = sale.get("date", sale.get("created_at", sale.get("timestamp", "")))

        if not email or not product or not date_str:
            continue

        purchase_date = _parse_date(date_str)
        if purchase_date is None:
            continue

        # Not old enough yet
        if purchase_date > cutoff:
            continue

        # Already reviewed
        if (email.lower(), product.lower()) in reviewed:
            continue

        # Already sent request (check flag in sale record)
        if sale.get("review_requested"):
            continue

        due.append({
            "email": email,
            "product": product,
            "purchase_date": purchase_date.isoformat(),
            "days_ago": (datetime.utcnow() - purchase_date).days,
        })

    return due


def send_review_requests(due_customers: list[dict]) -> int:
    """
    Send review request notifications.
    Currently sends via Telegram (admin notification).
    Email sending is a placeholder for when SMTP is configured.
    """
    if not due_customers:
        print("No customers due for review requests.")
        return 0

    sent = 0
    sales = _load_json(SALES_FILE)

    for customer in due_customers:
        # Send Telegram notification to admin
        msg = (
            f"<b>REVIEW REQUEST DUE</b>\n"
            f"Customer: {customer['email']}\n"
            f"Product: {customer['product']}\n"
            f"Purchased: {customer['days_ago']} days ago\n"
            f"Form: {REVIEW_FORM_URL}"
        )
        send_custom(msg)

        # Mark as requested in sales.json so we don't re-send
        for sale in sales:
            sale_email = sale.get("customer_email", sale.get("email", ""))
            sale_product = sale.get("product", sale.get("product_name", ""))
            if (sale_email.lower() == customer["email"].lower()
                    and sale_product.lower() == customer["product"].lower()):
                sale["review_requested"] = True
                sale["review_requested_at"] = datetime.utcnow().isoformat()

        sent += 1
        print(f"  Sent request: {customer['email']} -> {customer['product']}")

    # Save updated sales with review_requested flags
    if sent > 0:
        SALES_FILE.write_text(
            json.dumps(sales, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return sent


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Automated review request system"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Show customers due for review requests",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send review requests to due customers",
    )
    args = parser.parse_args()

    if not args.check and not args.send:
        parser.print_help()
        return

    due = find_due_customers()

    if args.check:
        if not due:
            print("No customers due for review requests.")
            print(f"  Sales file: {SALES_FILE} ({'exists' if SALES_FILE.exists() else 'MISSING'})")
            print(f"  Reviews file: {REVIEWS_FILE} ({'exists' if REVIEWS_FILE.exists() else 'MISSING'})")
            return

        print(f"Customers due for review request ({len(due)}):\n")
        for c in due:
            print(f"  {c['email']}")
            print(f"    Product: {c['product']}")
            print(f"    Purchased: {c['days_ago']} days ago ({c['purchase_date'][:10]})")
            print()

    if args.send:
        count = send_review_requests(due)
        print(f"\nDone. Sent {count} review request(s).")


if __name__ == "__main__":
    main()
