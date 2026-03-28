#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Morning Content Report. Reads overnight pipeline output and shows a clean
briefing Kalani can read with coffee.

Usage:
    python3 morning_content_report.py          # today's report
    python3 morning_content_report.py 2026-03-20  # specific date
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# --- Paths ---
BEHIQUE_DIR = Path.home() / "behique"
NEWS_DIR = BEHIQUE_DIR / "Ceiba" / "news"
DAILY_DIR = NEWS_DIR / "daily"
LOG_DIR = NEWS_DIR / "logs"
MEMES_DIR = NEWS_DIR / "memes"
STORIES_DIR = BEHIQUE_DIR / "tools" / "reel-pipeline" / "stories"
ARTICLES_FILE = NEWS_DIR / "articles.json"


def get_date(args):
    if args and args[0] != "--help":
        return args[0]
    return datetime.now().strftime("%Y-%m-%d")


def count_files(directory, pattern):
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def read_file_safe(path):
    try:
        return path.read_text()
    except Exception:
        return ""


def get_top_stories(date_str):
    """Pull story titles from today's stories.json or articles.json."""
    stories_file = DAILY_DIR / date_str / "stories.json"
    if stories_file.exists():
        try:
            stories = json.loads(stories_file.read_text())
            return [(s.get("title", "Untitled"), s.get("impact", "?"), s.get("source", "")) for s in stories]
        except Exception:
            pass

    # Fallback: read from articles.json
    if ARTICLES_FILE.exists():
        try:
            articles = json.loads(ARTICLES_FILE.read_text())
            today = [a for a in articles if a.get("fetched", "")[:10] == date_str]
            today.sort(key=lambda a: a.get("impact_score", 0), reverse=True)
            return [(a.get("title", "Untitled"), a.get("impact", "?"), a.get("source", "")) for a in today[:5]]
        except Exception:
            pass
    return []


def get_trending_topics(date_str):
    """Check for trending topic data from Google Trends scraper."""
    trends_output = BEHIQUE_DIR / "tools" / "trends_output"
    if not trends_output.exists():
        trends_output = BEHIQUE_DIR / "output" / "trends"

    if not trends_output.exists():
        return []

    # Look for most recent trends file
    trend_files = sorted(trends_output.glob("*.json"), reverse=True)
    if not trend_files:
        trend_files = sorted(trends_output.glob("*.csv"), reverse=True)

    if not trend_files:
        return []

    try:
        data = json.loads(trend_files[0].read_text())
        if isinstance(data, list):
            return [item.get("keyword", item.get("query", str(item))) for item in data[:8]]
        if isinstance(data, dict) and "results" in data:
            return [item.get("keyword", str(item)) for item in data["results"][:8]]
    except Exception:
        pass
    return []


def check_overnight_log(date_str):
    """Read overnight log for status info."""
    log_path = LOG_DIR / f"overnight-{date_str}.log"
    if not log_path.exists():
        return None, None, None

    content = log_path.read_text()
    lines = content.strip().split("\n")

    # Extract task counts from the final summary line
    tasks_ok = 0
    tasks_fail = 0
    for line in reversed(lines):
        if "ok" in line and "fail" in line:
            # Parse "Tasks: X run, Y ok, Z failed"
            parts = line.split(",")
            for part in parts:
                part = part.strip()
                if "ok" in part:
                    try:
                        tasks_ok = int(part.split()[0].split(":")[-1])
                    except (ValueError, IndexError):
                        pass
                if "fail" in part:
                    try:
                        tasks_fail = int(part.split()[0])
                    except (ValueError, IndexError):
                        pass
            break

    # Check for FAIL lines
    failures = [line for line in lines if "FAIL:" in line]
    return tasks_ok, tasks_fail, failures


