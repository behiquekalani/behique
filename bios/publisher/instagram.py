#!/usr/bin/env python3
"""
Instagram publishing helper.
Prepares posts for quick manual publishing or auto-publishes via Graph API.

For each due post:
- Copies caption to clipboard (pbcopy on Mac)
- Saves the image prompt for SD generation
- Opens Instagram web in default browser

If INSTAGRAM_ACCESS_TOKEN is set, attempts Graph API publish.
"""

import json
import os
import re
import subprocess
import webbrowser
from pathlib import Path

PUBLISHER_DIR = Path(__file__).parent
LOGS_DIR = PUBLISHER_DIR / "logs"


def parse_instagram_post(filepath: str) -> dict:
    """Parse an instagram-ready markdown file into structured data."""
    content = Path(filepath).read_text()

    result = {
        "title": "",
        "caption": "",
        "hashtags": "",
        "image_prompt": "",
        "carousel_slides": [],
        "best_time": "",
        "raw": content,
    }

    # Extract title
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract sections by ## headers
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

    for section in sections[1:]:  # skip first (before any ##)
        lines = section.strip().split("\n", 1)
        header = lines[0].strip().lower()
        body = lines[1].strip() if len(lines) > 1 else ""

        if "caption" in header:
            result["caption"] = body
        elif "hashtag" in header:
            result["hashtags"] = body
        elif "image prompt" in header:
            result["image_prompt"] = body
        elif "carousel" in header:
            slides = [
                line.strip()
                for line in body.split("\n")
                if line.strip() and line.strip().startswith("Slide")
            ]
            result["carousel_slides"] = slides
        elif "best time" in header:
            result["best_time"] = body

    return result


def copy_to_clipboard(text: str):
    """Copy text to macOS clipboard."""
    try:
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(text.encode("utf-8"))
        return True
    except Exception as e:
        print(f"  Clipboard error: {e}")
        return False


def prepare_post(schedule_entry: dict) -> dict:
    """
    Prepare an Instagram post for quick manual publishing.
    Returns parsed post data.
    """
    filepath = schedule_entry["file"]
    post_id = schedule_entry["id"]

    if not Path(filepath).exists():
        raise FileNotFoundError(f"Content file not found: {filepath}")

    post = parse_instagram_post(filepath)

    # Build full caption with hashtags
    full_caption = post["caption"]
    if post["hashtags"]:
        full_caption += "\n\n" + post["hashtags"]

    # Copy caption to clipboard
    if copy_to_clipboard(full_caption):
        print(f"  Caption copied to clipboard ({len(full_caption)} chars)")

    # Save image prompt for SD generation
    if post["image_prompt"]:
        prompt_file = LOGS_DIR / f"prompt-{post_id}.txt"
        prompt_file.write_text(post["image_prompt"])
        print(f"  Image prompt saved: {prompt_file}")

    # Try Graph API if token available
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    ig_account = os.environ.get("INSTAGRAM_ACCOUNT_ID")

    if token and ig_account:
        print("  Attempting Graph API publish...")
        success = graph_api_publish(token, ig_account, post)
        if success:
            print("  Published via Graph API")
            return post

    # Otherwise, open Instagram web
    print("  Opening Instagram web for manual posting...")
    webbrowser.open("https://www.instagram.com/")

    # Log the preparation
    log_entry = {
        "post_id": post_id,
        "title": post["title"],
        "caption_length": len(full_caption),
        "has_carousel": len(post["carousel_slides"]) > 0,
        "carousel_count": len(post["carousel_slides"]),
        "has_image_prompt": bool(post["image_prompt"]),
    }
    log_file = LOGS_DIR / f"ig-prep-{post_id}.json"
    log_file.write_text(json.dumps(log_entry, indent=2))

    return post


def graph_api_publish(token: str, account_id: str, post: dict) -> bool:
    """
    Publish via Instagram Graph API (requires Business account + image URL).
    This is a placeholder for when the API is configured.
    """
    try:
        import requests
    except ImportError:
        print("  requests library not installed, skipping API publish")
        return False

    # Graph API requires an image URL, not a local file.
    # For now, this is a stub. When image generation pipeline is ready,
    # upload the image to a public URL first, then use this.

    # Step 1: Create media container
    # POST https://graph.facebook.com/v19.0/{ig-user-id}/media
    #   image_url=<public_url>
    #   caption=<caption>
    #   access_token=<token>

    # Step 2: Publish media container
    # POST https://graph.facebook.com/v19.0/{ig-user-id}/media_publish
    #   creation_id=<container_id>
    #   access_token=<token>

    print("  Graph API publish: not yet configured (need image URL pipeline)")
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 instagram.py <path-to-post.md>")
        print("       python3 instagram.py preview <path-to-post.md>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "preview":
        if len(sys.argv) < 3:
            print("Usage: python3 instagram.py preview <path-to-post.md>")
            sys.exit(1)
        post = parse_instagram_post(sys.argv[2])
        print(f"\nTitle: {post['title']}")
        print(f"\nCaption ({len(post['caption'])} chars):")
        print(post["caption"][:300])
        if post["hashtags"]:
            print(f"\nHashtags: {post['hashtags'][:100]}...")
        if post["carousel_slides"]:
            print(f"\nCarousel: {len(post['carousel_slides'])} slides")
        if post["image_prompt"]:
            print(f"\nImage prompt: {post['image_prompt'][:100]}...")
        if post["best_time"]:
            print(f"\nBest time: {post['best_time']}")
    else:
        # Treat as file path
        filepath = cmd
        entry = {"id": "manual", "file": filepath, "platform": "instagram"}
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        prepare_post(entry)
