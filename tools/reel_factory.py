#!/usr/bin/env python3
"""
Reel Factory — Automated Short-Form Video Production Pipeline

Input: topic, subreddit, or RSS feed
Output: reel-ready package (script, image prompts, narration text, music mood)

Usage:
    python3 reel_factory.py topic "ADHD productivity tips"
    python3 reel_factory.py reddit "r/entrepreneur" --count 5
    python3 reel_factory.py rss --count 3
    python3 reel_factory.py batch --topics topics.txt --count 10
    python3 reel_factory.py list                # show queued reels
"""

import json
import os
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "tools" / "reel-pipeline" / "factory-output"
VOICE_BIBLE = BASE_DIR / "mem" / "voice-bible.md"
QUEUE_FILE = OUTPUT_DIR / "reel-queue.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def color(t, c):
    return f"\033[{c}m{t}\033[0m"

def green(t): return color(t, "32")
def cyan(t): return color(t, "36")
def dim(t): return color(t, "90")
def gold(t): return color(t, "33")


# ── SCRIPT GENERATOR ──────────────────────────────────────────

class ReelScript:
    """Generate a 30-60 second reel script."""

    # Hook formulas (first 3 seconds)
    HOOKS = [
        "Stop scrolling. {topic} is broken and here's why.",
        "I built {result} in {time}. Here's how.",
        "Nobody talks about this {topic} problem.",
        "You're doing {topic} wrong. Let me explain.",
        "{stat}. Let that sink in.",
        "The {topic} advice everyone gives is wrong.",
        "I tried {topic} for {time}. Here's what happened.",
        "This one {topic} trick changed everything.",
    ]

    # Body structures
    BODIES = {
        "listicle": "Point 1: {p1}\nPoint 2: {p2}\nPoint 3: {p3}",
        "story": "I was {before}. Then I discovered {discovery}. Now I'm {after}.",
        "myth_bust": "Everyone says {myth}. But actually {truth}. Here's proof: {proof}.",
        "tutorial": "Step 1: {s1}\nStep 2: {s2}\nStep 3: {s3}\nResult: {result}.",
        "hot_take": "{hot_take}. I know, controversial. But {reason}. And {proof}.",
    }

    # CTAs
    CTAS = [
        "Follow for more. Link in bio.",
        "Save this. You'll need it later.",
        "Comment 'system' and I'll send you the blueprint.",
        "Share this with someone who needs it.",
        "Follow @behikeai for daily builder tips.",
    ]

    MUSIC_MOODS = {
        "motivational": {"genre": "lo-fi hip hop", "energy": "medium", "bpm": "85-95"},
        "urgent": {"genre": "trap", "energy": "high", "bpm": "130-150"},
        "calm": {"genre": "ambient", "energy": "low", "bpm": "70-80"},
        "hype": {"genre": "drill", "energy": "high", "bpm": "140-160"},
        "emotional": {"genre": "piano", "energy": "low", "bpm": "60-80"},
    }

    @classmethod
    def generate(cls, topic, style="listicle", mood="motivational"):
        """Generate a complete reel script package."""
        reel_id = f"REEL-{hashlib.md5(f'{topic}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"

        # Pick hook
        hook = cls.HOOKS[hash(topic) % len(cls.HOOKS)].format(
            topic=topic,
            result="100+ products",
            time="2 weeks",
            stat="78 products built. $0 spent on courses"
        )

        # Generate body based on style
        if style == "listicle":
            body = f"1. {topic} starts with a system, not motivation.\n2. One page beats a 40-hour course.\n3. Ship daily. Perfect is the enemy of done."
        elif style == "story":
            body = f"6 months ago I had zero products, zero revenue, zero system.\nThen I found Claude Code and built a system.\nNow I have 89 products and growing."
        elif style == "myth_bust":
            body = f"Everyone says you need a course to learn {topic}.\nBut I built 89 products without taking a single course.\nThe system is the teacher. The results are the proof."
        elif style == "tutorial":
            body = f"Step 1: Pick a niche (don't overthink it).\nStep 2: Build one product in one day.\nStep 3: List it for $4.99.\nStep 4: Post about it.\nResult: first dollar."
        elif style == "hot_take":
            body = f"Courses are a scam. {topic} doesn't need 40 hours of video.\nIt needs one page you can fill in and build from.\nI prove it with every product I ship."
        else:
            body = f"Here's what nobody tells you about {topic}."

        # CTA
        cta = cls.CTAS[hash(topic + style) % len(cls.CTAS)]

        # Full script
        script = f"{hook}\n\n{body}\n\n{cta}"

        # Image prompts (for AI image generation)
        image_prompts = [
            f"Dark minimal desk setup with laptop showing code, neon accent lighting, top-down view, moody atmosphere",
            f"Close-up of hands typing on a mechanical keyboard, dark room, single monitor glow, cinematic",
            f"Minimalist product grid layout on dark background, digital products floating, 3D render style",
        ]

        # Narration segments
        words = script.split()
        duration_seconds = len(words) / 2.5  # ~150 words per minute

        music = cls.MUSIC_MOODS.get(mood, cls.MUSIC_MOODS["motivational"])

        return {
            "id": reel_id,
            "topic": topic,
            "style": style,
            "hook": hook,
            "body": body,
            "cta": cta,
            "full_script": script,
            "word_count": len(words),
            "estimated_duration": f"{int(duration_seconds)}s",
            "image_prompts": image_prompts,
            "music_mood": mood,
            "music_config": music,
            "narration_text": script,
            "status": "draft",
            "generated_at": datetime.now().isoformat(),
            "platforms": ["instagram_reel", "tiktok", "youtube_short"],
        }


