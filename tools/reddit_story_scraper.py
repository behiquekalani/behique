#!/usr/bin/env python3
"""
Reddit Story Scraper - feeds into the reel pipeline.

Scrapes top stories from Reddit via public RSS feeds (no API key needed),
converts them to the reel pipeline JSON format, and saves them to the
stories directory for video generation.

Usage:
    python3 reddit_story_scraper.py              # scrape all default subs
    python3 reddit_story_scraper.py --sub tifu   # specific subreddit
    python3 reddit_story_scraper.py --list        # show scraped stories
    python3 reddit_story_scraper.py --count 5     # top 5 per sub
    python3 reddit_story_scraper.py --min-score 2000  # higher quality filter
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import feedparser

# --- Configuration ---

DEFAULT_SUBREDDITS = [
    "tifu",
    "AmItheAsshole",
    "MaliciousCompliance",
    "pettyrevenge",
    "entitledparents",
    "relationship_advice",
]

STORIES_DIR = Path(__file__).parent / "reel-pipeline" / "stories"
TRACKER_FILE = Path(__file__).parent / ".reddit_scraped_ids.json"

MIN_SCORE_DEFAULT = 1000
MIN_TEXT_LENGTH = 500
MAX_TEXT_LENGTH = 3000
DEFAULT_COUNT = 3
SCENES_PER_STORY = 5

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) reel-pipeline/1.0"


# --- Text cleaning ---

def clean_reddit_text(text: str) -> str:
    """Remove Reddit-specific formatting, edits, TLDRs, update sections."""
    # Decode HTML entities
    text = html.unescape(text)

    # Remove edit sections (Edit:, EDIT:, Edit 1:, etc.)
    text = re.sub(
        r"\n*\s*\*?\*?Edit\s*\d*\s*:?\*?\*?\s*:?.*?(?=\n\n|\Z)",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove TLDR / TL;DR sections
    text = re.sub(
        r"\n*\s*\*?\*?TL\s*;?\s*DR\s*:?\*?\*?\s*:?.*?(?=\n\n|\Z)",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove Update sections
    text = re.sub(
        r"\n*\s*\*?\*?Update\s*\d*\s*:?\*?\*?\s*:?.*?(?=\n\n|\Z)",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove markdown formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)  # italic
    text = re.sub(r"~~(.+?)~~", r"\1", text)  # strikethrough
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # links
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)  # headers
    text = re.sub(r"^[>\s]+", "", text, flags=re.MULTILINE)  # blockquotes
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)

    # Remove "throwaway account" disclaimers
    text = re.sub(
        r"(?:throwaway|burner)\s+(?:account|because).*?[.\n]",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove "obligatory not today" / "this happened X ago" openers
    text = re.sub(
        r"^(?:obligatory|so\s+this\s+(?:happened|didn'?t\s+happen)\s+today).*?[.\n]\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove "on mobile" disclaimers
    text = re.sub(
        r"(?:on\s+mobile|formatting|english\s+is\s+not\s+my\s+first).*?[.\n]\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces
    text = re.sub(r"  +", " ", text)

    return text.strip()


def extract_selftext_from_rss(entry) -> str:
    """Extract the self text from an RSS entry's content."""
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        content = entry.summary

    # RSS wraps self posts in a table. Extract the actual text.
    # The self text is inside <!-- SC_OFF --><div class="md">...</div><!-- SC_ON -->
    md_match = re.search(
        r'<div class="md">\s*(<p>.*?)</div>\s*(?:<!-- SC_ON -->|<table)',
        content,
        re.DOTALL,
    )
    if md_match:
        raw = md_match.group(1)
    else:
        # Fallback: just strip all HTML tags
        raw = content

    # Strip HTML tags
    raw = re.sub(r"<br\s*/?>", "\n", raw)
    raw = re.sub(r"</p>\s*<p>", "\n\n", raw)
    raw = re.sub(r"<[^>]+>", "", raw)

    return html.unescape(raw).strip()


def extract_score_from_rss(entry) -> int:
    """Try to extract score. RSS doesn't always include it, so we estimate."""
    # Reddit RSS sometimes has score in the content as a link "[score] points"
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        content = entry.summary

    score_match = re.search(r"(\d+)\s+points?", content)
    if score_match:
        return int(score_match.group(1))

    # If we can't find score, assume top RSS posts are high-scoring
    return 0


# --- Scene splitting ---

