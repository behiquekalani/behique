#!/usr/bin/env python3
"""
Instagram Posting Preparation Tool.

Manages a posting queue, packages posts for upload, tracks schedules
across multiple accounts. Optionally auto-posts via Instagram Graph API
if INSTAGRAM_TOKEN env var is set.

Accounts: behikeai, kalaniandrez, dulc3recuerdo, s0ftrewind

Usage:
    python3 instagram_poster.py --list
    python3 instagram_poster.py --add --image path.jpg --caption "text" --account behikeai
    python3 instagram_poster.py --add --image path.jpg --caption "text" --schedule "2026-03-23 12:00"
    python3 instagram_poster.py --next
    python3 instagram_poster.py --done ID
    python3 instagram_poster.py --calendar
    python3 instagram_poster.py --import-daily
    python3 instagram_poster.py --stats
    python3 instagram_poster.py --post ID          (requires INSTAGRAM_TOKEN)
    python3 instagram_poster.py --auto-post         (requires INSTAGRAM_TOKEN)

Copyright 2026 Behike.
"""

import json
import os
import sys
import shutil
import argparse
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent.parent / "Ceiba" / "news"
QUEUE_FILE = BASE_DIR / "post-queue.json"
READY_DIR = BASE_DIR / "ready-to-post"
DAILY_DIR = BASE_DIR / "daily"
STATS_FILE = BASE_DIR / "post-stats.json"

ACCOUNTS = ["behikeai", "kalaniandrez", "dulc3recuerdo", "s0ftrewind"]

MAX_CAPTION_LEN = 2200
MAX_HASHTAGS = 30
TARGET_SIZE = (1080, 1080)


# ---------------------------------------------------------------------------
# Queue helpers
# ---------------------------------------------------------------------------

def load_queue() -> list:
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return []


def save_queue(queue: list):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2, default=str)


def gen_id(caption: str, ts: str) -> str:
    raw = f"{caption[:40]}{ts}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def load_stats() -> dict:
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"posted": []}


def save_stats(stats: dict):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def count_hashtags(text: str) -> int:
    return text.count("#")


def validate_caption(caption: str) -> list:
    issues = []
    if len(caption) > MAX_CAPTION_LEN:
        issues.append(f"Caption too long: {len(caption)}/{MAX_CAPTION_LEN} chars")
    ht = count_hashtags(caption)
    if ht > MAX_HASHTAGS:
        issues.append(f"Too many hashtags: {ht}/{MAX_HASHTAGS}")
    return issues


# ---------------------------------------------------------------------------
# Image processing
# ---------------------------------------------------------------------------

def resize_image(src: Path, dst: Path) -> bool:
    """Resize image to 1080x1080. Returns True if PIL was available."""
    try:
        from PIL import Image
        img = Image.open(src)
        img = img.resize(TARGET_SIZE, Image.LANCZOS)
        img.save(dst, quality=95)
        return True
    except ImportError:
        shutil.copy2(src, dst)
        return False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args):
    queue = load_queue()
    now = datetime.now().isoformat()
    schedule = args.schedule or ""
    account = args.account or "behikeai"

    if account not in ACCOUNTS:
        print(f"[!] Unknown account: {account}")
        print(f"    Valid accounts: {', '.join(ACCOUNTS)}")
        return

    caption = args.caption or ""
    issues = validate_caption(caption)
    if issues:
        for issue in issues:
            print(f"[!] {issue}")
        print("    Post queued anyway. Fix before posting.")

    image_path = Path(args.image) if args.image else None
    if image_path and not image_path.exists():
        print(f"[!] Image not found: {image_path}")
        return

    post_id = gen_id(caption, now)

    entry = {
        "id": post_id,
        "image": str(image_path) if image_path else "",
        "caption": caption,
        "account": account,
        "schedule": schedule,
        "status": "queued",
        "created": now,
        "issues": issues,
    }

    queue.append(entry)
    save_queue(queue)

    # Package it
    package_post(entry)

    print(f"[+] Post queued: {post_id}")
    print(f"    Account: {account}")
    print(f"    Schedule: {schedule or 'unscheduled'}")
    if issues:
        print(f"    Warnings: {len(issues)}")


