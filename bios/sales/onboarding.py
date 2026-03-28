#!/usr/bin/env python3
"""
Customer Onboarding System -- Post-Purchase Automation

Reads from bios/analytics/data/sales.json, detects new unprocessed sales,
and runs the full onboarding flow: Telegram welcome, email course enrollment,
personalized getting-started instructions, and logging.

Usage:
    python3 onboarding.py --process          # Check for new unprocessed sales
    python3 onboarding.py --stats            # Onboarding stats
    python3 onboarding.py --preview PRODUCT  # Preview onboarding message

Cron (every hour):
    0 * * * * cd /Users/kalani/behique/bios/sales && python3 onboarding.py --process

Env vars:
    TELEGRAM_BOT_TOKEN  - Bot token from @BotFather
    TELEGRAM_CHAT_ID    - Your chat/group ID
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
DATA_DIR = SALES_DIR / "data"
ONBOARDING_LOG = DATA_DIR / "onboarding_log.json"

ANALYTICS_DIR = SALES_DIR.parent / "analytics"
SALES_FILE = ANALYTICS_DIR / "data" / "sales.json"

# Email course lives in bios/publisher/
PUBLISHER_DIR = SALES_DIR.parent / "publisher"
sys.path.insert(0, str(PUBLISHER_DIR))
sys.path.insert(0, str(SALES_DIR))

DATA_DIR.mkdir(parents=True, exist_ok=True)

try:
    from email_course import add_subscriber
except ImportError:
    def add_subscriber(email, name):
        print(f"  [email_course] Not available. Would enroll: {name} <{email}>")
        return False

try:
    from notifier import send_custom
except ImportError:
    def send_custom(message):
        print(f"  [notifier] Not available. Message:\n{message}")
        return False

try:
    from invoice import generate_for_sale
except ImportError:
    def generate_for_sale(sale):
        print(f"  [invoice] Not available. Would generate invoice for sale {sale.get('id')}")
        return None

# ---------------------------------------------------------------------------
# Product onboarding messages
# ---------------------------------------------------------------------------

ONBOARDING_MESSAGES = {
    "behike os": {
        "short_name": "Behike OS",
        "instructions": (
            "Open in GoodNotes or print. Start with Module 01.\n"
            "Work through one module per day. Don't skip ahead."
        ),
    },
    "blueprint": {
        "short_name": "Blueprint",
        "instructions": (
            "Print it. Grab a pen. Fill in the dotted lines.\n"
            "This works best on paper, not on a screen."
        ),
    },
    "bundle": {
        "short_name": "Bundle",
        "instructions": (
            "Start with the Content Creator blueprint first.\n"
            "Once that's done, move to the next one in order."
        ),
    },
    "lumina": {
        "short_name": "Lumina",
        "instructions": (
            "Open index.html in your browser. Set the blue light filter.\n"
            "Works best in a dark room with headphones."
        ),
    },
}

# Fallback for products not in the map
DEFAULT_INSTRUCTIONS = (
    "Check your email for the download link.\n"
    "If anything looks off, reply to the confirmation email."
)

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def _load_json(path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def _save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=str))


def _load_onboarding_log():
    return _load_json(ONBOARDING_LOG)


def _save_onboarding_log(log):
    _save_json(ONBOARDING_LOG, log)


def _get_processed_sale_ids():
    """Return set of sale IDs already onboarded."""
    log = _load_onboarding_log()
    return {entry.get("sale_id") for entry in log if entry.get("sale_id")}


# ---------------------------------------------------------------------------
# Product matching
# ---------------------------------------------------------------------------


def _match_product(product_name):
    """Match a product name to its onboarding config. Case-insensitive partial match."""
    name_lower = product_name.lower().strip()
    for key, config in ONBOARDING_MESSAGES.items():
        if key in name_lower:
            return config
    return None


def _get_instructions(product_name):
    """Get the getting-started instructions for a product."""
    config = _match_product(product_name)
    if config:
        return config["instructions"]
    return DEFAULT_INSTRUCTIONS


def _get_short_name(product_name):
    """Get the display-friendly short name."""
    config = _match_product(product_name)
    if config:
        return config["short_name"]
    return product_name


# ---------------------------------------------------------------------------
# Onboarding actions
# ---------------------------------------------------------------------------


def _send_welcome_telegram(customer_email, product_name, price):
    """Send a welcome notification via Telegram."""
    short = _get_short_name(product_name)
    instructions = _get_instructions(product_name)

    # Extract a display name from email (before the @)
    display_name = customer_email.split("@")[0] if customer_email else "Customer"

    msg = (
        f"<b>NEW CUSTOMER</b>\n\n"
        f"Customer: {display_name}\n"
        f"Email: {customer_email}\n"
        f"Product: {short}\n"
        f"Price: ${price:.2f}\n\n"
        f"<b>Getting Started:</b>\n"
        f"{instructions}"
    )
    return send_custom(msg)


def _enroll_email_course(customer_email, product_name):
    """Add customer to the email course if not already enrolled."""
    display_name = customer_email.split("@")[0] if customer_email else "Customer"
    try:
        result = add_subscriber(customer_email, display_name)
        if result:
            print(f"  [onboarding] Enrolled {customer_email} in email course")
        else:
            print(f"  [onboarding] {customer_email} already enrolled or enrollment skipped")
        return result
    except Exception as e:
        print(f"  [onboarding] Email course enrollment failed: {e}")
        return False


def onboard_sale(sale):
    """Run the full onboarding flow for a single sale."""
    sale_id = sale.get("id", "unknown")
    product = sale.get("product", "Unknown Product")
    price = float(sale.get("price", 0))
    email = sale.get("customer_email", sale.get("email", ""))

    if not email:
        print(f"  [onboarding] Skipping sale {sale_id}: no customer email")
        return None

    short = _get_short_name(product)
    print(f"\n  Onboarding: {email} -- {short} (${price:.2f})")

    # 1. Send welcome Telegram notification
    telegram_ok = _send_welcome_telegram(email, product, price)

    # 2. Add to email course
    course_enrolled = _enroll_email_course(email, product)

    # 3. Generate invoice/receipt
    invoice_path = generate_for_sale(sale)

    # 4. Generate instructions (already included in Telegram message, log them too)
    instructions = _get_instructions(product)

    # 5. Log to onboarding_log.json
    log_entry = {
        "sale_id": sale_id,
        "customer_email": email,
        "product": product,
        "product_short": short,
        "price": price,
        "instructions": instructions,
        "telegram_sent": telegram_ok,
        "email_course_enrolled": course_enrolled,
        "invoice_generated": str(invoice_path) if invoice_path else None,
        "onboarded_at": datetime.now(timezone.utc).isoformat(),
    }

    log = _load_onboarding_log()
    log.append(log_entry)
    _save_onboarding_log(log)

    print(f"  [onboarding] Done. Telegram: {'yes' if telegram_ok else 'no'}, "
          f"Course: {'yes' if course_enrolled else 'no'}")

    return log_entry


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


def cmd_process():
    """Check for new unprocessed sales and onboard them."""
    sales = _load_json(SALES_FILE)
    processed_ids = _get_processed_sale_ids()

    if not sales:
        print("  No sales found in sales.json")
        return

    new_sales = [s for s in sales if s.get("id") not in processed_ids]

    if not new_sales:
        print(f"  All {len(sales)} sales already processed. Nothing to do.")
        return

    print(f"  Found {len(new_sales)} new sale(s) to onboard.\n")

    onboarded = 0
    for sale in new_sales:
        result = onboard_sale(sale)
        if result:
            onboarded += 1

    print(f"\n  Onboarded {onboarded}/{len(new_sales)} new customers.")


def cmd_stats():
    """Show onboarding statistics."""
    log = _load_onboarding_log()
    sales = _load_json(SALES_FILE)

    total_sales = len(sales)
    total_onboarded = len(log)
    pending = total_sales - total_onboarded

    # Count by product
    product_counts = {}
    telegram_sent = 0
    course_enrolled = 0

    for entry in log:
        product = entry.get("product_short", entry.get("product", "Unknown"))
        product_counts[product] = product_counts.get(product, 0) + 1
        if entry.get("telegram_sent"):
            telegram_sent += 1
        if entry.get("email_course_enrolled"):
            course_enrolled += 1

    print()
    print("=" * 50)
    print("  ONBOARDING STATS")
    print("=" * 50)
    print(f"  Total sales:           {total_sales}")
    print(f"  Onboarded:             {total_onboarded}")
    print(f"  Pending:               {pending}")
    print(f"  Telegram sent:         {telegram_sent}")
    print(f"  Email course enrolled: {course_enrolled}")

    if product_counts:
        print()
        print("  By product:")
        for product, count in sorted(product_counts.items(), key=lambda x: -x[1]):
            bar = "#" * count
            print(f"    {product:<20s} {count:>3d}  {bar}")

    # Recent onboardings
    if log:
        print()
        print("  Last 5 onboarded:")
        for entry in log[-5:]:
            ts = entry.get("onboarded_at", "")[:16].replace("T", " ")
            email = entry.get("customer_email", "?")
            product = entry.get("product_short", "?")
            print(f"    {ts}  {email:<30s}  {product}")

    print()


def cmd_preview(product_key):
    """Preview the onboarding message for a product."""
    # Try exact key first, then partial match
    product_key_lower = product_key.lower().strip()

    config = None
    for key, val in ONBOARDING_MESSAGES.items():
        if key == product_key_lower or product_key_lower in key or key in product_key_lower:
            config = val
            break

    if not config:
        print(f"\n  No onboarding message found for '{product_key}'.")
        print(f"  Available products: {', '.join(c['short_name'] for c in ONBOARDING_MESSAGES.values())}")
        return

    display_name = "alex"
    email = "alex@example.com"
    price = 47.00

    print()
    print("=" * 55)
    print(f"  ONBOARDING PREVIEW: {config['short_name']}")
    print("=" * 55)
    print()
    print("  Telegram notification:")
    print("  " + "-" * 40)
    print(f"  NEW CUSTOMER")
    print()
    print(f"  Customer: {display_name}")
    print(f"  Email: {email}")
    print(f"  Product: {config['short_name']}")
    print(f"  Price: ${price:.2f}")
    print()
    print(f"  Getting Started:")
    for line in config["instructions"].split("\n"):
        print(f"  {line}")
    print("  " + "-" * 40)
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Customer Onboarding System -- Post-Purchase Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python3 onboarding.py --process                # Onboard new sales
  python3 onboarding.py --stats                  # Show stats
  python3 onboarding.py --preview "behike os"    # Preview onboarding message
  python3 onboarding.py --preview blueprint      # Preview blueprint onboarding
  python3 onboarding.py --preview bundle         # Preview bundle onboarding
  python3 onboarding.py --preview lumina         # Preview lumina onboarding

Cron (every hour):
  0 * * * * cd /Users/kalani/behique/bios/sales && python3 onboarding.py --process
        """,
    )

    parser.add_argument("--process", action="store_true",
                        help="Check for new unprocessed sales and onboard them")
    parser.add_argument("--stats", action="store_true",
                        help="Show onboarding statistics")
    parser.add_argument("--preview", metavar="PRODUCT",
                        help="Preview onboarding message for a product")

    args = parser.parse_args()

    if not any([args.process, args.stats, args.preview]):
        parser.print_help()
        sys.exit(0)

    if args.process:
        cmd_process()

    if args.stats:
        cmd_stats()

    if args.preview:
        cmd_preview(args.preview)


if __name__ == "__main__":
    main()