def split_into_scenes(text: str, num_scenes: int = SCENES_PER_STORY) -> list[dict]:
    """Split narration text into scenes with image prompts."""
    # Split by sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= num_scenes:
        # Fewer sentences than scenes, one sentence per scene
        chunks = [[s] for s in sentences]
    else:
        # Distribute sentences across scenes roughly evenly
        chunk_size = len(sentences) / num_scenes
        chunks = []
        for i in range(num_scenes):
            start = int(i * chunk_size)
            end = int((i + 1) * chunk_size)
            if i == num_scenes - 1:
                end = len(sentences)
            chunks.append(sentences[start:end])

    scenes = []
    for i, chunk in enumerate(chunks):
        scene_text = " ".join(chunk)
        image_prompt = generate_image_prompt(scene_text, i, len(chunks))
        scenes.append({
            "text": scene_text,
            "image_prompt": image_prompt,
            "duration": max(3, min(6, len(scene_text) // 40)),
        })

    return scenes


def generate_image_prompt(scene_text: str, scene_index: int, total_scenes: int) -> str:
    """Generate a descriptive image prompt from scene text."""
    # Extract key nouns and actions for the prompt
    text_lower = scene_text.lower()

    # Determine mood
    mood = "neutral"
    if any(w in text_lower for w in ["angry", "furious", "rage", "mad", "yell"]):
        mood = "tense, dramatic lighting"
    elif any(w in text_lower for w in ["happy", "laugh", "joy", "smile", "relief"]):
        mood = "warm, bright, joyful atmosphere"
    elif any(w in text_lower for w in ["sad", "cry", "hurt", "pain", "broken"]):
        mood = "melancholic, muted tones, emotional"
    elif any(w in text_lower for w in ["shock", "surprise", "jaw", "believe"]):
        mood = "dramatic, high contrast, suspenseful"
    elif any(w in text_lower for w in ["revenge", "petty", "karma", "justice"]):
        mood = "satisfying, dramatic reveal lighting"

    # Determine setting
    setting = "indoor setting"
    if any(w in text_lower for w in ["office", "work", "boss", "coworker", "job"]):
        setting = "modern office environment"
    elif any(w in text_lower for w in ["home", "house", "kitchen", "room", "bed"]):
        setting = "cozy home interior"
    elif any(w in text_lower for w in ["school", "class", "teacher", "student"]):
        setting = "school hallway or classroom"
    elif any(w in text_lower for w in ["car", "drive", "road", "traffic"]):
        setting = "urban street or car interior"
    elif any(w in text_lower for w in ["store", "shop", "mall", "restaurant"]):
        setting = "retail or restaurant setting"
    elif any(w in text_lower for w in ["phone", "text", "call", "message"]):
        setting = "close-up of person with phone"

    # Determine framing
    if scene_index == 0:
        framing = "establishing wide shot"
    elif scene_index == total_scenes - 1:
        framing = "close-up emotional shot"
    else:
        framing = "medium shot"

    # Truncate scene text for the prompt
    short_text = scene_text[:80].rstrip()
    if len(scene_text) > 80:
        short_text += "..."

    return (
        f"Cinematic {framing}, {setting}, {mood}. "
        f"Visual interpretation of: {short_text} "
        f"Photorealistic, shallow depth of field, film grain, 16:9 aspect ratio"
    )


# --- Story conversion ---

def story_id(entry) -> str:
    """Generate a unique ID for a Reddit post."""
    link = getattr(entry, "link", "") or getattr(entry, "id", "")
    return hashlib.md5(link.encode()).hexdigest()[:12]


def slugify(title: str) -> str:
    """Convert a title to a filename-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:60]


def entry_to_story_json(entry, subreddit: str) -> dict | None:
    """Convert an RSS entry into the reel pipeline story JSON format."""
    selftext = extract_selftext_from_rss(entry)
    selftext = clean_reddit_text(selftext)

    if len(selftext) < MIN_TEXT_LENGTH:
        return None
    if len(selftext) > MAX_TEXT_LENGTH:
        # Truncate to max length at a sentence boundary
        truncated = selftext[:MAX_TEXT_LENGTH]
        last_period = truncated.rfind(".")
        if last_period > MIN_TEXT_LENGTH:
            selftext = truncated[:last_period + 1]
        else:
            selftext = truncated

    title = html.unescape(getattr(entry, "title", "Untitled"))

    # Extract hook (first sentence)
    first_sentence_match = re.match(r"^(.+?[.!?])\s", selftext)
    hook = first_sentence_match.group(1) if first_sentence_match else selftext[:100]

    scenes = split_into_scenes(selftext)

    return {
        "title": slugify(title),
        "hook": hook,
        "narration": selftext,
        "scenes": scenes,
        "tags": ["reddit", subreddit.lower()],
        "category": "reddit-stories",
        "source_subreddit": subreddit,
        "language": "en",
    }


# --- Tracker ---

def load_tracker() -> dict:
    """Load the set of already-processed story IDs."""
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"processed_ids": [], "stories": []}


def save_tracker(tracker: dict):
    """Save the tracker to disk."""
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


# --- Scraping ---

def fetch_subreddit_rss(subreddit: str, sort: str = "top") -> list:
    """Fetch RSS feed for a subreddit."""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}/.rss?t=week&limit=25"

    # feedparser can handle URLs directly, but we set a user agent
    feed = feedparser.parse(
        url,
        request_headers={"User-Agent": USER_AGENT},
    )

    if feed.bozo and not feed.entries:
        print(f"  Warning: Could not fetch r/{subreddit} RSS feed")
        return []

    return feed.entries


def scrape_subreddit(
    subreddit: str,
    count: int = DEFAULT_COUNT,
    min_score: int = MIN_SCORE_DEFAULT,
    tracker: dict = None,
) -> list[dict]:
    """Scrape top stories from a subreddit and return story JSONs."""
    if tracker is None:
        tracker = load_tracker()

    print(f"Fetching r/{subreddit}...")
    entries = fetch_subreddit_rss(subreddit)

    if not entries:
        print(f"  No entries found for r/{subreddit}")
        return []

    stories = []
    skipped_dup = 0
    skipped_short = 0
    skipped_score = 0

    for entry in entries:
        if len(stories) >= count:
            break

        sid = story_id(entry)

        # Skip duplicates
        if sid in tracker.get("processed_ids", []):
            skipped_dup += 1
            continue

        # Check score if available
        score = extract_score_from_rss(entry)
        # RSS top feed posts are usually high-scoring.
        # Only filter if we actually found a score and it's below threshold.
        if score > 0 and score < min_score:
            skipped_score += 1
            continue

        story = entry_to_story_json(entry, subreddit)
        if story is None:
            skipped_short += 1
            continue

        story["_id"] = sid
        story["_score"] = score
        stories.append(story)

    status_parts = [f"  Found {len(stories)} stories"]
    if skipped_dup:
        status_parts.append(f"{skipped_dup} duplicates skipped")
    if skipped_short:
        status_parts.append(f"{skipped_short} too short/long")
    if skipped_score:
        status_parts.append(f"{skipped_score} below score threshold")
    print(", ".join(status_parts))

    return stories


def save_story(story: dict, tracker: dict) -> str:
    """Save a story JSON to the stories directory. Returns the filename."""
    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"reddit-{story['title']}.json"
    filepath = STORIES_DIR / filename

    # Remove internal tracking fields before saving
    save_data = {k: v for k, v in story.items() if not k.startswith("_")}

    with open(filepath, "w") as f:
        json.dump(save_data, f, indent=2)

    # Track as processed
    tracker.setdefault("processed_ids", []).append(story["_id"])
    tracker.setdefault("stories", []).append({
        "id": story["_id"],
        "title": story["title"],
        "subreddit": story["source_subreddit"],
        "file": filename,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "processed": False,
    })

    return filename


# --- CLI ---

def list_scraped_stories():
    """List all scraped stories and their processing status."""
    tracker = load_tracker()
    stories = tracker.get("stories", [])

    if not stories:
        print("No scraped stories yet. Run without --list to scrape some.")
        return

    unprocessed = [s for s in stories if not s.get("processed")]
    processed = [s for s in stories if s.get("processed")]

    if unprocessed:
        print(f"\nUnprocessed stories ({len(unprocessed)}):")
        print("-" * 60)
        for s in unprocessed:
            print(f"  r/{s['subreddit']:20s}  {s['title']}")
            print(f"  {'':20s}  File: {s['file']}")
            print(f"  {'':20s}  Scraped: {s.get('scraped_at', 'unknown')}")
            print()

    if processed:
        print(f"\nAlready processed ({len(processed)}):")
        print("-" * 60)
        for s in processed:
            print(f"  r/{s['subreddit']:20s}  {s['title']}")


def _update_length_filters(min_len: int, max_len: int):
    """Update module-level length filter globals."""
    global MIN_TEXT_LENGTH, MAX_TEXT_LENGTH
    MIN_TEXT_LENGTH = min_len
    MAX_TEXT_LENGTH = max_len


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Reddit stories for the reel pipeline"
    )
    parser.add_argument(
        "--sub",
        type=str,
        help="Specific subreddit to scrape (without r/ prefix)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"Number of stories per subreddit (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=MIN_SCORE_DEFAULT,
        help=f"Minimum upvote score (default: {MIN_SCORE_DEFAULT})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List scraped stories and their status",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=MIN_TEXT_LENGTH,
        help=f"Minimum text length in chars (default: {MIN_TEXT_LENGTH})",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=MAX_TEXT_LENGTH,
        help=f"Maximum text length in chars (default: {MAX_TEXT_LENGTH})",
    )

    args = parser.parse_args()

    if args.list:
        list_scraped_stories()
        return

    # Override module-level length filters with CLI args
    _update_length_filters(args.min_length, args.max_length)

    subreddits = [args.sub] if args.sub else DEFAULT_SUBREDDITS
    tracker = load_tracker()

    total_saved = 0

    for sub in subreddits:
        stories = scrape_subreddit(
            sub,
            count=args.count,
            min_score=args.min_score,
            tracker=tracker,
        )

        for story in stories:
            filename = save_story(story, tracker)
            print(f"  Saved: {filename}")
            total_saved += 1

        # Rate limit between subreddits
        if len(subreddits) > 1:
            time.sleep(2)

    save_tracker(tracker)

    print(f"\nDone. {total_saved} new stories saved to {STORIES_DIR}")
    if total_saved > 0:
        print("Run the reel pipeline to generate videos from these stories.")


if __name__ == "__main__":
    main()
