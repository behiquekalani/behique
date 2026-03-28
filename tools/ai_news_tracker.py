#!/usr/bin/env python3
"""
AI News Tracker -- Aggregates tech/AI news with impact scoring.

Monitors RSS feeds, scores news by market impact (ForexFactory style),
and outputs a daily digest. Tracks key events like model releases,
CEO moves, funding rounds, regulatory changes.

Usage:
    python3 ai_news_tracker.py                    # fetch + display today's news
    python3 ai_news_tracker.py --fetch             # fetch new articles
    python3 ai_news_tracker.py --digest            # show daily digest
    python3 ai_news_tracker.py --digest --format html  # HTML digest
    python3 ai_news_tracker.py --search "claude"   # search past news
    python3 ai_news_tracker.py --top 10            # top 10 by impact
    python3 ai_news_tracker.py --track "sam altman" # add person to track
"""
import json
import os
import re
import sys
import time
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# --- Config ---
DATA_DIR = Path(__file__).parent.parent / "Ceiba" / "news"
ARTICLES_FILE = DATA_DIR / "articles.json"
TRACKED_FILE = DATA_DIR / "tracked.json"
DIGEST_DIR = DATA_DIR / "digests"

# RSS feeds to monitor
FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "ai"},
    {"name": "Ars Technica AI", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "category": "tech"},
    {"name": "Hacker News Best", "url": "https://hnrss.org/best?q=AI+OR+LLM+OR+GPT+OR+Claude+OR+NVIDIA", "category": "ai"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "category": "research"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "releases"},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml", "category": "releases"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "releases"},
    {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/", "category": "hardware"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "ai"},
    # Reddit - where news breaks first
    {"name": "r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/hot.rss", "category": "research"},
    {"name": "r/LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA/hot.rss", "category": "ai"},
    {"name": "r/artificial", "url": "https://www.reddit.com/r/artificial/hot.rss", "category": "ai"},
    {"name": "r/ClaudeAI", "url": "https://www.reddit.com/r/ClaudeAI/hot.rss", "category": "ai"},
    {"name": "r/OpenAI", "url": "https://www.reddit.com/r/OpenAI/hot.rss", "category": "ai"},
    {"name": "r/singularity", "url": "https://www.reddit.com/r/singularity/hot.rss", "category": "ai"},
    {"name": "r/StableDiffusion", "url": "https://www.reddit.com/r/StableDiffusion/hot.rss", "category": "ai"},
    {"name": "r/technology", "url": "https://www.reddit.com/r/technology/hot.rss", "category": "tech"},
]

# Impact keywords for scoring
IMPACT_KEYWORDS = {
    "high": [
        "launch", "release", "announce", "acquire", "billion", "million funding",
        "ipo", "regulation", "ban", "lawsuit", "breakthrough", "open source",
        "gpt-5", "gpt-6", "claude 4", "claude 5", "gemini 2", "llama 4",
        "fired", "resign", "ceo", "arrested", "sec", "ftc", "antitrust",
        "nvidia", "blackwell", "h100", "h200", "b100", "b200",
        "agi", "superintelligence", "safety", "alignment",
        "apple intelligence", "siri", "alexa", "cortana",
    ],
    "medium": [
        "update", "feature", "partnership", "integration", "api",
        "pricing", "model", "benchmark", "performance", "fine-tune",
        "agent", "plugin", "tool", "mcp", "function calling",
        "series a", "series b", "series c", "seed round", "valuation",
        "layoff", "hire", "expansion", "revenue",
    ],
    "low": [
        "tutorial", "guide", "how to", "review", "comparison",
        "opinion", "analysis", "research paper", "arxiv",
        "community", "developer", "conference", "meetup",
    ],
}

# People/companies to track
DEFAULT_TRACKED = [
    {"name": "Sam Altman", "type": "person", "org": "OpenAI"},
    {"name": "Dario Amodei", "type": "person", "org": "Anthropic"},
    {"name": "Jensen Huang", "type": "person", "org": "NVIDIA"},
    {"name": "Satya Nadella", "type": "person", "org": "Microsoft"},
    {"name": "Sundar Pichai", "type": "person", "org": "Google"},
    {"name": "Mark Zuckerberg", "type": "person", "org": "Meta"},
    {"name": "Elon Musk", "type": "person", "org": "xAI"},
    {"name": "OpenAI", "type": "company", "org": "OpenAI"},
    {"name": "Anthropic", "type": "company", "org": "Anthropic"},
    {"name": "NVIDIA", "type": "company", "org": "NVIDIA"},
    {"name": "Google DeepMind", "type": "company", "org": "Google"},
    {"name": "Meta AI", "type": "company", "org": "Meta"},
    {"name": "Mistral", "type": "company", "org": "Mistral"},
    {"name": "Hugging Face", "type": "company", "org": "Hugging Face"},
]


