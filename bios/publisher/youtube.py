#!/usr/bin/env python3
"""
YouTube publishing helper.
Formats video metadata from script files and handles upload preparation.

If YOUTUBE_API_KEY is set, uploads via YouTube Data API v3.
Otherwise generates upload instructions with pre-formatted metadata.
"""

import json
import os
import re
import sys
from pathlib import Path

PUBLISHER_DIR = Path(__file__).parent
LOGS_DIR = PUBLISHER_DIR / "logs"


def parse_youtube_script(filepath: str) -> dict:
    """Parse a youtube script markdown file into structured metadata."""
    content = Path(filepath).read_text()

    result = {
        "title": "",
        "description": "",
        "tags": [],
        "script": "",
        "thumbnail_prompt": "",
        "category": "Science & Technology",
        "privacy": "public",
        "raw": content,
    }

    # Extract title from first # heading
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()
        # Clean title: remove batch/script prefixes
        result["title"] = re.sub(r"^(Script|Video|Batch)\s*\d*\s*[-:]\s*", "", result["title"])

    # Extract sections
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n", 1)
        header = lines[0].strip().lower()
        body = lines[1].strip() if len(lines) > 1 else ""

        if any(x in header for x in ["description", "desc"]):
            result["description"] = body
        elif "tag" in header:
            # Parse comma-separated or hashtag-style tags
            raw_tags = body.replace("#", "").replace("\n", ",")
            result["tags"] = [t.strip() for t in raw_tags.split(",") if t.strip()]
        elif "script" in header or "content" in header:
            result["script"] = body
        elif "thumbnail" in header:
            result["thumbnail_prompt"] = body
        elif "categor" in header:
            result["category"] = body.strip()

    # If no description found, generate from script
    if not result["description"] and result["script"]:
        # Take first 2 paragraphs as description
        paragraphs = [p.strip() for p in result["script"].split("\n\n") if p.strip()]
        result["description"] = "\n\n".join(paragraphs[:2])

    # If no tags, extract from content
    if not result["tags"]:
        hashtags = re.findall(r"#(\w+)", content)
        if hashtags:
            result["tags"] = hashtags[:15]

    return result


def format_upload_instructions(video_data: dict) -> str:
    """Generate formatted upload instructions for manual YouTube upload."""
    instructions = []
    instructions.append("=" * 60)
    instructions.append("YOUTUBE UPLOAD INSTRUCTIONS")
    instructions.append("=" * 60)
    instructions.append("")
    instructions.append(f"TITLE:")
    instructions.append(f"  {video_data['title']}")
    instructions.append("")
    instructions.append(f"DESCRIPTION:")
    instructions.append(f"  {video_data['description'][:500]}")
    instructions.append("")

    if video_data["tags"]:
        instructions.append(f"TAGS:")
        instructions.append(f"  {', '.join(video_data['tags'][:15])}")
        instructions.append("")

    instructions.append(f"CATEGORY: {video_data['category']}")
    instructions.append(f"PRIVACY: {video_data['privacy']}")
    instructions.append("")

    if video_data["thumbnail_prompt"]:
        instructions.append("THUMBNAIL PROMPT:")
        instructions.append(f"  {video_data['thumbnail_prompt']}")
        instructions.append("")

    instructions.append("STEPS:")
    instructions.append("  1. Go to https://studio.youtube.com/")
    instructions.append("  2. Click 'Create' -> 'Upload video'")
    instructions.append("  3. Select your video file")
    instructions.append("  4. Copy the title and description above")
    instructions.append("  5. Add tags")
    instructions.append("  6. Set visibility and publish")
    instructions.append("=" * 60)

    return "\n".join(instructions)


def prepare_upload(schedule_entry: dict) -> dict:
    """Prepare a YouTube video for upload."""
    filepath = schedule_entry["file"]
    post_id = schedule_entry["id"]

    if not Path(filepath).exists():
        raise FileNotFoundError(f"Script file not found: {filepath}")

    video = parse_youtube_script(filepath)

    api_key = os.environ.get("YOUTUBE_API_KEY")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")

    if api_key and client_secret:
        print("  Attempting YouTube API upload...")
        success = api_upload(video)
        if success:
            return video

    # Generate upload instructions
    instructions = format_upload_instructions(video)
    print(instructions)

    # Save instructions to file
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    instructions_file = LOGS_DIR / f"yt-upload-{post_id}.txt"
    instructions_file.write_text(instructions)
    print(f"\n  Instructions saved: {instructions_file}")

    # Save metadata as JSON for potential API use later
    meta_file = LOGS_DIR / f"yt-meta-{post_id}.json"
    meta = {k: v for k, v in video.items() if k != "raw"}
    meta_file.write_text(json.dumps(meta, indent=2))

    return video


def api_upload(video_data: dict) -> bool:
    """
    Upload via YouTube Data API v3.
    Requires OAuth2 credentials. Placeholder for future implementation.
    """
    # YouTube API upload requires:
    # 1. OAuth2 flow (not just API key)
    # 2. google-api-python-client + google-auth libraries
    # 3. A video file (not just metadata)
    #
    # When ready:
    # pip install google-api-python-client google-auth-oauthlib
    # Use MediaFileUpload for the video file
    # Set snippet (title, description, tags, categoryId)
    # Set status (privacyStatus)

    print("  YouTube API upload: not yet configured")
    print("  Install: pip install google-api-python-client google-auth-oauthlib")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 youtube.py <path-to-script.md>")
        print("       python3 youtube.py preview <path-to-script.md>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "preview":
        if len(sys.argv) < 3:
            print("Usage: python3 youtube.py preview <path-to-script.md>")
            sys.exit(1)
        video = parse_youtube_script(sys.argv[2])
        print(f"\nTitle: {video['title']}")
        print(f"Description: {video['description'][:200]}...")
        print(f"Tags: {', '.join(video['tags'][:10])}")
        print(f"Category: {video['category']}")
        if video["thumbnail_prompt"]:
            print(f"Thumbnail: {video['thumbnail_prompt'][:100]}...")
    else:
        filepath = cmd
        entry = {"id": "manual", "file": filepath, "platform": "youtube"}
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        prepare_upload(entry)