def print_report(date_str):
    today_dir = DAILY_DIR / date_str

    # Header
    print()
    print("=" * 60)
    print(f"  BEHIKE MORNING BRIEFING // {date_str}")
    print("=" * 60)
    print()

    # Overnight status
    tasks_ok, tasks_fail, failures = check_overnight_log(date_str)
    if tasks_ok is not None:
        status = "ALL CLEAR" if tasks_fail == 0 else f"{tasks_fail} FAILED"
        print(f"  Overnight status: {status}")
        if failures:
            print(f"  Failures:")
            for f in failures:
                print(f"    - {f.strip()}")
        print()
    else:
        print("  Overnight pipeline did not run (no log found).")
        print(f"  Run: ~/behique/tools/overnight.sh")
        print()

    # Content ready
    print("-" * 60)
    print("  CONTENT READY TO POST")
    print("-" * 60)
    print()

    carousels = count_files(today_dir, "carousel-*.html")
    captions_en = count_files(today_dir, "caption-*-en.txt")
    captions_es = count_files(today_dir, "caption-*-es.txt")
    reels = count_files(today_dir, "reel-*.json")
    tts = count_files(today_dir, "reel-*-narration.wav")

    if carousels + captions_en + reels == 0:
        print("  No content generated yet for today.")
        print()
    else:
        print(f"  Carousels:       {carousels}")
        print(f"  Captions (EN):   {captions_en}")
        print(f"  Captions (ES):   {captions_es}")
        print(f"  Reel scripts:    {reels}")
        print(f"  TTS narrations:  {tts}")
        print()

        # List the actual files
        if today_dir.exists():
            files = sorted(today_dir.iterdir())
            if files:
                print(f"  Location: {today_dir}/")
                for f in files:
                    size_kb = f.stat().st_size / 1024
                    print(f"    {f.name:<35} {size_kb:>6.1f} KB")
                print()

    # Top stories
    print("-" * 60)
    print("  TOP STORIES")
    print("-" * 60)
    print()

    stories = get_top_stories(date_str)
    if stories:
        for i, (title, impact, source) in enumerate(stories, 1):
            # Truncate long titles
            display_title = title if len(title) <= 55 else title[:52] + "..."
            print(f"  {i}. [{impact}] {display_title}")
            if source:
                print(f"     {source}")
        print()
    else:
        print("  No stories fetched today.")
        print()

    # Scraped content
    print("-" * 60)
    print("  SCRAPED CONTENT")
    print("-" * 60)
    print()

    # Memes
    meme_count = count_files(MEMES_DIR, "*.json") if MEMES_DIR.exists() else 0
    print(f"  Memes in library:    {meme_count}")

    # Reddit stories
    story_count = count_files(STORIES_DIR, "*.json") if STORIES_DIR.exists() else 0
    print(f"  Reddit stories:      {story_count}")

    # Niche gaps
    niche_report = NEWS_DIR / "niche-gaps.html"
    if not niche_report.exists():
        niche_report = BEHIQUE_DIR / "tools" / "niche-gaps.html"
    niche_status = "ready" if niche_report.exists() else "not generated"
    print(f"  Niche gap report:    {niche_status}")

    print()

    # Trending topics
    trending = get_trending_topics(date_str)
    if trending:
        print("-" * 60)
        print("  TRENDING TOPICS")
        print("-" * 60)
        print()
        for topic in trending:
            print(f"  - {topic}")
        print()

    # Action items
    print("-" * 60)
    print("  TODAY'S ACTIONS")
    print("-" * 60)
    print()

    actions = []
    if carousels > 0:
        actions.append(f"Screenshot {carousels} carousel(s) and post to @behikeai")
    if captions_en > 0:
        actions.append(f"Review {captions_en} caption(s), pick EN or ES")
    if reels > 0:
        actions.append(f"Run {reels} reel(s) through make_reel.py")
    if meme_count > 0:
        actions.append("Review meme library for reposts")
    if not stories and not carousels:
        actions.append("Run overnight.sh manually to generate content")

    if actions:
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")
    else:
        print("  Nothing urgent. Focus on building.")

    print()
    print("=" * 60)
    print()


def main():
    args = sys.argv[1:]

    if args and args[0] == "--help":
        print(__doc__)
        sys.exit(0)

    date_str = get_date(args)

    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {date_str}")
        print("Use YYYY-MM-DD format, e.g.: 2026-03-21")
        sys.exit(1)

    print_report(date_str)


if __name__ == "__main__":
    main()
