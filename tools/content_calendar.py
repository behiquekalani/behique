#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Smart Content Calendar. Auto-generates a 7-day posting calendar based on
available content, best posting times, content type rotation, and account
assignment rules.

Usage:
    python3 content_calendar.py --generate            # generate next 7 days
    python3 content_calendar.py --today                # what to post today
    python3 content_calendar.py --reschedule           # re-shuffle the calendar
    python3 content_calendar.py --show                 # display current calendar
    python3 content_calendar.py --config               # show scheduling config
    python3 content_calendar.py --help

Output:
    Ceiba/news/calendar-YYYY-MM-DD.md   (human readable)
    Ceiba/news/calendar-YYYY-MM-DD.json (machine readable)
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
QUEUE_FILE = NEWS_DIR / "post-queue.json"
ANALYTICS_FILE = NEWS_DIR / "analytics.json"
INSIGHTS_FILE = NEWS_DIR / "performance-insights.json"
SCRIPTS_DIR = NEWS_DIR / "scripts"
DAILY_DIR = NEWS_DIR / "daily"
MEME_DIR = NEWS_DIR / "memes"
READY_DIR = NEWS_DIR / "ready-to-post"

ACCOUNTS = ["behikeai", "kalaniandrez", "dulc3recuerdo", "s0ftrewind"]

# --- Copywriting framework rotation ---
FRAMEWORKS = ["PAS", "BAB", "AIDCA", "Story-Lesson", "Contrarian", "Data-Led", "Question-Answer", "Confession"]
FRAMEWORK_LOG = NEWS_DIR / "framework-usage.json"
CAROUSEL_THEME_LOG = NEWS_DIR / "carousel-themes.json"