def package_post(entry: dict):
    """Create a ready-to-post package for a queue entry."""
    pkg_dir = READY_DIR / entry["id"]
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Save caption
    with open(pkg_dir / "caption.txt", "w") as f:
        f.write(entry["caption"])

    # Process image
    if entry.get("image") and Path(entry["image"]).exists():
        src = Path(entry["image"])
        dst = pkg_dir / f"image{src.suffix}"
        pil_ok = resize_image(src, dst)
        if not pil_ok:
            entry.setdefault("issues", [])
            if "PIL not available, image not resized" not in entry.get("issues", []):
                entry["issues"].append("PIL not available, image not resized")

    # Save metadata
    meta = {
        "id": entry["id"],
        "account": entry.get("account", "behikeai"),
        "schedule": entry.get("schedule", ""),
        "created": entry.get("created", ""),
        "hashtag_count": count_hashtags(entry.get("caption", "")),
        "caption_length": len(entry.get("caption", "")),
        "issues": entry.get("issues", []),
    }
    with open(pkg_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)


def cmd_list(args):
    queue = load_queue()
    if not queue:
        print("Queue is empty.")
        return

    for entry in queue:
        status_icon = {
            "queued": "[ ]",
            "posted": "[x]",
            "failed": "[!]",
        }.get(entry.get("status", "queued"), "[ ]")

        schedule = entry.get("schedule", "")
        sched_str = f" @ {schedule}" if schedule else ""
        caption_preview = entry.get("caption", "")[:60]
        if len(entry.get("caption", "")) > 60:
            caption_preview += "..."

        print(f"{status_icon} {entry['id']}  [{entry.get('account', '?')}]{sched_str}")
        print(f"    {caption_preview}")
        if entry.get("issues"):
            for issue in entry["issues"]:
                print(f"    ! {issue}")
        print()


def cmd_next(args):
    queue = load_queue()
    pending = [e for e in queue if e.get("status") == "queued"]

    if not pending:
        print("No pending posts.")
        return

    # Sort by schedule time, unscheduled last
    def sort_key(e):
        s = e.get("schedule", "")
        if s:
            try:
                return datetime.fromisoformat(s)
            except ValueError:
                pass
        return datetime.max

    pending.sort(key=sort_key)
    entry = pending[0]

    print(f"Next post: {entry['id']}")
    print(f"  Account:  {entry.get('account', '?')}")
    print(f"  Schedule: {entry.get('schedule', 'unscheduled')}")
    print(f"  Caption:  {entry.get('caption', '')[:100]}")
    print(f"  Image:    {entry.get('image', 'none')}")
    print(f"  Package:  {READY_DIR / entry['id']}")

    if entry.get("issues"):
        print("  Issues:")
        for issue in entry["issues"]:
            print(f"    - {issue}")


def cmd_done(args):
    queue = load_queue()
    found = False

    for entry in queue:
        if entry["id"] == args.done:
            entry["status"] = "posted"
            entry["posted_at"] = datetime.now().isoformat()
            found = True

            # Track in stats
            stats = load_stats()
            stats["posted"].append({
                "id": entry["id"],
                "account": entry.get("account", "?"),
                "posted_at": entry["posted_at"],
            })
            save_stats(stats)
            break

    if found:
        save_queue(queue)
        print(f"[x] Marked as posted: {args.done}")
    else:
        print(f"[!] Post not found: {args.done}")


