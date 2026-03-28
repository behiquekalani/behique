#!/usr/bin/env python3
"""
Instagram Posting Pipeline
Handles reel uploads via Instagram Graph API or manual posting queue.

Since Instagram requires a Business/Creator account + Facebook Page for API access,
this script supports two modes:

1. QUEUE MODE (default): Organizes reels into a posting schedule with captions,
   hashtags, and posting order. Generates a visual posting calendar.

2. API MODE (--api): Uses Instagram Graph API for auto-posting.
   Requires: IG Business account, Facebook Page, access token.

Usage:
    python3 instagram_post.py --queue              # generate posting schedule
    python3 instagram_post.py --queue --days 14     # 14-day schedule
    python3 instagram_post.py --prepare story-name  # prepare one reel for posting
    python3 instagram_post.py --api --token TOKEN   # auto-post via API
"""
import json, os, sys, shutil
from pathlib import Path
from datetime import datetime, timedelta

PIPELINE_DIR = Path(__file__).parent
OUTPUT_DIR = PIPELINE_DIR / "output"
POSTING_DIR = PIPELINE_DIR / "posting-queue"
STORIES_DIR = PIPELINE_DIR / "stories"


# Hashtag sets for emotional content
HASHTAG_SETS = {
    'nostalgia': '#nostalgia #memories #childhood #throwback #remember #growingup #family #emotional #relatable #fyp',
    'family': '#family #love #home #parents #grandparents #familylove #familyiseverything #homesick #fyp #viral',
    'loss': '#grief #loss #memories #loveyouforever #missyou #inlovingmemory #healing #fyp #emotional #relatable',
    'growing_up': '#growingup #adulting #millennials #genz #childhood #nostalgia #relatable #fyp #viral #emotional',
}

# Caption templates
CAPTION_TEMPLATES = [
    "{title}\n\nSome things you don't realize you're holding onto until they're gone.\n\n{hashtags}",
    "{title}\n\nThis one hit different.\n\n{hashtags}",
    "{title}\n\nDo you have one of these? Drop a comment.\n\n{hashtags}",
    "{title}\n\nNot everything valuable has a price tag.\n\n{hashtags}",
    "{title}\n\nThe smallest things carry the biggest weight.\n\n{hashtags}",
    "{title}\n\nSave this if it made you feel something.\n\n{hashtags}",
]

# Best posting times for Instagram Reels (EST)
BEST_TIMES = [
    "07:00",  # Morning commute
    "12:00",  # Lunch break
    "17:00",  # After work
    "20:00",  # Evening wind-down
    "21:00",  # Night scroll
]


def classify_story(story):
    """Classify story for hashtag selection."""
    text = story.get("narration", " ".join(s["text"] for s in story.get("scenes", [])))
    text_lower = text.lower()

    if any(w in text_lower for w in ['passed', 'gone', 'died', 'last time', 'funeral', 'heaven']):
        return 'loss'
    elif any(w in text_lower for w in ['grandma', 'grandpa', 'mom', 'dad', 'family', 'parents', 'brother', 'sister']):
        return 'family'
    elif any(w in text_lower for w in ['kid', 'child', 'school', 'teenager', 'grew up', 'first time']):
        return 'growing_up'
    return 'nostalgia'


def prepare_reel_for_posting(story_name):
    """Prepare a single reel with caption, hashtags, and metadata."""
    ig_reel = OUTPUT_DIR / f"{story_name}_instagram.mp4"
    story_json = STORIES_DIR / f"{story_name}.json"

    if not ig_reel.exists():
        print(f"[ERROR] No Instagram reel found for {story_name}")
        print(f"  Run: python3 instagram_compose.py {story_name}")
        return None

    with open(story_json) as f:
        story = json.load(f)

    title = story.get("title", story_name.replace("-", " ").title())
    category = classify_story(story)
    hashtags = HASHTAG_SETS[category]

    # Pick caption template based on story index for variety
    template_idx = hash(story_name) % len(CAPTION_TEMPLATES)
    caption = CAPTION_TEMPLATES[template_idx].format(title=title, hashtags=hashtags)

    # Get file size
    size_mb = os.path.getsize(ig_reel) / (1024 * 1024)

    metadata = {
        'story_name': story_name,
        'title': title,
        'category': category,
        'caption': caption,
        'hashtags': hashtags,
        'file': str(ig_reel),
        'size_mb': round(size_mb, 1),
        'created': datetime.now().isoformat(),
    }

    return metadata


