#!/usr/bin/env python3
"""
BIOS Puerto Rico Local Intelligence Scraper.
Scrapes PR-specific news from free RSS sources.

Usage:
    python3 bios/ingestion/pr_scraper.py --run
"""

import argparse
import hashlib
import json
import os
import re
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
SIGNALS_FILE = STORAGE_DIR / "pr_signals.json"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIGNALS = 200
DELAY_BETWEEN_SOURCES = 2
USER_AGENT = "BIOS/2.0 (Behike Intelligence System - PR Module)"

# --- Sources ---

RSS_SOURCES = {
    "fortaleza": "https://www.fortaleza.pr.gov/blog/feed/",
    "elnuevodia": "https://www.elnuevodia.com/arc/outboundfeeds/rss/",
    "googlenews_pr": "https://news.google.com/rss/search?q=puerto+rico&hl=en-US&gl=US&ceid=US:en",
}

# --- Category detection ---

CATEGORY_KEYWORDS = {
    "Government": [
        "governor", "gobernador", "legislat", "senate", "senado", "law", "ley",
        "fortaleza", "gobierno", "executive", "bill", "municipal", "alcald",
        "fema", "federal", "oversight", "fiscal", "junta", "promesa",
    ],
    "Economy": [
        "econom", "tax", "impuesto", "gdp", "pib", "inflation", "employ",
        "unemployment", "desempleo", "business", "market", "trade", "invest",
        "bond", "debt", "deuda", "wage", "salary", "crypto", "bank",
    ],
    "Weather": [
        "hurricane", "huracan", "storm", "tormenta", "flood", "inundacion",
        "weather", "clima", "tropical", "earthquake", "terremoto", "tsunami",
        "rain", "lluvia", "wind", "viento", "drought", "sequia",
    ],
    "Infrastructure": [
        "power", "energia", "luma", "aqueduct", "acueducto", "water", "agua",
        "road", "carretera", "bridge", "puente", "airport", "aeropuerto",
        "port", "puerto", "grid", "electric", "blackout", "apagon",
        "construction", "transit", "transport",
    ],
    "Business": [
        "startup", "company", "empresa", "retail", "tourism", "turismo",
        "hotel", "restaurant", "pharma", "manufacturing", "tech", "amazon",
        "walmart", "costco", "store", "shop", "commerce", "export",
    ],
}

# --- Sentiment keywords ---

POSITIVE_WORDS = [
    "growth", "recovery", "invest", "approval", "launch", "deal", "upgrade",
    "record", "improve", "boost", "gain", "progress", "success", "fund",
    "crecimiento", "mejora", "exito", "avance",
]

NEGATIVE_WORDS = [
    "crisis", "collapse", "threat", "warning", "damage", "loss", "decline",
    "blackout", "flood", "hurricane", "layoff", "debt", "default", "ban",
    "crisis", "colapso", "amenaza", "dano", "perdida",
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
    """Scan title for positive/negative keywords."""
    lower = title.lower()
    for word in POSITIVE_WORDS:
        if word in lower:
            return "positive"
    for word in NEGATIVE_WORDS:
        if word in lower:
            return "negative"
    return "neutral"


def categorize(title, description=""):
    """Assign a category based on keyword matching."""
    text = f"{title} {description}".lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return "General"


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


def strip_html(text):
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def scrape_rss(source_name, url, session):
    """Scrape a single RSS feed using feedparser."""
    signals = []
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        for entry in feed.entries[:30]:
            title = getattr(entry, "title", "").strip()
            if not title:
                continue
            link = getattr(entry, "link", "").strip()
            description = ""
            if hasattr(entry, "summary"):
                description = strip_html(entry.summary[:500])
            elif hasattr(entry, "description"):
                description = strip_html(entry.description[:500])

            signals.append({
                "id": make_id(source_name, title),
                "source": source_name,
                "title": title,
                "url": link,
                "timestamp": parse_timestamp(entry),
                "description": description,
                "sentiment_hint": sentiment_hint(title),
                "category": categorize(title, description),
            })
    except Exception as e:
        print(f"  WARN: {source_name} failed: {e}")

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
    print("BIOS PR Intelligence Scraper starting...")
    session = get_session()
    existing = load_signals()
    existing_ids = {s["id"] for s in existing}
    all_new = []
    sources_hit = 0

    for source_name, url in RSS_SOURCES.items():
        signals = scrape_rss(source_name, url, session)
        new = [s for s in signals if s["id"] not in existing_ids]
        for s in new:
            existing_ids.add(s["id"])
        all_new.extend(new)
        if signals:
            sources_hit += 1
            print(f"  {source_name}: {len(signals)} fetched, {len(new)} new")
        else:
            print(f"  {source_name}: no entries (feed may be unavailable)")
        time.sleep(DELAY_BETWEEN_SOURCES)

    # Merge and save
    merged = existing + all_new
    total = save_signals(merged)

    # Category breakdown
    cats = {}
    for s in all_new:
        cat = s.get("category", "General")
        cats[cat] = cats.get(cat, 0) + 1

    print(f"\nScraped {len(all_new)} new PR signals from {sources_hit} sources")
    if cats:
        print("Categories: " + ", ".join(f"{k}={v}" for k, v in sorted(cats.items())))
    print(f"Total signals in store: {total}")


def main():
    parser = argparse.ArgumentParser(description="BIOS PR Intelligence Scraper")
    parser.add_argument("--run", action="store_true", help="Run the scraper")
    args = parser.parse_args()

    if args.run:
        run()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
