#!/usr/bin/env python3
"""
Public Build - Auto-generate social posts from git activity.

Monitors git commits, quest completions, and milestones.
Generates social media posts in Behike's voice.
Outputs to a queue for review before posting.

Usage:
    python3 public_build.py                  # Generate posts from today's commits
    python3 public_build.py --since yesterday # Custom date range
    python3 public_build.py --week           # Full week summary
    python3 public_build.py --milestone      # Check for milestone posts
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "Ceiba" / "content-queue"
VOICE_BIBLE = BASE_DIR / "mem" / "voice-bible.md"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t): return color(t, "32")
def cyan(t): return color(t, "36")
def dim(t): return color(t, "90")
def gold(t): return color(t, "33")


def get_commits(since="today"):
    """Get git commits since a date."""
    if since == "today":
        since_date = datetime.now().strftime("%Y-%m-%d")
    elif since == "yesterday":
        since_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif since == "week":
        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        since_date = since

    result = subprocess.run(
        ["git", "log", f"--since={since_date}", "--pretty=format:%H|%s|%ai|%an",
         "--no-merges"],
        capture_output=True, text=True, cwd=BASE_DIR
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) >= 3:
            commits.append({
                "hash": parts[0][:8],
                "message": parts[1],
                "date": parts[2],
                "author": parts[3] if len(parts) > 3 else ""
            })
    return commits


def get_diff_stats(since="today"):
    """Get file change statistics."""
    if since == "today":
        since_date = datetime.now().strftime("%Y-%m-%d")
    else:
        since_date = since

    result = subprocess.run(
        ["git", "diff", f"--stat", f"HEAD@{{'{since_date}'}}", "HEAD"],
        capture_output=True, text=True, cwd=BASE_DIR
    )

    # Parse shortstat
    result2 = subprocess.run(
        ["git", "log", f"--since={since_date}", "--shortstat", "--pretty=format:"],
        capture_output=True, text=True, cwd=BASE_DIR
    )

    files_changed = 0
    insertions = 0
    deletions = 0

    for line in result2.stdout.split("\n"):
        match = re.search(r"(\d+) files? changed", line)
        if match:
            files_changed += int(match.group(1))
        ins = re.search(r"(\d+) insertions?", line)
        if ins:
            insertions += int(ins.group(1))
        dels = re.search(r"(\d+) deletions?", line)
        if dels:
            deletions += int(dels.group(1))

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "net": insertions - deletions
    }


def detect_milestones(commits, stats):
    """Detect milestone events worth posting about."""
    milestones = []

    # Product count milestones
    product_count = len(list((BASE_DIR / "READY-TO-SELL/products-organized").iterdir()))
    if product_count >= 100:
        milestones.append({"type": "product_count", "value": product_count, "text": f"100+ products built"})
    elif product_count >= 75:
        milestones.append({"type": "product_count", "value": product_count, "text": f"{product_count} products built"})
    elif product_count >= 50:
        milestones.append({"type": "product_count", "value": product_count, "text": f"{product_count} products built"})

    # Commit milestones
    total_commits = int(subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, cwd=BASE_DIR
    ).stdout.strip() or "0")

    if total_commits % 50 == 0 and total_commits > 0:
        milestones.append({"type": "commits", "value": total_commits, "text": f"{total_commits} commits"})

    # Lines of code milestones
    if stats["insertions"] > 1000:
        milestones.append({"type": "loc", "value": stats["insertions"], "text": f"{stats['insertions']}+ lines written today"})

    # Feature keywords in commits
    features = []
    for c in commits:
        msg = c["message"].lower()
        if any(w in msg for w in ["feat:", "feature:", "build:", "new:"]):
            features.append(c["message"])

    if len(features) >= 5:
        milestones.append({"type": "features", "value": len(features), "text": f"{len(features)} features shipped"})

    return milestones


def generate_post(post_type, data):
    """Generate a social media post in Behike voice."""
    posts = []

    if post_type == "daily":
        commits = data["commits"]
        stats = data["stats"]

        # Extract what was built (from commit messages)
        built_items = []
        for c in commits:
            msg = c["message"]
            # Clean up commit message
            msg = re.sub(r"^(feat|fix|update|chore|refactor):\s*", "", msg)
            msg = re.sub(r"\s*Co-Authored-By.*", "", msg)
            if len(msg) > 10:
                built_items.append(msg.split("\n")[0][:100])

        if not built_items:
            return []

        # Short post (Twitter/Instagram caption)
        short = f"Today I built:\n"
        for item in built_items[:5]:
            short += f"• {item}\n"
        short += f"\n{stats['files_changed']} files changed. {stats['insertions']} lines written.\n"
        short += f"\nStop planning. Start building."
        posts.append({"type": "short", "platform": "twitter/instagram", "text": short})

        # Thread post (longer, for Twitter thread or LinkedIn)
        if len(built_items) >= 3:
            thread = f"I shipped {len(commits)} things today. Here's what I built and why.\n\n"
            thread += f"Thread 🧵\n\n"
            for i, item in enumerate(built_items[:7], 1):
                thread += f"{i}/ {item}\n\n"
            thread += f"Total: {stats['files_changed']} files, {stats['insertions']}+ lines of code.\n\n"
            thread += f"The system works. You just have to sit down and build.\n\n"
            thread += f"What did you ship today?"
            posts.append({"type": "thread", "platform": "twitter/linkedin", "text": thread})

    elif post_type == "milestone":
        milestone = data["milestone"]

        text = f"{milestone['text']}.\n\n"
        text += f"Not a course. Not a promise. Built. Shipped. Live.\n\n"

        if milestone["type"] == "product_count":
            text += f"From $0 revenue to {milestone['value']} products. With ADHD. With Claude Code.\n\n"
            text += f"The system works."
        elif milestone["type"] == "loc":
            text += f"{milestone['value']}+ lines of code in one day. Not because I'm fast. Because I have a system.\n\n"
            text += f"AI builds. I direct."

        posts.append({"type": "milestone", "platform": "all", "text": text})

    elif post_type == "weekly":
        commits = data["commits"]
        stats = data["stats"]

        text = f"Weekly build report:\n\n"
        text += f"Commits: {len(commits)}\n"
        text += f"Files changed: {stats['files_changed']}\n"
        text += f"Lines written: {stats['insertions']}\n"
        text += f"Lines deleted: {stats['deletions']}\n"
        text += f"Net new: +{stats['net']}\n\n"

        # Group commits by day
        by_day = {}
        for c in commits:
            day = c["date"][:10]
            by_day.setdefault(day, []).append(c["message"].split("\n")[0][:60])

        for day, msgs in sorted(by_day.items()):
            text += f"{day}: {len(msgs)} commits\n"

        text += f"\nEvery week I build. Every week I ship. That's the system."
        posts.append({"type": "weekly", "platform": "all", "text": text})

    return posts


def save_queue(posts, since):
    """Save posts to the content queue for review."""
    queue_file = OUTPUT_DIR / f"build-posts-{datetime.now().strftime('%Y-%m-%d')}.json"

    existing = []
    if queue_file.exists():
        existing = json.loads(queue_file.read_text())

    for post in posts:
        post["generated_at"] = datetime.now().isoformat()
        post["status"] = "draft"  # draft → approved → posted
        existing.append(post)

    queue_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    return queue_file


def main():
    since = "today"
    mode = "daily"

    for arg in sys.argv[1:]:
        if arg == "--week":
            since = "week"
            mode = "weekly"
        elif arg == "--milestone":
            mode = "milestone"
        elif arg.startswith("--since"):
            since = sys.argv[sys.argv.index(arg) + 1]

    print(cyan(f"\n{'='*50}"))
    print(cyan(f"  PUBLIC BUILD - Auto Social Posts"))
    print(cyan(f"{'='*50}"))

    commits = get_commits(since)
    stats = get_diff_stats(since if since != "week" else (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))

    print(f"\n  Commits: {green(str(len(commits)))}")
    print(f"  Files changed: {green(str(stats['files_changed']))}")
    print(f"  Lines written: {green(str(stats['insertions']))}")
    print(f"  Lines deleted: {dim(str(stats['deletions']))}")

    if not commits:
        print(f"\n  No commits found for period: {since}")
        return

    posts = []

    if mode == "daily":
        posts = generate_post("daily", {"commits": commits, "stats": stats})

    elif mode == "weekly":
        posts = generate_post("weekly", {"commits": commits, "stats": stats})

    elif mode == "milestone":
        milestones = detect_milestones(commits, stats)
        for m in milestones:
            posts.extend(generate_post("milestone", {"milestone": m}))

    # Always check milestones
    milestones = detect_milestones(commits, stats)
    for m in milestones:
        posts.extend(generate_post("milestone", {"milestone": m}))

    if not posts:
        print(f"\n  No posts generated (not enough activity)")
        return

    # Save to queue
    queue_file = save_queue(posts, since)

    print(f"\n  Generated: {gold(str(len(posts)))} posts")
    print(f"  Queue: {dim(str(queue_file))}")

    print(f"\n  {cyan('Preview:')}\n")
    for i, post in enumerate(posts[:3], 1):
        print(f"  [{post['type']}] ({post['platform']})")
        print(f"  {'─'*40}")
        for line in post['text'].split('\n')[:8]:
            print(f"  {line}")
        if len(post['text'].split('\n')) > 8:
            print(f"  ...")
        print()

    print(f"  Review and approve: edit {queue_file}")
    print(f"  Then post manually or use the posting pipeline.")


if __name__ == "__main__":
    main()
