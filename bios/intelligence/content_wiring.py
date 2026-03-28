#!/usr/bin/env python3
"""
BIOS Content Wiring Engine -- Reactive content matching.
Connects the intelligence layer (signals.json) to the content library.

Reads trending signals, scans the content empire for keyword matches,
scores relevance, and outputs a reactive_queue.json with actionable
publish recommendations.

Usage:
    python3 bios/intelligence/content_wiring.py              # Generate reactive queue
    python3 bios/intelligence/content_wiring.py --digest      # Print what to post today
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
QUEUE_FILE = STORAGE_DIR / "reactive_queue.json"
CONTENT_DIR = BASE_DIR / "Ceiba" / "projects" / "content-empire"

# ---------------------------------------------------------------------------
# Platform detection -- checks full relative path, not just filename
# ---------------------------------------------------------------------------

PLATFORM_RULES = [
    ("instagram-es/", "instagram"),
    ("instagram-content-batch", "instagram"),
    ("instagram-opb-batch", "instagram"),
    ("twitter-en/", "twitter"),
    ("twitter-es/", "twitter"),
    ("twitter-threads", "twitter"),
    ("twitter-batch", "twitter"),
    ("youtube-scripts/", "youtube"),
    ("youtube-scripts-batch", "youtube"),
    ("youtube-shorts-en/", "youtube"),
    ("youtube-shorts-en-batch", "youtube"),
    ("youtube-shorts-es/", "youtube"),
    ("tiktok-en/", "tiktok"),
    ("tiktok-es/", "tiktok"),
    ("tiktok-batch", "tiktok"),
    ("tiktok-scripts-batch", "tiktok"),
    ("newsletter-en/", "newsletter"),
    ("newsletter-es/", "newsletter"),
    ("newsletter-issues", "newsletter"),
    ("blog-posts-batch", "blog"),
    ("linkedin-en/", "linkedin"),
    ("linkedin-es/", "linkedin"),
    ("linkedin-batch", "linkedin"),
    ("linkedin-content-batch", "linkedin"),
    ("pinterest/", "pinterest"),
    ("pinterest-batch", "pinterest"),
]

# ---------------------------------------------------------------------------
# Topic keyword maps -- tighter, more specific keywords per topic
# Generic words like "market", "business" are deliberately excluded from
# topics where they would match too broadly.
# ---------------------------------------------------------------------------

TOPIC_KEYWORDS = {
    "ai": [
        "artificial intelligence", "machine learning", "llm", "gpt",
        "claude", "openai", "chatbot", "deep learning", "neural network",
        "transformer", "ollama", "langchain", "whisper", "midjourney",
        "generative ai", "fine-tune", "rag", "embeddings", "prompt engineering",
        "ai agent", "ai tool", "ai automation",
    ],
    "crypto": [
        "bitcoin", "btc", "ethereum", "eth", "blockchain", "defi", "nft",
        "web3", "token", "crypto wallet", "mining", "staking", "altcoin",
        "solana", "binance", "cryptocurrency",
    ],
    "markets": [
        "stock market", "investing", "portfolio", "trading", "bull market",
        "bear market", "earnings", "dividend", "s&p 500", "nasdaq", "dow jones",
        "recession", "rally", "wall street", "index fund", "etf",
    ],
    "business": [
        "startup", "entrepreneur", "revenue", "saas", "side hustle",
        "freelance", "agency", "pricing strategy", "b2b", "roi",
        "monetize", "gumroad", "shopify", "ecommerce", "dropship",
    ],
    "tech": [
        "open source", "github", "deploy", "server", "cloud", "vps",
        "docker", "linux", "python", "javascript", "react", "api",
    ],
    "prediction_market": [
        "polymarket", "prediction market", "betting odds", "forecast",
    ],
    "geopolitics": [
        "geopolitical", "war", "conflict", "sanction", "tariff",
        "trade war", "nato",
    ],
    "inflation": [
        "inflation", "cpi", "cost of living", "purchasing power",
        "monetary policy",
    ],
    "oil": [
        "oil price", "petroleum", "crude oil", "opec", "energy crisis",
    ],
    "gold": [
        "gold price", "precious metal", "safe haven",
    ],
    "stocks": [
        "stock pick", "equity", "share price", "stock trading",
    ],
    "fed": [
        "federal reserve", "interest rate", "rate cut", "rate hike", "powell",
    ],
    "polymarket": [
        "polymarket", "prediction market",
    ],
    "puerto_rico": [
        "puerto rico", "boricua", "caribbean island",
    ],
    "pr": [
        "puerto rico", "boricua",
    ],
    "pr_local": [
        "puerto rico", "boricua", "local business",
    ],
}

# Stopwords for keyword extraction
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "this", "that", "are",
    "was", "be", "has", "had", "have", "not", "no", "can", "will", "do",
    "if", "my", "your", "you", "we", "our", "they", "them", "their",
    "he", "she", "his", "her", "so", "as", "up", "out", "all", "just",
    "how", "what", "when", "why", "who", "which", "where", "than",
    "more", "most", "about", "into", "over", "also", "one", "two",
    "here", "there", "then", "now", "very", "too", "each", "every",
    "some", "any", "been", "being", "would", "could", "should", "does",
    "did", "get", "got", "going", "make", "like", "know", "think",
    "still", "even", "much", "many", "few", "new", "old", "first",
    "last", "only", "own", "same", "other", "way", "day", "use",
    "used", "using", "don", "want", "need", "re", "ve", "ll", "s", "t",
    "m", "d", "i", "me", "slide", "post", "content", "batch", "hook",
    "body", "cta", "script", "caption", "thread", "issue", "pin",
    "follow", "save", "comment", "share", "type", "goal", "cover",
    "text", "image", "video", "reel", "carousel", "single", "bold",
    "dark", "background", "face", "corner", "people", "thing", "things",
}


# ---------------------------------------------------------------------------
# Content scanner
# ---------------------------------------------------------------------------

def detect_platform(rel_path: str) -> str:
    """Detect platform from the full relative path."""
    path_lower = rel_path.lower()
    for substring, platform in PLATFORM_RULES:
        if substring in path_lower:
            return platform
    return "unknown"


def extract_title(text: str, filename: str) -> str:
    """Pull the first meaningful heading or post title from a content file."""
    for line in text.split("\n")[:40]:
        line = line.strip()
        if not line:
            continue
        # Skip generic batch headers
        if line.startswith("# ") and "batch" not in line.lower() and "lote" not in line.lower():
            return line.lstrip("# ").strip()[:80]
        if "**HOOK:**" in line or "**Hook:**" in line:
            part = line.split(":**", 1)
            if len(part) > 1:
                return part[1].strip().strip('"').strip("'")[:80]
        if line.startswith("## THREAD") or line.startswith("## POST") or line.startswith("## TikTok"):
            # Try to get the title portion after the colon
            if ":" in line:
                return line.split(":", 1)[1].strip()[:80]
    return Path(filename).stem.replace("-", " ").title()[:80]


def build_text_index(text: str) -> str:
    """Lowercase, clean text for keyword searching."""
    text_lower = text.lower()
    text_clean = re.sub(r"https?://\S+", " ", text_lower)
    text_clean = re.sub(r"[#*\[\](){}|`>_~\-]", " ", text_clean)
    # Collapse whitespace
    text_clean = re.sub(r"\s+", " ", text_clean)
    return text_clean


def scan_content_library() -> list:
    """Scan all content files and build an index."""
    content_index = []

    if not CONTENT_DIR.exists():
        print(f"[ERROR] Content directory not found: {CONTENT_DIR}")
        return content_index

    # Collect all .md files matching content patterns
    file_patterns = [
        "instagram-content-batch-*.md",
        "instagram-opb-batch-*.md",
        "twitter-threads*.md",
        "twitter-batch-*.md",
        "youtube-scripts-batch-*.md",
        "youtube-shorts-en-batch-*.md",
        "tiktok-batch-*.md",
        "tiktok-scripts-batch-*.md",
        "newsletter-issues-*.md",
        "blog-posts-batch-*.md",
        "linkedin-batch-*.md",
        "linkedin-content-batch-*.md",
        "pinterest-batch-*.md",
    ]

    subdir_patterns = [
        ("youtube-scripts", "batch-*.md"),
        ("newsletter-en", "*.md"),
        ("newsletter-es", "*.md"),
        ("tiktok-en", "*.md"),
        ("tiktok-es", "*.md"),
        ("twitter-en", "*.md"),
        ("twitter-es", "*.md"),
        ("linkedin-en", "*.md"),
        ("linkedin-es", "*.md"),
        ("instagram-es", "*.md"),
        ("youtube-shorts-en", "*.md"),
        ("youtube-shorts-es", "*.md"),
        ("pinterest", "*.md"),
    ]

    matched_files = set()
    for pattern in file_patterns:
        for fp in CONTENT_DIR.glob(pattern):
            matched_files.add(fp)
    for subdir, pattern in subdir_patterns:
        subdir_path = CONTENT_DIR / subdir
        if subdir_path.exists():
            for fp in subdir_path.glob(pattern):
                matched_files.add(fp)

    for filepath in sorted(matched_files):
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if len(text.strip()) < 50:
            continue

        rel_path = str(filepath.relative_to(BASE_DIR))
        platform = detect_platform(rel_path)
        title = extract_title(text, filepath.name)
        searchable = build_text_index(text)
        word_count = len(searchable.split())

        content_index.append({
            "file": rel_path,
            "platform": platform,
            "title": title,
            "searchable": searchable,
            "word_count": word_count,
        })

    return content_index


# ---------------------------------------------------------------------------
# Signal processing
# ---------------------------------------------------------------------------

def load_signals() -> list:
    """Load and validate signals from disk."""
    if not SIGNALS_FILE.exists():
        print(f"[ERROR] Signals file not found: {SIGNALS_FILE}")
        return []
    try:
        data = json.loads(SIGNALS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            print("[ERROR] signals.json is not a list")
            return []
        return data
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in signals.json: {e}")
        return []


def extract_trending_topics(signals: list) -> list:
    """Extract trending topics with weighted scores. Returns [(topic, score), ...]."""
    topic_scores = defaultdict(float)
    topic_counts = Counter()

    for signal in signals:
        category = signal.get("category", "")
        tags = signal.get("tags", [])
        priority = signal.get("priority", 0)
        engagement = signal.get("engagement", 0)
        sentiment_abs = abs(signal.get("sentiment", 0))

        weight = (priority * 0.5) + (engagement * 0.3) + (sentiment_abs * 0.2)

        if category:
            topic_scores[category] += weight
            topic_counts[category] += 1
        for tag in tags:
            topic_scores[tag] += weight
            topic_counts[tag] += 1

    ranked = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def extract_signal_keywords(signals: list) -> list:
    """Extract specific keywords from signal titles for precise matching."""
    # Pull distinctive words from high-priority signal titles
    word_freq = Counter()
    for signal in signals:
        priority = signal.get("priority", 0)
        if priority < 0.3:
            continue
        title = signal.get("title", "").lower()
        desc = signal.get("description", "").lower()
        combined = f"{title} {desc}"
        combined = re.sub(r"[^a-z\s]", " ", combined)
        words = combined.split()
        for w in words:
            if len(w) >= 4 and w not in STOPWORDS:
                word_freq[w] += 1
    # Return words that appear in multiple signals (actually trending)
    return [w for w, c in word_freq.most_common(50) if c >= 2]


# ---------------------------------------------------------------------------
# Matching and scoring
# ---------------------------------------------------------------------------

def count_phrase_hits(searchable: str, phrase: str) -> int:
    """Count how many times a phrase appears in the searchable text."""
    if len(phrase) < 3:
        return 0
    count = 0
    start = 0
    while True:
        idx = searchable.find(phrase, start)
        if idx == -1:
            break
        count += 1
        start = idx + len(phrase)
    return count


def score_content(content_item: dict, trending_topics: list, signal_keywords: list) -> dict:
    """Score a content item against trending topics. Returns match info or None."""
    searchable = content_item["searchable"]
    word_count = max(content_item["word_count"], 100)

    matched_topics = []
    topic_hit_details = []
    raw_score = 0.0

    # Phase 1: Match against topic keyword phrases
    for topic, topic_weight in trending_topics[:10]:
        phrases = TOPIC_KEYWORDS.get(topic, [])
        if not phrases:
            continue

        total_hits = 0
        hit_phrases = []
        for phrase in phrases:
            hits = count_phrase_hits(searchable, phrase)
            if hits > 0:
                total_hits += hits
                hit_phrases.append(phrase)

        if total_hits == 0:
            continue

        # Density: hits per 1000 words. Cap at a reasonable level.
        density = (total_hits / word_count) * 1000
        density_factor = min(density / 20.0, 1.0)  # 20 hits per 1000 words = max

        # Breadth: how many different phrases matched
        breadth_factor = min(len(hit_phrases) / max(len(phrases), 1), 1.0)

        # Topic contribution: combine density, breadth, and topic trending weight
        # Normalize topic_weight: log scale since some topics dominate
        import math
        norm_weight = min(math.log1p(topic_weight) / 5.0, 1.0)

        contribution = (density_factor * 0.4) + (breadth_factor * 0.3) + (norm_weight * 0.3)
        raw_score += contribution

        matched_topics.append(topic)
        topic_hit_details.append({
            "topic": topic,
            "hits": hit_phrases[:5],
            "hit_count": total_hits,
            "density": round(density, 1),
        })

    # Phase 2: Bonus for signal-specific keyword matches
    signal_hits = 0
    for kw in signal_keywords:
        if kw in searchable:
            signal_hits += 1
    if signal_hits > 0:
        raw_score += min(signal_hits / 20.0, 0.15)  # Small bonus, max 0.15

    if not matched_topics:
        return None

    # Normalize: with 10 topics, max raw_score would be ~10.15
    # We want good differentiation in the 0-1 range
    num_topics = len(matched_topics)
    relevance_score = raw_score / max(len(trending_topics[:10]), 1)
    relevance_score = min(relevance_score, 1.0)
    relevance_score = round(relevance_score, 3)

    return {
        "file": content_item["file"],
        "title": content_item["title"],
        "relevance_score": relevance_score,
        "matched_topics": matched_topics,
        "target_platform": content_item["platform"],
        "match_details": topic_hit_details,
        "num_topic_matches": num_topics,
    }


def determine_action(relevance_score: float, num_topics: int) -> str:
    """Decide action. Higher bar for PUBLISH_NOW."""
    if relevance_score >= 0.25 and num_topics >= 2:
        return "PUBLISH_NOW"
    if relevance_score >= 0.35:
        return "PUBLISH_NOW"
    return "QUEUE_FOR_REVIEW"


def build_reason(match_details: list, action: str, trending_topics: list) -> str:
    """Build a human-readable reason string."""
    parts = []
    for md in match_details[:3]:
        topic = md["topic"]
        hits = ", ".join(md["hits"][:2])
        density = md["density"]
        parts.append(f"{topic} [{hits}] ({density} hits/1k words)")

    topic_str = "; ".join(parts)
    if action == "PUBLISH_NOW":
        return f"High relevance to trending signals: {topic_str}"
    return f"Partial match: {topic_str}"


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def generate_reactive_queue() -> dict:
    """Full pipeline: signals -> content scan -> scoring -> queue."""
    print("[1/4] Loading signals...")
    signals = load_signals()
    if not signals:
        return {"generated_at": datetime.now(timezone.utc).isoformat(), "trending_topics": [], "queue": []}

    print(f"      {len(signals)} signals loaded")

    print("[2/4] Extracting trending topics...")
    trending = extract_trending_topics(signals)
    top_topics = [t[0] for t in trending[:10]]
    signal_keywords = extract_signal_keywords(signals)
    print(f"      Top topics: {', '.join(top_topics)}")
    print(f"      Signal keywords: {', '.join(signal_keywords[:15])}...")

    print("[3/4] Scanning content library...")
    content_index = scan_content_library()
    print(f"      {len(content_index)} content files indexed")

    print("[4/4] Scoring and ranking...")
    queue = []
    for item in content_index:
        match = score_content(item, trending, signal_keywords)
        if match:
            action = determine_action(match["relevance_score"], match["num_topic_matches"])
            reason = build_reason(match["match_details"], action, trending)
            queue.append({
                "file": match["file"],
                "title": match["title"],
                "relevance_score": match["relevance_score"],
                "matched_topics": match["matched_topics"],
                "action": action,
                "target_platform": match["target_platform"],
                "reason": reason,
            })

    queue.sort(key=lambda x: x["relevance_score"], reverse=True)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trending_topics": top_topics,
        "queue": queue,
    }

    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    publish_now = sum(1 for q in queue if q["action"] == "PUBLISH_NOW")
    review = sum(1 for q in queue if q["action"] == "QUEUE_FOR_REVIEW")
    print(f"\n[DONE] Reactive queue written to {QUEUE_FILE}")
    print(f"       {len(queue)} content items matched ({publish_now} PUBLISH_NOW, {review} QUEUE_FOR_REVIEW)")

    return result


def print_digest(result: dict):
    """Print a human-readable digest of what to post today."""
    print("=" * 72)
    print("  BIOS CONTENT WIRING -- DAILY DIGEST")
    print(f"  Generated: {result['generated_at']}")
    print("=" * 72)

    topics = result.get("trending_topics", [])
    print(f"\n  TRENDING: {', '.join(topics)}")

    queue = result.get("queue", [])
    if not queue:
        print("\n  No content matches found.")
        print("  The library may need new material aligned with current signals.")
        return

    publish_now = [q for q in queue if q["action"] == "PUBLISH_NOW"]
    review = [q for q in queue if q["action"] == "QUEUE_FOR_REVIEW"]

    if publish_now:
        print(f"\n  -- PUBLISH NOW ({len(publish_now)} items) --")
        by_platform = defaultdict(list)
        for item in publish_now:
            by_platform[item["target_platform"]].append(item)

        for platform in sorted(by_platform.keys()):
            items = by_platform[platform][:3]  # Top 3 per platform
            print(f"\n  [{platform.upper()}]")
            for item in items:
                score = item["relevance_score"]
                topics_str = ", ".join(item["matched_topics"][:3])
                print(f"    {score:.3f} | {item['title'][:58]}")
                print(f"           Topics: {topics_str}")
                print(f"           File: {item['file']}")
                print(f"           Why: {item['reason'][:70]}")
                print()

    if review:
        print(f"\n  -- REVIEW QUEUE ({len(review)} items, top 10) --\n")
        for item in review[:10]:
            score = item["relevance_score"]
            plat = item["target_platform"]
            print(f"    {score:.3f} | [{plat:>10}] {item['title'][:50]}")

    # Summary
    platforms = Counter(q["target_platform"] for q in publish_now)
    if platforms:
        print("\n  -- PLATFORM SUMMARY (PUBLISH_NOW) --")
        for plat, count in platforms.most_common():
            print(f"    {plat:>12}: {count} items")

    total_publish = len(publish_now)
    total_review = len(review)
    print(f"\n  TOTAL: {total_publish} ready to publish, {total_review} need review")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    digest_mode = "--digest" in sys.argv

    result = generate_reactive_queue()

    if digest_mode:
        print()
        print_digest(result)
    else:
        queue = result.get("queue", [])
        publish_now = [q for q in queue if q["action"] == "PUBLISH_NOW"]
        if publish_now:
            print(f"\nTop 5 to publish now:")
            for item in publish_now[:5]:
                print(f"  [{item['target_platform']:>10}] {item['relevance_score']:.3f} -- {item['title'][:55]}")
            print(f"\nRun with --digest for the full breakdown.")
