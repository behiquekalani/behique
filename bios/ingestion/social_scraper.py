#!/usr/bin/env python3
"""
BIOS Unified Social Scraper - scrapes 6 free sources for market signals.
No API keys needed. All sources use public JSON/REST endpoints.

Sources:
  1. Reddit r/wallstreetbets (top)
  2. Reddit r/cryptocurrency (top)
  3. Reddit r/polymarket (new)
  4. Reddit r/economics (top)
  5. CoinGecko top movers
  6. Crypto Fear & Greed Index

Usage:
    python3 bios/ingestion/social_scraper.py          # Interactive run
    python3 bios/ingestion/social_scraper.py --run     # Cron mode (no prompts)
"""

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

import random
import urllib.request

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
OUTPUT_FILE = STORAGE_DIR / "social_signals.json"
PROXY_FILE = BASE_DIR / "config" / "proxies.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# ---------------------------------------------------------------------------
# Proxy support
# ---------------------------------------------------------------------------

_proxies = []

def _load_proxies():
    """Load proxies from config/proxies.txt. Format: ip:port:user:pass or ip:port"""
    global _proxies
    if PROXY_FILE.exists():
        lines = PROXY_FILE.read_text().strip().splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(":")
            if len(parts) == 4:
                ip, port, user, pwd = parts
                _proxies.append(f"http://{user}:{pwd}@{ip}:{port}")
            elif len(parts) == 2:
                _proxies.append(f"http://{parts[0]}:{parts[1]}")
        if _proxies:
            print(f"  [PROXY] Loaded {len(_proxies)} proxies")
    else:
        print("  [PROXY] No proxy file found at config/proxies.txt - using direct connection")
        print("  [WARN] Your real IP is exposed. Get proxies from webshare.io (free)")

_load_proxies()


def _get_proxy_handler():
    """Return a random proxy handler, or None if no proxies loaded."""
    if not _proxies:
        return None
    proxy_url = random.choice(_proxies)
    return urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_json(url, timeout=15):
    """Fetch JSON from a URL through a random proxy if available."""
    req = Request(url, headers=HEADERS)
    handler = _get_proxy_handler()
    if handler:
        opener = urllib.request.build_opener(handler)
        with opener.open(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    else:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())


def _make_id(source, raw):
    """Deterministic signal ID from source + raw string."""
    h = hashlib.md5(f"{source}:{raw}".encode()).hexdigest()[:12]
    return f"{source}_{h}"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Source 1-4: Reddit subreddits
# ---------------------------------------------------------------------------


def _scrape_reddit(subreddit, sort="top", limit=25):
    """Scrape a single subreddit via Reddit's public JSON API."""
    # Use old.reddit.com which is less aggressive with blocking
    url = f"https://old.reddit.com/r/{subreddit}/{sort}.json?limit={limit}&t=day"
    data = _get_json(url)

    signals = []
    for child in data.get("data", {}).get("children", []):
        p = child.get("data", {})
        title = p.get("title", "")
        sig_id = _make_id(f"reddit_{subreddit}", title)

        # Basic sentiment hint from title
        title_lower = title.lower()
        neg = ["crash", "fall", "drop", "fear", "bear", "dump", "recession",
               "loss", "sell", "collapse", "ban", "scam", "risk"]
        pos = ["surge", "rise", "gain", "bull", "moon", "pump", "rally",
               "buy", "profit", "growth", "record", "breakthrough"]
        n = sum(1 for w in neg if w in title_lower)
        p_count = sum(1 for w in pos if w in title_lower)
        if n + p_count > 0:
            hint = "bearish" if n > p_count else ("bullish" if p_count > n else "mixed")
        else:
            hint = "neutral"

        signals.append({
            "id": sig_id,
            "source": f"reddit/r/{subreddit}",
            "title": title[:200],
            "score": p.get("score", 0),
            "comments": p.get("num_comments", 0),
            "sentiment_hint": hint,
            "timestamp": datetime.fromtimestamp(
                p.get("created_utc", 0), tz=timezone.utc
            ).isoformat(),
            "url": f"https://reddit.com{p.get('permalink', '')}",
        })
    return signals


def scrape_wsb():
    """Reddit r/wallstreetbets top posts."""
    return _scrape_reddit("wallstreetbets", sort="top")


def scrape_crypto():
    """Reddit r/cryptocurrency top posts."""
    return _scrape_reddit("cryptocurrency", sort="top")


def scrape_polymarket():
    """Reddit r/polymarket new posts."""
    return _scrape_reddit("polymarket", sort="new")


def scrape_economics():
    """Reddit r/economics top posts."""
    return _scrape_reddit("economics", sort="top")


# ---------------------------------------------------------------------------
# Source 5: CoinGecko top movers
# ---------------------------------------------------------------------------


def scrape_coingecko():
    """CoinGecko top movers by 24h price change (free, no key)."""
    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
        "&sparkline=false&price_change_percentage=24h"
    )
    data = _get_json(url)

    # Sort by absolute 24h change to get biggest movers
    movers = sorted(
        data,
        key=lambda c: abs(c.get("price_change_percentage_24h_in_currency", 0) or 0),
        reverse=True,
    )[:15]

    signals = []
    for coin in movers:
        name = coin.get("name", "Unknown")
        symbol = coin.get("symbol", "").upper()
        change = coin.get("price_change_percentage_24h_in_currency", 0) or 0
        price = coin.get("current_price", 0)
        sig_id = _make_id("coingecko", f"{symbol}_{datetime.now(timezone.utc).strftime('%Y%m%d')}")

        if change > 5:
            hint = "bullish"
        elif change < -5:
            hint = "bearish"
        elif change > 0:
            hint = "slightly_bullish"
        elif change < 0:
            hint = "slightly_bearish"
        else:
            hint = "neutral"

        signals.append({
            "id": sig_id,
            "source": "coingecko",
            "title": f"{name} ({symbol}) {change:+.1f}% | ${price:,.2f}",
            "score": int(abs(change) * 10),
            "comments": 0,
            "sentiment_hint": hint,
            "timestamp": _now_iso(),
            "url": f"https://www.coingecko.com/en/coins/{coin.get('id', '')}",
        })
    return signals


