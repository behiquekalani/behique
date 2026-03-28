#!/usr/bin/env python3
"""
BIOS News Fetcher - Phase 2 perception pipeline.
Fetches news from multiple RSS feeds, deduplicates, tags, and stores.

Usage:
    python3 bios/ingestion/news_fetcher.py              # Fetch all sources
    python3 bios/ingestion/news_fetcher.py --source tech # Fetch one category
    python3 bios/ingestion/news_fetcher.py --digest      # Print latest digest
"""

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen, Request
from xml.etree import ElementTree

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# RSS feed sources grouped by category
FEEDS = {
    "markets": [
        ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
        ("CNBC Top News", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
        ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ],
    "crypto": [
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("CoinTelegraph", "https://cointelegraph.com/rss"),
    ],
    "tech": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ],
    "world": [
        ("Reuters World", "https://feeds.reuters.com/reuters/topNews"),
        ("AP News", "https://rsshub.app/apnews/topics/apf-topnews"),
    ],
    "pr_local": [
        ("Google News PR", "https://news.google.com/rss/search?q=puerto+rico&hl=en-US&gl=US&ceid=US:en"),
    ],
}

# Keywords for auto-tagging
TAG_RULES = {
    "oil": ["oil", "petroleum", "crude", "opec", "energy sector", "barrel"],
    "gold": ["gold", "precious metal", "safe haven"],
    "crypto": ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "defi"],
    "inflation": ["inflation", "cpi", "consumer price", "cost of living"],
    "fed": ["federal reserve", "fed rate", "interest rate", "fomc", "powell"],
    "geopolitics": ["war", "conflict", "invasion", "sanctions", "military", "troops"],
    "stimulus": ["stimulus", "relief", "aid package", "government spending", "infrastructure bill"],
    "ai": ["artificial intelligence", "ai ", "machine learning", "chatgpt", "llm", "openai", "anthropic"],
    "puerto_rico": ["puerto rico", "pr ", "isla", "colmena", "act 60", "fema"],
    "stocks": ["s&p", "nasdaq", "dow jones", "stock market", "wall street", "earnings"],
}

ASSET_MAP = {
    "oil": ["oil", "XLE", "USO"],
    "gold": ["gold", "GLD"],
    "crypto": ["BTC", "ETH"],
    "stocks": ["SPY", "QQQ"],
    "fed": ["USD", "bonds", "TLT"],
}

HEADERS = {
    "User-Agent": "BIOS/1.0 (Behike Intelligence System)"
}


def fetch_feed(name, url, timeout=15):
    """Fetch and parse a single RSS feed."""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            content = resp.read()
        root = ElementTree.fromstring(content)

        items = []
        # Handle both RSS and Atom feeds
        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate", "")
            items.append({
                "title": title,
                "url": link,
                "description": desc[:500],
                "pub_date": pub_date,
                "source": name,
            })

        # Atom format
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//atom:entry", ns) or root.findall(".//entry"):
                title = ""
                link = ""
                summary = ""
                t = entry.find("atom:title", ns) or entry.find("title")
                if t is not None:
                    title = (t.text or "").strip()
                l = entry.find("atom:link", ns) or entry.find("link")
                if l is not None:
                    link = l.get("href", "")
                s = entry.find("atom:summary", ns) or entry.find("summary") or entry.find("content")
                if s is not None:
                    summary = (s.text or "")[:500]
                items.append({
                    "title": title,
                    "url": link,
                    "description": summary,
                    "pub_date": "",
                    "source": name,
                })

        return items[:20]  # Max 20 per feed
    except Exception as e:
        print(f"  WARN: {name} fetch failed: {e}")
        return []


def auto_tag(text):
    """Tag a piece of text based on keyword rules."""
    text_lower = text.lower()
    tags = []
    assets = []
    for tag, keywords in TAG_RULES.items():
        for kw in keywords:
            if kw in text_lower:
                tags.append(tag)
                if tag in ASSET_MAP:
                    assets.extend(ASSET_MAP[tag])
                break
    return list(set(tags)), list(set(assets))


