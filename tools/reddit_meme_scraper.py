# Copyright (c) 2026 Kalani Andre Gomez Padin / Behique
# All rights reserved.
# Reddit Meme Scraper - Scrapes top memes from Reddit for reposting to Instagram/TikTok/X

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests

# Config
DEFAULT_SUBS = [
    "memes",
    "ProgrammerHumor",
    "meirl",
    "me_irl",
    "dankmemes",
    "technicallythetruth",
]
MEME_DIR = Path.home() / "behique" / "Ceiba" / "news" / "memes"
SCRAPED_IDS_FILE = MEME_DIR / ".meme_scraped_ids.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
RSS_URL = "https://www.reddit.com/r/{sub}/hot.rss"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Behique-Meme-Scraper/1.0"
REQUEST_DELAY = 2  # seconds between RSS fetches to avoid rate limiting

# Hashtag sets by subreddit
HASHTAG_MAP = {
    "memes": "#memes #funny #meme #lol #humor #viral #trending",
    "ProgrammerHumor": "#programming #coding #developer #tech #programmer #devlife #codehumor",
    "meirl": "#meirl #relatable #mood #same #viral #funny",
    "me_irl": "#meirl #relatable #mood #same #viral #funny",
    "dankmemes": "#dankmemes #memes #funny #dank #humor #viral",
    "technicallythetruth": "#technicallythetruth #facts #funny #truth #humor #viral",
}
DEFAULT_HASHTAGS = "#memes #funny #viral #trending #humor"


