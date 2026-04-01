#!/usr/bin/env python3
"""
YouTube Engine — Complete video production management system.

Manages 100+ scripts, generates thumbnails, optimizes metadata,
tracks production status, and creates upload-ready packages.

Usage:
    python3 youtube-engine.py scripts              # List all scripts by category
    python3 youtube-engine.py next                  # Suggest next video to produce
    python3 youtube-engine.py package <script>      # Create upload-ready package
    python3 youtube-engine.py thumbnail <title>     # Generate thumbnail HTML
    python3 youtube-engine.py metadata <script>     # Generate title/desc/tags
    python3 youtube-engine.py shorts                # List all shorts scripts
    python3 youtube-engine.py stats                 # Production statistics
    python3 youtube-engine.py schedule              # Suggest posting schedule
"""

import json
import os
import re
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "Ceiba/projects/content-empire/youtube-scripts"
OUTPUT_DIR = BASE_DIR / "tools/youtube-engine-output"
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails"
PACKAGES_DIR = OUTPUT_DIR / "packages"
TRACKER_FILE = OUTPUT_DIR / "production-tracker.json"

for d in [OUTPUT_DIR, THUMBNAILS_DIR, PACKAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def color(t, c): return f"\033[{c}m{t}\033[0m"
def green(t): return color(t, "32")
def cyan(t): return color(t, "36")
def gold(t): return color(t, "33")
def dim(t): return color(t, "90")
def red(t): return color(t, "31")


def load_tracker():
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text())
    return {"videos": {}, "produced": 0, "uploaded": 0}

