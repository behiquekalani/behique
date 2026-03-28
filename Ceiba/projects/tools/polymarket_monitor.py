#!/usr/bin/env python3
"""
Polymarket Monitor - Price tracking and opportunity detection
Tracks active markets, alerts on mispriced opportunities, and logs data.

Usage:
    python3 polymarket_monitor.py              # Show active markets
    python3 polymarket_monitor.py --track      # Start price tracking loop
    python3 polymarket_monitor.py --trending   # Show trending/high-volume markets
    python3 polymarket_monitor.py --search "bitcoin"  # Search markets

Requires: pip3 install requests
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Polymarket CLOB API (read-only, no auth needed)
BASE_URL = "https://clob.polymarket.com"
GAMMA_URL = "https://gamma-api.polymarket.com"

# Data directory
DATA_DIR = Path(os.path.expanduser("~/behique/Ceiba/projects/polymarket-data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_markets(limit=20, active=True):
    """Fetch active markets from Polymarket."""
    try:
        params = {
            "limit": limit,
            "active": active,
            "closed": False,
            "order": "volume24hr",
            "ascending": False,
        }
        resp = requests.get(f"{GAMMA_URL}/markets", params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"API returned status {resp.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []


def get_market_details(condition_id):
    """Get detailed market data including order book."""
    try:
        resp = requests.get(f"{GAMMA_URL}/markets/{condition_id}", timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"Error fetching market details: {e}")
        return None


def search_markets(query, limit=20):
    """Search markets by keyword."""
    try:
        params = {
            "limit": limit,
            "active": True,
            "closed": False,
            "tag_slug": query.lower().replace(" ", "-"),
        }
        resp = requests.get(f"{GAMMA_URL}/markets", params=params, timeout=15)
        if resp.status_code == 200:
            results = resp.json()
            if results:
                return results

        # Fallback: search by text
        params = {
            "limit": limit,
            "active": True,
            "closed": False,
        }
        resp = requests.get(f"{GAMMA_URL}/markets", params=params, timeout=15)
        if resp.status_code == 200:
            all_markets = resp.json()
            return [m for m in all_markets if query.lower() in m.get("question", "").lower()
                    or query.lower() in m.get("description", "").lower()]
        return []
    except Exception as e:
        print(f"Error searching markets: {e}")
        return []


def format_market(market):
    """Format a market for display."""
    question = market.get("question", "Unknown")
    volume = market.get("volume", 0)
    volume_24h = market.get("volume24hr", 0)
    liquidity = market.get("liquidity", 0)

    # Get outcomes and prices (API returns these as JSON strings)
    outcomes_raw = market.get("outcomes", "[]")
    prices_raw = market.get("outcomePrices", "[]")
    try:
        outcomes = json.loads(outcomes_raw) if isinstance(outcomes_raw, str) else outcomes_raw
    except (json.JSONDecodeError, TypeError):
        outcomes = []
    try:
        outcome_prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
    except (json.JSONDecodeError, TypeError):
        outcome_prices = []

    # Format volume
    def fmt_vol(v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return "$0"
        if v >= 1_000_000:
            return f"${v/1_000_000:.1f}M"
        elif v >= 1_000:
            return f"${v/1_000:.1f}K"
        return f"${v:.0f}"

    # Format prices
    prices_str = ""
    if outcomes and outcome_prices:
        price_parts = []
        for i, outcome in enumerate(outcomes):
            if i < len(outcome_prices):
                try:
                    price = float(outcome_prices[i])
                    pct = price * 100
                    price_parts.append(f"{outcome}: {pct:.1f}%")
                except (TypeError, ValueError):
                    pass
        prices_str = " | ".join(price_parts)

    end_date = market.get("endDate", "")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            days_left = (end_dt - datetime.now(timezone.utc)).days
            end_str = f"{days_left}d left"
        except Exception:
            end_str = ""
    else:
        end_str = ""

    return {
        "question": question,
        "prices": prices_str,
        "volume_24h": fmt_vol(volume_24h),
        "total_volume": fmt_vol(volume),
        "liquidity": fmt_vol(liquidity),
        "end_date": end_str,
        "slug": market.get("slug", ""),
        "id": market.get("id", ""),
    }


def display_markets(markets, title="Markets"):
    """Pretty print markets."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    for i, market in enumerate(markets, 1):
        fm = format_market(market)
        print(f"  {i}. {fm['question']}")
        if fm['prices']:
            print(f"     Prices: {fm['prices']}")
        print(f"     24h Vol: {fm['volume_24h']} | Total: {fm['total_volume']} | Liq: {fm['liquidity']} | {fm['end_date']}")
        if fm['slug']:
            print(f"     URL: polymarket.com/event/{fm['slug']}")
        print()


