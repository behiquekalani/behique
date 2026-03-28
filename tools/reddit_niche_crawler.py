#!/usr/bin/env python3
"""
Reddit Niche Demand Crawler - finds unserved market gaps.

Scans Reddit via RSS for complaints about missing software, dead projects,
and unmet needs. Scores findings by demand signals and generates actionable
reports for product research.

Usage:
    python3 reddit_niche_crawler.py                # scan all subs
    python3 reddit_niche_crawler.py --sub macapps  # specific sub
    python3 reddit_niche_crawler.py --digest       # generate HTML report
    python3 reddit_niche_crawler.py --top 10       # show top 10 gaps
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: pip3 install feedparser")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "Ceiba" / "news"
GAPS_FILE = OUTPUT_DIR / "niche-gaps.json"
DIGEST_FILE = OUTPUT_DIR / "niche-digest.html"
SEEN_FILE = OUTPUT_DIR / ".niche-seen-ids"

SUBREDDITS = [
    # Software / SaaS gaps
    "macapps",
    "mac",
    "SaaS",
    "software",
    "startups",
    "Entrepreneur",
    "webdev",
    "bioinformatics",
    "selfhosted",
    "smallbusiness",
    # E-commerce / Dropshipping gaps
    "dropship",
    "shopify",
    "FulfillmentByAmazon",
    "EtsySellers",
    "ecommerce",
    "flipping",
    # Digital products / Creator gaps
    "digitalnomad",
    "passive_income",
    "juststart",
    "Blogging",
    "podcasting",
    "NewTubers",
    # ADHD / Productivity (our niche)
    "ADHD",
    "productivity",
    "getdisciplined",
    # AI tools gaps
    "ChatGPT",
    "LocalLLaMA",
    "artificial",
    "ClaudeAI",
]

# Demand signal keywords (case-insensitive matching)
DEMAND_KEYWORDS = [
    r"wish there was",
    r"no mac version",
    r"looking for (?:an? )?alternative",
    r"any alternative to",
    r"is there a",
    r"does anyone know",
    r"this app is dead",
    r"abandoned",
    r"no longer maintained",
    r"discontinued",
    r"looking for a tool",
    r"need a tool",
    r"replacement for",
    r"went offline",
    r"shutting down",
    r"shut down",
    r"no free option",
    r"too expensive",
    r"nothing like this exists",
    r"can't find anything",
    r"open.?source alternative",
    # E-commerce / product gaps
    r"where (?:can|do) (?:i|you) (?:buy|find|get)",
    r"can't find (?:a|this|any)",
    r"out of stock everywhere",
    r"sold out",
    r"overpriced",
    r"cheaper alternative",
    r"budget (?:option|version|alternative)",
    r"anyone selling",
    r"where to buy",
    # ADHD / productivity gaps
    r"adhd.friendly",
    r"nothing works for my adhd",
    r"tried everything",
    r"every app i've tried",
    r"finally found something",
]

# High-intent bonus keywords
HIGH_INTENT_KEYWORDS = [
    r"would pay",
    r"shut up and take my money",
    r"take my money",
    r"i'd pay",
    r"willing to pay",
    r"happy to pay",
    r"instant buy",
    r"day one purchase",
]

# Platform detection
PLATFORM_PATTERNS = {
    "Mac": r"\b(?:mac(?:os)?|apple|m[1-4])\b",
    "Windows": r"\b(?:windows|win(?:10|11)?|pc)\b",
    "Linux": r"\b(?:linux|ubuntu|debian|fedora|arch)\b",
    "iOS": r"\b(?:ios|iphone|ipad)\b",
    "Android": r"\b(?:android)\b",
    "Web": r"\b(?:web(?:app)?|browser|saas|cloud|online)\b",
    "Mobile": r"\b(?:mobile|phone)\b",
    "CLI": r"\b(?:cli|command.?line|terminal)\b",
    "Self-hosted": r"\b(?:self.?host|docker|homelab)\b",
}

# Product type detection
PRODUCT_TYPE_PATTERNS = {
    "SaaS": r"\b(?:saas|subscription|monthly|cloud.?based)\b",
    "Desktop App": r"\b(?:desktop|native|app|application)\b",
    "Mobile App": r"\b(?:mobile app|phone app|ios app|android app)\b",
    "Browser Extension": r"\b(?:extension|addon|plugin|chrome)\b",
    "Template": r"\b(?:template|boilerplate|starter)\b",
    "Guide": r"\b(?:guide|course|tutorial|how.?to)\b",
    "API": r"\b(?:api|endpoint|sdk|library)\b",
    "Open Source Tool": r"\b(?:open.?source|foss|libre)\b",
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Rate limiting
REQUEST_DELAY = 2.0  # seconds between RSS fetches


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post_id(url: str) -> str:
    """Generate a stable short ID from a post URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def load_seen_ids() -> set:
    """Load previously processed post IDs."""
    if SEEN_FILE.exists():
        return set(SEEN_FILE.read_text().strip().splitlines())
    return set()


