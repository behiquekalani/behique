#!/usr/bin/env python3
"""
notify.py — Ceiba's Telegram relay
Runs natively on Mac (not in sandbox), watches ~/behique/pending-notifications/
for .json files and sends them via Telegram, then deletes them.

Usage:
  # Send directly (one-shot):
  python3 ~/behique/tools/notify.py "your message here"

  # Run as watcher (called by LaunchAgent every 60s):
  python3 ~/behique/tools/notify.py --watch

  # Queue a message from anywhere (sandbox-safe, no internet needed):
  python3 ~/behique/tools/notify.py --queue "your message here"
"""

import sys
import os
import json
import glob
import ssl
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Fix macOS Python SSL certificate verification
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

# ── Config ──────────────────────────────────────────────────────────────────
PENDING_DIR = Path.home() / "behique" / "pending-notifications"
CONFIG_FILE = Path.home() / "behique" / ".ceiba-config"
LOG_FILE = Path.home() / "behique" / "output" / "notify-log.txt"


def load_token() -> str:
    """Load Telegram bot token from .ceiba-config."""
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"')
    # Fallback to env var
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in .ceiba-config or environment")
    return token


def load_chat_id() -> str:
    """Load Telegram chat ID from .ceiba-config."""
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            if line.startswith("TELEGRAM_CHAT_ID="):
                return line.split("=", 1)[1].strip().strip('"')
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not chat_id:
        raise ValueError("No TELEGRAM_CHAT_ID found in .ceiba-config or environment")
    return chat_id


def send_telegram(message: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    try:
        token = load_token()
        chat_id = load_chat_id()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        log(f"ERROR sending Telegram: {e}")
        return False


def queue_message(message: str, label: str = "msg") -> Path:
    """Write a message to the pending-notifications folder (sandbox-safe)."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    filepath = PENDING_DIR / f"{ts}-{label}.json"
    filepath.write_text(json.dumps({
        "message": message,
        "queued_at": datetime.now().isoformat(),
        "label": label
    }, indent=2))
    return filepath


def watch():
    """Process all pending notification files and send them."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(PENDING_DIR.glob("*.json"))

    if not files:
        return  # Nothing to do

    log(f"Processing {len(files)} pending notification(s)...")

    for filepath in files:
        try:
            data = json.loads(filepath.read_text())
            message = data.get("message", "")
            label = data.get("label", "unknown")

            if not message:
                filepath.unlink()
                continue

            success = send_telegram(message)
            if success:
                log(f"✓ Sent [{label}]: {message[:60]}...")
                filepath.unlink()  # Delete after successful send
            else:
                log(f"✗ Failed [{label}] — will retry next cycle")

        except Exception as e:
            log(f"ERROR processing {filepath.name}: {e}")


def log(msg: str):
    """Append a timestamped line to the notify log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if args[0] == "--watch":
        # Called by LaunchAgent — process pending queue
        watch()

    elif args[0] == "--queue":
        # Queue a message (safe to call from sandbox or scheduled tasks)
        if len(args) < 2:
            print("Usage: notify.py --queue 'your message'")
            sys.exit(1)
        message = " ".join(args[1:])
        label = args[2] if len(args) > 2 else "ceiba"
        path = queue_message(message, label)
        print(f"Queued: {path}")

    else:
        # Direct send — called from Mac terminal with internet access
        message = " ".join(args)
        success = send_telegram(message)
        if success:
            print("✓ Sent")
        else:
            print("✗ Failed — check ~/behique/output/notify-log.txt")
            sys.exit(1)