# ── QUEUE MANAGER ──────────────────────────────────────────

def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return {"reels": [], "produced": 0, "total_generated": 0}

def save_queue(queue):
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))


# ── CLI ──────────────────────────────────────────

def cmd_topic(args):
    """Generate reels from a topic."""
    topic = " ".join(args) if args else "building with AI"
    styles = ["listicle", "story", "myth_bust", "tutorial", "hot_take"]
    moods = ["motivational", "urgent", "calm", "hype", "emotional"]

    queue = load_queue()
    generated = []

    for i, style in enumerate(styles):
        mood = moods[i % len(moods)]
        reel = ReelScript.generate(topic, style=style, mood=mood)
        queue["reels"].append(reel)
        queue["total_generated"] += 1
        generated.append(reel)

        # Save individual reel script
        reel_file = OUTPUT_DIR / f"{reel['id']}.json"
        reel_file.write_text(json.dumps(reel, indent=2, ensure_ascii=False))

    save_queue(queue)

    print(cyan(f"\n{'='*50}"))
    print(cyan(f"  REEL FACTORY — {len(generated)} reels generated"))
    print(cyan(f"{'='*50}"))
    print(f"  Topic: {gold(topic)}")
    print(f"  Styles: {', '.join(styles)}")

    for reel in generated:
        print(f"\n  {cyan(reel['id'])} [{reel['style']}] {reel['estimated_duration']}")
        print(f"    Hook: {reel['hook'][:60]}...")
        print(f"    Music: {reel['music_mood']} ({reel['music_config']['genre']})")

    print(f"\n  Queue: {len(queue['reels'])} reels total")
    print(f"  Output: {OUTPUT_DIR}")


def cmd_batch(args):
    """Generate reels from a topics file."""
    topics_file = None
    count = 5

    i = 0
    while i < len(args):
        if args[i] == "--topics":
            topics_file = args[i+1]
            i += 2
        elif args[i] == "--count":
            count = int(args[i+1])
            i += 2
        else:
            i += 1

    if topics_file and Path(topics_file).exists():
        topics = Path(topics_file).read_text().strip().split("\n")
    else:
        topics = [
            "ADHD productivity system",
            "building 100 products in 2 weeks",
            "why courses are a scam",
            "the one-page business blueprint",
            "AI tools for solopreneurs",
            "how I built a store for $0",
            "stop watching start building",
            "the ADHD builder's advantage",
            "first dollar is the hardest",
            "my AI employee works 24/7",
        ]

    topics = topics[:count]
    total = 0

    for topic in topics:
        print(f"\n  Generating: {topic}")
        # Generate one reel per topic with random style
        styles = ["listicle", "story", "myth_bust", "tutorial", "hot_take"]
        style = styles[hash(topic) % len(styles)]
        reel = ReelScript.generate(topic.strip(), style=style)

        queue = load_queue()
        queue["reels"].append(reel)
        queue["total_generated"] += 1
        save_queue(queue)

        reel_file = OUTPUT_DIR / f"{reel['id']}.json"
        reel_file.write_text(json.dumps(reel, indent=2, ensure_ascii=False))
        total += 1

    print(f"\n  {green(str(total))} reels generated from {len(topics)} topics")


def cmd_list(args):
    """List queued reels."""
    queue = load_queue()
    reels = queue.get("reels", [])

    print(cyan(f"\n  REEL QUEUE ({len(reels)} reels)"))
    print(f"  {'─'*40}")

    for reel in reels[-10:]:
        status_color = {"draft": "90", "ready": "33", "produced": "32"}.get(reel["status"], "90")
        print(f"  {color(reel['status'], status_color):12s} {cyan(reel['id'])} {reel['topic'][:30]} [{reel['style']}] {reel['estimated_duration']}")

    print(f"\n  Total: {len(reels)} | Produced: {queue.get('produced', 0)}")


def main():
    if len(sys.argv) < 2:
        print(cyan("""
  Reel Factory — Automated Content Production
  =============================================

  Commands:
    topic <topic>              Generate 5 reels from a topic
    batch [--topics file] [--count N]  Batch generate from topics
    list                       Show reel queue

  Examples:
    python3 reel_factory.py topic "ADHD productivity"
    python3 reel_factory.py batch --count 10
    python3 reel_factory.py list
        """))
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "topic":
        cmd_topic(args)
    elif cmd == "batch":
        cmd_batch(args)
    elif cmd == "list":
        cmd_list(args)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