def cmd_calendar(args):
    queue = load_queue()
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=7)

    print(f"Posting Calendar: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
    print("=" * 60)

    for account in ACCOUNTS:
        posts = [
            e for e in queue
            if e.get("account") == account and e.get("schedule")
        ]

        # Filter to this week
        week_posts = []
        for p in posts:
            try:
                sched = datetime.fromisoformat(p["schedule"])
                if week_start <= sched < week_end:
                    week_posts.append(p)
            except (ValueError, KeyError):
                continue

        week_posts.sort(key=lambda p: p.get("schedule", ""))

        print(f"\n@{account} ({len(week_posts)} this week)")
        if not week_posts:
            print("  (no scheduled posts)")
        for p in week_posts:
            status = "DONE" if p.get("status") == "posted" else "PENDING"
            sched = p.get("schedule", "?")
            caption = p.get("caption", "")[:50]
            print(f"  {sched}  [{status}]  {caption}")


def cmd_import_daily(args):
    today = datetime.now().strftime("%Y-%m-%d")
    daily_path = DAILY_DIR / today

    if not daily_path.exists():
        print(f"[!] No daily folder found: {daily_path}")
        print("    Expected structure: Ceiba/news/daily/YYYY-MM-DD/")
        return

    imported = 0
    queue = load_queue()
    existing_images = {e.get("image") for e in queue}

    for item in sorted(daily_path.iterdir()):
        if item.is_dir():
            # Look for post data inside subdirectories
            caption_file = item / "caption.txt"
            caption = ""
            if caption_file.exists():
                caption = caption_file.read_text().strip()

            # Find image
            image = None
            for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                candidates = list(item.glob(f"*{ext}"))
                if candidates:
                    image = candidates[0]
                    break

            if not image and not caption:
                continue

            image_str = str(image) if image else ""
            if image_str in existing_images and image_str:
                continue

            # Determine account based on content type
            account = _auto_assign_account(item, caption)

            now = datetime.now().isoformat()
            post_id = gen_id(caption, now)

            entry = {
                "id": post_id,
                "image": image_str,
                "caption": caption,
                "account": account,
                "schedule": "",
                "status": "queued",
                "created": now,
                "issues": validate_caption(caption),
            }

            queue.append(entry)
            package_post(entry)
            imported += 1

        elif item.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            # Standalone image file
            image_str = str(item)
            if image_str in existing_images:
                continue

            # Check for matching caption file
            caption_file = item.with_suffix(".txt")
            caption = ""
            if caption_file.exists():
                caption = caption_file.read_text().strip()

            account = _auto_assign_account(item, caption)
            now = datetime.now().isoformat()
            post_id = gen_id(caption or item.name, now)

            entry = {
                "id": post_id,
                "image": image_str,
                "caption": caption,
                "account": account,
                "schedule": "",
                "status": "queued",
                "created": now,
                "issues": validate_caption(caption) if caption else ["No caption provided"],
            }

            queue.append(entry)
            package_post(entry)
            imported += 1

    save_queue(queue)
    print(f"[+] Imported {imported} posts from {daily_path}")


def _auto_assign_account(path: Path, caption: str) -> str:
    """Auto-assign account based on content type and language."""
    name_lower = path.name.lower()

    # Carousel content goes to behikeai
    if "carousel" in name_lower or "slide" in name_lower:
        return "behikeai"

    # Reel content: check language
    if "reel" in name_lower or "video" in name_lower:
        # Simple Spanish detection
        spanish_markers = ["el", "la", "de", "en", "por", "como", "para", "que"]
        caption_words = caption.lower().split() if caption else []
        spanish_count = sum(1 for w in caption_words if w in spanish_markers)

        if spanish_count >= 2:
            return "dulc3recuerdo"
        return "s0ftrewind"

    # Default
    return "behikeai"


def cmd_stats(args):
    queue = load_queue()
    stats = load_stats()
    posted_list = stats.get("posted", [])

    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())

    print("Instagram Poster Stats")
    print("=" * 40)

    # Per-account breakdown
    for account in ACCOUNTS:
        total_posted = len([p for p in posted_list if p.get("account") == account])
        in_queue = len([
            e for e in queue
            if e.get("account") == account and e.get("status") == "queued"
        ])

        # This week
        this_week = 0
        for p in posted_list:
            if p.get("account") != account:
                continue
            try:
                posted_at = datetime.fromisoformat(p["posted_at"])
                if posted_at >= week_start:
                    this_week += 1
            except (ValueError, KeyError):
                continue

        print(f"\n@{account}")
        print(f"  Total posted:  {total_posted}")
        print(f"  This week:     {this_week}")
        print(f"  In queue:      {in_queue}")

    # Totals
    total_queued = len([e for e in queue if e.get("status") == "queued"])
    total_posted = len(posted_list)
    print(f"\nOverall: {total_posted} posted, {total_queued} in queue")


# ---------------------------------------------------------------------------
# Instagram Graph API (optional)
# ---------------------------------------------------------------------------

def get_api_token() -> str:
    token = os.environ.get("INSTAGRAM_TOKEN", "")
    if not token:
        print("[!] INSTAGRAM_TOKEN env var not set.")
        print("    Set it to use auto-posting features.")
        print("    Requires a Facebook Business account + Instagram Graph API access.")
    return token


def cmd_post(args):
    token = get_api_token()
    if not token:
        return

    queue = load_queue()
    entry = None
    for e in queue:
        if e["id"] == args.post:
            entry = e
            break

    if not entry:
        print(f"[!] Post not found: {args.post}")
        return

    if entry.get("status") == "posted":
        print(f"[!] Already posted: {args.post}")
        return

    success = _api_publish(entry, token)
    if success:
        entry["status"] = "posted"
        entry["posted_at"] = datetime.now().isoformat()
        save_queue(queue)

        stats = load_stats()
        stats["posted"].append({
            "id": entry["id"],
            "account": entry.get("account", "?"),
            "posted_at": entry["posted_at"],
        })
        save_stats(stats)
        print(f"[x] Posted via API: {args.post}")
    else:
        entry["status"] = "failed"
        save_queue(queue)
        print(f"[!] Failed to post: {args.post}")


