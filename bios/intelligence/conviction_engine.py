#!/usr/bin/env python3
"""
BIOS Conviction Score Engine v1
Reads news + social signals, produces conviction scores (0-100) per topic.

Scoring layers:
  - Velocity  (30%): mention growth rate (last 6h vs previous 6h)
  - Sentiment (25%): average sentiment normalized to 0-100
  - Volume    (25%): total mention count across all sources
  - Diversity (20%): number of distinct sources mentioning the topic

Usage:
    python3 bios/intelligence/conviction_engine.py --run       # Cron mode, write convictions.json
    python3 bios/intelligence/conviction_engine.py --digest    # Human-readable output
    python3 bios/intelligence/conviction_engine.py             # Default: run + digest
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
SOCIAL_SIGNALS_FILE = STORAGE_DIR / "social_signals.json"
OUTPUT_FILE = STORAGE_DIR / "convictions.json"

# ---------------------------------------------------------------------------
# Topic keyword map
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS = {
    "oil":          ["oil", "petroleum", "crude", "opec", "brent", "wti"],
    "crypto":       ["crypto", "cryptocurrency", "blockchain", "defi"],
    "btc":          ["btc", "bitcoin"],
    "eth":          ["eth", "ethereum"],
    "gold":         ["gold", "xau"],
    "stocks":       ["stocks", "stock market", "s&p", "sp500", "nasdaq", "dow jones", "equities"],
    "fed":          ["fed", "federal reserve", "fomc", "interest rate", "rate hike", "rate cut", "powell"],
    "inflation":    ["inflation", "cpi", "consumer price"],
    "war":          ["war", "conflict", "military", "invasion", "missile", "troops", "iran", "geopolit"],
    "puerto_rico":  ["puerto rico", "pr ", "isla", "fema", "luma"],
    "polymarket":   ["polymarket", "prediction market"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> list:
    """Load a JSON file. Return empty list if missing or malformed."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def parse_ts(ts_str: str) -> datetime:
    """Parse an ISO timestamp string into a timezone-aware datetime."""
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def match_topics(text: str) -> list[str]:
    """Return all topics that match keywords in the given text."""
    text_lower = text.lower()
    matched = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched.append(topic)
                break
    return matched


def extract_source(signal: dict) -> str:
    """Pull a normalized source name from a signal dict."""
    src = signal.get("source", "unknown")
    # Normalize reddit subreddits to just "reddit"
    if src.startswith("r/"):
        return "reddit"
    return src.lower().strip()

# ---------------------------------------------------------------------------
# Scoring layers
# ---------------------------------------------------------------------------

def score_velocity(recent_count: int, previous_count: int) -> float:
    """
    Velocity: how fast mentions are growing.
    recent_count  = signals in last 6 hours
    previous_count = signals in 6-12 hours ago window
    Returns 0-100.
    """
    if previous_count == 0 and recent_count == 0:
        return 0.0
    if previous_count == 0:
        # New topic appearing out of nowhere, high velocity
        return min(100.0, recent_count * 20.0)
    ratio = recent_count / previous_count
    # ratio=1 means flat (50), ratio=2 means doubling (80), ratio=0.5 means declining (25)
    score = 50.0 * ratio
    return max(0.0, min(100.0, score))


def score_sentiment(sentiments: list[float]) -> float:
    """
    Average sentiment from -1..1 mapped to 0..100.
    -1 = 0, 0 = 50, 1 = 100.
    Strong negative sentiment also creates conviction (actionable fear).
    We use absolute distance from neutral as a signal strength multiplier.
    """
    if not sentiments:
        return 50.0  # neutral default
    avg = sum(sentiments) / len(sentiments)
    # Map -1..1 to 0..100
    base = (avg + 1.0) * 50.0
    # Amplify extremes: strong negative or positive both raise conviction
    intensity = abs(avg)
    # Blend: 60% directional + 40% intensity
    return max(0.0, min(100.0, base * 0.6 + intensity * 100.0 * 0.4))


def score_volume(count: int, max_count: int) -> float:
    """
    Volume: total mentions as percentage of max across all topics.
    Returns 0-100.
    """
    if max_count == 0:
        return 0.0
    return min(100.0, (count / max_count) * 100.0)


def score_diversity(source_count: int, max_sources: int) -> float:
    """
    Cross-source diversity: how many different sources mention this topic.
    Returns 0-100.
    """
    if max_sources == 0:
        return 0.0
    return min(100.0, (source_count / max(max_sources, 1)) * 100.0)

# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

