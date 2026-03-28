#!/usr/bin/env python3
"""
BIOS Unified Telegram Notification Bot
Consolidates all alerts into one clean bot.

Usage:
    python3 telegram_bot.py test      # send a test message
    python3 telegram_bot.py status    # show bot info and chat ID
"""

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from datetime import datetime

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

RATE_LIMIT = 20          # max messages per window
RATE_WINDOW = 60         # window in seconds
MAX_RETRIES = 3
RETRY_DELAY = 2          # seconds between retries

# ---------------------------------------------------------------------------
# Prefixes (unicode, no emoji import needed)
# ---------------------------------------------------------------------------

PREFIX_SALE     = "\U0001F7E2"   # green circle
PREFIX_HIGH     = "\U0001F53A"   # red triangle
PREFIX_MEDIUM   = "\U0001F7E1"   # yellow circle
PREFIX_DAILY    = "\U0001F4CA"   # chart
PREFIX_SYSTEM   = "\u2699\uFE0F" # gear
PREFIX_CONTENT  = "\U0001F4C5"   # calendar

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

_timestamps: deque = deque()
_lock = threading.Lock()


def _rate_ok() -> bool:
    """Return True if we can send another message within the rate window."""
    now = time.time()
    with _lock:
        # purge old timestamps
        while _timestamps and _timestamps[0] < now - RATE_WINDOW:
            _timestamps.popleft()
        if len(_timestamps) >= RATE_LIMIT:
            return False
        _timestamps.append(now)
        return True


# ---------------------------------------------------------------------------
# Core send
# ---------------------------------------------------------------------------

def _telegram_api(method: str, payload: dict) -> dict:
    """Call a Telegram Bot API method. Returns parsed JSON response."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _send(text: str) -> bool:
    """Send a message via Telegram with rate limiting and retry.

    Falls back to stdout when no token is configured.
    Returns True on success.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[BIOS notify] {text}")
        return True

    if not _rate_ok():
        print(f"[BIOS notify] RATE LIMITED — dropped: {text[:80]}", file=sys.stderr)
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = _telegram_api("sendMessage", {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
            })
            if result.get("ok"):
                return True
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            else:
                print(
                    f"[BIOS notify] FAILED after {MAX_RETRIES} retries: {exc}",
                    file=sys.stderr,
                )
    return False


# ---------------------------------------------------------------------------
# Public notification functions
# ---------------------------------------------------------------------------

def notify_sale(product: str, amount: float, platform: str = "eBay") -> bool:
    """Notify about a new sale."""
    msg = (
        f"{PREFIX_SALE} *New sale on {platform}*\n"
        f"Product: {product}\n"
        f"Amount: ${amount:.2f}"
    )
    return _send(msg)


def notify_signal(
    topic: str, score: float, level: str = "HIGH", direction: str = "UP"
) -> bool:
    """Notify about a market / trend signal."""
    prefix = PREFIX_HIGH if level.upper() == "HIGH" else PREFIX_MEDIUM
    msg = (
        f"{prefix} *{level.upper()} conviction alert*\n"
        f"Topic: {topic}\n"
        f"Score: {score:.1f} | Direction: {direction}"
    )
    return _send(msg)


def notify_daily(summary_dict: dict) -> bool:
    """Send morning briefing. summary_dict keys become bullet points."""
    now = datetime.now().strftime("%A, %B %d")
    lines = [f"{PREFIX_DAILY} *Morning Briefing — {now}*", ""]
    for key, value in summary_dict.items():
        lines.append(f"  • *{key}:* {value}")
    return _send("\n".join(lines))


def notify_system(message: str, severity: str = "INFO") -> bool:
    """Notify about system events (fleet status, errors, cron failures)."""
    tag = severity.upper()
    msg = f"{PREFIX_SYSTEM} *SYSTEM [{tag}]* — {message}"
    return _send(msg)


def notify_content(
    platform: str, post_title: str, scheduled_time: str
) -> bool:
    """Notify about scheduled content."""
    msg = (
        f"{PREFIX_CONTENT} *Post scheduled*\n"
        f"Platform: {platform}\n"
        f"Title: {post_title}\n"
        f"Time: {scheduled_time}"
    )
    return _send(msg)


def send_raw(message: str) -> bool:
    """Send an arbitrary message."""
    return _send(message)


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def _cmd_test():
    """Send a test notification for every type."""
    print("Sending test notifications...\n")

    notify_sale("Vintage Polaroid Camera", 47.99, "eBay")
    notify_signal("AI Headphones Trend", 0.92, "HIGH", "UP")
    notify_daily({
        "Revenue (24h)": "$128.50",
        "Active listings": "34",
        "Signals queued": "3",
        "Content scheduled": "2 posts",
    })
    notify_system("All cron jobs healthy", "INFO")
    notify_content("Instagram", "Top 5 AI Tools for Sellers", "2026-03-25 09:00 AST")
    send_raw("BIOS notification bot is online.")

    print("\nDone. Check your Telegram.")


def _cmd_status():
    """Show bot info and chat ID."""
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN is not set.")
        print("Export it and try again:")
        print("  export TELEGRAM_BOT_TOKEN='your-token-here'")
        print("  export TELEGRAM_CHAT_ID='your-chat-id'")
        return

    try:
        info = _telegram_api("getMe", {})
        if info.get("ok"):
            bot = info["result"]
            print(f"Bot name     : {bot.get('first_name', '?')}")
            print(f"Bot username : @{bot.get('username', '?')}")
            print(f"Bot ID       : {bot.get('id', '?')}")
        else:
            print(f"API error: {info}")
    except Exception as exc:
        print(f"Failed to reach Telegram API: {exc}")

    if TELEGRAM_CHAT_ID:
        print(f"Chat ID      : {TELEGRAM_CHAT_ID}")
    else:
        print("TELEGRAM_CHAT_ID is not set.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "test":
        _cmd_test()
    elif cmd == "status":
        _cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 telegram_bot.py [test|status]")
        sys.exit(1)