def basic_sentiment(text):
    """Very basic sentiment scoring. Will upgrade in Phase 4."""
    text_lower = text.lower()
    negative = ["crash", "fall", "drop", "fear", "crisis", "war", "conflict",
                "recession", "inflation", "layoff", "ban", "sanction", "risk",
                "threat", "collapse", "decline", "loss", "warn"]
    positive = ["surge", "rise", "gain", "growth", "rally", "boom", "record",
                "breakthrough", "innovation", "launch", "profit", "deal",
                "approval", "stimulus", "invest", "opportunity"]
    neg_count = sum(1 for w in negative if w in text_lower)
    pos_count = sum(1 for w in positive if w in text_lower)
    total = neg_count + pos_count
    if total == 0:
        return 0.0
    return round((pos_count - neg_count) / total, 2)


def make_signal(item, category):
    """Convert a feed item into a BIOS signal object."""
    text = f"{item['title']} {item['description']}"
    tags, assets = auto_tag(text)
    sentiment = basic_sentiment(text)

    # Generate unique ID from title
    sig_id = hashlib.md5(item["title"].encode()).hexdigest()[:12]

    return {
        "id": f"sig_{sig_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": item["source"],
        "category": category,
        "title": item["title"],
        "url": item["url"],
        "description": item["description"][:300],
        "tags": tags,
        "assets": assets,
        "sentiment": sentiment,
        "priority": len(tags) + abs(sentiment),
    }


def load_signals():
    """Load existing signals."""
    if SIGNALS_FILE.exists():
        try:
            with open(SIGNALS_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_signals(signals):
    """Save signals, keeping last 500."""
    signals = signals[-500:]
    with open(SIGNALS_FILE, "w") as f:
        json.dump(signals, f, indent=2)


def fetch_all(categories=None):
    """Fetch from all (or specified) feed categories."""
    existing = load_signals()
    existing_ids = {s["id"] for s in existing}
    new_signals = []

    sources = FEEDS if not categories else {k: v for k, v in FEEDS.items() if k in categories}

    for category, feeds in sources.items():
        print(f"  [{category}]")
        for name, url in feeds:
            items = fetch_feed(name, url)
            for item in items:
                signal = make_signal(item, category)
                if signal["id"] not in existing_ids:
                    new_signals.append(signal)
                    existing_ids.add(signal["id"])
            if items:
                print(f"    {name}: {len(items)} items")
            time.sleep(0.5)

    if new_signals:
        all_signals = existing + new_signals
        save_signals(all_signals)
        print(f"\n  {len(new_signals)} new signals stored. Total: {len(all_signals)}")
    else:
        print(f"\n  No new signals. Total: {len(existing)}")

    return new_signals


def print_digest(count=15):
    """Print latest signals as a digest."""
    signals = load_signals()
    if not signals:
        print("  No signals yet. Run without --digest first.")
        return

    # Sort by priority (highest first), then recency
    signals.sort(key=lambda s: (s.get("priority", 0), s.get("timestamp", "")), reverse=True)

    print(f"\n  BIOS INTELLIGENCE DIGEST")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("  " + "=" * 55)

    for s in signals[:count]:
        tags = ", ".join(s.get("tags", [])) or "untagged"
        assets = ", ".join(s.get("assets", [])) or "-"
        sent = s.get("sentiment", 0)
        sent_str = "+" if sent > 0 else ("-" if sent < 0 else "~")

        print(f"\n  [{s['source']}] {sent_str}")
        print(f"  {s['title'][:80]}")
        print(f"  Tags: {tags} | Assets: {assets}")

    print()


def main():
    if "--digest" in sys.argv:
        print_digest()
    elif "--source" in sys.argv:
        idx = sys.argv.index("--source")
        if idx + 1 < len(sys.argv):
            cat = sys.argv[idx + 1]
            fetch_all(categories=[cat])
        else:
            print("Usage: --source CATEGORY")
    else:
        print("  BIOS News Fetcher starting...")
        fetch_all()


if __name__ == "__main__":
    main()
