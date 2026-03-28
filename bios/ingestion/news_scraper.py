#!/usr/bin/env python3
"""
BIOS News Scraper - Financial and general news from free sources.
No API keys needed. Uses RSS/JSON feeds only.

Usage:
    python3 bios/ingestion/news_scraper.py --run
"""

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: pip install feedparser")
    raise SystemExit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    raise SystemExit(1)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIGNALS = 500
DELAY_BETWEEN_SOURCES = 2
USER_AGENT = "BIOS/2.0 (Behike Intelligence System)"

# --- Sources ---

RSS_SOURCES = {
    "reuters": "https://www.reutersagency.com/feed/",
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "marketwatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "googlenews": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
}

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_MAX_ITEMS = 15

# --- Sentiment keywords ---

BULLISH_WORDS = [
    "surge", "soar", "rally", "gain", "rise", "jump", "record", "boom",
    "breakthrough", "profit", "bull", "growth", "recovery", "optimism",
    "approval", "launch", "deal", "invest", "opportunity", "upgrade",
]

BEARISH_WORDS = [
    "crash", "plunge", "drop", "fall", "decline", "loss", "bear", "fear",
    "recession", "crisis", "war", "layoff", "ban", "sanction", "risk",
    "threat", "collapse", "warning", "downturn", "sell-off", "default",
]


def get_session():
    """Build a requests session with optional proxy."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    proxy_url = os.environ.get("PROXY_URL")
    if proxy_url:
        session.proxies = {"http": proxy_url, "https": proxy_url}
    return session


def make_id(source, title):
    """MD5 hash of source + title."""
    raw = f"{source}:{title}".encode("utf-8")
    return hashlib.md5(raw).hexdigest()


def sentiment_hint(title):
    """Scan title for bullish/bearish keywords."""
    lower = title.lower()
    for word in BULLISH_WORDS:
        if word in lower:
            return "bullish"
    for word in BEARISH_WORDS:
        if word in lower:
            return "bearish"
    return "neutral"


def parse_timestamp(entry):
    """Try to extract an ISO timestamp from a feedparser entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            pass
    return datetime.now(timezone.utc).isoformat()


def scrape_rss(source_name, url, session):
    """Scrape a single RSS feed using feedparser."""
    signals = []
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        for entry in feed.entries[:25]:
            title = getattr(entry, "title", "").strip()
            if not title:
                continue
            link = getattr(entry, "link", "").strip()
            description = ""
            if hasattr(entry, "summary"):
                description = entry.summary[:500].strip()
            elif hasattr(entry, "description"):
                description = entry.description[:500].strip()

            signals.append({
                "id": make_id(source_name, title),
                "source": source_name,
                "title": title,
                "url": link,
                "timestamp": parse_timestamp(entry),
                "description": description,
                "sentiment_hint": sentiment_hint(title),
            })
    except Exception as e:
        print(f"  WARN: {source_name} failed: {e}")

    return signals


def scrape_hackernews(session):
    """Scrape top stories from Hacker News JSON API."""
    signals = []
    try:
        resp = session.get(HN_TOP_URL, timeout=15)
        resp.raise_for_status()
        story_ids = resp.json()[:HN_MAX_ITEMS]

        for sid in story_ids:
            try:
                item_resp = session.get(HN_ITEM_URL.format(sid), timeout=10)
                item_resp.raise_for_status()
                item = item_resp.json()
                if not item or item.get("type") != "story":
                    continue

                title = item.get("title", "").strip()
                if not title:
                    continue

                url = item.get("url", f"https://news.ycombinator.com/item?id={sid}")
                ts = datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc).isoformat()

                signals.append({
                    "id": make_id("hackernews", title),
                    "source": "hackernews",
                    "title": title,
                    "url": url,
                    "timestamp": ts,
                    "description": "",
                    "sentiment_hint": sentiment_hint(title),
                })
            except Exception:
                continue

    except Exception as e:
        print(f"  WARN: hackernews failed: {e}")

    return signals


def load_signals():
    """Load existing signals from disk."""
    if SIGNALS_FILE.exists():
        try:
            with open(SIGNALS_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_signals(signals):
    """Save signals, keeping last MAX_SIGNALS, deduplicated by id."""
    seen = set()
    deduped = []
    for s in reversed(signals):
        if s["id"] not in seen:
            seen.add(s["id"])
            deduped.append(s)
    deduped.reverse()
    deduped = deduped[-MAX_SIGNALS:]
    with open(SIGNALS_FILE, "w") as f:
        json.dump(deduped, f, indent=2)
    return len(deduped)


def run():
    """Main scrape run."""
    print("BIOS News Scraper starting...")
    session = get_session()
    existing = load_signals()
    existing_ids = {s["id"] for s in existing}
    all_new = []
    sources_hit = 0

    # RSS sources
    for source_name, url in RSS_SOURCES.items():
        signals = scrape_rss(source_name, url, session)
        new = [s for s in signals if s["id"] not in existing_ids]
        for s in new:
            existing_ids.add(s["id"])
        all_new.extend(new)
        if signals:
            sources_hit += 1
            print(f"  {source_name}: {len(signals)} fetched, {len(new)} new")
        time.sleep(DELAY_BETWEEN_SOURCES)

    # Hacker News
    signals = scrape_hackernews(session)
    new = [s for s in signals if s["id"] not in existing_ids]
    for s in new:
        existing_ids.add(s["id"])
    all_new.extend(new)
    if signals:
        sources_hit += 1
        print(f"  hackernews: {len(signals)} fetched, {len(new)} new")

    # Merge and save
    merged = existing + all_new
    total = save_signals(merged)
    print(f"\nScraped {len(all_new)} signals from {sources_hit} sources")
    print(f"Total signals in store: {total}")


def main():
    parser = argparse.ArgumentParser(description="BIOS News Scraper")
    parser.add_argument("--run", action="store_true", help="Run the scraper")
    args = parser.parse_args()

    if args.run:
        run()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
