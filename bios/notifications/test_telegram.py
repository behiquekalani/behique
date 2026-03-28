#!/usr/bin/env python3
"""
Quick test: sends a single message to verify Telegram bot credentials work.

Reads from environment variables first, falls back to ~/behique/.env.telegram
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env_file():
    """Load TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from .env.telegram if not in env."""
    env_path = Path.home() / "behique" / ".env.telegram"
    if not env_path.exists():
        return

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


def main():
    load_env_file()

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        print("Either export it or create ~/behique/.env.telegram")
        print("See TELEGRAM_SETUP.md for instructions.")
        sys.exit(1)

    if not chat_id:
        print("ERROR: TELEGRAM_CHAT_ID is not set.")
        print("See TELEGRAM_SETUP.md Step 2 for how to get it.")
        sys.exit(1)

    message = "BIOS is online. All systems operational."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("ok"):
            print("SUCCESS: Message sent to Telegram.")
            print(f"  Chat ID: {chat_id}")
            print(f"  Message: {message}")
        else:
            print(f"FAILED: Telegram API returned ok=false")
            print(f"  Response: {result}")
            sys.exit(1)

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"FAILED: HTTP {exc.code}")
        print(f"  {body}")
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"FAILED: Could not connect to Telegram API")
        print(f"  {exc.reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
