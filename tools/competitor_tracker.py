#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Competitor Tracker. Track competitor accounts, analyze their best content,
and generate ideas inspired by what works.

Usage:
    python3 competitor_tracker.py --add @account --platform ig
    python3 competitor_tracker.py --add @account --platform tt --niche "AI education"
    python3 competitor_tracker.py --list                                # list tracked competitors
    python3 competitor_tracker.py --log @account --post-id P1 --likes 500 --comments 30 --type carousel --hook "Question hook" --topic "AI tools"
    python3 competitor_tracker.py --analyze @account                    # analyze their content
    python3 competitor_tracker.py --analyze-all                         # analyze all competitors
    python3 competitor_tracker.py --steal                               # generate inspired content ideas
    python3 competitor_tracker.py --steal --count 5                     # generate 5 ideas
    python3 competitor_tracker.py --report                              # full competitor landscape report
    python3 competitor_tracker.py --help

Data stored at: Ceiba/news/competitors.json
"""

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
COMPETITORS_FILE = NEWS_DIR / "competitors.json"

PLATFORMS = ["ig", "tt", "yt", "x"]
CONTENT_TYPES = ["carousel", "reel", "story", "photo", "video", "short", "thread"]
HOOK_TYPES = ["question", "bold_claim", "statistic", "story_opener", "controversy",
              "how_to", "list", "challenge", "trend_ride", "behind_scenes"]


# --- Data helpers ---

def load_data() -> dict:
    """Load competitor tracking data."""
    if COMPETITORS_FILE.exists():
        with open(COMPETITORS_FILE) as f:
            return json.load(f)
    return {"competitors": {}, "created": datetime.now().isoformat()}


def save_data(data: dict):
    """Save competitor tracking data."""
    COMPETITORS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(COMPETITORS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# --- Commands ---

def cmd_add(args):
    """Add a competitor to track."""
    data = load_data()
    handle = args.add.lstrip("@")
    platform = args.platform or "ig"
    niche = args.niche or ""

    if handle in data["competitors"]:
        print(f"[!] @{handle} is already tracked.")
        existing = data["competitors"][handle]
        print(f"    Platform: {existing.get('platform', '?')}")
        print(f"    Posts logged: {len(existing.get('posts', []))}")
        return

    data["competitors"][handle] = {
        "handle": handle,
        "platform": platform,
        "niche": niche,
        "added_at": datetime.now().isoformat(),
        "posts": [],
        "notes": "",
    }

    save_data(data)
    print(f"[+] Now tracking @{handle} on {platform}")
    if niche:
        print(f"    Niche: {niche}")


def cmd_list(args):
    """List all tracked competitors."""
    data = load_data()
    competitors = data.get("competitors", {})

    if not competitors:
        print("No competitors tracked yet.")
        print("Add one: python3 competitor_tracker.py --add @account --platform ig")
        return

    print(f"\nTracked competitors ({len(competitors)}):\n")
    print(f"{'Handle':>20}  {'Platform':>8}  {'Posts':>5}  {'Niche'}")
    print("-" * 70)

    for handle, info in sorted(competitors.items()):
        platform = info.get("platform", "?")
        posts = len(info.get("posts", []))
        niche = info.get("niche", "")[:30]
        print(f"  @{handle:<18}  {platform:>8}  {posts:>5}  {niche}")

    print()


def cmd_log(args):
    """Log a competitor's post performance."""
    data = load_data()
    handle = args.log.lstrip("@")

    if handle not in data["competitors"]:
        print(f"[!] @{handle} is not tracked. Add first with --add")
        return

    post = {
        "post_id": args.post_id or f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "content_type": args.type or "unknown",
        "topic": args.topic or "",
        "hook": args.hook or "",
        "hook_type": args.hook_type or "",
        "hashtags": args.hashtags.split(",") if args.hashtags else [],
        "metrics": {
            "likes": args.likes or 0,
            "comments": args.comments or 0,
            "shares": args.shares or 0,
            "saves": args.saves or 0,
            "views": args.views or 0,
        },
        "logged_at": datetime.now().isoformat(),
        "notes": args.notes or "",
    }

    # Calculate engagement (using views if available, otherwise likes as proxy)
    base = post["metrics"]["views"] if post["metrics"]["views"] > 0 else post["metrics"]["likes"] * 10
    if base > 0:
        total = sum(post["metrics"].values())
        post["engagement_rate"] = round((total / base) * 100, 2)
    else:
        post["engagement_rate"] = 0

    data["competitors"][handle]["posts"].append(post)
    save_data(data)

    print(f"[LOGGED] Post for @{handle}")
    print(f"  Type: {post['content_type']}")
    print(f"  Topic: {post['topic']}")
    print(f"  Likes: {post['metrics']['likes']}, Comments: {post['metrics']['comments']}")
    if post["engagement_rate"] > 0:
        print(f"  Engagement: {post['engagement_rate']}%")