def detect_opportunities(markets):
    """Find potential mispriced markets based on simple heuristics."""
    opportunities = []

    for market in markets:
        prices_raw = market.get("outcomePrices", "[]")
        try:
            outcome_prices = json.loads(prices_raw) if isinstance(prices_raw, str) else (prices_raw or [])
        except (json.JSONDecodeError, TypeError):
            continue
        volume_24h = float(market.get("volume24hr", 0) or 0)
        liquidity = float(market.get("liquidity", 0) or 0)

        if not outcome_prices or len(outcome_prices) < 2:
            continue

        try:
            yes_price = float(outcome_prices[0])
            no_price = float(outcome_prices[1])
        except (TypeError, ValueError, IndexError):
            continue

        # Opportunity 1: Prices near 50/50 with high volume (contested markets)
        if 0.40 <= yes_price <= 0.60 and volume_24h > 10000:
            opportunities.append({
                "market": market,
                "reason": "Contested market (40-60% range) with high volume. Research for edge.",
                "type": "contested"
            })

        # Opportunity 2: Very cheap YES shares (high risk, high reward)
        if yes_price <= 0.15 and volume_24h > 5000:
            opportunities.append({
                "market": market,
                "reason": f"Cheap YES at {yes_price*100:.0f}%. If you believe this event is more likely than the market thinks, potential 5-6x return.",
                "type": "longshot"
            })

        # Opportunity 3: Very expensive YES shares (potential short)
        if yes_price >= 0.90 and volume_24h > 5000:
            opportunities.append({
                "market": market,
                "reason": f"YES at {yes_price*100:.0f}%. If you believe this is overpriced, cheap NO at {no_price*100:.0f}%.",
                "type": "overpriced"
            })

        # Opportunity 4: Low liquidity + high interest (spreads may be wide)
        if volume_24h > 50000 and liquidity < 10000:
            opportunities.append({
                "market": market,
                "reason": "High volume but low liquidity. Spread opportunities may exist.",
                "type": "spread"
            })

    return opportunities