def save_seen_ids(ids: set):
    """Persist processed post IDs."""
    SEEN_FILE.write_text("\n".join(sorted(ids)) + "\n")


def load_existing_gaps() -> list:
    """Load existing gaps from disk."""
    if GAPS_FILE.exists():
        try:
            return json.loads(GAPS_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_gaps(gaps: list):
    """Save gaps to disk."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GAPS_FILE.write_text(json.dumps(gaps, indent=2, ensure_ascii=False))


def clean_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def matches_demand(title: str, body: str) -> list:
    """Return list of matched demand keywords."""
    combined = f"{title} {body}".lower()
    matched = []
    for kw in DEMAND_KEYWORDS:
        if re.search(kw, combined, re.IGNORECASE):
            matched.append(kw)
    return matched


def detect_platforms(text: str) -> list:
    """Detect mentioned platforms."""
    platforms = []
    lower = text.lower()
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, lower):
            platforms.append(platform)
    return platforms or ["Unknown"]


def detect_product_type(text: str) -> list:
    """Detect potential product type."""
    types = []
    lower = text.lower()
    for ptype, pattern in PRODUCT_TYPE_PATTERNS.items():
        if re.search(pattern, lower):
            types.append(ptype)
    return types or ["Unknown"]


def extract_alternatives(text: str) -> list:
    """Try to pull out mentioned alternative tools/apps."""
    # Look for patterns like "I tried X", "X is dead", "moved from X"
    alternatives = []
    patterns = [
        r"(?:tried|using|use|used|moved from|switched from|migrated from)\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)",
        r"([A-Z][a-zA-Z0-9]+)\s+(?:is dead|shut down|discontinued|abandoned|no longer)",
        r"alternative to\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)",
        r"replacement for\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)",
    ]
    for pat in patterns:
        for match in re.finditer(pat, text):
            alt = match.group(1).strip()
            # Filter out common false positives
            if alt.lower() not in {"i", "the", "a", "an", "it", "this", "that", "my", "we", "they", "but", "not", "any", "some"}:
                if alt not in alternatives:
                    alternatives.append(alt)
    return alternatives


def extract_gap_summary(title: str, body: str) -> str:
    """Extract a short summary of what is missing/wanted."""
    # Prefer the title as the gap summary, cleaned up
    summary = title.strip()
    if len(summary) > 200:
        summary = summary[:200] + "..."
    return summary


def score_post(upvotes: int, comments: int, has_high_intent: bool, age_days: int, demand_count: int) -> float:
    """
    Calculate demand score for a post.

    Base: upvotes
    Bonus: comments (each comment = 2 points of signal)
    Bonus: high intent keywords (x1.5 multiplier)
    Bonus: multiple demand keywords matched
    Penalty: older than 90 days (decaying relevance)
    """
    score = float(upvotes)

    # Comment bonus: each comment is strong signal
    score += comments * 2.0

    # Multiple demand signals bonus
    if demand_count > 1:
        score *= 1.0 + (demand_count - 1) * 0.15

    # High intent multiplier
    if has_high_intent:
        score *= 1.5

    # Age penalty: posts older than 90 days lose relevance
    if age_days > 90:
        decay = max(0.2, 1.0 - (age_days - 90) / 365.0)
        score *= decay

    return round(score, 1)


def parse_age_days(published_parsed) -> int:
    """Convert feedparser time struct to age in days."""
    if not published_parsed:
        return 0
    try:
        pub_time = time.mktime(published_parsed)
        now = time.time()
        return int((now - pub_time) / 86400)
    except (TypeError, ValueError, OverflowError):
        return 0


# ---------------------------------------------------------------------------
# RSS Fetching
# ---------------------------------------------------------------------------

def fetch_subreddit(sub: str, sort: str = "new", limit: int = 50) -> list:
    """Fetch posts from a subreddit via RSS. Returns list of raw entries."""
    # Reddit RSS supports: new, hot, top, rising
    url = f"https://www.reddit.com/r/{sub}/{sort}/.rss?limit={limit}"

    try:
        feed = feedparser.parse(
            url,
            agent=USER_AGENT,
        )
        if feed.bozo and not feed.entries:
            print(f"  [!] Failed to fetch r/{sub}: {feed.bozo_exception}")
            return []
        return feed.entries
    except Exception as e:
        print(f"  [!] Error fetching r/{sub}: {e}")
        return []


def process_entry(entry, subreddit: str) -> dict | None:
    """Process a single RSS entry. Returns a gap dict or None."""
    title = clean_html(entry.get("title", ""))
    body = clean_html(entry.get("summary", ""))
    link = entry.get("link", "")
    pid = post_id(link)

    # Check for demand signals
    demand_matches = matches_demand(title, body)
    if not demand_matches:
        return None

    # Extract metadata
    combined_text = f"{title} {body}"
    upvotes = 0
    comments = 0

    # Try to extract score from content (Reddit RSS sometimes includes it)
    score_match = re.search(r'(\d+)\s+(?:points?|upvotes?)', body)
    if score_match:
        upvotes = int(score_match.group(1))

    comment_match = re.search(r'(\d+)\s+comments?', body)
    if comment_match:
        comments = int(comment_match.group(1))

    # Check high intent
    has_high_intent = any(
        re.search(kw, combined_text, re.IGNORECASE) for kw in HIGH_INTENT_KEYWORDS
    )

    # Age
    age_days = parse_age_days(entry.get("published_parsed"))

    # Calculate score
    demand_score = score_post(upvotes, comments, has_high_intent, age_days, len(demand_matches))

    # Build gap object
    gap = {
        "id": pid,
        "title": title,
        "url": link,
        "subreddit": subreddit,
        "gap_summary": extract_gap_summary(title, body),
        "platforms": detect_platforms(combined_text),
        "product_types": detect_product_type(combined_text),
        "alternatives_mentioned": extract_alternatives(combined_text),
        "demand_keywords_matched": demand_matches,
        "high_intent": has_high_intent,
        "upvotes": upvotes,
        "comments": comments,
        "demand_score": demand_score,
        "age_days": age_days,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "body_preview": body[:500] if body else "",
    }

    return gap


# ---------------------------------------------------------------------------
# Core scanning
# ---------------------------------------------------------------------------

def scan_subreddits(subs: list[str] | None = None) -> list:
    """Scan subreddits and return new gap findings."""
    if subs is None:
        subs = SUBREDDITS

    seen = load_seen_ids()
    existing = load_existing_gaps()
    existing_ids = {g["id"] for g in existing}
    new_gaps = []

    for sub in subs:
        print(f"  Scanning r/{sub}...")

        # Fetch both new and hot for better coverage
        entries = []
        for sort in ["new", "hot"]:
            batch = fetch_subreddit(sub, sort=sort, limit=50)
            entries.extend(batch)
            time.sleep(REQUEST_DELAY)

        # Deduplicate entries by link
        seen_links = set()
        unique_entries = []
        for e in entries:
            link = e.get("link", "")
            if link not in seen_links:
                seen_links.add(link)
                unique_entries.append(e)

        found = 0
        for entry in unique_entries:
            pid = post_id(entry.get("link", ""))
            if pid in seen or pid in existing_ids:
                continue

            gap = process_entry(entry, sub)
            if gap:
                new_gaps.append(gap)
                seen.add(pid)
                found += 1

        print(f"    Found {found} new demand signals")

    # Merge with existing, sort by score
    all_gaps = existing + new_gaps
    all_gaps.sort(key=lambda g: g.get("demand_score", 0), reverse=True)

    # Save
    save_gaps(all_gaps)
    save_seen_ids(seen)

    return new_gaps


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def show_top(n: int = 20):
    """Print top N gaps to terminal."""
    gaps = load_existing_gaps()
    if not gaps:
        print("No gaps found yet. Run a scan first.")
        return

    gaps.sort(key=lambda g: g.get("demand_score", 0), reverse=True)
    top = gaps[:n]

    print(f"\n  Top {len(top)} Niche Gaps (sorted by demand score)\n")
    print(f"  {'#':<4} {'Score':<8} {'Sub':<16} {'Platforms':<20} {'Title'}")
    print(f"  {'='*4} {'='*8} {'='*16} {'='*20} {'='*50}")

    for i, g in enumerate(top, 1):
        platforms = ", ".join(g.get("platforms", ["?"]))
        title = g["title"][:60]
        sub = g["subreddit"][:14]
        score = g.get("demand_score", 0)
        intent = " $" if g.get("high_intent") else ""
        print(f"  {i:<4} {score:<8.1f} r/{sub:<14} {platforms:<20} {title}{intent}")

    print(f"\n  Total gaps tracked: {len(gaps)}")
    print(f"  Data: {GAPS_FILE}")


# ---------------------------------------------------------------------------
# HTML Digest
# ---------------------------------------------------------------------------

def generate_digest():
    """Generate an HTML report of top gaps."""
    gaps = load_existing_gaps()
    if not gaps:
        print("No gaps to report. Run a scan first.")
        return

    gaps.sort(key=lambda g: g.get("demand_score", 0), reverse=True)
    top = gaps[:20]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = ""
    for i, g in enumerate(top, 1):
        platforms = ", ".join(g.get("platforms", []))
        product_types = ", ".join(g.get("product_types", []))
        alternatives = ", ".join(g.get("alternatives_mentioned", [])) or "None found"
        keywords = ", ".join(g.get("demand_keywords_matched", []))
        intent_badge = '<span class="badge intent">$ High Intent</span>' if g.get("high_intent") else ""
        score = g.get("demand_score", 0)
        body = g.get("body_preview", "")[:300]
        if len(g.get("body_preview", "")) > 300:
            body += "..."

        rows += f"""
        <tr class="gap-row" onclick="this.nextElementSibling.classList.toggle('hidden')">
            <td class="rank">{i}</td>
            <td class="score">{score:.1f}</td>
            <td>r/{g['subreddit']}</td>
            <td>
                <a href="{g['url']}" target="_blank">{g['title'][:80]}</a>
                {intent_badge}
            </td>
            <td>{platforms}</td>
        </tr>
        <tr class="detail hidden">
            <td colspan="5">
                <div class="detail-grid">
                    <div>
                        <strong>Product Types:</strong> {product_types}<br>
                        <strong>Alternatives Mentioned:</strong> {alternatives}<br>
                        <strong>Demand Keywords:</strong> {keywords}<br>
                        <strong>Upvotes:</strong> {g.get('upvotes', 0)} | <strong>Comments:</strong> {g.get('comments', 0)} | <strong>Age:</strong> {g.get('age_days', 0)} days
                    </div>
                    <div class="preview">{body}</div>
                </div>
            </td>
        </tr>"""

    # Sub distribution
    sub_counts = {}
    for g in gaps:
        s = g["subreddit"]
        sub_counts[s] = sub_counts.get(s, 0) + 1
    sub_stats = " | ".join(f"r/{s}: {c}" for s, c in sorted(sub_counts.items(), key=lambda x: -x[1]))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Niche Gap Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', 'Segoe UI', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 2rem;
            line-height: 1.5;
        }}
        h1 {{
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: #fff;
        }}
        .meta {{
            color: #666;
            font-size: 0.85rem;
            margin-bottom: 1.5rem;
        }}
        .stats {{
            background: #111;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.85rem;
            color: #888;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        th {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 2px solid #333;
            color: #888;
            font-weight: 500;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .gap-row {{
            cursor: pointer;
            transition: background 0.15s;
        }}
        .gap-row:hover {{
            background: #151515;
        }}
        .gap-row td {{
            padding: 0.75rem;
            border-bottom: 1px solid #1a1a1a;
        }}
        .rank {{ color: #555; width: 3rem; }}
        .score {{
            color: #4ade80;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
            width: 5rem;
        }}
        a {{
            color: #60a5fa;
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
        .badge {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }}
        .badge.intent {{
            background: #422006;
            color: #fbbf24;
        }}
        .detail {{
            background: #0d0d0d;
        }}
        .detail td {{
            padding: 1rem;
            border-bottom: 1px solid #1a1a1a;
        }}
        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            font-size: 0.85rem;
            color: #999;
        }}
        .preview {{
            background: #111;
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            color: #777;
            max-height: 150px;
            overflow-y: auto;
        }}
        .hidden {{ display: none; }}
        .footer {{
            margin-top: 2rem;
            color: #444;
            font-size: 0.75rem;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>Niche Gap Report</h1>
    <p class="meta">Generated {now} | Top 20 of {len(gaps)} total gaps</p>

    <div class="stats">
        <strong>Distribution:</strong> {sub_stats}
    </div>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Score</th>
                <th>Source</th>
                <th>Gap</th>
                <th>Platform</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <p class="footer">
        Click any row to expand details. | Reddit Niche Demand Crawler by Ceiba
    </p>
</body>
</html>"""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DIGEST_FILE.write_text(html_content)
    print(f"  Digest saved: {DIGEST_FILE}")
    print(f"  Gaps included: {len(top)} of {len(gaps)} total")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Reddit Niche Demand Crawler. Finds unserved market gaps."
    )
    parser.add_argument(
        "--sub",
        type=str,
        help="Scan a specific subreddit (e.g. macapps)",
    )
    parser.add_argument(
        "--digest",
        action="store_true",
        help="Generate HTML digest report",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Show top N gaps (default: 20)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear all saved data and start fresh",
    )

    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.reset:
        for f in [GAPS_FILE, SEEN_FILE, DIGEST_FILE]:
            if f.exists():
                f.unlink()
        print("  Reset complete. All data cleared.")
        return

    if args.digest:
        generate_digest()
        return

    if args.top > 0:
        show_top(args.top)
        return

    # Default: scan
    subs = [args.sub] if args.sub else None
    print(f"\n  Reddit Niche Demand Crawler")
    print(f"  Scanning {len(subs or SUBREDDITS)} subreddits...\n")

    new_gaps = scan_subreddits(subs)
    total = len(load_existing_gaps())

    print(f"\n  Done. {len(new_gaps)} new gaps found.")
    print(f"  Total gaps tracked: {total}")
    print(f"  Data: {GAPS_FILE}\n")

    # Show quick summary of new finds
    if new_gaps:
        new_gaps.sort(key=lambda g: g.get("demand_score", 0), reverse=True)
        print(f"  New findings:")
        for g in new_gaps[:5]:
            score = g.get("demand_score", 0)
            intent = " [$]" if g.get("high_intent") else ""
            print(f"    [{score:.0f}] {g['title'][:70]}{intent}")
        if len(new_gaps) > 5:
            print(f"    ... and {len(new_gaps) - 5} more. Use --top to see all.")


if __name__ == "__main__":
    main()