def ensure_dirs():
    """Create data directories."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    if not TRACKED_FILE.exists():
        with open(TRACKED_FILE, "w") as f:
            json.dump(DEFAULT_TRACKED, f, indent=2)


def load_articles():
    """Load existing articles."""
    if ARTICLES_FILE.exists():
        with open(ARTICLES_FILE) as f:
            return json.load(f)
    return []


def save_articles(articles):
    """Save articles to disk."""
    with open(ARTICLES_FILE, "w") as f:
        json.dump(articles, f, indent=2, default=str)


def load_tracked():
    """Load tracked people/companies."""
    if TRACKED_FILE.exists():
        with open(TRACKED_FILE) as f:
            return json.load(f)
    return DEFAULT_TRACKED


def article_id(title, url):
    """Generate unique ID for deduplication."""
    return hashlib.md5(f"{title}:{url}".encode()).hexdigest()[:12]


def score_impact(title, summary=""):
    """Score article impact: HIGH / MEDIUM / LOW."""
    text = f"{title} {summary}".lower()

    high_hits = sum(1 for kw in IMPACT_KEYWORDS["high"] if kw.lower() in text)
    med_hits = sum(1 for kw in IMPACT_KEYWORDS["medium"] if kw.lower() in text)

    if high_hits >= 2:
        return "HIGH", high_hits * 3 + med_hits
    elif high_hits >= 1:
        return "HIGH", high_hits * 3 + med_hits
    elif med_hits >= 2:
        return "MEDIUM", med_hits * 2
    elif med_hits >= 1:
        return "MEDIUM", med_hits * 2
    else:
        return "LOW", 1


def find_mentions(text, tracked):
    """Find tracked people/companies mentioned in text."""
    mentions = []
    text_lower = text.lower()
    for entity in tracked:
        if entity["name"].lower() in text_lower:
            mentions.append(entity["name"])
    return mentions


def fetch_feeds():
    """Fetch all RSS feeds and return new articles."""
    try:
        import feedparser
    except ImportError:
        print("feedparser not installed. Run: pip install feedparser")
        print("Attempting install...")
        os.system(f"{sys.executable} -m pip install feedparser -q")
        try:
            import feedparser
        except ImportError:
            print("Failed to install feedparser.")
            return []

    existing = load_articles()
    existing_ids = {a["id"] for a in existing}
    tracked = load_tracked()
    new_articles = []

    for feed_info in FEEDS:
        try:
            print(f"  Fetching {feed_info['name']}...")
            feed = feedparser.parse(feed_info["url"])

            for entry in feed.entries[:15]:  # last 15 per feed
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                summary = entry.get("summary", "")[:500]
                published = entry.get("published", "")

                # Parse date
                try:
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6]).isoformat()
                    else:
                        pub_date = datetime.now().isoformat()
                except Exception:
                    pub_date = datetime.now().isoformat()

                aid = article_id(title, link)
                if aid in existing_ids:
                    continue

                # Clean HTML from summary
                summary_clean = re.sub(r"<[^>]+>", "", summary).strip()

                # Score
                impact, impact_score = score_impact(title, summary_clean)
                mentions = find_mentions(f"{title} {summary_clean}", tracked)

                article = {
                    "id": aid,
                    "title": title,
                    "url": link,
                    "summary": summary_clean[:300],
                    "source": feed_info["name"],
                    "category": feed_info["category"],
                    "published": pub_date,
                    "fetched": datetime.now().isoformat(),
                    "impact": impact,
                    "impact_score": impact_score,
                    "mentions": mentions,
                }

                new_articles.append(article)
                existing_ids.add(aid)

        except Exception as e:
            print(f"  Error fetching {feed_info['name']}: {e}")

    if new_articles:
        all_articles = existing + new_articles
        # Keep last 30 days only
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        all_articles = [a for a in all_articles if a.get("fetched", "") > cutoff]
        save_articles(all_articles)

    return new_articles


def display_articles(articles, limit=20):
    """Display articles in terminal."""
    impact_colors = {"HIGH": "\033[91m", "MEDIUM": "\033[93m", "LOW": "\033[90m"}
    reset = "\033[0m"

    for i, a in enumerate(articles[:limit], 1):
        color = impact_colors.get(a["impact"], "")
        mentions = f" [{', '.join(a['mentions'])}]" if a.get("mentions") else ""
        print(f"  {color}[{a['impact']}]{reset} {a['title']}{mentions}")
        print(f"         {a['source']} | {a['published'][:10]}")
        if a.get("summary"):
            print(f"         {a['summary'][:120]}...")
        print()


def generate_digest(articles, fmt="text"):
    """Generate daily digest."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Filter to today's articles
    today_articles = [a for a in articles if a.get("fetched", "")[:10] == today]
    if not today_articles:
        today_articles = articles[:20]  # fallback to most recent

    # Sort by impact score
    today_articles.sort(key=lambda a: a.get("impact_score", 0), reverse=True)

    high = [a for a in today_articles if a["impact"] == "HIGH"]
    medium = [a for a in today_articles if a["impact"] == "MEDIUM"]
    low = [a for a in today_articles if a["impact"] == "LOW"]

    if fmt == "html":
        return generate_html_digest(today, high, medium, low)

    # Text digest
    lines = [
        f"{'=' * 60}",
        f"  AI NEWS DIGEST -- {today}",
        f"  {len(today_articles)} stories | {len(high)} HIGH | {len(medium)} MEDIUM | {len(low)} LOW",
        f"{'=' * 60}",
        "",
    ]

    if high:
        lines.append("  BREAKING / HIGH IMPACT")
        lines.append("  " + "-" * 40)
        for a in high:
            mentions = f" [{', '.join(a['mentions'])}]" if a.get("mentions") else ""
            lines.append(f"  [!!!] {a['title']}{mentions}")
            lines.append(f"        {a['source']} | {a['url']}")
            lines.append("")

    if medium:
        lines.append("  NOTABLE")
        lines.append("  " + "-" * 40)
        for a in medium:
            lines.append(f"  [**]  {a['title']}")
            lines.append(f"        {a['source']}")
            lines.append("")

    if low:
        lines.append(f"  + {len(low)} more stories (low impact)")
        lines.append("")

    # Entity summary
    all_mentions = []
    for a in today_articles:
        all_mentions.extend(a.get("mentions", []))
    if all_mentions:
        from collections import Counter
        mention_counts = Counter(all_mentions)
        lines.append("  MENTIONED TODAY")
        lines.append("  " + "-" * 40)
        for name, count in mention_counts.most_common(10):
            lines.append(f"  {name}: {count}x")
        lines.append("")

    return "\n".join(lines)