def save_snapshot(markets):
    """Save market data snapshot for historical tracking."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_file = DATA_DIR / f"snapshot_{timestamp}.json"

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "market_count": len(markets),
        "markets": []
    }

    for market in markets:
        snapshot["markets"].append({
            "id": market.get("id"),
            "question": market.get("question"),
            "outcomes": market.get("outcomes"),
            "outcomePrices": market.get("outcomePrices"),
            "volume24hr": market.get("volume24hr"),
            "liquidity": market.get("liquidity"),
        })

    with open(snapshot_file, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"  Snapshot saved: {snapshot_file.name}")


def tracking_loop(interval=300):
    """Continuously track markets and alert on changes."""
    print(f"\n  Starting price tracking (checking every {interval}s)")
    print(f"  Press Ctrl+C to stop\n")

    prev_prices = {}

    while True:
        try:
            markets = get_markets(limit=50)
            if not markets:
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] No data. Retrying...")
                time.sleep(interval)
                continue

            # Check for price movements
            alerts = []
            for market in markets:
                mid = market.get("id", "")
                prices_raw = market.get("outcomePrices", "[]")
                try:
                    prices = json.loads(prices_raw) if isinstance(prices_raw, str) else (prices_raw or [])
                except (json.JSONDecodeError, TypeError):
                    continue
                if not prices or not mid:
                    continue

                try:
                    current_yes = float(prices[0])
                except (TypeError, ValueError):
                    continue

                if mid in prev_prices:
                    prev_yes = prev_prices[mid]
                    change = current_yes - prev_yes
                    if abs(change) >= 0.03:  # 3%+ move
                        direction = "UP" if change > 0 else "DOWN"
                        alerts.append(
                            f"  ALERT: {market.get('question', '')[:60]}... "
                            f"moved {direction} {abs(change)*100:.1f}% "
                            f"({prev_yes*100:.1f}% -> {current_yes*100:.1f}%)"
                        )

                prev_prices[mid] = current_yes

            # Display
            now = datetime.now().strftime("%H:%M:%S")
            print(f"  [{now}] Tracked {len(markets)} markets. ", end="")

            if alerts:
                print(f"{len(alerts)} alerts:")
                for alert in alerts:
                    print(alert)
            else:
                print("No significant moves.")

            # Save snapshot every cycle
            save_snapshot(markets)

            # Check for opportunities
            opps = detect_opportunities(markets)
            if opps:
                print(f"  Opportunities found: {len(opps)}")
                for opp in opps[:3]:
                    q = opp["market"].get("question", "")[:50]
                    print(f"    - [{opp['type']}] {q}... {opp['reason'][:60]}")

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n  Tracking stopped.")
            break
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(interval)


def main():
    args = sys.argv[1:]

    if "--track" in args:
        interval = 300  # 5 minutes default
        for i, arg in enumerate(args):
            if arg == "--interval" and i + 1 < len(args):
                interval = int(args[i + 1])
        tracking_loop(interval)

    elif "--search" in args:
        idx = args.index("--search")
        if idx + 1 < len(args):
            query = args[idx + 1]
            print(f"\n  Searching for: {query}")
            markets = search_markets(query)
            if markets:
                display_markets(markets, f"Search Results: '{query}'")
            else:
                print(f"  No markets found for '{query}'")
        else:
            print("  Usage: --search 'query'")

    elif "--trending" in args:
        markets = get_markets(limit=20)
        if markets:
            display_markets(markets, "Trending Markets (by 24h Volume)")

            # Show opportunities
            opps = detect_opportunities(markets)
            if opps:
                print(f"\n{'='*70}")
                print(f" Potential Opportunities ({len(opps)} found)")
                print(f"{'='*70}\n")
                for opp in opps:
                    fm = format_market(opp["market"])
                    print(f"  [{opp['type'].upper()}] {fm['question']}")
                    print(f"    {opp['reason']}")
                    print()

    elif "--opportunities" in args:
        markets = get_markets(limit=100)
        opps = detect_opportunities(markets)
        if opps:
            print(f"\n{'='*70}")
            print(f" Opportunities ({len(opps)} found)")
            print(f"{'='*70}\n")
            for opp in opps:
                fm = format_market(opp["market"])
                print(f"  [{opp['type'].upper()}] {fm['question']}")
                print(f"    Prices: {fm['prices']}")
                print(f"    24h Vol: {fm['volume_24h']} | {opp['reason']}")
                print()
        else:
            print("  No opportunities detected in current markets.")

    else:
        # Default: show top markets
        markets = get_markets(limit=15)
        if markets:
            display_markets(markets, "Top Polymarket Markets")
            save_snapshot(markets)
        else:
            print("  Could not fetch markets. Check internet connection.")

        print("  Commands:")
        print("    --trending        Show high-volume markets")
        print("    --search 'query'  Search markets")
        print("    --track           Start price tracking loop")
        print("    --opportunities   Find mispriced markets")
        print("    --interval N      Set tracking interval (seconds)")


if __name__ == "__main__":
    main()