def cmd_analyze(args):
    """Analyze a competitor's content patterns."""
    data = load_data()
    handle = args.analyze.lstrip("@")

    if handle not in data["competitors"]:
        print(f"[!] @{handle} is not tracked.")
        return

    comp = data["competitors"][handle]
    posts = comp.get("posts", [])

    if not posts:
        print(f"[!] No posts logged for @{handle}")
        print("    Log posts with: --log @account --post-id P1 --likes N ...")
        return

    print()
    print("=" * 60)
    print(f"  ANALYSIS: @{handle}")
    print("=" * 60)
    print()
    print(f"  Platform: {comp.get('platform', '?')}")
    print(f"  Niche: {comp.get('niche', 'N/A')}")
    print(f"  Posts analyzed: {len(posts)}")
    print()

    # Content type breakdown
    type_counts = Counter(p.get("content_type", "unknown") for p in posts)
    type_engagement = defaultdict(list)
    for p in posts:
        ct = p.get("content_type", "unknown")
        type_engagement[ct].append(p.get("engagement_rate", 0))

    print("  Content type mix:")
    for ct, count in type_counts.most_common():
        avg_eng = sum(type_engagement[ct]) / len(type_engagement[ct]) if type_engagement[ct] else 0
        pct = (count / len(posts)) * 100
        print(f"    {ct}: {count} posts ({pct:.0f}%), {avg_eng:.1f}% avg engagement")

    # Hook analysis
    hook_types = Counter(p.get("hook_type", "") for p in posts if p.get("hook_type"))
    if hook_types:
        print()
        print("  Hook styles used:")
        hook_eng = defaultdict(list)
        for p in posts:
            ht = p.get("hook_type", "")
            if ht:
                hook_eng[ht].append(p.get("engagement_rate", 0))
        for ht, count in hook_types.most_common():
            avg = sum(hook_eng[ht]) / len(hook_eng[ht])
            print(f"    {ht}: {count} times, {avg:.1f}% avg engagement")

    # Topic analysis
    topic_words = Counter()
    for p in posts:
        topic = p.get("topic", "")
        for word in topic.lower().split():
            if len(word) > 3:
                topic_words[word] += 1

    if topic_words:
        print()
        print("  Most common topics:")
        for word, count in topic_words.most_common(10):
            print(f"    '{word}': {count} mentions")

    # Top posts
    sorted_posts = sorted(posts, key=lambda p: p.get("engagement_rate", 0), reverse=True)
    print()
    print("  Top 5 posts:")
    for i, p in enumerate(sorted_posts[:5], 1):
        topic = p.get("topic", p.get("post_id", "?"))[:35]
        eng = p.get("engagement_rate", 0)
        ct = p.get("content_type", "?")
        hook = p.get("hook", "")[:30]
        print(f"    {i}. [{ct}] {topic} ({eng:.1f}%)")
        if hook:
            print(f"       Hook: \"{hook}\"")

    # Hashtag analysis
    hashtag_counts = Counter()
    for p in posts:
        for tag in p.get("hashtags", []):
            hashtag_counts[tag] += 1

    if hashtag_counts:
        print()
        print("  Most used hashtags:")
        for tag, count in hashtag_counts.most_common(10):
            print(f"    {tag}: {count}")

    # Posting frequency
    avg_likes = sum(p["metrics"]["likes"] for p in posts) / len(posts)
    avg_comments = sum(p["metrics"]["comments"] for p in posts) / len(posts)
    print()
    print("  Averages:")
    print(f"    Likes: {avg_likes:.0f}")
    print(f"    Comments: {avg_comments:.0f}")

    print()
    print("=" * 60)
    print()


