#!/usr/bin/env python3
"""
Polymarket Auto-Trader -- conviction-based signal tracker.

Reads convictions.json hourly, generates SIGNAL/COOL DOWN entries,
tracks history, and optionally sends Telegram alerts.

Does NOT auto-execute trades. Signals only.

Usage:
    python3 bios/trading/auto_trader.py --monitor       # continuous mode, checks every hour
    python3 bios/trading/auto_trader.py --check         # single check, then exit
    python3 bios/trading/auto_trader.py --history       # show past signals
    python3 bios/trading/auto_trader.py --stats         # accuracy tracking

Dependencies: stdlib only (+ requests for optional Telegram alerts)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# -- Paths --------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
BIOS_DIR = BASE_DIR.parent
STORAGE_DIR = BIOS_DIR / "storage"
CONVICTIONS_FILE = STORAGE_DIR / "convictions.json"
SIGNAL_HISTORY_FILE = BASE_DIR / "signal_history.json"
CONFIG_FILE = BASE_DIR / "trader_config.json"

# -- Thresholds ---------------------------------------------------------------

HIGH_THRESHOLD = 75       # conviction score >= this triggers SIGNAL
COOL_DOWN_THRESHOLD = 50  # conviction score < this triggers COOL DOWN
CHECK_INTERVAL = 3600     # 1 hour in seconds

# -- Config -------------------------------------------------------------------

DEFAULT_CONFIG = {
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "enabled": True,
    "check_interval_seconds": CHECK_INTERVAL,
    "high_threshold": HIGH_THRESHOLD,
    "cool_down_threshold": COOL_DOWN_THRESHOLD,
}


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_config():
    config = DEFAULT_CONFIG.copy()
    saved = load_json(CONFIG_FILE, {})
    config.update(saved)
    # Env vars override file config
    if os.environ.get("TRADER_TELEGRAM_TOKEN"):
        config["telegram_bot_token"] = os.environ["TRADER_TELEGRAM_TOKEN"]
    if os.environ.get("TRADER_TELEGRAM_CHAT"):
        config["telegram_chat_id"] = os.environ["TRADER_TELEGRAM_CHAT"]
    return config


def load_signal_history():
    return load_json(SIGNAL_HISTORY_FILE, {"signals": [], "active_highs": {}})


def save_signal_history(history):
    save_json(SIGNAL_HISTORY_FILE, history)


# -- Telegram -----------------------------------------------------------------

def send_telegram(message, config):
    """Send a Telegram message if configured. Fails silently."""
    token = config.get("telegram_bot_token", "")
    chat_id = config.get("telegram_chat_id", "")
    if not token or not chat_id:
        return False

    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }, timeout=10)
        return resp.ok
    except Exception:
        return False


# -- Signal logic -------------------------------------------------------------

def check_convictions(config):
    """Read convictions, generate signals, return new entries."""
    convictions = load_json(CONVICTIONS_FILE, {})
    history = load_signal_history()
    active_highs = history.get("active_highs", {})
    new_signals = []
    now = datetime.now(timezone.utc).isoformat()

    # Handle both dict and list formats for convictions
    topics = {}
    if isinstance(convictions, dict):
        topics = convictions
    elif isinstance(convictions, list):
        for item in convictions:
            key = item.get("topic") or item.get("name") or item.get("id", "unknown")
            topics[key] = item

    if not topics:
        print(f"  No convictions found in {CONVICTIONS_FILE}")
        return []

    for topic_key, data in topics.items():
        # Extract score -- support multiple field names
        score = None
        for field in ("conviction", "score", "confidence", "strength"):
            if isinstance(data, dict) and field in data:
                score = data[field]
                break
        if isinstance(data, (int, float)):
            score = data

        if score is None:
            continue

        # Extract sentiment
        sentiment = "neutral"
        if isinstance(data, dict):
            sentiment = data.get("sentiment", data.get("direction", "neutral"))

        # Normalize sentiment to positive/negative/neutral
        if isinstance(sentiment, str):
            sentiment = sentiment.lower()
            if sentiment in ("positive", "bullish", "long", "up", "yes"):
                sentiment = "positive"
            elif sentiment in ("negative", "bearish", "short", "down", "no"):
                sentiment = "negative"
            else:
                sentiment = "neutral"

        # HIGH SIGNAL: score >= threshold + positive sentiment
        if score >= config.get("high_threshold", HIGH_THRESHOLD) and sentiment == "positive":
            if topic_key not in active_highs:
                entry = {
                    "type": "SIGNAL",
                    "topic": topic_key,
                    "score": score,
                    "sentiment": sentiment,
                    "timestamp": now,
                    "details": data if isinstance(data, dict) else {"raw": data},
                }
                new_signals.append(entry)
                active_highs[topic_key] = {
                    "signal_time": now,
                    "entry_score": score,
                }
                print(f"  SIGNAL: {topic_key} (score={score}, sentiment={sentiment})")

        # COOL DOWN: score dropped below threshold
        elif score < config.get("cool_down_threshold", COOL_DOWN_THRESHOLD):
            if topic_key in active_highs:
                prev = active_highs.pop(topic_key)
                entry = {
                    "type": "COOL DOWN",
                    "topic": topic_key,
                    "score": score,
                    "sentiment": sentiment,
                    "timestamp": now,
                    "signal_entry_score": prev.get("entry_score"),
                    "signal_time": prev.get("signal_time"),
                }
                new_signals.append(entry)
                print(f"  COOL DOWN: {topic_key} (score={score}, was={prev.get('entry_score')})")

    # Save updated history
    history["signals"].extend(new_signals)
    history["active_highs"] = active_highs
    history["last_check"] = now
    save_signal_history(history)

    return new_signals


def run_check(config):
    """Run a single conviction check and send alerts."""
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}] Checking convictions...")

    new_signals = check_convictions(config)

    if not new_signals:
        print("  No new signals.")
        return

    # Send Telegram alerts for HIGH signals
    for sig in new_signals:
        if sig["type"] == "SIGNAL":
            msg = (
                f"*POLYMARKET SIGNAL*\n"
                f"Topic: {sig['topic']}\n"
                f"Score: {sig['score']}\n"
                f"Sentiment: {sig['sentiment']}\n"
                f"Time: {sig['timestamp']}"
            )
            sent = send_telegram(msg, config)
            if sent:
                print(f"  Telegram alert sent for: {sig['topic']}")


# -- Monitor mode -------------------------------------------------------------

def monitor(config):
    """Continuous monitoring loop."""
    interval = config.get("check_interval_seconds", CHECK_INTERVAL)
    print(f"Starting monitor mode (interval: {interval}s)")
    print(f"Watching: {CONVICTIONS_FILE}")
    print(f"History:  {SIGNAL_HISTORY_FILE}")
    telegram_configured = bool(config.get("telegram_bot_token") and config.get("telegram_chat_id"))
    print(f"Telegram: {'configured' if telegram_configured else 'not configured'}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            run_check(config)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


# -- History display ----------------------------------------------------------

def show_history():
    """Print signal history."""
    history = load_signal_history()
    signals = history.get("signals", [])
    active = history.get("active_highs", {})

    if not signals:
        print("No signal history yet.")
        return

    print(f"Total signals: {len(signals)}")
    print(f"Active HIGH positions: {len(active)}")
    print()

    # Show last 20 signals
    recent = signals[-20:]
    for sig in recent:
        icon = ">>>" if sig["type"] == "SIGNAL" else "<<<"
        ts = sig.get("timestamp", "?")[:19]
        score = sig.get("score", "?")
        print(f"  {icon} [{ts}] {sig['type']:10s} | {sig['topic'][:40]:40s} | score={score}")

    if active:
        print(f"\nActive HIGH topics:")
        for topic, info in active.items():
            print(f"  - {topic} (entered at score={info.get('entry_score')}, {info.get('signal_time', '?')[:19]})")


# -- Stats --------------------------------------------------------------------

def show_stats():
    """Show accuracy and signal statistics."""
    history = load_signal_history()
    signals = history.get("signals", [])
    active = history.get("active_highs", {})

    if not signals:
        print("No signal data yet.")
        return

    signal_count = sum(1 for s in signals if s["type"] == "SIGNAL")
    cooldown_count = sum(1 for s in signals if s["type"] == "COOL DOWN")

    # Group by topic
    topics_seen = {}
    for sig in signals:
        topic = sig["topic"]
        if topic not in topics_seen:
            topics_seen[topic] = {"signals": 0, "cooldowns": 0, "scores": []}
        topics_seen[topic]["scores"].append(sig.get("score", 0))
        if sig["type"] == "SIGNAL":
            topics_seen[topic]["signals"] += 1
        else:
            topics_seen[topic]["cooldowns"] += 1

    # Completed cycles (SIGNAL followed by COOL DOWN)
    completed = cooldown_count
    # Score deltas for completed cycles
    deltas = []
    for sig in signals:
        if sig["type"] == "COOL DOWN" and sig.get("signal_entry_score") is not None:
            delta = sig.get("score", 0) - sig["signal_entry_score"]
            deltas.append(delta)

    print("=== SIGNAL STATS ===")
    print(f"Total SIGNAL entries:    {signal_count}")
    print(f"Total COOL DOWN entries: {cooldown_count}")
    print(f"Currently active:        {len(active)}")
    print(f"Completed cycles:        {completed}")
    print(f"Unique topics tracked:   {len(topics_seen)}")
    print()

    if deltas:
        avg_delta = sum(deltas) / len(deltas)
        print(f"Avg score change (signal->cooldown): {avg_delta:+.1f}")
        print(f"Min delta: {min(deltas):+.1f}  Max delta: {max(deltas):+.1f}")
    else:
        print("No completed cycles yet for accuracy tracking.")

    if topics_seen:
        print(f"\nTop topics by signal count:")
        ranked = sorted(topics_seen.items(), key=lambda x: x[1]["signals"], reverse=True)
        for topic, info in ranked[:10]:
            print(f"  {topic[:45]:45s} signals={info['signals']} cooldowns={info['cooldowns']}")


# -- CLI ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Polymarket conviction-based signal tracker"
    )
    parser.add_argument("--monitor", action="store_true",
                        help="Continuous mode, checks every hour")
    parser.add_argument("--check", action="store_true",
                        help="Single check, then exit")
    parser.add_argument("--history", action="store_true",
                        help="Show past signals")
    parser.add_argument("--stats", action="store_true",
                        help="Show accuracy and signal statistics")
    parser.add_argument("--init-config", action="store_true",
                        help="Create default config file")

    args = parser.parse_args()
    config = load_config()

    if args.init_config:
        if not CONFIG_FILE.exists():
            save_json(CONFIG_FILE, DEFAULT_CONFIG)
            print(f"Config created: {CONFIG_FILE}")
            print("Edit it to add your Telegram bot token and chat ID.")
        else:
            print(f"Config already exists: {CONFIG_FILE}")
        return

    if args.monitor:
        monitor(config)
    elif args.check:
        run_check(config)
    elif args.history:
        show_history()
    elif args.stats:
        show_stats()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
