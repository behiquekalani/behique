#!/usr/bin/env python3
"""
Telegram notification helper for Gumroad sales.

Sends sale alerts and daily summaries via Telegram bot.
Falls back to stdout if no bot token is configured.

Usage:
    python3 notifier.py test "Test message"
    python3 notifier.py sale "Behike OS" 97.00 "buyer@example.com"
    python3 notifier.py summary 5 485.00 "Behike OS"

Env vars:
    TELEGRAM_BOT_TOKEN  - Bot token from @BotFather
    TELEGRAM_CHAT_ID    - Your chat/group ID
"""

import os
import sys
import json
import urllib.request
import urllib.error

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def _send_telegram(message: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    if not BOT_TOKEN or not CHAT_ID:
        print(f"[notifier] No Telegram config. Message:\n{message}")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("ok"):
                return True
            print(f"[notifier] Telegram API error: {result}")
            return False
    except urllib.error.URLError as e:
        print(f"[notifier] Failed to send Telegram message: {e}")
        return False
    except Exception as e:
        print(f"[notifier] Unexpected error: {e}")
        return False


def send_sale_notification(product: str, price: float, email: str) -> bool:
    """Send a sale alert to Telegram."""
    msg = (
        f"<b>SALE</b>\n"
        f"Product: {product}\n"
        f"Price: ${price:.2f}\n"
        f"Buyer: {email}"
    )
    return _send_telegram(msg)


def send_daily_summary(
    total_sales: int,
    total_revenue: float,
    top_product: str,
    all_time_revenue: float = 0,
) -> bool:
    """Send the daily digest summary to Telegram."""
    if total_sales == 0:
        msg = "No sales today. Keep building."
    else:
        msg = (
            f"<b>Daily Summary</b>\n"
            f"Sales: {total_sales}\n"
            f"Revenue: ${total_revenue:.2f}\n"
            f"Top product: {top_product}"
        )
        if all_time_revenue > 0:
            msg += f"\nAll-time: ${all_time_revenue:.2f}"
    return _send_telegram(msg)


def send_custom(message: str) -> bool:
    """Send an arbitrary message to Telegram."""
    return _send_telegram(message)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "test":
        message = sys.argv[2] if len(sys.argv) > 2 else "Notifier test - system is working."
        ok = send_custom(message)
        print("Sent." if ok else "Printed to stdout (no Telegram config).")

    elif cmd == "sale":
        if len(sys.argv) < 5:
            print("Usage: python3 notifier.py sale <product> <price> <email>")
            return
        send_sale_notification(sys.argv[2], float(sys.argv[3]), sys.argv[4])

    elif cmd == "summary":
        if len(sys.argv) < 5:
            print("Usage: python3 notifier.py summary <total_sales> <total_revenue> <top_product>")
            return
        send_daily_summary(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
