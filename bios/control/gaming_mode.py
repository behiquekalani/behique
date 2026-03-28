#!/usr/bin/env python3
"""
Gaming Mode Toggle for Cobo.
Pauses all BIOS jobs on Cobo when gaming, resumes when done.

Usage:
    python3 bios/control/gaming_mode.py toggle    # Toggle mode
    python3 bios/control/gaming_mode.py status     # Show current mode
    python3 bios/control/gaming_mode.py gaming     # Force gaming mode
    python3 bios/control/gaming_mode.py normal     # Force normal mode
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = BASE_DIR / "bios" / "config.json"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def notify_telegram(message, config):
    token = os.environ.get(config["telegram"]["bot_token_env"], "")
    chat_id = os.environ.get(config["telegram"]["chat_id_env"], "")
    if not token or not chat_id:
        print(f"  (Telegram not configured, skipping notification)")
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    except Exception as e:
        print(f"  (Telegram notification failed: {e})")


def set_mode(mode):
    config = load_config()
    old_mode = config["fleet"]["cobo"].get("mode", "normal")

    if old_mode == mode:
        print(f"  Cobo is already in {mode} mode.")
        return

    config["fleet"]["cobo"]["mode"] = mode

    if mode == "gaming":
        config["fleet"]["cobo"]["paused_since"] = datetime.now().isoformat()
        msg = "Cobo entering gaming mode. All BIOS jobs paused."
    else:
        config["fleet"]["cobo"]["paused_since"] = None
        msg = "Cobo back online. BIOS jobs resuming."

    save_config(config)
    print(f"  {msg}")
    notify_telegram(msg, config)


def show_status():
    config = load_config()
    cobo = config["fleet"]["cobo"]
    mode = cobo.get("mode", "normal")
    paused = cobo.get("paused_since")

    print(f"\n  COBO STATUS")
    print(f"  Mode: {mode.upper()}")
    if paused:
        print(f"  Paused since: {paused}")
    print(f"  IP: {cobo['ip']}")
    print(f"  Enabled: {cobo.get('enabled', False)}")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: gaming_mode.py [toggle|status|gaming|normal]")
        return

    cmd = sys.argv[1].lower()

    if cmd == "toggle":
        config = load_config()
        current = config["fleet"]["cobo"].get("mode", "normal")
        new_mode = "gaming" if current == "normal" else "normal"
        set_mode(new_mode)
    elif cmd == "status":
        show_status()
    elif cmd in ("gaming", "normal"):
        set_mode(cmd)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