def cmd_auto_post(args):
    token = get_api_token()
    if not token:
        return

    queue = load_queue()
    now = datetime.now()
    due = []

    for e in queue:
        if e.get("status") != "queued":
            continue
        if not e.get("schedule"):
            continue
        try:
            sched = datetime.fromisoformat(e["schedule"])
            if sched <= now:
                due.append(e)
        except ValueError:
            continue

    if not due:
        print("No posts due for auto-posting.")
        return

    print(f"Found {len(due)} post(s) due. Publishing...")

    stats = load_stats()
    for entry in due:
        success = _api_publish(entry, token)
        if success:
            entry["status"] = "posted"
            entry["posted_at"] = datetime.now().isoformat()
            stats["posted"].append({
                "id": entry["id"],
                "account": entry.get("account", "?"),
                "posted_at": entry["posted_at"],
            })
            print(f"  [x] {entry['id']} -> @{entry.get('account', '?')}")
        else:
            entry["status"] = "failed"
            print(f"  [!] {entry['id']} FAILED")

    save_queue(queue)
    save_stats(stats)


def _api_publish(entry: dict, token: str) -> bool:
    """
    Publish a post via Instagram Graph API.
    Requires: Facebook Business account, Instagram Graph API token,
    and a publicly accessible image URL.

    This is a basic implementation. For production use, you would need
    to handle image uploads to a public URL first.
    """
    try:
        import urllib.request
        import urllib.parse

        ig_user_id = os.environ.get("INSTAGRAM_USER_ID", "")
        if not ig_user_id:
            print("[!] INSTAGRAM_USER_ID env var not set.")
            return False

        image_url = entry.get("image_url", "")
        if not image_url:
            print("[!] Post needs a public image_url for API posting.")
            print("    Local images must be uploaded to a public URL first.")
            return False

        # Step 1: Create media container
        create_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
        params = urllib.parse.urlencode({
            "image_url": image_url,
            "caption": entry.get("caption", ""),
            "access_token": token,
        })

        req = urllib.request.Request(f"{create_url}?{params}", method="POST")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            container_id = data.get("id")

        if not container_id:
            print("[!] Failed to create media container.")
            return False

        # Step 2: Publish
        publish_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
        params = urllib.parse.urlencode({
            "creation_id": container_id,
            "access_token": token,
        })

        req = urllib.request.Request(f"{publish_url}?{params}", method="POST")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return "id" in data

    except Exception as e:
        print(f"[!] API error: {e}")
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Instagram posting preparation tool. Copyright 2026 Behike."
    )

    # Modes
    parser.add_argument("--list", action="store_true", help="List all queued posts")
    parser.add_argument("--add", action="store_true", help="Add a post to the queue")
    parser.add_argument("--next", action="store_true", help="Show the next due post")
    parser.add_argument("--done", type=str, help="Mark a post as done by ID")
    parser.add_argument("--calendar", action="store_true", help="Show this week's posting calendar")
    parser.add_argument("--import-daily", action="store_true", help="Import from daily news pipeline")
    parser.add_argument("--stats", action="store_true", help="Show posting statistics")
    parser.add_argument("--post", type=str, help="Post a specific item via API (requires INSTAGRAM_TOKEN)")
    parser.add_argument("--auto-post", action="store_true", help="Auto-post all due items via API")

    # Add-mode options
    parser.add_argument("--image", type=str, help="Path to image file")
    parser.add_argument("--caption", type=str, help="Post caption text")
    parser.add_argument("--account", type=str, help=f"Account: {', '.join(ACCOUNTS)}")
    parser.add_argument("--schedule", type=str, help="Schedule time: YYYY-MM-DD HH:MM")

    args = parser.parse_args()

    # Route to command
    if args.add:
        cmd_add(args)
    elif args.list:
        cmd_list(args)
    elif args.next:
        cmd_next(args)
    elif args.done:
        cmd_done(args)
    elif args.calendar:
        cmd_calendar(args)
    elif args.import_daily:
        cmd_import_daily(args)
    elif args.stats:
        cmd_stats(args)
    elif args.post:
        cmd_post(args)
    elif args.auto_post:
        cmd_auto_post(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