def cmd_analyze_all(args):
    """Analyze all tracked competitors."""
    data = load_data()
    for handle in data.get("competitors", {}):
        args.analyze = handle
        cmd_analyze(args)


def cmd_steal(args):
    """Generate content ideas inspired by competitor top-performing content."""
    data = load_data()
    competitors = data.get("competitors", {})

    if not competitors:
        print("[!] No competitors tracked. Add some first.")
        return

    # Collect all posts across competitors
    all_posts = []
    for handle, comp in competitors.items():
        for post in comp.get("posts", []):
            post["_competitor"] = handle
            post["_platform"] = comp.get("platform", "?")
            post["_niche"] = comp.get("niche", "")
            all_posts.append(post)

    if not all_posts:
        print("[!] No posts logged for any competitor.")
        print("    Log posts first with --log")
        return

    # Sort by engagement
    all_posts.sort(key=lambda p: p.get("engagement_rate", 0), reverse=True)

    # Take top performing posts
    top_posts = all_posts[:20]
    count = args.count or 3

    # Generate ideas from top posts
    idea_templates = [
        "Create a {type} about '{topic}' but from Behike's perspective. Use a {hook_type} hook.",
        "The topic '{topic}' performs well as a {type}. Create our version focusing on the builder angle.",
        "@{comp} got {eng}% engagement with '{topic}'. Create something similar but with Behike's voice.",
        "Competitor uses '{hook}' as a hook style. Apply this to our '{topic}' content.",
        "Take the concept of '{topic}' and reframe it as a {type} for Spanish-speaking builders.",
    ]

    print()
    print("=" * 60)
    print("  CONTENT IDEAS (Inspired by competitor analysis)")
    print("=" * 60)
    print()

    ideas = []
    used_topics = set()

    for post in top_posts:
        if len(ideas) >= count:
            break

        topic = post.get("topic", "")
        if not topic or topic in used_topics:
            continue
        used_topics.add(topic)

        template = random.choice(idea_templates)
        idea = template.format(
            type=post.get("content_type", "reel"),
            topic=topic,
            hook_type=post.get("hook_type", "bold_claim"),
            hook=post.get("hook", "")[:40],
            comp=post.get("_competitor", "?"),
            eng=post.get("engagement_rate", 0),
        )

        ideas.append({
            "idea": idea,
            "inspired_by": f"@{post['_competitor']}",
            "original_type": post.get("content_type", "?"),
            "original_topic": topic,
            "original_engagement": post.get("engagement_rate", 0),
            "suggested_type": post.get("content_type", "reel"),
            "suggested_hook": post.get("hook_type", "bold_claim"),
        })

        print(f"  {len(ideas)}. {idea}")
        print(f"     Inspired by: @{post['_competitor']} ({post.get('engagement_rate', 0)}% engagement)")
        print()

    if not ideas:
        print("  Could not generate ideas. Need more post data.")
        print("  Log competitor posts with --log")

    # Save ideas to a file
    ideas_file = NEWS_DIR / "competitor-ideas.json"
    existing_ideas = []
    if ideas_file.exists():
        try:
            with open(ideas_file) as f:
                existing_ideas = json.load(f).get("ideas", [])
        except Exception:
            pass

    for idea in ideas:
        idea["generated_at"] = datetime.now().isoformat()

    all_ideas = existing_ideas + ideas
    with open(ideas_file, "w") as f:
        json.dump({"ideas": all_ideas, "last_generated": datetime.now().isoformat()}, f, indent=2)

    print(f"  Saved {len(ideas)} new ideas to {ideas_file}")
    print("=" * 60)
    print()