# ---------------------------------------------------------------------------
# Source 6: Crypto Fear & Greed Index
# ---------------------------------------------------------------------------


def scrape_fear_greed():
    """Alternative.me Crypto Fear & Greed Index (free, no key)."""
    url = "https://api.alternative.me/fng/?limit=1&format=json"
    data = _get_json(url)

    entries = data.get("data", [])
    if not entries:
        return []

    entry = entries[0]
    value = int(entry.get("value", 50))
    label = entry.get("value_classification", "Neutral")
    ts = int(entry.get("timestamp", 0))

    if value <= 25:
        hint = "extreme_fear"
    elif value <= 40:
        hint = "bearish"
    elif value <= 60:
        hint = "neutral"
    elif value <= 75:
        hint = "bullish"
    else:
        hint = "extreme_greed"

    sig_id = _make_id("fear_greed", f"{value}_{datetime.now(timezone.utc).strftime('%Y%m%d')}")

    return [{
        "id": sig_id,
        "source": "fear_greed_index",
        "title": f"Crypto Fear & Greed: {value} ({label})",
        "score": value,
        "comments": 0,
        "sentiment_hint": hint,
        "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else _now_iso(),
        "url": "https://alternative.me/crypto/fear-and-greed-index/",
    }]


# ---------------------------------------------------------------------------
# Source 7: Hacker News (top stories - always works, no auth)
# ---------------------------------------------------------------------------


def scrape_hackernews():
    """Hacker News top stories via Firebase API."""
    ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = _get_json(ids_url)[:15]

    signals = []
    for story_id in ids:
        try:
            story = _get_json(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            title = story.get("title", "")
            sig_id = _make_id("hackernews", str(story_id))
            signals.append({
                "id": sig_id,
                "source": "hackernews",
                "title": title,
                "score": story.get("score", 0),
                "comments": story.get("descendants", 0),
                "sentiment_hint": "neutral",
                "timestamp": datetime.fromtimestamp(story.get("time", 0), tz=timezone.utc).isoformat(),
                "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            })
        except Exception:
            continue
    return signals


# ---------------------------------------------------------------------------
# Source 8: Polymarket direct API (real money predictions)
# ---------------------------------------------------------------------------


def scrape_polymarket():
    """Polymarket active markets via gamma API."""
    url = "https://gamma-api.polymarket.com/markets?limit=20&active=true&closed=false"
    try:
        data = _get_json(url)
    except Exception:
        return []

    signals = []
    for market in data:
        question = market.get("question", "")
        sig_id = _make_id("polymarket", market.get("id", question))

        # Extract probability as sentiment
        outcomes = market.get("outcomePrices", [])
        prob = 0.5
        if outcomes and len(outcomes) > 0:
            try:
                prob = float(outcomes[0])
            except (ValueError, TypeError):
                prob = 0.5

        if prob > 0.7:
            hint = "high_probability"
        elif prob > 0.5:
            hint = "likely"
        elif prob > 0.3:
            hint = "uncertain"
        else:
            hint = "unlikely"

        signals.append({
            "id": sig_id,
            "source": "polymarket",
            "title": f"[{prob*100:.0f}%] {question}",
            "score": int(prob * 100),
            "comments": 0,
            "sentiment_hint": hint,
            "timestamp": _now_iso(),
            "url": f"https://polymarket.com/event/{market.get('slug', '')}",
        })
    return signals


# Reddit wrapper that gracefully skips if blocked
def scrape_reddit_safe(subreddit, sort="top"):
    """Try Reddit, return empty list if blocked."""
    try:
        return _scrape_reddit(subreddit, sort)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

SOURCES = [
    ("r/wallstreetbets", lambda: scrape_reddit_safe("wallstreetbets")),
    ("r/cryptocurrency", lambda: scrape_reddit_safe("CryptoCurrency")),
    ("r/economics", lambda: scrape_reddit_safe("economics")),
    ("Hacker News", scrape_hackernews),
    ("Polymarket", scrape_polymarket),
    ("CoinGecko", scrape_coingecko),
    ("Fear & Greed", scrape_fear_greed),
]


def load_existing():
    """Load existing signals from disk."""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_signals(signals):
    """Save signals to disk, keeping last 1000."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    trimmed = signals[-1000:]
    with open(OUTPUT_FILE, "w") as f:
        json.dump(trimmed, f, indent=2)


def run():
    """Run all scrapers, deduplicate, append to storage."""
    print("BIOS Social Scraper")
    print("=" * 40)

    existing = load_existing()
    seen_ids = {s["id"] for s in existing}
    all_new = []
    sources_ok = 0

    for name, fn in SOURCES:
        print(f"  [{name}] ", end="", flush=True)
        try:
            signals = fn()
            new = [s for s in signals if s["id"] not in seen_ids]
            for s in new:
                seen_ids.add(s["id"])
            all_new.extend(new)
            sources_ok += 1
            print(f"{len(signals)} fetched, {len(new)} new")
        except Exception as e:
            print(f"FAILED: {e}")

        # Rate limit between sources
        time.sleep(2)

    if all_new:
        combined = existing + all_new
        save_signals(combined)

    total = len(existing) + len(all_new)
    print()
    print(f"Scraped {len(all_new)} signals from {sources_ok} sources")
    print(f"Total in storage: {total}")
    return all_new


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    else:
        run()
