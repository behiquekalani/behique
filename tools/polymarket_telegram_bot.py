#!/usr/bin/env python3
"""
Polymarket Telegram Alert Bot
Monitors prediction markets and sends alerts to Telegram when:
- A market moves 5%+ in a short time
- A new high-volume market appears
- A contested market (40-60%) has high activity
- Custom watchlist markets change

Usage:
    python3 tools/polymarket_telegram_bot.py                # Run once, send alerts
    python3 tools/polymarket_telegram_bot.py --daemon        # Run continuously (every 5 min)
    python3 tools/polymarket_telegram_bot.py --watchlist     # Show current watchlist
    python3 tools/polymarket_telegram_bot.py --add "bitcoin" # Add keyword to watchlist

Requires:
    pip3 install requests
    Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment or .env
"""

import requests
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Config
GAMMA_URL = "https://gamma-api.polymarket.com"
DATA_DIR = Path(os.path.expanduser("~/behique/Ceiba/projects/polymarket-data"))
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
PRICE_HISTORY_FILE = DATA_DIR / "price_history.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Telegram config (from env or .env file)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Alert thresholds
MOVE_THRESHOLD = 0.05      # 5% price move triggers alert
VOLUME_THRESHOLD = 500000  # $500K+ 24h volume for "hot market" alert
CONTESTED_RANGE = (0.35, 0.65)  # Markets in this range are "contested"


def load_env():
    """Load .env file if it exists."""
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    env_file = Path(os.path.expanduser("~/behique/.env"))
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == 'TELEGRAM_BOT_TOKEN':
                        TELEGRAM_BOT_TOKEN = val
                    elif key == 'TELEGRAM_CHAT_ID':
                        TELEGRAM_CHAT_ID = val