def cmd_report(args):
    """Full competitor landscape report."""
    data = load_data()
    competitors = data.get("competitors", {})

    if not competitors:
        print("[!] No competitors tracked.")
        return

    print()
    print("=" * 60)
    print("  COMPETITOR LANDSCAPE REPORT")
    print("=" * 60)
    print()

    # Overview
    total_posts = sum(len(c.get("posts", [])) for c in competitors.values())
    platforms = Counter(c.get("platform", "?") for c in competitors.values())

    print(f"  Competitors tracked: {len(competitors)}")
    print(f"  Total posts logged: {total_posts}")
    print(f"  Platforms: {', '.join(f'{p} ({n})' for p, n in platforms.most_common())}")
    print()

    # Per-competitor summary
    print(f"  {'Competitor':>20}  {'Posts':>5}  {'Avg Eng':>8}  {'Best Type':>12}  {'Niche'}")
    print("  " + "-" * 75)

    for handle, comp in sorted(competitors.items()):
        posts = comp.get("posts", [])
        niche = comp.get("niche", "")[:20]

        if posts:
            avg_eng = sum(p.get("engagement_rate", 0) for p in posts) / len(posts)
            type_counts = Counter(p.get("content_type", "?") for p in posts)
            best_type = type_counts.most_common(1)[0][0]
        else:
            avg_eng = 0
            best_type = "N/A"

        print(f"  @{handle:<18}  {len(posts):>5}  {avg_eng:>7.1f}%  {best_type:>12}  {niche}")

    # Global patterns
    if total_posts >= 5:
        print()
        print("  GLOBAL PATTERNS:")

        all_types = Counter()
        all_hooks = Counter()
        type_eng = defaultdict(list)

        for comp in competitors.values():
            for p in comp.get("posts", []):
                ct = p.get("content_type", "")
                if ct:
                    all_types[ct] += 1
                    type_eng[ct].append(p.get("engagement_rate", 0))
                ht = p.get("hook_type", "")
                if ht:
                    all_hooks[ht] += 1

        print()
        print("    Most common content types across competitors:")
        for ct, count in all_types.most_common(5):
            avg = sum(type_eng[ct]) / len(type_eng[ct])
            print(f"      {ct}: {count} posts, {avg:.1f}% avg engagement")

        if all_hooks:
            print()
            print("    Most common hook styles:")
            for ht, count in all_hooks.most_common(5):
                print(f"      {ht}: {count} uses")

    print()
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Competitor Tracker. Analyze what works for others, apply it to Behike. Copyright 2026 Behike."
    )

    # Management
    parser.add_argument("--add", type=str, help="Add a competitor account to track")
    parser.add_argument("--platform", choices=PLATFORMS, help="Platform: ig, tt, yt, x")
    parser.add_argument("--niche", type=str, help="Competitor's niche/category")
    parser.add_argument("--list", action="store_true", help="List tracked competitors")

    # Logging
    parser.add_argument("--log", type=str, help="Log a post for a competitor")
    parser.add_argument("--post-id", type=str, help="Post identifier")
    parser.add_argument("--likes", type=int, default=0)
    parser.add_argument("--comments", type=int, default=0)
    parser.add_argument("--shares", type=int, default=0)
    parser.add_argument("--saves", type=int, default=0)
    parser.add_argument("--views", type=int, default=0)
    parser.add_argument("--type", choices=CONTENT_TYPES, help="Content type")
    parser.add_argument("--topic", type=str, help="Post topic")
    parser.add_argument("--hook", type=str, help="Hook text used")
    parser.add_argument("--hook-type", choices=HOOK_TYPES, help="Hook style")
    parser.add_argument("--hashtags", type=str, help="Comma-separated hashtags")
    parser.add_argument("--notes", type=str, help="Additional notes")

    # Analysis
    parser.add_argument("--analyze", type=str, help="Analyze a competitor's content")
    parser.add_argument("--analyze-all", action="store_true", help="Analyze all competitors")
    parser.add_argument("--steal", action="store_true", help="Generate inspired content ideas")
    parser.add_argument("--count", type=int, default=3, help="Number of ideas to generate")
    parser.add_argument("--report", action="store_true", help="Full competitor landscape report")

    args = parser.parse_args()

    if args.add:
        cmd_add(args)
    elif args.list:
        cmd_list(args)
    elif args.log:
        cmd_log(args)
    elif args.analyze:
        cmd_analyze(args)
    elif args.analyze_all:
        cmd_analyze_all(args)
    elif args.steal:
        cmd_steal(args)
    elif args.report:
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