def load_framework_usage() -> dict:
    """Load the framework usage log."""
    if FRAMEWORK_LOG.exists():
        try:
            with open(FRAMEWORK_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return {"usage": []}


def save_framework_usage(data: dict):
    """Save framework usage log."""
    FRAMEWORK_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(FRAMEWORK_LOG, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_next_framework() -> str:
    """Pick the next copywriting framework, enforcing rotation.

    Rules:
    - If a framework was used 3+ times in the last 7 days, skip it.
    - Prefer the least-recently-used framework.
    - PAS is capped at 30% (max 3 out of every 10 posts).
    """
    data = load_framework_usage()
    usage = data.get("usage", [])

    now = datetime.now()
    week_ago = now - timedelta(days=7)

    # Count usage in last 7 days
    recent = [u for u in usage if _parse_iso(u.get("date", "")) >= week_ago]
    counts = defaultdict(int)
    for u in recent:
        fw = u.get("framework", "")
        if fw:
            counts[fw] += 1

    # Filter out overused frameworks
    available = []
    for fw in FRAMEWORKS:
        count = counts.get(fw, 0)
        if fw == "PAS" and count >= 3:
            continue  # PAS capped at ~30%
        if count >= 3:
            continue  # Any framework capped at 3x/week
        available.append(fw)

    if not available:
        available = FRAMEWORKS  # Reset if all are maxed

    # Pick the least-recently-used
    last_used = {}
    for u in reversed(usage):
        fw = u.get("framework", "")
        if fw and fw not in last_used:
            last_used[fw] = u.get("date", "")

    # Sort available by least recently used
    def sort_key(fw):
        last = last_used.get(fw, "")
        return last if last else "0000"

    available.sort(key=sort_key)
    return available[0]


def log_framework_usage(framework: str, content_id: str = ""):
    """Log that a framework was used."""
    data = load_framework_usage()
    data["usage"].append({
        "framework": framework,
        "date": datetime.now().isoformat(),
        "content_id": content_id,
    })
    # Keep only last 60 entries
    data["usage"] = data["usage"][-60:]
    save_framework_usage(data)


def load_carousel_themes() -> dict:
    """Load carousel theme usage for variety enforcement."""
    if CAROUSEL_THEME_LOG.exists():
        try:
            with open(CAROUSEL_THEME_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return {"themes": []}


def save_carousel_themes(data: dict):
    """Save carousel theme usage."""
    CAROUSEL_THEME_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CAROUSEL_THEME_LOG, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_next_carousel_color() -> str:
    """Pick a carousel accent color, enforcing variety.
    Avoids repeating the same color in consecutive posts."""
    colors = ["blue", "green", "orange", "purple", "red", "teal", "yellow", "pink"]
    data = load_carousel_themes()
    recent = data.get("themes", [])[-5:]
    recent_colors = [t.get("color", "") for t in recent]

    for color in colors:
        if color not in recent_colors:
            return color
    return colors[0]


def log_carousel_theme(color: str, layout: str = "", content_id: str = ""):
    """Log a carousel theme choice."""
    data = load_carousel_themes()
    data["themes"].append({
        "color": color,
        "layout": layout,
        "date": datetime.now().isoformat(),
        "content_id": content_id,
    })
    data["themes"] = data["themes"][-60:]
    save_carousel_themes(data)


def _parse_iso(iso_str: str) -> datetime:
    """Parse ISO datetime string, returning epoch on failure."""
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return datetime.min


# --- Default scheduling config ---
# Times in 24h format. These are starting defaults.
# The system will adjust based on performance_tracker insights.
DEFAULT_CONFIG = {
    "posts_per_day": {
        "behikeai": 2,
        "kalaniandrez": 1,
        "dulc3recuerdo": 1,
        "s0ftrewind": 1,
    },
    "best_times": {
        # Hour slots in 24h format, ordered by priority
        "behikeai": [9, 12, 18],
        "kalaniandrez": [10, 17, 20],
        "dulc3recuerdo": [11, 15, 19],
        "s0ftrewind": [12, 18, 21],
    },
    "account_content_rules": {
        # Which content types go to which account
        "behikeai": ["carousel", "news", "education", "quote"],
        "kalaniandrez": ["reel", "story", "education"],
        "dulc3recuerdo": ["meme", "quote", "reel"],
        "s0ftrewind": ["meme", "reel", "story"],
    },
    "rotation_rules": {
        # Max consecutive posts of same type per account
        "max_consecutive_same_type": 2,
        # Minimum gap (hours) between posts on same account
        "min_gap_hours": 4,
    },
}


def load_config() -> dict:
    """Load scheduling config, merging defaults with any performance insights."""
    config = DEFAULT_CONFIG.copy()

    # Override best times with performance data if available
    if INSIGHTS_FILE.exists():
        try:
            with open(INSIGHTS_FILE) as f:
                insights = json.load(f)

            best_hours = insights.get("best_posting_hours", [])
            if best_hours:
                # Use top 3 hours from insights for all accounts
                top_hours = [h["hour"] for h in best_hours[:3]]
                for account in ACCOUNTS:
                    config["best_times"][account] = top_hours
        except Exception:
            pass

    return config


def load_queue() -> list:
    """Load the posting queue."""
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return []


def _detect_content_type(entry: dict) -> str:
    """Detect content type from a queue entry or file path."""
    image = entry.get("image", "").lower()
    caption = entry.get("caption", "").lower()
    post_id = entry.get("id", "").lower()

    if "carousel" in image or "carousel" in post_id:
        return "carousel"
    if "reel" in image or "reel" in post_id or "video" in image:
        return "reel"
    if "meme" in image or "meme" in post_id:
        return "meme"
    if "quote" in image or "quote" in post_id:
        return "quote"
    if "story" in image or "story" in post_id:
        return "story"

    # Detect from caption content
    if caption:
        if any(w in caption for w in ["why ", "how ", "what ", " matters", " truth"]):
            return "education"
        if "#meme" in caption or "#funny" in caption:
            return "meme"

    return "news"


def _find_available_content() -> dict:
    """Find all available content across sources, categorized by type."""
    available = defaultdict(list)

    # From post queue (unscheduled, queued items)
    queue = load_queue()
    for entry in queue:
        if entry.get("status") == "queued" and not entry.get("schedule"):
            ct = _detect_content_type(entry)
            available[ct].append({
                "source": "queue",
                "id": entry.get("id", ""),
                "caption": entry.get("caption", "")[:60],
                "image": entry.get("image", ""),
                "account": entry.get("account", ""),
                "type": ct,
            })

    # From scripts directory
    if SCRIPTS_DIR.exists():
        for script_file in sorted(SCRIPTS_DIR.glob("*.json")):
            try:
                with open(script_file) as f:
                    script = json.load(f)
                ct = "reel"
                available[ct].append({
                    "source": "script",
                    "id": script_file.stem,
                    "caption": script.get("hook", script.get("title", ""))[:60],
                    "file": str(script_file),
                    "type": ct,
                })
            except Exception:
                continue

    # From today's daily output
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = DAILY_DIR / today
    if today_dir.exists():
        for item in sorted(today_dir.iterdir()):
            if item.suffix == ".html" and "carousel" in item.name:
                available["carousel"].append({
                    "source": "daily",
                    "id": item.stem,
                    "file": str(item),
                    "type": "carousel",
                })
            elif item.suffix == ".json" and "reel" in item.name:
                available["reel"].append({
                    "source": "daily",
                    "id": item.stem,
                    "file": str(item),
                    "type": "reel",
                })

    # From memes directory (unposted)
    if MEME_DIR.exists():
        for img in sorted(MEME_DIR.glob("*.jpg")) + sorted(MEME_DIR.glob("*.png")):
            caption_file = img.with_suffix(".txt")
            caption = ""
            if caption_file.exists():
                caption = caption_file.read_text().strip()[:60]
            available["meme"].append({
                "source": "meme",
                "id": img.stem,
                "file": str(img),
                "caption": caption,
                "type": "meme",
            })

    return dict(available)


def _assign_content_to_slot(content_item: dict, account: str, slot_time: datetime) -> dict:
    """Create a calendar slot from content + account + time.
    Assigns a copywriting framework and carousel color for variety."""
    # Pick framework and color with rotation enforcement
    framework = get_next_framework()
    log_framework_usage(framework, content_item.get("id", ""))

    slot = {
        "time": slot_time.isoformat(),
        "hour": slot_time.hour,
        "day": slot_time.strftime("%A"),
        "date": slot_time.strftime("%Y-%m-%d"),
        "account": account,
        "content_type": content_item.get("type", "unknown"),
        "content_id": content_item.get("id", ""),
        "content_source": content_item.get("source", ""),
        "caption_preview": content_item.get("caption", "")[:50],
        "file": content_item.get("file", content_item.get("image", "")),
        "status": "scheduled",
        "framework": framework,
    }

    # Add carousel-specific variety data
    if content_item.get("type") in ("carousel", "news"):
        color = get_next_carousel_color()
        layouts = ["single-column", "split", "card-grid"]
        # Rotate layouts
        theme_data = load_carousel_themes()
        recent_layouts = [t.get("layout", "") for t in theme_data.get("themes", [])[-3:]]
        layout = "single-column"
        for l in layouts:
            if l not in recent_layouts:
                layout = l
                break
        log_carousel_theme(color, layout, content_item.get("id", ""))
        slot["carousel_color"] = color
        slot["carousel_layout"] = layout

    return slot


def generate_calendar(days: int = 7) -> dict:
    """Generate a posting calendar for the next N days."""
    config = load_config()
    available = _find_available_content()
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    calendar = {
        "generated_at": datetime.now().isoformat(),
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=days)).strftime("%Y-%m-%d"),
        "days": [],
    }

    # Flatten available content into pools per type
    content_pools = {}
    for ct, items in available.items():
        content_pools[ct] = list(items)
        random.shuffle(content_pools[ct])

    # Track what type was last assigned per account (for rotation)
    last_type = {a: "" for a in ACCOUNTS}

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")
        day_str = current_date.strftime("%Y-%m-%d")

        day_entry = {
            "date": day_str,
            "day": day_name,
            "slots": [],
        }

        for account in ACCOUNTS:
            posts_today = config["posts_per_day"].get(account, 1)
            times = config["best_times"].get(account, [12])
            allowed_types = config["account_content_rules"].get(account, ["news"])
            max_consec = config["rotation_rules"]["max_consecutive_same_type"]

            for slot_idx in range(min(posts_today, len(times))):
                hour = times[slot_idx % len(times)]
                slot_time = current_date.replace(hour=hour)

                # Pick content type with rotation
                chosen_item = None
                for ct in allowed_types:
                    # Skip if we already used this type max_consec times in a row
                    if ct == last_type[account]:
                        # Allow it but prefer other types
                        continue
                    pool = content_pools.get(ct, [])
                    if pool:
                        chosen_item = pool.pop(0)
                        last_type[account] = ct
                        break

                # Fallback: use any available type
                if not chosen_item:
                    for ct in allowed_types:
                        pool = content_pools.get(ct, [])
                        if pool:
                            chosen_item = pool.pop(0)
                            last_type[account] = ct
                            break

                if chosen_item:
                    slot = _assign_content_to_slot(chosen_item, account, slot_time)
                    day_entry["slots"].append(slot)
                else:
                    # No content available, create a placeholder
                    day_entry["slots"].append({
                        "time": slot_time.isoformat(),
                        "hour": hour,
                        "day": day_name,
                        "date": day_str,
                        "account": account,
                        "content_type": "TBD",
                        "content_id": "",
                        "content_source": "needs_creation",
                        "caption_preview": "[Content needed]",
                        "file": "",
                        "status": "needs_content",
                    })

        # Sort slots by time
        day_entry["slots"].sort(key=lambda s: s.get("time", ""))
        calendar["days"].append(day_entry)

    return calendar


def save_calendar(calendar: dict) -> tuple:
    """Save calendar as both JSON and markdown. Returns (json_path, md_path)."""
    NEWS_DIR.mkdir(parents=True, exist_ok=True)

    date_str = calendar.get("start_date", datetime.now().strftime("%Y-%m-%d"))

    # Save JSON
    json_path = NEWS_DIR / f"calendar-{date_str}.json"
    with open(json_path, "w") as f:
        json.dump(calendar, f, indent=2, default=str)

    # Save markdown
    md_path = NEWS_DIR / f"calendar-{date_str}.md"
    md_lines = [
        f"# Content Calendar",
        f"Generated: {calendar.get('generated_at', '')}",
        f"Period: {calendar.get('start_date', '')} to {calendar.get('end_date', '')}",
        "",
    ]

    for day in calendar.get("days", []):
        md_lines.append(f"## {day['day']}, {day['date']}")
        md_lines.append("")

        if not day.get("slots"):
            md_lines.append("No posts scheduled.")
            md_lines.append("")
            continue

        md_lines.append(f"| Time | Account | Type | Framework | Content | Status |")
        md_lines.append(f"|------|---------|------|-----------|---------|--------|")

        for slot in day["slots"]:
            h = slot.get("hour", 0)
            period = "AM" if h < 12 else "PM"
            dh = h if h <= 12 else h - 12
            if dh == 0:
                dh = 12
            time_str = f"{dh}:00 {period}"

            account = f"@{slot.get('account', '?')}"
            ct = slot.get("content_type", "?")
            framework = slot.get("framework", "-")
            preview = slot.get("caption_preview", "")[:25] or slot.get("content_id", "")[:25]
            status = slot.get("status", "?")

            md_lines.append(f"| {time_str} | {account} | {ct} | {framework} | {preview} | {status} |")

        md_lines.append("")

    # Summary
    total_slots = sum(len(d.get("slots", [])) for d in calendar.get("days", []))
    needs_content = sum(
        1 for d in calendar.get("days", [])
        for s in d.get("slots", [])
        if s.get("status") == "needs_content"
    )

    md_lines.append("## Summary")
    md_lines.append("")
    md_lines.append(f"- Total scheduled: {total_slots}")
    md_lines.append(f"- Content needed: {needs_content}")
    md_lines.append(f"- Ready to post: {total_slots - needs_content}")
    md_lines.append("")

    md_path.write_text("\n".join(md_lines))

    return json_path, md_path


def cmd_generate(args):
    """Generate a 7-day calendar."""
    print("\n[CALENDAR] Scanning available content...")
    available = _find_available_content()

    total_items = sum(len(items) for items in available.values())
    print(f"  Found {total_items} content items:")
    for ct, items in sorted(available.items()):
        print(f"    {ct}: {len(items)}")

    print(f"\n[CALENDAR] Generating {7}-day calendar...")
    calendar = generate_calendar(7)

    json_path, md_path = save_calendar(calendar)

    total_slots = sum(len(d.get("slots", [])) for d in calendar.get("days", []))
    needs_content = sum(
        1 for d in calendar.get("days", [])
        for s in d.get("slots", [])
        if s.get("status") == "needs_content"
    )

    print()
    print("=" * 60)
    print("  CONTENT CALENDAR GENERATED")
    print("=" * 60)
    print()

    for day in calendar["days"]:
        print(f"  {day['day']}, {day['date']}")
        for slot in day.get("slots", []):
            h = slot.get("hour", 0)
            period = "AM" if h < 12 else "PM"
            dh = h if h <= 12 else h - 12
            if dh == 0:
                dh = 12
            status_icon = "[x]" if slot["status"] == "scheduled" else "[ ]"
            print(f"    {status_icon} {dh:2d}:00 {period}  @{slot['account']:15s}  {slot['content_type']:10s}  {slot.get('caption_preview', '')[:30]}")
        print()

    print(f"  Total slots: {total_slots}")
    print(f"  Ready: {total_slots - needs_content}")
    print(f"  Needs content: {needs_content}")
    print()
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")
    print("=" * 60)
    print()


def cmd_today(args):
    """Show what to post today."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Try to find a calendar that covers today
    calendar_data = None
    for cal_file in sorted(NEWS_DIR.glob("calendar-*.json"), reverse=True):
        try:
            with open(cal_file) as f:
                cal = json.load(f)
            if cal.get("start_date", "") <= today <= cal.get("end_date", ""):
                calendar_data = cal
                break
        except Exception:
            continue

    if not calendar_data:
        print("[!] No calendar covers today. Run: python3 content_calendar.py --generate")
        return

    # Find today's slots
    today_slots = []
    for day in calendar_data.get("days", []):
        if day.get("date") == today:
            today_slots = day.get("slots", [])
            break

    if not today_slots:
        print(f"No posts scheduled for today ({today}).")
        return

    now = datetime.now()

    print()
    print(f"  TODAY'S POSTING SCHEDULE ({today})")
    print("=" * 60)
    print()

    for slot in today_slots:
        h = slot.get("hour", 0)
        period = "AM" if h < 12 else "PM"
        dh = h if h <= 12 else h - 12
        if dh == 0:
            dh = 12

        is_past = now.hour > h
        status = "DONE" if is_past else "UPCOMING"
        if slot.get("status") == "needs_content":
            status = "NEEDS CONTENT"

        print(f"  {dh:2d}:00 {period}  [{status}]")
        print(f"    Account: @{slot.get('account', '?')}")
        print(f"    Type: {slot.get('content_type', '?')}")
        print(f"    Content: {slot.get('caption_preview', '') or slot.get('content_id', '')}")
        if slot.get("file"):
            print(f"    File: {slot['file']}")
        print()

    upcoming = [s for s in today_slots if now.hour <= s.get("hour", 0)]
    if upcoming:
        next_slot = upcoming[0]
        h = next_slot.get("hour", 0)
        period = "AM" if h < 12 else "PM"
        dh = h if h <= 12 else h - 12
        if dh == 0:
            dh = 12
        print(f"  NEXT UP: {dh}:00 {period} on @{next_slot.get('account', '?')}")
    else:
        print(f"  All posts for today are done or past due.")

    print("=" * 60)
    print()


def cmd_show(args):
    """Show the most recent calendar."""
    cal_files = sorted(NEWS_DIR.glob("calendar-*.md"), reverse=True)
    if not cal_files:
        print("[!] No calendar found. Run: python3 content_calendar.py --generate")
        return

    latest = cal_files[0]
    print(latest.read_text())


def cmd_reschedule(args):
    """Regenerate the calendar with reshuffled content."""
    print("[CALENDAR] Reshuffling calendar...")
    calendar = generate_calendar(7)
    json_path, md_path = save_calendar(calendar)
    print(f"[DONE] New calendar saved:")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")


def cmd_config(args):
    """Show current scheduling configuration."""
    config = load_config()
    print()
    print("  SCHEDULING CONFIGURATION")
    print("=" * 60)
    print()
    print("  Posts per day:")
    for acct, count in config["posts_per_day"].items():
        print(f"    @{acct}: {count}")
    print()
    print("  Best posting times (24h):")
    for acct, times in config["best_times"].items():
        formatted = [f"{h}:00" for h in times]
        print(f"    @{acct}: {', '.join(formatted)}")
    print()
    print("  Content type assignments:")
    for acct, types in config["account_content_rules"].items():
        print(f"    @{acct}: {', '.join(types)}")
    print()
    print("  Rotation rules:")
    for key, val in config["rotation_rules"].items():
        print(f"    {key}: {val}")
    print()

    if INSIGHTS_FILE.exists():
        print("  [i] Performance insights detected. Best times may be adjusted.")
    else:
        print("  [i] No performance insights yet. Using defaults.")
        print("      Run: python3 performance_tracker.py --insights")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Smart Content Calendar. Auto-generates posting schedules. Copyright 2026 Behike."
    )
    parser.add_argument("--generate", action="store_true", help="Generate next 7 days calendar")
    parser.add_argument("--today", action="store_true", help="Show today's posting schedule")
    parser.add_argument("--show", action="store_true", help="Display current calendar")
    parser.add_argument("--reschedule", action="store_true", help="Reshuffle and regenerate calendar")
    parser.add_argument("--config", action="store_true", help="Show scheduling configuration")

    args = parser.parse_args()

    if args.generate:
        cmd_generate(args)
    elif args.today:
        cmd_today(args)
    elif args.show:
        cmd_show(args)
    elif args.reschedule:
        cmd_reschedule(args)
    elif args.config:
        cmd_config(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
