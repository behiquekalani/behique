#!/usr/bin/env python3
"""
TikTok posting helper.
Since TikTok's API is restricted, this prepares posts for manual upload:
- Copies caption + hashtags to clipboard
- Opens TikTok web upload page
- Logs scheduled posts to tiktok_queue.json

Usage:
  python3 tiktok_api.py --prepare "caption" --video path/to/video.mp4
  python3 tiktok_api.py --queue          # show pending queue
  python3 tiktok_api.py --clear ID       # mark queue item as posted
"""

import argparse
import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

PUBLISHER_DIR = Path(__file__).parent
QUEUE_FILE = PUBLISHER_DIR / "tiktok_queue.json"


def _clipboard(text):
    """Copy text to clipboard (macOS)."""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(text.encode())
        return True
    except Exception:
        return False


def _load_queue():
    """Load the queue from disk."""
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def _save_queue(queue):
    """Save the queue to disk."""
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def prepare_post(video_path, caption, hashtags=None, schedule_time=None):
    """
    Prepare a TikTok post for manual upload.
    Copies caption to clipboard, opens TikTok upload, logs to queue.
    """
    video = Path(video_path)
    if not video.exists():
        print(f"Warning: Video file not found: {video_path}")
        print("  Continuing anyway (will log to queue).")

    # Build full caption
    full_caption = caption
    if hashtags:
        tags = hashtags if isinstance(hashtags, list) else [h.strip() for h in hashtags.split(",")]
        tag_str = " ".join(t if t.startswith("#") else f"#{t}" for t in tags)
        full_caption = f"{caption}\n\n{tag_str}"

    # Copy to clipboard
    if _clipboard(full_caption):
        print(f"Caption copied to clipboard ({len(full_caption)} chars)")
    else:
        print("Could not copy to clipboard. Caption:")
        print(full_caption)

    # Open TikTok web upload
    webbrowser.open("https://www.tiktok.com/upload")
    print(f"Opened TikTok upload page.")
    if video.exists():
        print(f"Video file: {video.resolve()}")

    # Log to queue
    queue = _load_queue()
    entry = {
        "id": len(queue) + 1,
        "caption": caption,
        "hashtags": hashtags or [],
        "video_path": str(video.resolve()) if video.exists() else str(video_path),
        "status": "pending",
        "created": datetime.now().isoformat(),
        "scheduled": schedule_time,
        "posted": None,
    }
    queue.append(entry)
    _save_queue(queue)
    print(f"Queued as #{entry['id']} in {QUEUE_FILE.name}")

    return entry


def show_queue():
    """Display all items in the queue."""
    queue = _load_queue()
    if not queue:
        print("Queue is empty.")
        return
    pending = [q for q in queue if q["status"] == "pending"]
    posted = [q for q in queue if q["status"] == "posted"]
    print(f"TikTok Queue: {len(pending)} pending, {len(posted)} posted\n")
    for item in queue:
        status = "POSTED" if item["status"] == "posted" else "PENDING"
        cap = item["caption"][:50]
        date = item["created"][:10]
        print(f"  #{item['id']} [{status}] {date} | {cap}...")


def mark_posted(item_id):
    """Mark a queue item as posted."""
    queue = _load_queue()
    for item in queue:
        if item["id"] == item_id:
            item["status"] = "posted"
            item["posted"] = datetime.now().isoformat()
            _save_queue(queue)
            print(f"Marked #{item_id} as posted.")
            return True
    print(f"Item #{item_id} not found in queue.")
    return False


def main():
    parser = argparse.ArgumentParser(description="TikTok posting helper")
    parser.add_argument("--prepare", type=str, help="Caption for the post")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--hashtags", type=str, help="Comma-separated hashtags")
    parser.add_argument("--schedule", type=str, help="Schedule time (ISO format, for logging)")
    parser.add_argument("--queue", action="store_true", help="Show pending queue")
    parser.add_argument("--clear", type=int, help="Mark queue item as posted by ID")
    args = parser.parse_args()

    if args.queue:
        show_queue()
    elif args.clear:
        mark_posted(args.clear)
    elif args.prepare:
        if not args.video:
            print("Error: --video is required with --prepare")
            sys.exit(1)
        prepare_post(args.video, args.prepare, args.hashtags, args.schedule)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