def build_convictions() -> dict:
    """Run the full conviction scoring pipeline."""
    now = datetime.now(timezone.utc)
    cutoff_6h = now - timedelta(hours=6)
    cutoff_12h = now - timedelta(hours=12)

    # Load both signal sources
    news_signals = load_json(SIGNALS_FILE)
    social_signals = load_json(SOCIAL_SIGNALS_FILE)
    all_signals = news_signals + social_signals

    if not all_signals:
        return {
            "generated_at": now.isoformat(),
            "signal_count": 0,
            "convictions": [],
        }

    # ---------------------------------------------------------------------------
    # Bucket signals by topic
    # ---------------------------------------------------------------------------
    topic_data = defaultdict(lambda: {
        "recent": [],      # last 6h
        "previous": [],    # 6-12h ago
        "all": [],         # everything
        "sentiments": [],
        "sources": set(),
    })

    for sig in all_signals:
        title = sig.get("title", "") + " " + sig.get("description", "")
        ts = parse_ts(sig.get("timestamp", ""))
        sentiment = sig.get("sentiment", 0.0)
        source = extract_source(sig)

        # Also check tags and assets fields
        tag_text = " ".join(sig.get("tags", []) + sig.get("assets", []))
        full_text = title + " " + tag_text

        topics = match_topics(full_text)
        for topic in topics:
            bucket = topic_data[topic]
            bucket["all"].append(sig)
            bucket["sentiments"].append(sentiment)
            bucket["sources"].add(source)

            if ts >= cutoff_6h:
                bucket["recent"].append(sig)
            elif ts >= cutoff_12h:
                bucket["previous"].append(sig)

    if not topic_data:
        return {
            "generated_at": now.isoformat(),
            "signal_count": len(all_signals),
            "convictions": [],
        }

    # ---------------------------------------------------------------------------
    # Calculate max values for normalization
    # ---------------------------------------------------------------------------
    max_volume = max(len(d["all"]) for d in topic_data.values())
    max_sources = max(len(d["sources"]) for d in topic_data.values())

    # ---------------------------------------------------------------------------
    # Score each topic
    # ---------------------------------------------------------------------------
    convictions = []

    for topic, data in topic_data.items():
        velocity = score_velocity(len(data["recent"]), len(data["previous"]))
        sentiment = score_sentiment(data["sentiments"])
        volume = score_volume(len(data["all"]), max_volume)
        diversity = score_diversity(len(data["sources"]), max_sources)

        # Master conviction score (weighted)
        master = (
            velocity  * 0.30 +
            sentiment * 0.25 +
            volume    * 0.25 +
            diversity * 0.20
        )
        master = round(master, 1)

        # Classify
        if master >= 75:
            level = "HIGH"
        elif master >= 50:
            level = "MEDIUM"
        else:
            level = "LOW"

        convictions.append({
            "topic": topic,
            "score": master,
            "level": level,
            "velocity": round(velocity, 1),
            "sentiment": round(sentiment, 1),
            "volume": round(volume, 1),
            "diversity": round(diversity, 1),
            "sources": sorted(data["sources"]),
            "signal_count": len(data["all"]),
        })

    # Sort by score descending
    convictions.sort(key=lambda x: x["score"], reverse=True)

    return {
        "generated_at": now.isoformat(),
        "signal_count": len(all_signals),
        "topics_detected": len(convictions),
        "convictions": convictions,
    }


def print_digest(result: dict):
    """Print a human-readable conviction digest."""
    print("=" * 60)
    print("  BIOS CONVICTION SCORE DIGEST")
    print(f"  Generated: {result['generated_at'][:19]}")
    print(f"  Signals analyzed: {result['signal_count']}")
    print(f"  Topics detected: {result.get('topics_detected', 0)}")
    print("=" * 60)

    if not result["convictions"]:
        print("\n  No topics detected. Check signal files.\n")
        return

    # Group by level
    for level_name in ["HIGH", "MEDIUM", "LOW"]:
        items = [c for c in result["convictions"] if c["level"] == level_name]
        if not items:
            continue

        label = {
            "HIGH": "[!!] HIGH CONVICTION (actionable)",
            "MEDIUM": "[--] MEDIUM (monitor)",
            "LOW": "[  ] LOW (background noise)",
        }[level_name]

        print(f"\n  {label}")
        print("  " + "-" * 50)

        for c in items:
            print(f"    {c['topic'].upper():15s}  score={c['score']:5.1f}  "
                  f"vel={c['velocity']:5.1f}  sent={c['sentiment']:5.1f}  "
                  f"vol={c['volume']:5.1f}  div={c['diversity']:5.1f}")
            print(f"    {'':15s}  signals={c['signal_count']}  "
                  f"sources=[{', '.join(c['sources'])}]")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    flags = set(sys.argv[1:])
    do_run = "--run" in flags
    do_digest = "--digest" in flags

    # Default: do both if no flags
    if not do_run and not do_digest:
        do_run = True
        do_digest = True

    result = build_convictions()

    if do_run:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(json.dumps(result, indent=2))
        print(f"[conviction_engine] Wrote {len(result['convictions'])} convictions "
              f"to {OUTPUT_FILE}")

    if do_digest:
        print_digest(result)


if __name__ == "__main__":
    main()
