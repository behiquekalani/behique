#!/usr/bin/env python3
"""
Content scheduling engine for Behike publishing pipeline.
Reads ready content from content-empire, manages a publish queue,
and tracks post status across platforms.

Usage:
    python3 scheduler.py queue instagram 3    # Queue next 3 IG posts
    python3 scheduler.py queue twitter 5      # Queue next 5 tweets
    python3 scheduler.py list                 # Show full schedule
    python3 scheduler.py due                  # Show posts due now
    python3 scheduler.py publish              # Attempt to publish due items
    python3 scheduler.py stats                # Show queue stats
"""

import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PUBLISHER_DIR = Path(__file__).parent
SCHEDULE_FILE = PUBLISHER_DIR / "schedule.json"
CONTENT_BASE = Path.home() / "behique" / "Ceiba" / "projects" / "content-empire"

# Platform -> content directory mapping
PLATFORM_DIRS = {
    "instagram": CONTENT_BASE / "instagram-ready",
    "twitter": CONTENT_BASE / "twitter-en",
    "tiktok": CONTENT_BASE / "tiktok-en",
    "youtube": CONTENT_BASE / "youtube-scripts",
    "linkedin": CONTENT_BASE / "linkedin-en",
    "pinterest": CONTENT_BASE / "pinterest-en",
    "instagram-es": CONTENT_BASE / "instagram-es",
    "twitter-es": CONTENT_BASE / "twitter-es",
    "tiktok-es": CONTENT_BASE / "tiktok-es",
    "linkedin-es": CONTENT_BASE / "linkedin-es",
    "youtube-shorts": CONTENT_BASE / "youtube-shorts-en",
    "youtube-shorts-es": CONTENT_BASE / "youtube-shorts-es",
    "newsletter": CONTENT_BASE / "newsletter-en",
    "newsletter-es": CONTENT_BASE / "newsletter-es",
}

DEFAULT_TZ = "America/Puerto_Rico"


def load_schedule() -> list:
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE) as f:
            return json.load(f)
    return []


def save_schedule(schedule: list):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=2, default=str)


def get_queued_files(platform: str) -> set:
    """Get set of files already in the queue for a platform."""
    schedule = load_schedule()
    return {
        entry["file"]
        for entry in schedule
        if entry["platform"] == platform and entry["status"] in ("queued", "published")
    }


def get_available_content(platform: str) -> list:
    """Get content files not yet queued for a platform."""
    content_dir = PLATFORM_DIRS.get(platform)
    if not content_dir or not content_dir.exists():
        print(f"No content directory found for platform: {platform}")
        print(f"Available platforms: {', '.join(PLATFORM_DIRS.keys())}")
        return []

    queued = get_queued_files(platform)
    available = []
    for f in sorted(content_dir.iterdir()):
        if f.suffix == ".md" and str(f) not in queued:
            available.append(f)
    return available


def auto_schedule(
    platform: str,
    count: int = 1,
    posts_per_day: int = 1,
    start_time: str = "10:00",
    timezone: str = DEFAULT_TZ,
) -> list:
    """
    Queue content and automatically space posts throughout the day.
    Returns list of newly created schedule entries.
    """
    available = get_available_content(platform)
    if not available:
        print(f"No unqueued content available for {platform}")
        return []

    to_queue = available[:count]
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)

    # Parse start time
    hour, minute = map(int, start_time.split(":"))

    # Calculate time slots spread across the day
    if posts_per_day == 1:
        slots_minutes = [hour * 60 + minute]
    else:
        # Spread posts between start_time and 9 PM
        end_minutes = 21 * 60  # 9 PM
        start_minutes = hour * 60 + minute
        total_window = end_minutes - start_minutes
        gap = total_window // posts_per_day
        slots_minutes = [start_minutes + (i * gap) for i in range(posts_per_day)]

    schedule = load_schedule()
    new_entries = []
    day_offset = 0
    slot_index = 0

    for content_file in to_queue:
        # Calculate scheduled time
        slot_m = slots_minutes[slot_index]
        scheduled = now.replace(
            hour=slot_m // 60,
            minute=slot_m % 60,
            second=0,
            microsecond=0,
        ) + timedelta(days=day_offset)

        # If scheduled time is in the past, push to tomorrow
        if scheduled <= now:
            scheduled += timedelta(days=1)
            day_offset += 1

        entry = {
            "id": str(uuid.uuid4())[:8],
            "file": str(content_file),
            "platform": platform,
            "scheduled_time": scheduled.isoformat(),
            "status": "queued",
            "published_at": None,
            "queued_at": now.isoformat(),
        }

        schedule.append(entry)
        new_entries.append(entry)

        slot_index += 1
        if slot_index >= len(slots_minutes):
            slot_index = 0
            day_offset += 1

    save_schedule(schedule)
    return new_entries


def get_due(timezone: str = DEFAULT_TZ) -> list:
    """Return posts that should be published now."""
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    schedule = load_schedule()
    due = []
    for entry in schedule:
        if entry["status"] != "queued":
            continue
        scheduled = datetime.fromisoformat(entry["scheduled_time"])
        if scheduled <= now:
            due.append(entry)
    return due