def send_telegram(message):
    """Send a message via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"  [NO TELEGRAM] {message[:100]}")
        return False

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"  Telegram error: {e}")
        return False


def get_markets(limit=100):
    """Fetch active markets from Polymarket."""
    try:
        params = {
            "limit": limit,
            "active": True,
            "closed": False,
            "order": "volume24hr",
            "ascending": False,
        }
        resp = requests.get(f"{GAMMA_URL}/markets", params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        print(f"  API error: {e}")
        return []


def parse_prices(market):
    """Parse outcome prices from market data."""
    prices_raw = market.get("outcomePrices", "[]")
    try:
        prices = json.loads(prices_raw) if isinstance(prices_raw, str) else (prices_raw or [])
        if prices and len(prices) >= 2:
            return float(prices[0]), float(prices[1])
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return None, None


def load_price_history():
    """Load previous price snapshots."""
    if PRICE_HISTORY_FILE.exists():
        with open(PRICE_HISTORY_FILE) as f:
            return json.load(f)
    return {}


def save_price_history(history):
    """Save price snapshot."""
    with open(PRICE_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def load_watchlist():
    """Load keyword watchlist."""
    if WATCHLIST_FILE.exists():
        with open(WATCHLIST_FILE) as f:
            return json.load(f)
    # Default watchlist
    default = ["bitcoin", "btc", "ethereum", "eth", "trump", "fed", "interest rate",
               "ceasefire", "election", "ai", "openai", "tesla"]
    save_watchlist(default)
    return default


def save_watchlist(watchlist):
    """Save watchlist."""
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(watchlist, f, indent=2)


def check_alerts(markets, prev_prices):
    """Check all alert conditions and return list of alerts."""
    alerts = []
    watchlist = load_watchlist()

    for market in markets:
        mid = market.get("id", "")
        question = market.get("question", "")
        yes_price, no_price = parse_prices(market)
        volume_24h = float(market.get("volume24hr", 0) or 0)
        slug = market.get("slug", "")

        if yes_price is None:
            continue

        # 1. Price movement alert
        if mid in prev_prices:
            prev_yes = prev_prices[mid].get("yes", yes_price)
            change = yes_price - prev_yes
            if abs(change) >= MOVE_THRESHOLD:
                direction = "UP" if change > 0 else "DOWN"
                emoji = "📈" if change > 0 else "📉"
                alerts.append({
                    "type": "MOVE",
                    "message": f"{emoji} *PRICE MOVE*\n{question[:80]}\n"
                               f"YES: {prev_yes*100:.1f}% -> {yes_price*100:.1f}% ({direction} {abs(change)*100:.1f}%)\n"
                               f"Vol: ${volume_24h:,.0f}\n"
                               f"polymarket.com/event/{slug}",
                    "priority": 2,
                })

        # 2. High volume new market
        if mid not in prev_prices and volume_24h > VOLUME_THRESHOLD:
            alerts.append({
                "type": "NEW_HOT",
                "message": f"🔥 *NEW HOT MARKET*\n{question[:80]}\n"
                           f"YES: {yes_price*100:.1f}% | Vol: ${volume_24h:,.0f}\n"
                           f"polymarket.com/event/{slug}",
                "priority": 1,
            })

        # 3. Contested market with high volume
        if CONTESTED_RANGE[0] <= yes_price <= CONTESTED_RANGE[1] and volume_24h > 100000:
            # Only alert once per market per day
            today = datetime.now().strftime("%Y-%m-%d")
            contested_key = f"contested_{mid}_{today}"
            if contested_key not in prev_prices:
                alerts.append({
                    "type": "CONTESTED",
                    "message": f"⚔️ *CONTESTED MARKET*\n{question[:80]}\n"
                               f"YES: {yes_price*100:.1f}% (near 50/50)\n"
                               f"Vol: ${volume_24h:,.0f}\n"
                               f"polymarket.com/event/{slug}",
                    "priority": 3,
                })
                prev_prices[contested_key] = {"flagged": True}

        # 4. Watchlist keyword match on new markets
        if mid not in prev_prices:
            q_lower = question.lower()
            for keyword in watchlist:
                if keyword.lower() in q_lower:
                    alerts.append({
                        "type": "WATCHLIST",
                        "message": f"👁️ *WATCHLIST: {keyword.upper()}*\n{question[:80]}\n"
                                   f"YES: {yes_price*100:.1f}% | Vol: ${volume_24h:,.0f}\n"
                                   f"polymarket.com/event/{slug}",
                        "priority": 2,
                    })
                    break  # One alert per market

        # Update price history
        prev_prices[mid] = {
            "yes": yes_price,
            "no": no_price,
            "volume": volume_24h,
            "question": question[:100],
            "updated": datetime.now().isoformat(),
        }

    return alerts, prev_prices


def run_check():
    """Run one check cycle."""
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] Checking markets...")

    markets = get_markets(limit=100)
    if not markets:
        print("  No markets fetched.")
        return

    prev_prices = load_price_history()
    alerts, updated_prices = check_alerts(markets, prev_prices)
    save_price_history(updated_prices)

    if alerts:
        # Sort by priority (lower = more important)
        alerts.sort(key=lambda a: a["priority"])

        # Batch alerts into one message if multiple
        if len(alerts) <= 3:
            for alert in alerts:
                send_telegram(alert["message"])
                print(f"  ALERT [{alert['type']}]: sent")
        else:
            # Combine into summary
            summary = f"🚨 *{len(alerts)} POLYMARKET ALERTS*\n\n"
            for alert in alerts[:5]:  # Max 5 in summary
                summary += alert["message"] + "\n\n"
            if len(alerts) > 5:
                summary += f"...and {len(alerts) - 5} more."
            send_telegram(summary)
            print(f"  Sent {len(alerts)} alerts (batched)")
    else:
        print(f"  No alerts. {len(markets)} markets tracked.")


def daemon_mode(interval=300):
    """Run continuously."""
    print(f"  Polymarket Alert Bot started (checking every {interval}s)")
    print(f"  Telegram: {'configured' if TELEGRAM_BOT_TOKEN else 'NOT configured'}")
    print(f"  Press Ctrl+C to stop\n")

    while True:
        try:
            run_check()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n  Bot stopped.")
            break
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(interval)


def main():
    load_env()
    args = sys.argv[1:]

    if "--daemon" in args:
        interval = 300
        for i, arg in enumerate(args):
            if arg == "--interval" and i + 1 < len(args):
                interval = int(args[i + 1])
        daemon_mode(interval)

    elif "--watchlist" in args:
        wl = load_watchlist()
        print(f"  Watchlist ({len(wl)} keywords):")
        for kw in wl:
            print(f"    - {kw}")

    elif "--add" in args:
        idx = args.index("--add")
        if idx + 1 < len(args):
            keyword = args[idx + 1]
            wl = load_watchlist()
            if keyword.lower() not in [k.lower() for k in wl]:
                wl.append(keyword)
                save_watchlist(wl)
                print(f"  Added '{keyword}' to watchlist.")
            else:
                print(f"  '{keyword}' already in watchlist.")
        else:
            print("  Usage: --add 'keyword'")

    elif "--remove" in args:
        idx = args.index("--remove")
        if idx + 1 < len(args):
            keyword = args[idx + 1]
            wl = load_watchlist()
            wl = [k for k in wl if k.lower() != keyword.lower()]
            save_watchlist(wl)
            print(f"  Removed '{keyword}' from watchlist.")

    else:
        # Single check
        run_check()


if __name__ == "__main__":
    main()