def load_scraped_ids() -> dict:
    """Load the set of already-scraped post IDs."""
    if SCRAPED_IDS_FILE.exists():
        with open(SCRAPED_IDS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_scraped_ids(scraped: dict):
    """Save scraped IDs to disk."""
    MEME_DIR.mkdir(parents=True, exist_ok=True)
    with open(SCRAPED_IDS_FILE, "w") as f:
        json.dump(scraped, f, indent=2)


def slugify(text: str, max_len: int = 60) -> str:
    """Turn a title into a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    text = re.sub(r"-+", "-", text)
    return text[:max_len].rstrip("_-")


def extract_image_url(entry) -> str | None:
    """Extract direct image URL from an RSS entry."""
    # Check media_thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get("url", "")
        if any(url.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            return url

    # Check links
    for link in getattr(entry, "links", []):
        href = link.get("href", "")
        if any(href.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            return href

    # Check content for image URLs
    content = ""
    if hasattr(entry, "content"):
        content = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        content = entry.summary or ""

    # Find i.redd.it or i.imgur.com image links
    img_patterns = [
        r'(https?://i\.redd\.it/[^\s"<>]+\.(?:jpg|jpeg|png|gif|webp))',
        r'(https?://i\.imgur\.com/[^\s"<>]+\.(?:jpg|jpeg|png|gif|webp))',
        r'(https?://[^\s"<>]+\.(?:jpg|jpeg|png|gif|webp))',
    ]
    for pattern in img_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_score(entry) -> int:
    """Try to extract score/upvotes from RSS entry. Returns 0 if not found."""
    # Reddit RSS doesn't always include score directly.
    # We check for it in various places.
    content = ""
    if hasattr(entry, "content"):
        content = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        content = entry.summary or ""

    # Look for "points" pattern in content
    match = re.search(r"(\d+)\s+points?", content)
    if match:
        return int(match.group(1))

    return 0


def extract_post_id(entry) -> str:
    """Extract a unique post ID from the entry."""
    # Use the entry ID or link as unique key
    entry_id = getattr(entry, "id", "") or getattr(entry, "link", "")
    # Extract just the Reddit post ID (t3_xxxxx format or the path)
    match = re.search(r"/comments/([a-z0-9]+)/", entry_id)
    if match:
        return match.group(1)
    return entry_id


def clean_title(title: str) -> str:
    """Clean up a Reddit title for use as an Instagram caption."""
    # Remove common Reddit-isms
    title = re.sub(r"\[OC\]", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\[deleted\]", "", title, flags=re.IGNORECASE)
    title = re.sub(r"u/\w+", "", title)
    title = re.sub(r"r/\w+", "", title)
    title = title.strip(" -.,;:")
    return title


def generate_caption(title: str, subreddit: str) -> str:
    """Generate an Instagram-ready caption from the meme title."""
    cleaned = clean_title(title)
    hashtags = HASHTAG_MAP.get(subreddit, DEFAULT_HASHTAGS)
    caption = f"{cleaned}\n\n{hashtags}"
    return caption


def download_image(url: str, filepath: Path) -> bool:
    """Download an image from URL to filepath."""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=30, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and "octet-stream" not in content_type:
            return False

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [!] Download failed: {e}")
        return False


def scrape_subreddit(sub: str, count: int, min_score: int, scraped_ids: dict) -> list:
    """Scrape memes from a single subreddit. Returns list of saved meme info dicts."""
    url = RSS_URL.format(sub=sub)
    print(f"\n[*] Fetching r/{sub} ...")

    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [!] Failed to fetch RSS for r/{sub}: {e}")
        return []

    feed = feedparser.parse(resp.text)
    if not feed.entries:
        print(f"  [!] No entries found for r/{sub}")
        return []

    saved = []
    for entry in feed.entries:
        if len(saved) >= count:
            break

        post_id = extract_post_id(entry)
        if post_id in scraped_ids:
            continue

        title = getattr(entry, "title", "untitled")
        score = extract_score(entry)

        if score < min_score and min_score > 0:
            # If we can't extract score from RSS, let it through when min_score is default
            # RSS feeds often don't have score data, so we only filter if score was found
            if score > 0:
                continue

        image_url = extract_image_url(entry)
        if not image_url:
            continue

        # Determine file extension
        parsed = urlparse(image_url)
        ext = Path(parsed.path).suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            ext = ".jpg"

        slug = slugify(title)
        filename = f"{sub}_{score}_{slug}{ext}"
        filepath = MEME_DIR / filename

        print(f"  [+] Downloading: {title[:60]}...")
        if download_image(image_url, filepath):
            # Save caption file
            caption = generate_caption(title, sub)
            caption_path = filepath.with_suffix(".txt")
            with open(caption_path, "w") as f:
                f.write(caption)

            # Track as scraped
            permalink = getattr(entry, "link", "")
            scraped_ids[post_id] = {
                "title": title,
                "subreddit": sub,
                "score": score,
                "image_url": image_url,
                "permalink": permalink,
                "file": str(filepath),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            saved.append({
                "title": title,
                "file": str(filepath),
                "score": score,
                "subreddit": sub,
            })
            print(f"  [+] Saved: {filename}")
        else:
            print(f"  [!] Skipped (download failed)")

    return saved


def list_scraped():
    """Show all previously scraped memes."""
    scraped = load_scraped_ids()
    if not scraped:
        print("No memes scraped yet.")
        return

    print(f"\nTotal scraped: {len(scraped)} memes\n")
    print(f"{'Subreddit':<22} {'Score':<8} {'Title':<50} {'Date'}")
    print("-" * 110)

    for post_id, info in sorted(scraped.items(), key=lambda x: x[1].get("scraped_at", ""), reverse=True):
        sub = info.get("subreddit", "?")
        score = info.get("score", 0)
        title = info.get("title", "?")[:48]
        date = info.get("scraped_at", "?")
        print(f"r/{sub:<20} {score:<8} {title:<50} {date}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape top memes from Reddit for Instagram/TikTok/X reposting."
    )
    parser.add_argument(
        "--sub",
        type=str,
        default=None,
        help="Specific subreddit to scrape (without r/). Default: all configured subs.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Max memes to grab per subreddit. Default: 5.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=1000,
        help="Minimum upvote score to include. Default: 1000.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_scraped",
        help="Show previously scraped memes instead of scraping.",
    )

    args = parser.parse_args()

    if args.list_scraped:
        list_scraped()
        return

    # Ensure output directory exists
    MEME_DIR.mkdir(parents=True, exist_ok=True)

    scraped_ids = load_scraped_ids()
    subs = [args.sub] if args.sub else DEFAULT_SUBS
    total_saved = []

    for sub in subs:
        results = scrape_subreddit(sub, args.count, args.min_score, scraped_ids)
        total_saved.extend(results)
        save_scraped_ids(scraped_ids)  # Save after each sub in case of interruption
        if sub != subs[-1]:
            time.sleep(REQUEST_DELAY)

    print(f"\n{'='*60}")
    print(f"Done. Saved {len(total_saved)} new memes to {MEME_DIR}")
    if total_saved:
        print("\nNew memes:")
        for m in total_saved:
            print(f"  - r/{m['subreddit']}: {m['title'][:60]}")


if __name__ == "__main__":
    main()