def save_tracker(data):
    TRACKER_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def get_scripts():
    """Load and categorize all scripts."""
    scripts = []
    for f in sorted(SCRIPTS_DIR.glob("*.md")):
        content = f.read_text()
        lines = content.split('\n')
        title = ""
        for line in lines[:10]:
            if line.startswith('# '):
                title = line[2:].strip()
                break
            elif line.startswith('## '):
                title = line[3:].strip()
                break

        if not title:
            title = f.stem.replace('-', ' ').replace('_', ' ').title()

        # Detect category from filename
        name = f.stem.lower()
        if 'short' in name:
            category = 'shorts'
        elif any(w in name for w in ['adhd', 'wellness', 'mental']):
            category = 'adhd-wellness'
        elif any(w in name for w in ['ai', 'claude', 'automation', 'n8n']):
            category = 'ai-tools'
        elif any(w in name for w in ['ecommerce', 'ebay', 'gumroad', 'product']):
            category = 'ecommerce'
        elif any(w in name for w in ['finance', 'money', 'budget']):
            category = 'finance'
        elif any(w in name for w in ['gaming', 'roblox']):
            category = 'gaming'
        elif any(w in name for w in ['brand', 'content', 'social']):
            category = 'content'
        elif any(w in name for w in ['solopreneur', 'business', 'service']):
            category = 'business'
        else:
            category = 'general'

        word_count = len(content.split())
        est_minutes = max(1, word_count // 150)  # ~150 words per minute speaking

        scripts.append({
            "file": f.name,
            "title": title[:80],
            "category": category,
            "word_count": word_count,
            "est_minutes": est_minutes,
            "path": str(f),
        })

    return scripts


def cmd_scripts(args):
    """List all scripts by category."""
    scripts = get_scripts()
    tracker = load_tracker()

    categories = {}
    for s in scripts:
        categories.setdefault(s["category"], []).append(s)

    print(cyan(f"\n{'='*60}"))
    print(cyan(f"  YOUTUBE ENGINE — {len(scripts)} Scripts"))
    print(cyan(f"{'='*60}"))

    for cat in sorted(categories.keys()):
        items = categories[cat]
        print(f"\n  {gold(cat.upper())} ({len(items)} scripts)")
        print(f"  {'─'*50}")
        for s in items[:5]:
            status = tracker.get("videos", {}).get(s["file"], {}).get("status", "script")
            status_color = {"script": "90", "recorded": "33", "edited": "36", "uploaded": "32"}.get(status, "90")
            print(f"    {color(status, status_color):10s} {s['title'][:45]:45s} {dim(f'{s['est_minutes']}min')}")
        if len(items) > 5:
            print(f"    {dim(f'... +{len(items)-5} more')}")

    print(f"\n  Total: {len(scripts)} scripts | Produced: {tracker.get('produced', 0)} | Uploaded: {tracker.get('uploaded', 0)}")


def cmd_next(args):
    """Suggest the next video to produce based on priority."""
    scripts = get_scripts()
    tracker = load_tracker()

    # Priority scoring
    priority_categories = {
        'ai-tools': 10,      # Highest demand
        'adhd-wellness': 9,   # Unique niche
        'ecommerce': 8,
        'business': 7,
        'content': 6,
        'finance': 5,
        'gaming': 4,
        'general': 3,
        'shorts': 8,          # Quick wins
    }

    unproduced = [s for s in scripts if s["file"] not in tracker.get("videos", {})]

    # Score and sort
    for s in unproduced:
        s["priority"] = priority_categories.get(s["category"], 3)
        # Bonus for shorter videos (easier to produce)
        if s["est_minutes"] <= 5:
            s["priority"] += 2
        # Bonus for shorts
        if s["category"] == "shorts":
            s["priority"] += 3

    unproduced.sort(key=lambda x: -x["priority"])

    print(cyan(f"\n  TOP 10 NEXT VIDEOS TO PRODUCE"))
    print(f"  {'─'*50}")
    for i, s in enumerate(unproduced[:10], 1):
        print(f"  {i:2d}. [{gold(s['category']):12s}] {s['title'][:40]:40s} ~{s['est_minutes']}min  P{s['priority']}")

    if unproduced:
        top = unproduced[0]
        print(f"\n  {green('RECOMMENDED')}: {top['title']}")
        print(f"  File: {top['file']}")
        print(f"  Category: {top['category']} | ~{top['est_minutes']} min | Priority: {top['priority']}")
        print(f"\n  To package: python3 youtube-engine.py package {top['file']}")


def cmd_thumbnail(args):
    """Generate a YouTube thumbnail HTML."""
    title = " ".join(args) if args else "ADHD Productivity System"

    # Split into max 3 lines
    words = title.split()
    if len(words) <= 3:
        lines = [title]
    elif len(words) <= 6:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        third = len(words) // 3
        lines = [" ".join(words[:third]), " ".join(words[third:third*2]), " ".join(words[third*2:])]

    title_html = "<br>".join(lines)
    thumb_id = hashlib.md5(title.encode()).hexdigest()[:8]

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@800;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:1280px;height:720px;background:#0a0a0a;color:#fff;font-family:'Inter',sans-serif;
display:flex;align-items:center;padding:0 80px;overflow:hidden;position:relative;}}
.content{{flex:1;}}
.title{{font-size:56px;font-weight:900;line-height:1.1;max-width:700px;}}
.title span{{color:#00e5ff;}}
.accent-bar{{width:80px;height:5px;background:#00e5ff;margin:20px 0;}}
.sub{{font-size:20px;color:#888;font-weight:600;letter-spacing:2px;text-transform:uppercase;}}
.face-zone{{width:300px;height:300px;border-radius:50%;background:linear-gradient(135deg,#111,#1a1a1a);
border:3px solid #00e5ff;display:flex;align-items:center;justify-content:center;font-size:48px;
flex-shrink:0;margin-left:40px;}}
.brand{{position:absolute;bottom:24px;right:40px;font-size:14px;color:#333;letter-spacing:4px;}}
.badge{{position:absolute;top:24px;left:40px;background:#ff4444;color:#fff;padding:6px 18px;
border-radius:4px;font-size:14px;font-weight:800;letter-spacing:1px;}}
</style></head><body>
<div class="badge">NEW VIDEO</div>
<div class="content">
<div class="title">{title_html}</div>
<div class="accent-bar"></div>
<div class="sub">@behikeai</div>
</div>
<div class="face-zone">&#128100;</div>
<div class="brand">BEHIKE</div>
</body></html>"""

    thumb_file = THUMBNAILS_DIR / f"thumb-{thumb_id}.html"
    thumb_file.write_text(html)
    print(f"  Thumbnail saved: {thumb_file}")
    print(f"  Open in Brave and screenshot at 1280x720")

    # Also try to render with Brave
    png_file = THUMBNAILS_DIR / f"thumb-{thumb_id}.png"
    try:
        import subprocess
        brave = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        subprocess.run([brave, "--headless", "--disable-gpu", "--no-sandbox",
                       "--window-size=1280,720", "--force-device-scale-factor=2",
                       f"--screenshot={png_file}", f"file://{thumb_file}"],
                      capture_output=True, timeout=15)
        if png_file.exists():
            print(f"  PNG rendered: {png_file}")
    except:
        pass


def cmd_metadata(args):
    """Generate optimized title, description, and tags for a script."""
    if not args:
        print("Usage: youtube-engine.py metadata <script-filename>")
        return

    script_file = SCRIPTS_DIR / args[0]
    if not script_file.exists():
        # Try fuzzy match
        matches = [f for f in SCRIPTS_DIR.glob("*.md") if args[0] in f.name]
        if matches:
            script_file = matches[0]
        else:
            print(f"Script not found: {args[0]}")
            return

    content = script_file.read_text()
    lines = content.split('\n')

    # Extract title
    title = ""
    for line in lines[:10]:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Generate SEO title variants
    print(cyan(f"\n  METADATA: {script_file.name}"))
    print(f"  {'─'*50}")

    print(f"\n  {gold('TITLE OPTIONS:')}")
    print(f"    1. {title}")
    print(f"    2. I Built 100+ Products With This System | {title}")
    print(f"    3. {title} (ADHD-Friendly)")
    print(f"    4. {title} in 2026 — What Actually Works")

    print(f"\n  {gold('DESCRIPTION:')}")
    desc = f"""I built 100+ digital products in 2 weeks using this exact system. No courses. No theory. Just the system.

In this video, I break down {title.lower()} — step by step.

TIMESTAMPS:
00:00 - Intro
00:30 - The Problem
02:00 - The System
05:00 - Demo
08:00 - Results

PRODUCTS MENTIONED:
behike.gumroad.com/l/starter (FREE)
behike.gumroad.com/l/blueprint-bundle ($49 - All 15 Blueprints)
behike.gumroad.com/l/behike-os ($97 - Complete System)

CONNECT:
Instagram: @behikeai
Gumroad: behike.gumroad.com

#behike #solopreneur #ADHD #buildinpublic #digitalproducts"""

    for line in desc.split('\n'):
        print(f"    {line}")

    print(f"\n  {gold('TAGS:')}")
    tags = f"behike, {title.lower()}, solopreneur, ADHD, digital products, building in public, claude code, AI tools, productivity, side hustle, make money online, gumroad"
    print(f"    {tags}")

    # Save metadata
    meta_file = OUTPUT_DIR / f"meta-{script_file.stem}.json"
    meta_file.write_text(json.dumps({
        "script": script_file.name,
        "title_options": [
            title,
            f"I Built 100+ Products With This System | {title}",
            f"{title} (ADHD-Friendly)",
            f"{title} in 2026 — What Actually Works",
        ],
        "description": desc,
        "tags": tags,
        "generated_at": datetime.now().isoformat()
    }, indent=2, ensure_ascii=False))
    print(f"\n  Saved: {meta_file}")


def cmd_package(args):
    """Create a complete upload-ready package for a video."""
    if not args:
        print("Usage: youtube-engine.py package <script-filename>")
        return

    script_file = SCRIPTS_DIR / args[0]
    if not script_file.exists():
        matches = [f for f in SCRIPTS_DIR.glob("*.md") if args[0] in f.name]
        if matches:
            script_file = matches[0]
        else:
            print(f"Script not found: {args[0]}")
            return

    content = script_file.read_text()
    title = ""
    for line in content.split('\n')[:10]:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    pkg_dir = PACKAGES_DIR / script_file.stem
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Copy script
    (pkg_dir / "script.md").write_text(content)

    # Generate thumbnail
    cmd_thumbnail(title.split() if title else ["Video"])

    # Generate metadata
    cmd_metadata([script_file.name])

    # Create checklist
    checklist = f"""# Upload Checklist: {title}

## Pre-Recording
- [ ] Script reviewed and timed
- [ ] Screen recording software ready (OBS/QuickTime)
- [ ] Microphone tested
- [ ] Desktop clean (close unnecessary tabs)
- [ ] Demo files/apps ready

## Recording
- [ ] Record intro (30 seconds, hook + what they'll learn)
- [ ] Record main content
- [ ] Record CTA (follow, link in bio, comment)
- [ ] Review recording for quality

## Post-Production
- [ ] Edit video (cuts, zoom-ins, transitions)
- [ ] Add background music (lo-fi, low volume)
- [ ] Add captions/subtitles
- [ ] Export at 1080p minimum (4K preferred)
- [ ] Thumbnail screenshot taken

## Upload
- [ ] Title: SEO-optimized (check metadata file)
- [ ] Description: with timestamps, links, and tags
- [ ] Tags: 10-15 relevant keywords
- [ ] Thumbnail: custom (from thumbnails/ folder)
- [ ] End screen: link to next video + subscribe
- [ ] Cards: link to relevant product/video
- [ ] Visibility: Public
- [ ] Schedule: {(datetime.now() + timedelta(days=1)).strftime('%A %B %d')} at 9:00 AM EST

## Post-Upload
- [ ] Share on Instagram (@behikeai)
- [ ] Share on Twitter
- [ ] Pin comment with product link
- [ ] Reply to first 10 comments within 1 hour
"""
    (pkg_dir / "upload-checklist.md").write_text(checklist)

    print(f"\n  {green('PACKAGE CREATED')}: {pkg_dir}")
    print(f"  ├── script.md")
    print(f"  ├── upload-checklist.md")
    print(f"  └── metadata in youtube-engine-output/")

    # Update tracker
    tracker = load_tracker()
    tracker["videos"][script_file.name] = {
        "title": title,
        "status": "packaged",
        "packaged_at": datetime.now().isoformat()
    }
    save_tracker(tracker)


def cmd_shorts(args):
    """List all shorts scripts."""
    scripts = [s for s in get_scripts() if s["category"] == "shorts"]
    print(cyan(f"\n  YOUTUBE SHORTS ({len(scripts)} scripts)"))
    print(f"  {'─'*50}")
    for s in scripts:
        print(f"    {s['title'][:50]:50s} {dim(f'~{s['est_minutes']}min')} {dim(s['file'])}")


def cmd_stats(args):
    """Show production statistics."""
    scripts = get_scripts()
    tracker = load_tracker()
    categories = {}
    for s in scripts:
        categories.setdefault(s["category"], []).append(s)

    print(cyan(f"\n  YOUTUBE ENGINE STATS"))
    print(f"  {'─'*40}")
    print(f"  Total scripts:    {green(str(len(scripts)))}")
    print(f"  Produced:         {gold(str(tracker.get('produced', 0)))}")
    print(f"  Uploaded:         {green(str(tracker.get('uploaded', 0)))}")
    print(f"  Packaged:         {gold(str(len([v for v in tracker.get('videos', {}).values() if v.get('status') == 'packaged'])))}")
    print(f"\n  By category:")
    for cat, items in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"    {cat:20s} {len(items)} scripts")

    total_minutes = sum(s["est_minutes"] for s in scripts)
    print(f"\n  Total content:    ~{total_minutes} minutes ({total_minutes//60}h {total_minutes%60}m)")
    print(f"  Avg per video:    ~{total_minutes//len(scripts)} minutes")


def cmd_schedule(args):
    """Suggest a posting schedule."""
    scripts = get_scripts()

    # Prioritize by category
    priority_order = ['ai-tools', 'adhd-wellness', 'shorts', 'ecommerce', 'business', 'content', 'finance', 'gaming', 'general']

    scheduled = []
    day = datetime.now()

    for cat in priority_order:
        cat_scripts = [s for s in scripts if s["category"] == cat][:3]  # 3 per category
        for s in cat_scripts:
            day += timedelta(days=2)  # Post every other day
            scheduled.append({"date": day.strftime("%a %b %d"), "script": s})

    print(cyan(f"\n  SUGGESTED POSTING SCHEDULE (every other day)"))
    print(f"  {'─'*50}")
    for item in scheduled[:14]:  # 2 weeks
        s = item["script"]
        print(f"  {gold(item['date']):12s} [{s['category']:12s}] {s['title'][:40]}")

    print(f"\n  Total planned: {len(scheduled)} videos over {len(scheduled)*2} days")


def main():
    if len(sys.argv) < 2:
        print(cyan("""
  YouTube Engine — Video Production System
  ==========================================

  Commands:
    scripts          List all scripts by category
    next             Suggest next video to produce
    package <file>   Create upload-ready package
    thumbnail <title>  Generate thumbnail HTML + PNG
    metadata <file>  Generate title/desc/tags
    shorts           List all shorts scripts
    stats            Production statistics
    schedule         Suggest posting schedule
        """))
        return

    cmds = {
        "scripts": cmd_scripts, "next": cmd_next, "package": cmd_package,
        "thumbnail": cmd_thumbnail, "metadata": cmd_metadata,
        "shorts": cmd_shorts, "stats": cmd_stats, "schedule": cmd_schedule,
    }

    cmd = sys.argv[1]
    if cmd in cmds:
        cmds[cmd](sys.argv[2:])
    else:
        print(f"Unknown: {cmd}")

if __name__ == "__main__":
    main()
