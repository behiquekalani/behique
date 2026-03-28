#!/usr/bin/env python3
"""
BIOS Polymarket Fetcher - Monitors prediction markets for signals.
Integrates with existing polymarket_telegram_bot.py data.

Usage:
    python3 bios/ingestion/polymarket_fetcher.py          # Fetch top markets
    python3 bios/ingestion/polymarket_fetcher.py --movers  # Show biggest movers
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
POLY_FILE = STORAGE_DIR / "polymarket.json"
SIGNALS_FILE = STORAGE_DIR / "signals.json"

GAMMA_URL = "https://gamma-api.polymarket.com"


def fetch_markets(limit=20):
    """Fetch top active markets from Polymarket."""
    try:
        url = f"{GAMMA_URL}/markets?limit={limit}&active=true&closed=false&order=volume24hr&ascending=false"
        req = Request(url, headers={"User-Agent": "BIOS/1.0"})
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ERROR fetching Polymarket: {e}")
        return []


def load_previous():
    """Load previous market data for comparison."""
    if POLY_FILE.exists():
        try:
            with open(POLY_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_markets(data):
    with open(POLY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def detect_movers(current, previous, threshold=0.05):
    """Find markets that moved significantly."""
    movers = []
    prev_map = {m.get("question", ""): m for m in previous.get("markets", [])}

    for market in current:
        question = market.get("question", "")
        if question in prev_map:
            old_price = float(prev_map[question].get("outcomePrices", "[0.5]").strip("[]").split(",")[0].strip('"'))
            new_price = float(market.get("outcomePrices", "[0.5]").strip("[]").split(",")[0].strip('"'))
            change = abs(new_price - old_price)
            if change >= threshold:
                movers.append({
                    "question": question,
                    "old_price": round(old_price, 3),
                    "new_price": round(new_price, 3),
                    "change": round(change, 3),
                    "direction": "UP" if new_price > old_price else "DOWN",
                    "volume": market.get("volume", 0),
                })
    return movers


def market_to_signal(market):
    """Convert a Polymarket entry to a BIOS signal."""
    import hashlib
    question = market.get("question", "")
    sig_id = hashlib.md5(question.encode()).hexdigest()[:12]

    try:
        price = float(market.get("outcomePrices", "[0.5]").strip("[]").split(",")[0].strip('"'))
    except Exception:
        price = 0.5

    # Determine if this is a contested market (40-60% = uncertain)
    contested = 0.4 <= price <= 0.6

    return {
        "id": f"poly_{sig_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "Polymarket",
        "category": "prediction_market",
        "title": question[:100],
        "url": f"https://polymarket.com",
        "description": f"Price: {price:.1%} YES. Volume: ${float(market.get('volume', 0)):,.0f}",
        "tags": ["polymarket", "prediction"],
        "assets": [],
        "sentiment": round(price - 0.5, 2),
        "priority": 2 if contested else 1,
    }


def main():
    print("  BIOS Polymarket Fetcher...")
    markets = fetch_markets(20)

    if not markets:
        print("  No data received.")
        return

    previous = load_previous()

    # Save current data
    save_markets({"markets": markets, "fetched_at": datetime.utcnow().isoformat()})

    # Detect movers
    movers = detect_movers(markets, previous)

    # Add signals
    signals_file = SIGNALS_FILE
    existing_signals = []
    if signals_file.exists():
        try:
            with open(signals_file) as f:
                existing_signals = json.load(f)
        except Exception:
            pass

    existing_ids = {s["id"] for s in existing_signals}
    new_count = 0

    for market in markets[:10]:
        signal = market_to_signal(market)
        if signal["id"] not in existing_ids:
            existing_signals.append(signal)
            existing_ids.add(signal["id"])
            new_count += 1

    existing_signals = existing_signals[-500:]
    with open(signals_file, "w") as f:
        json.dump(existing_signals, f, indent=2)

    print(f"  {len(markets)} markets fetched. {new_count} new signals. {len(movers)} movers.")

    if "--movers" in sys.argv and movers:
        print(f"\n  TOP MOVERS:")
        for m in sorted(movers, key=lambda x: x["change"], reverse=True)[:10]:
            print(f"    {m['direction']:4s} {m['change']:+.1%}  {m['question'][:60]}")

    if "--movers" in sys.argv and not movers:
        # Show top markets instead
        print(f"\n  TOP MARKETS BY VOLUME:")
        for m in markets[:10]:
            q = m.get("question", "?")[:55]
            try:
                price = float(m.get("outcomePrices", "[0.5]").strip("[]").split(",")[0])
            except Exception:
                price = 0.5
            vol = float(m.get("volume", 0))
            print(f"    {price:5.1%}  ${vol:>12,.0f}  {q}")


if __name__ == "__main__":
    main()
