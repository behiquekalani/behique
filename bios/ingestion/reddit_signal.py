#!/usr/bin/env python3
"""
BIOS Reddit Signal Tracker - Phase 3 social intelligence.
Scrapes Reddit for market signals, sentiment, and emerging narratives.
Uses Reddit's public JSON API (no auth needed).

Usage:
    python3 bios/ingestion/reddit_signal.py              # Fetch all subs
    python3 bios/ingestion/reddit_signal.py --sub crypto  # One category
    python3 bios/ingestion/reddit_signal.py --digest      # Show top signals
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
REDDIT_FILE = STORAGE_DIR / "reddit_raw.json"

SUBREDDITS = {
    "markets": ["wallstreetbets", "investing", "stocks", "economics"],
    "crypto": ["cryptocurrency", "bitcoin", "ethtrader", "polymarket"],
    "ai": ["artificial", "MachineLearning", "LocalLLaMA", "ClaudeAI"],
    "business": ["Entrepreneur", "smallbusiness", "SaaS", "startups"],
    "pr": ["PuertoRico"],
}

TAG_RULES = {
    "oil": ["oil", "petroleum", "crude", "opec", "energy"],
    "gold": ["gold", "precious metal"],
    "crypto": ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "sol"],
    "inflation": ["inflation", "cpi", "consumer price"],
    "fed": ["federal reserve", "fed rate", "interest rate", "fomc"],
    "geopolitics": ["war", "conflict", "invasion", "sanctions", "military"],
    "stimulus": ["stimulus", "relief", "aid package"],
    "ai": ["artificial intelligence", " ai ", "machine learning", "llm", "openai"],
    "stocks": ["s&p", "nasdaq", "dow", "stock market", "earnings"],
    "polymarket": ["polymarket", "prediction market", "kalshi"],
    "puerto_rico": ["puerto rico", "colmena", "act 60"],
}

HEADERS = {
    "User-Agent": "BIOS/1.0 (Behike Intelligence System; research)"
}


def fetch_subreddit(name, limit=25):
    """Fetch hot posts from a subreddit."""
    try:
        url = f"https://www.reddit.com/r/{name}/hot.json?limit={limit}"
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())

        posts = []
        for child in data.get("data", {}).get("children", []):
            p = child.get("data", {})
            posts.append({
                "title": p.get("title", ""),
                "selftext": (p.get("selftext", "") or "")[:500],
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "created_utc": p.get("created_utc", 0),
                "subreddit": name,
                "author": p.get("author", ""),
                "upvote_ratio": p.get("upvote_ratio", 0),
            })
        return posts
    except Exception as e:
        print(f"    WARN: r/{name} failed: {e}")
        return []


def auto_tag(text):
    """Tag text based on keywords."""
    text_lower = text.lower()
    tags = []
    for tag, keywords in TAG_RULES.items():
        for kw in keywords:
            if kw in text_lower:
                tags.append(tag)
                break
    return list(set(tags))


def basic_sentiment(text):
    """Basic sentiment score."""
    text_lower = text.lower()
    neg = ["crash", "fall", "drop", "fear", "crisis", "bear", "dump", "scam",
           "recession", "ban", "risk", "collapse", "loss", "sell", "short"]
    pos = ["surge", "rise", "gain", "bull", "moon", "pump", "rally", "record",
           "breakthrough", "buy", "long", "profit", "opportunity", "growth"]
    n = sum(1 for w in neg if w in text_lower)
    p = sum(1 for w in pos if w in text_lower)
    total = n + p
    if total == 0:
        return 0.0
    return round((p - n) / total, 2)


def engagement_score(post):
    """Score based on engagement velocity."""
    age_hours = max(1, (time.time() - post.get("created_utc", time.time())) / 3600)
    score = post.get("score", 0)
    comments = post.get("num_comments", 0)
    return round((score + comments * 2) / age_hours, 1)


def post_to_signal(post, category):
    """Convert Reddit post to BIOS signal."""
    text = f"{post['title']} {post['selftext']}"
    tags = auto_tag(text)
    sentiment = basic_sentiment(text)
    eng = engagement_score(post)
    sig_id = hashlib.md5(post["title"].encode()).hexdigest()[:12]

    return {
        "id": f"reddit_{sig_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": f"r/{post['subreddit']}",
        "category": category,
        "title": post["title"][:120],
        "url": post["url"],
        "description": post["selftext"][:200] if post["selftext"] else "",
        "tags": tags,
        "assets": [],
        "sentiment": sentiment,
        "priority": round(eng / 100, 2) + len(tags) * 0.5,
        "engagement": eng,
        "score": post["score"],
        "comments": post["num_comments"],
        "author": post["author"],
    }


def load_signals():
    if SIGNALS_FILE.exists():
        try:
            with open(SIGNALS_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_signals(signals):
    signals = signals[-500:]
    with open(SIGNALS_FILE, "w") as f:
        json.dump(signals, f, indent=2)


def fetch_all(categories=None):
    """Fetch from all or specified subreddit categories."""
    existing = load_signals()
    existing_ids = {s["id"] for s in existing}
    new_signals = []
    all_posts = []

    cats = categories or list(SUBREDDITS.keys())

    for cat in cats:
        subs = SUBREDDITS.get(cat, [])
        print(f"  [{cat}]")
        for sub in subs:
            posts = fetch_subreddit(sub)
            all_posts.extend(posts)
            new_in_sub = 0
            for post in posts:
                signal = post_to_signal(post, cat)
                if signal["id"] not in existing_ids:
                    new_signals.append(signal)
                    existing_ids.add(signal["id"])
                    new_in_sub += 1
            print(f"    r/{sub}: {len(posts)} posts, {new_in_sub} new signals")
            time.sleep(2)  # Rate limiting

    # Save raw data
    with open(REDDIT_FILE, "w") as f:
        json.dump({"posts": all_posts, "fetched_at": datetime.now(timezone.utc).isoformat()}, f)

    if new_signals:
        all_sigs = existing + new_signals
        save_signals(all_sigs)
        print(f"\n  {len(new_signals)} new signals. Total: {len(all_sigs)}")
    else:
        print(f"\n  No new signals. Total: {len(existing)}")

    return new_signals


def print_digest(count=15):
    """Print top Reddit signals."""
    signals = load_signals()
    reddit_sigs = [s for s in signals if s.get("source", "").startswith("r/")]
    if not reddit_sigs:
        print("  No Reddit signals yet.")
        return

    reddit_sigs.sort(key=lambda s: s.get("priority", 0), reverse=True)

    print(f"\n  REDDIT SIGNAL DIGEST")
    print("  " + "=" * 55)

    for s in reddit_sigs[:count]:
        tags = ", ".join(s.get("tags", [])) or "untagged"
        eng = s.get("engagement", 0)
        sent = s.get("sentiment", 0)
        arrow = "+" if sent > 0 else ("-" if sent < 0 else "~")

        print(f"\n  [{s['source']}] {arrow} eng:{eng:.0f}")
        print(f"  {s['title'][:75]}")
        print(f"  Tags: {tags} | Score: {s.get('score', 0)} | Comments: {s.get('comments', 0)}")


def main():
    if "--digest" in sys.argv:
        print_digest()
    elif "--sub" in sys.argv:
        idx = sys.argv.index("--sub")
        if idx + 1 < len(sys.argv):
            fetch_all(categories=[sys.argv[idx + 1]])
    else:
        print("  BIOS Reddit Signal Tracker...")
        fetch_all()


if __name__ == "__main__":
    main()