def generate_html_digest(date, high, medium, low):
    """Generate HTML digest for content creation."""
    all_items = high + medium + low

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI News Digest -- {date}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,sans-serif;background:#0a0a0f;color:#e8e8f0;padding:24px;max-width:800px;margin:0 auto}}
h1{{font-size:28px;margin-bottom:8px}}
.meta{{color:#888;margin-bottom:24px;font-size:14px}}
.section{{margin-bottom:32px}}
.section h2{{font-size:18px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #1e1e2e}}
.article{{padding:12px 0;border-bottom:1px solid #1e1e2e}}
.article:last-child{{border:none}}
.title{{font-size:15px;font-weight:600}}
.title a{{color:#a29bfe;text-decoration:none}}
.source{{font-size:12px;color:#888;margin-top:4px}}
.impact{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}}
.impact-HIGH{{background:#e74c3c;color:#fff}}
.impact-MEDIUM{{background:#f39c12;color:#000}}
.impact-LOW{{background:#333;color:#888}}
.mentions{{font-size:12px;color:#6c5ce7;margin-top:4px}}
.summary{{font-size:13px;color:#aaa;margin-top:4px}}
.stats{{display:flex;gap:24px;margin-bottom:24px}}
.stat{{text-align:center}}
.stat-num{{font-size:28px;font-weight:800;color:#a29bfe}}
.stat-label{{font-size:11px;color:#888}}
</style>
</head>
<body>
<h1>AI News Digest</h1>
<p class="meta">{date} | Auto-generated by Ceiba News Tracker</p>
<div class="stats">
<div class="stat"><div class="stat-num">{len(all_items)}</div><div class="stat-label">Stories</div></div>
<div class="stat"><div class="stat-num">{len(high)}</div><div class="stat-label">High Impact</div></div>
<div class="stat"><div class="stat-num">{len(medium)}</div><div class="stat-label">Medium</div></div>
</div>
"""

    if high:
        html += '<div class="section"><h2>Breaking / High Impact</h2>\n'
        for a in high:
            mentions_html = f'<div class="mentions">Mentions: {", ".join(a.get("mentions", []))}</div>' if a.get("mentions") else ""
            html += f'''<div class="article">
<span class="impact impact-HIGH">HIGH</span>
<div class="title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
<div class="source">{a['source']} | {a['published'][:10]}</div>
{mentions_html}
<div class="summary">{a.get('summary', '')[:200]}</div>
</div>\n'''
        html += '</div>\n'

    if medium:
        html += '<div class="section"><h2>Notable</h2>\n'
        for a in medium:
            html += f'''<div class="article">
<span class="impact impact-MEDIUM">MEDIUM</span>
<div class="title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
<div class="source">{a['source']} | {a['published'][:10]}</div>
</div>\n'''
        html += '</div>\n'

    if low:
        html += f'<div class="section"><h2>Other ({len(low)} stories)</h2>\n'
        for a in low[:5]:
            html += f'''<div class="article">
<span class="impact impact-LOW">LOW</span>
<div class="title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
<div class="source">{a['source']}</div>
</div>\n'''
        html += '</div>\n'

    html += "</body></html>"
    return html


def search_articles(query, articles):
    """Search articles by keyword."""
    query_lower = query.lower()
    results = [
        a for a in articles
        if query_lower in a.get("title", "").lower()
        or query_lower in a.get("summary", "").lower()
        or query_lower in " ".join(a.get("mentions", [])).lower()
    ]
    return sorted(results, key=lambda a: a.get("impact_score", 0), reverse=True)


def add_tracked(name, entity_type="person", org=""):
    """Add a person or company to track."""
    tracked = load_tracked()
    for t in tracked:
        if t["name"].lower() == name.lower():
            print(f"  Already tracking: {name}")
            return
    tracked.append({"name": name, "type": entity_type, "org": org})
    with open(TRACKED_FILE, "w") as f:
        json.dump(tracked, f, indent=2)
    print(f"  Now tracking: {name} ({entity_type})")


def main():
    parser = argparse.ArgumentParser(description="AI News Tracker with Impact Scoring")
    parser.add_argument("--fetch", action="store_true", help="Fetch new articles from RSS feeds")
    parser.add_argument("--digest", action="store_true", help="Generate daily digest")
    parser.add_argument("--format", choices=["text", "html"], default="text", help="Digest format")
    parser.add_argument("--search", help="Search articles by keyword")
    parser.add_argument("--top", type=int, help="Show top N articles by impact")
    parser.add_argument("--track", help="Add person/company to track")
    parser.add_argument("--track-type", default="person", choices=["person", "company"])
    parser.add_argument("--track-org", default="")
    parser.add_argument("--list-tracked", action="store_true", help="Show tracked entities")
    parser.add_argument("--save", help="Save digest to file")

    args = parser.parse_args()
    ensure_dirs()

    if args.track:
        add_tracked(args.track, args.track_type, args.track_org)
        return

    if args.list_tracked:
        tracked = load_tracked()
        print(f"\n  Tracking {len(tracked)} entities:\n")
        for t in tracked:
            print(f"  [{t['type']}] {t['name']} ({t.get('org', '')})")
        return

    # Default: fetch + digest
    if args.fetch or (not args.digest and not args.search and not args.top):
        print("\n  Fetching AI news...\n")
        new = fetch_feeds()
        print(f"\n  {len(new)} new articles found.\n")

    articles = load_articles()

    if args.search:
        results = search_articles(args.search, articles)
        print(f"\n  Search: '{args.search}' -- {len(results)} results\n")
        display_articles(results)
        return

    if args.top:
        sorted_articles = sorted(articles, key=lambda a: a.get("impact_score", 0), reverse=True)
        print(f"\n  Top {args.top} by Impact\n")
        display_articles(sorted_articles, limit=args.top)
        return

    if args.digest or (not args.search and not args.top):
        digest = generate_digest(articles, fmt=args.format)

        if args.save or args.format == "html":
            today = datetime.now().strftime("%Y-%m-%d")
            ext = "html" if args.format == "html" else "md"
            save_path = args.save or str(DIGEST_DIR / f"digest-{today}.{ext}")
            with open(save_path, "w") as f:
                f.write(digest)
            print(f"  Digest saved to: {save_path}")
        else:
            print(digest)


if __name__ == "__main__":
    main()