def generate_posting_queue(days=14):
    """Generate a posting schedule for all ready reels."""
    POSTING_DIR.mkdir(exist_ok=True)

    # Find all Instagram-ready reels
    ig_reels = sorted(OUTPUT_DIR.glob("*_instagram.mp4"))
    if not ig_reels:
        print("No Instagram reels found. Run instagram_compose.py --all first.")
        return

    print(f"Found {len(ig_reels)} Instagram-ready reels")

    # Prepare metadata for each
    queue = []
    for reel in ig_reels:
        name = reel.stem.replace("_instagram", "")
        meta = prepare_reel_for_posting(name)
        if meta:
            queue.append(meta)

    # Create posting schedule - 2 reels per day at optimal times
    posts_per_day = 2
    schedule = []
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    for i, meta in enumerate(queue):
        day_offset = i // posts_per_day
        time_idx = i % posts_per_day

        if day_offset >= days:
            break

        post_date = start_date + timedelta(days=day_offset)
        post_time = BEST_TIMES[time_idx % len(BEST_TIMES)]
        hour, minute = map(int, post_time.split(':'))
        post_datetime = post_date.replace(hour=hour, minute=minute)

        schedule.append({
            **meta,
            'scheduled_date': post_datetime.strftime('%Y-%m-%d'),
            'scheduled_time': post_time,
            'post_number': i + 1,
            'day': day_offset + 1,
        })

    # Save schedule
    schedule_file = POSTING_DIR / "schedule.json"
    with open(schedule_file, 'w') as f:
        json.dump(schedule, f, indent=2)

    # Generate human-readable posting guide
    guide_lines = [
        "# Instagram Posting Schedule",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total reels: {len(schedule)}",
        f"Schedule: {posts_per_day} posts/day for {min(days, len(schedule) // posts_per_day + 1)} days",
        "",
        "---",
        "",
    ]

    current_day = None
    for post in schedule:
        if post['scheduled_date'] != current_day:
            current_day = post['scheduled_date']
            day_name = datetime.strptime(current_day, '%Y-%m-%d').strftime('%A')
            guide_lines.append(f"\n## {current_day} ({day_name})")
            guide_lines.append("")

        guide_lines.append(f"### Post #{post['post_number']} - {post['scheduled_time']}")
        guide_lines.append(f"**Reel:** `{post['story_name']}`")
        guide_lines.append(f"**File:** `{post['file']}`")
        guide_lines.append(f"**Size:** {post['size_mb']} MB")
        guide_lines.append(f"**Category:** {post['category']}")
        guide_lines.append("")
        guide_lines.append("**Caption (copy-paste):**")
        guide_lines.append("```")
        guide_lines.append(post['caption'])
        guide_lines.append("```")
        guide_lines.append("")

    # Copy reels to posting queue directory with numbered names
    guide_lines.append("\n---\n")
    guide_lines.append("## Quick Upload Order")
    guide_lines.append("")
    for post in schedule:
        numbered_name = f"{post['post_number']:02d}_{post['story_name']}.mp4"
        dest = POSTING_DIR / numbered_name
        if not dest.exists():
            shutil.copy2(post['file'], dest)
        guide_lines.append(f"{post['post_number']:02d}. `{numbered_name}` - {post['scheduled_time']} on {post['scheduled_date']}")

    guide_file = POSTING_DIR / "POSTING_GUIDE.md"
    with open(guide_file, 'w') as f:
        f.write('\n'.join(guide_lines))

    print(f"\n{'='*50}")
    print(f"  POSTING QUEUE READY")
    print(f"  {len(schedule)} reels scheduled over {min(days, len(schedule) // posts_per_day + 1)} days")
    print(f"  Schedule: {schedule_file}")
    print(f"  Guide: {guide_file}")
    print(f"  Reels copied to: {POSTING_DIR}/")
    print(f"{'='*50}")
    print(f"\nNext steps:")
    print(f"  1. Create Instagram Business/Creator account")
    print(f"  2. Open POSTING_GUIDE.md for copy-paste captions")
    print(f"  3. Upload reels in order from {POSTING_DIR}/")
    print(f"  4. Post at scheduled times for maximum reach")


def main():
    if '--queue' in sys.argv:
        days = 14
        if '--days' in sys.argv:
            idx = sys.argv.index('--days')
            days = int(sys.argv[idx + 1])
        generate_posting_queue(days)

    elif '--prepare' in sys.argv:
        idx = sys.argv.index('--prepare')
        name = sys.argv[idx + 1]
        meta = prepare_reel_for_posting(name)
        if meta:
            print(json.dumps(meta, indent=2))

    elif '--api' in sys.argv:
        print("Instagram Graph API posting requires:")
        print("  1. Instagram Business or Creator account")
        print("  2. Facebook Page connected to Instagram")
        print("  3. Facebook App with instagram_content_publish permission")
        print("  4. Access token")
        print("")
        print("For now, use --queue mode for manual posting with prepared captions.")
        print("API auto-posting will be added once Instagram account is set up.")

    else:
        print("Usage:")
        print("  python3 instagram_post.py --queue              # generate posting schedule")
        print("  python3 instagram_post.py --queue --days 14    # 14-day schedule")
        print("  python3 instagram_post.py --prepare story-name # prepare one reel")
        print("  python3 instagram_post.py --api                # auto-post (needs setup)")


if __name__ == '__main__':
    main()
