#!/usr/bin/env python3
"""
Daily Content Generator -- One command, full day of posts.

Fetches news, scores impact, generates carousels + captions,
and outputs a ready-to-post content bundle.

Usage:
    python3 daily_content.py                 # full daily run
    python3 daily_content.py --fetch-only    # just fetch news
    python3 daily_content.py --posts-only    # just generate posts from existing data
    python3 daily_content.py --count 5       # generate 5 posts instead of default 10
"""
import json
import sys
import os
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
DATA_DIR = TOOLS_DIR.parent / "Ceiba" / "news"
ARTICLES_FILE = DATA_DIR / "articles.json"
CAROUSEL_DIR = DATA_DIR / "carousels"
POSTS_DIR = DATA_DIR / "posts"
BUNDLE_DIR = DATA_DIR / "daily-bundles"

# Shape mapping: keywords in title/summary -> Robert Greene shape
SHAPE_MAP = {
    "nvidia": "bolt",
    "jensen": "bolt",
    "gtc": "bolt",
    "gpu": "bolt",
    "openai": "diamond",
    "anthropic": "diamond",
    "claude": "diamond",
    "regulation": "shield",
    "security": "shield",
    "safety": "shield",
    "monitor": "shield",
    "compliance": "shield",
    "brain": "brain",
    "agent": "brain",
    "memory": "brain",
    "neural": "brain",
    "research": "brain",
    "google": "hexagon",
    "deepmind": "hexagon",
    "meta": "hexagon",
    "apple": "circle",
    "openclaw": "claw",
    "drug": "circle",
    "health": "circle",
    "mistral": "tower",
    "startup": "arrow",
    "funding": "arrow",
}

# Theme rotation
THEMES = ["ink", "bone", "slate", "warm"]


def fetch_news():
    """Fetch latest news via ai_news_tracker."""
    print("  Fetching news...")
    result = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "ai_news_tracker.py"), "--fetch"],
        capture_output=True, text=True, cwd=str(TOOLS_DIR.parent)
    )
    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        for line in lines[-5:]:
            print(f"  {line.strip()}")
    else:
        print(f"  Fetch failed: {result.stderr[:200]}")
    return result.returncode == 0


def pick_shape(article):
    """Pick a Robert Greene shape based on article content."""
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    for keyword, shape in SHAPE_MAP.items():
        if keyword in text:
            return shape
    return "diamond"


def generate_shape_text(article, shape):
    """Generate the Robert Greene shaped text paragraph for a story."""
    title = article["title"]
    summary = article.get("summary", "")
    mentions = article.get("mentions", [])

    # Build a short, punchy paragraph for shaping
    parts = []
    # Start with the core fact
    if summary:
        sentences = summary.replace(". ", ".\n").split("\n")
        for s in sentences[:3]:
            s = s.strip()
            if s and len(s) > 10:
                parts.append(s)

    # Only add shaped text for ~40% of posts (occasional, not every one)
    if not parts:
        return ""

    text = " ".join(parts)
    # Clean em dashes
    text = text.replace("\u2014", ".").replace("\u2013", ".").replace("—", ".")
    while ".." in text:
        text = text.replace("..", ".")

    return text[:300]  # Cap at 300 chars for shape readability


def generate_daily_bundle(count=10):
    """Generate a full day's worth of content."""
    if not ARTICLES_FILE.exists():
        print("  No articles found. Run --fetch-only first.")
        return

    articles = json.load(open(ARTICLES_FILE))
    articles.sort(key=lambda a: a.get("impact_score", 0), reverse=True)
    high = [a for a in articles if a["impact"] == "HIGH"][:count]

    if not high:
        print("  No HIGH impact stories found.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    bundle = {
        "date": today,
        "generated": datetime.now().isoformat(),
        "posts": [],
    }

    print(f"\n  Generating {len(high)} posts for {today}\n")

    for i, article in enumerate(high):
        theme = THEMES[i % len(THEMES)]
        shape = pick_shape(article)
        title = article["title"]

        print(f"  [{i+1}/{len(high)}] {title[:60]}...")
        print(f"          theme={theme}, shape={shape}")

        # Generate carousel HTML
        shape_text = generate_shape_text(article, shape) if i % 3 == 0 else ""
        args = [
            sys.executable, str(TOOLS_DIR / "carousel_generator.py"),
            "--from-tracker", str(i + 1),
            "--theme", theme,
        ]
        if shape_text:
            args.extend(["--shape", shape, "--shape-text", shape_text])

        result = subprocess.run(args, capture_output=True, text=True, cwd=str(TOOLS_DIR.parent))
        carousel_path = ""
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "Carousel:" in line:
                    carousel_path = line.split("Carousel:")[1].strip()

        # Generate caption
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "news_to_post.py"), "--story", str(i + 1), "--save"],
            capture_output=True, text=True, cwd=str(TOOLS_DIR.parent)
        )

        bundle["posts"].append({
            "index": i + 1,
            "title": title,
            "source": article["source"],
            "impact": article["impact"],
            "theme": theme,
            "shape": shape if shape_text else None,
            "carousel": carousel_path,
        })

    # Save bundle manifest
    bundle_path = BUNDLE_DIR / f"bundle-{today}.json"
    with open(bundle_path, "w") as f:
        json.dump(bundle, f, indent=2)

    # Print summary
    print(f"\n  {'=' * 50}")
    print(f"  Daily bundle: {bundle_path}")
    print(f"  Posts: {len(bundle['posts'])}")
    print(f"  Carousels: {CAROUSEL_DIR}")
    print(f"  Captions: {POSTS_DIR}")
    print(f"  {'=' * 50}")
    print(f"\n  Next: Open carousels in browser, screenshot each slide.")
    print(f"  Captions are saved as JSON in {POSTS_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Daily Content Generator")
    parser.add_argument("--fetch-only", action="store_true", help="Just fetch news")
    parser.add_argument("--posts-only", action="store_true", help="Generate posts from existing data")
    parser.add_argument("--count", type=int, default=10, help="Number of posts to generate")

    args = parser.parse_args()

    print(f"\n  Daily Content Generator")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    if args.fetch_only:
        fetch_news()
        return

    if not args.posts_only:
        fetch_news()
        print()

    generate_daily_bundle(count=args.count)


if __name__ == "__main__":
    main()