def mark_published(post_id: str):
    """Mark a post as published."""
    schedule = load_schedule()
    tz = ZoneInfo(DEFAULT_TZ)
    now = datetime.now(tz)
    for entry in schedule:
        if entry["id"] == post_id:
            entry["status"] = "published"
            entry["published_at"] = now.isoformat()
            break
    save_schedule(schedule)


def mark_failed(post_id: str, reason: str = ""):
    """Mark a post as failed."""
    schedule = load_schedule()
    tz = ZoneInfo(DEFAULT_TZ)
    now = datetime.now(tz)
    for entry in schedule:
        if entry["id"] == post_id:
            entry["status"] = "failed"
            entry["failed_at"] = now.isoformat()
            entry["fail_reason"] = reason
            break
    save_schedule(schedule)


def list_schedule(status_filter: str = None):
    """Print the current schedule."""
    schedule = load_schedule()
    if status_filter:
        schedule = [e for e in schedule if e["status"] == status_filter]

    if not schedule:
        print("Schedule is empty.")
        return

    print(f"\n{'ID':<10} {'Platform':<15} {'Status':<12} {'Scheduled':<22} {'File'}")
    print("-" * 100)
    for entry in sorted(schedule, key=lambda x: x["scheduled_time"]):
        filename = Path(entry["file"]).name
        sched = entry["scheduled_time"][:16].replace("T", " ")
        print(f"{entry['id']:<10} {entry['platform']:<15} {entry['status']:<12} {sched:<22} {filename}")
    print(f"\nTotal: {len(schedule)} posts")


def show_stats():
    """Show queue statistics."""
    schedule = load_schedule()
    if not schedule:
        print("No posts in schedule.")
        return

    by_status = {}
    by_platform = {}
    for e in schedule:
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1
        by_platform[e["platform"]] = by_platform.get(e["platform"], 0) + 1

    print("\n--- Schedule Stats ---")
    print(f"Total posts: {len(schedule)}")
    print("\nBy status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print("\nBy platform:")
    for platform, count in sorted(by_platform.items()):
        print(f"  {platform}: {count}")

    due = get_due()
    print(f"\nDue now: {len(due)}")


def publish_due():
    """Attempt to publish all due posts."""
    due = get_due()
    if not due:
        print("Nothing due right now.")
        return

    print(f"\n{len(due)} post(s) due for publishing:\n")

    for entry in due:
        platform = entry["platform"]
        print(f"  [{entry['id']}] {platform}: {Path(entry['file']).name}")

        try:
            if platform in ("instagram", "instagram-es"):
                from instagram import prepare_post
                prepare_post(entry)
            elif platform in ("youtube", "youtube-shorts", "youtube-shorts-es"):
                from youtube import prepare_upload
                prepare_upload(entry)
            else:
                # Generic: just print the content for manual posting
                print(f"    -> Manual post required for {platform}")
                content_path = Path(entry["file"])
                if content_path.exists():
                    text = content_path.read_text()[:200]
                    print(f"    Preview: {text}...")

            mark_published(entry["id"])
            print(f"    -> Marked as published")
        except Exception as e:
            mark_failed(entry["id"], str(e))
            print(f"    -> FAILED: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "queue":
        if len(sys.argv) < 3:
            print("Usage: python3 scheduler.py queue <platform> [count] [posts_per_day] [start_time]")
            print(f"Platforms: {', '.join(PLATFORM_DIRS.keys())}")
            return
        platform = sys.argv[2]
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        ppd = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        start = sys.argv[5] if len(sys.argv) > 5 else "10:00"

        new = auto_schedule(platform, count=count, posts_per_day=ppd, start_time=start)
        if new:
            print(f"\nQueued {len(new)} post(s) for {platform}:")
            for entry in new:
                sched = entry["scheduled_time"][:16].replace("T", " ")
                print(f"  [{entry['id']}] {sched} - {Path(entry['file']).name}")

    elif cmd == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        list_schedule(status)

    elif cmd == "due":
        due = get_due()
        if due:
            print(f"\n{len(due)} post(s) due now:")
            for entry in due:
                print(f"  [{entry['id']}] {entry['platform']}: {Path(entry['file']).name}")
        else:
            print("Nothing due right now.")

    elif cmd == "publish":
        publish_due()

    elif cmd == "stats":
        show_stats()

    elif cmd == "clear":
        status = sys.argv[2] if len(sys.argv) > 2 else "published"
        schedule = load_schedule()
        before = len(schedule)
        schedule = [e for e in schedule if e["status"] != status]
        save_schedule(schedule)
        print(f"Cleared {before - len(schedule)} {status} entries.")

    elif cmd == "platforms":
        print("\nAvailable platforms:")
        for name, path in sorted(PLATFORM_DIRS.items()):
            exists = path.exists()
            count = len(list(path.glob("*.md"))) if exists else 0
            status = f"{count} files" if exists else "not found"
            print(f"  {name:<20} {status:<15} {path}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
