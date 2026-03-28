#!/usr/bin/env python3
"""
Instagram Posting Queue & Preview System
Manages the posting schedule for finished reels.
Generates a visual posting calendar and preview page.

Usage:
    python3 posting_queue.py --preview     # open preview in browser
    python3 posting_queue.py --schedule    # show posting schedule
    python3 posting_queue.py --export      # export queue as JSON for automation
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
INSTAGRAM_DIR = PIPELINE_DIR / "instagram_ready"
QUEUE_FILE = PIPELINE_DIR / "posting_queue.json"

# Posting schedule: optimal times for Instagram engagement
# Best times: Tue/Wed/Thu 10am-1pm, Fri 11am
POSTING_TIMES = [
    ("Tuesday", "10:00"),
    ("Wednesday", "11:00"),
    ("Thursday", "10:00"),
    ("Friday", "11:00"),
    ("Saturday", "09:00"),
]

# Posting order (emotional arc for maximum engagement)
POSTING_ORDER = [
    "grandmas-recipe-card",      # universal, warm start
    "dads-old-truck",            # father figure, deep
    "first-apartment-key",       # coming of age, relatable
    "abuela-calling-your-name",  # cultural, specific
    "childhood-bedroom-ceiling", # quiet, introspective
    "last-voicemail",            # heavy, emotional peak
    "moms-morning-routine",      # mother figure
    "first-paycheck",            # achievement + family
    "the-basketball-court",      # nostalgia, friendship
    "old-sneakers",              # sacrifice, gratitude
    "the-family-table",          # family, loss
    "the-bus-stop",              # father, routine
    "sunday-morning-cartoons",   # childhood, siblings
    "the-voicemail-you-saved",   # grief, technology
    "the-hoodie",                # young love, memory
    "the-neighborhood",          # change, growing up
]


def build_queue():
    """Build posting queue from available reels."""
    available = []
    for name in POSTING_ORDER:
        mp4 = INSTAGRAM_DIR / f"{name}.mp4"
        caption = INSTAGRAM_DIR / f"{name}_caption.txt"
        if mp4.exists():
            size_mb = mp4.stat().st_size / (1024 * 1024)
            cap_text = caption.read_text() if caption.exists() else ""
            available.append({
                "name": name,
                "file": str(mp4),
                "caption_file": str(caption) if caption.exists() else None,
                "caption": cap_text,
                "size_mb": round(size_mb, 1),
            })

    # Also add any reels not in POSTING_ORDER
    for mp4 in sorted(INSTAGRAM_DIR.glob("*.mp4")):
        name = mp4.stem
        if name not in [a["name"] for a in available]:
            available.append({
                "name": name,
                "file": str(mp4),
                "caption_file": None,
                "caption": "",
                "size_mb": round(mp4.stat().st_size / (1024*1024), 1),
            })

    # Assign posting dates starting from next posting slot
    now = datetime.now()
    schedule = []
    slot_idx = 0

    for reel in available:
        # Find next posting slot
        while True:
            days_ahead = slot_idx // len(POSTING_TIMES) * 7
            day_name, time_str = POSTING_TIMES[slot_idx % len(POSTING_TIMES)]
            target_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day_name)

            post_date = now + timedelta(days=days_ahead)
            # Adjust to correct day of week
            current_day = post_date.weekday()
            delta = target_day - current_day
            if delta <= 0:
                delta += 7
            post_date = now + timedelta(days=delta + (slot_idx // len(POSTING_TIMES)) * 7)

            hour, minute = map(int, time_str.split(":"))
            post_date = post_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if post_date > now:
                break
            slot_idx += 1

        reel["scheduled"] = post_date.isoformat()
        reel["scheduled_display"] = post_date.strftime("%a %b %d, %I:%M %p")
        schedule.append(reel)
        slot_idx += 1

    return schedule


def show_schedule():
    """Print the posting schedule."""
    queue = build_queue()
    if not queue:
        print("No reels ready. Run instagram_pipeline.py --all first.")
        return

    print(f"\n{'='*70}")
    print(f"  INSTAGRAM POSTING QUEUE ({len(queue)} reels)")
    print(f"{'='*70}")
    print(f"{'#':>3} {'Date':<22} {'Story':<30} {'Size':>6}")
    print(f"{'-'*70}")

    for i, reel in enumerate(queue):
        print(f"{i+1:>3}. {reel['scheduled_display']:<22} {reel['name']:<30} {reel['size_mb']:>5.1f}M")

    print(f"{'-'*70}")
    first = queue[0]['scheduled_display']
    last = queue[-1]['scheduled_display']
    print(f"  First post: {first}")
    print(f"  Last post:  {last}")
    print(f"  Cadence: 5 posts/week (Tue-Sat)")
    print()


def export_queue():
    """Export queue as JSON for automation tools."""
    queue = build_queue()
    with open(QUEUE_FILE, 'w') as f:
        json.dump({"queue": queue, "generated_at": datetime.now().isoformat()}, f, indent=2)
    print(f"Queue exported to {QUEUE_FILE} ({len(queue)} reels)")


def generate_preview():
    """Generate HTML preview page for all reels."""
    queue = build_queue()
    if not queue:
        print("No reels ready.")
        return

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Reel Preview - Posting Queue</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #111; color: #eee; font-family: -apple-system, system-ui, sans-serif; }}
.header {{
    text-align: center; padding: 40px 20px 20px;
    background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.header h1 {{ font-size: 2em; }}
.header p {{ color: #888; -webkit-text-fill-color: #888; margin-top: 8px; }}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px; padding: 30px; max-width: 1400px; margin: 0 auto;
}}
.card {{
    background: #1a1a1a; border-radius: 16px; overflow: hidden;
    border: 1px solid #333; transition: transform 0.2s;
}}
.card:hover {{ transform: scale(1.02); border-color: #fd1d1d; }}
.card video {{
    width: 100%; aspect-ratio: 9/16; object-fit: cover;
    background: #000;
}}
.card-body {{ padding: 16px; }}
.card-title {{ font-size: 1.1em; font-weight: 600; margin-bottom: 8px; }}
.card-meta {{ color: #888; font-size: 0.85em; margin-bottom: 12px; }}
.card-caption {{
    font-size: 0.8em; color: #aaa; max-height: 80px; overflow-y: auto;
    background: #222; padding: 10px; border-radius: 8px;
    white-space: pre-wrap;
}}
.schedule-badge {{
    display: inline-block; background: #833ab4; color: white;
    padding: 3px 10px; border-radius: 12px; font-size: 0.75em;
}}
.stats {{
    text-align: center; padding: 20px; color: #666;
    border-top: 1px solid #222; margin-top: 20px;
}}
</style>
</head>
<body>
<div class="header">
    <h1>Reel Preview Queue</h1>
    <p>{len(queue)} reels ready to post</p>
</div>
<div class="grid">
"""

    for i, reel in enumerate(queue):
        # Use relative path for video
        rel_path = os.path.relpath(reel["file"], PIPELINE_DIR)
        caption_preview = reel["caption"][:200].replace("<", "&lt;").replace("\n", "<br>") if reel["caption"] else "No caption"
        title = reel["name"].replace("-", " ").title()

        html += f"""
    <div class="card">
        <video src="{rel_path}" controls preload="none" poster=""></video>
        <div class="card-body">
            <div class="card-title">#{i+1} {title}</div>
            <div class="card-meta">
                <span class="schedule-badge">{reel['scheduled_display']}</span>
                {reel['size_mb']}MB
            </div>
            <div class="card-caption">{caption_preview}</div>
        </div>
    </div>
"""

    html += f"""
</div>
<div class="stats">
    Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | {len(queue)} reels |
    First post: {queue[0]['scheduled_display'] if queue else 'N/A'}
</div>
</body>
</html>"""

    preview_path = PIPELINE_DIR / "reel_preview.html"
    with open(preview_path, 'w') as f:
        f.write(html)

    print(f"Preview saved: {preview_path}")
    return preview_path


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)

    if "--schedule" in sys.argv:
        show_schedule()
    elif "--export" in sys.argv:
        export_queue()
    elif "--preview" in sys.argv:
        path = generate_preview()
        if path:
            show_schedule()
    else:
        show_schedule()
        generate_preview()
