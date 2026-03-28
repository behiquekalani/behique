#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Performance Tracker. Tracks posted content performance and identifies
what works best. Feeds insights back into the script writer.

Usage:
    python3 performance_tracker.py --log POST_ID --likes 150 --comments 12 --shares 8 --saves 45 --reach 2500
    python3 performance_tracker.py --log POST_ID --likes 150 --comments 12 --content-type carousel --topic "AI tools" --hook-style question --account behikeai
    python3 performance_tracker.py --report              # show performance report
    python3 performance_tracker.py --report --weekly      # this week only
    python3 performance_tracker.py --top 10               # top 10 posts by engagement
    python3 performance_tracker.py --insights             # generate insights for script writer
    python3 performance_tracker.py --export               # export data as CSV
    python3 performance_tracker.py --help

Data stored at: Ceiba/news/analytics.json
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
ANALYTICS_FILE = NEWS_DIR / "analytics.json"
INSIGHTS_FILE = NEWS_DIR / "performance-insights.json"

ACCOUNTS = ["behikeai", "kalaniandrez", "dulc3recuerdo", "s0ftrewind"]

CONTENT_TYPES = ["carousel", "reel", "story", "meme", "quote", "photo", "video"]
HOOK_STYLES = ["question", "bold_claim", "statistic", "story_opener", "controversy", "how_to", "list"]


# --- Data helpers ---

def load_analytics() -> dict:
    """Load analytics data from disk."""
    if ANALYTICS_FILE.exists():
        with open(ANALYTICS_FILE) as f:
            return json.load(f)
    return {"posts": [], "created": datetime.now().isoformat()}


def save_analytics(data: dict):
    """Save analytics data to disk."""
    ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def calc_engagement_rate(likes: int, comments: int, shares: int, saves: int, reach: int) -> float:
    """Calculate engagement rate as percentage."""
    if reach <= 0:
        return 0.0
    total_interactions = likes + comments + shares + saves
    return round((total_interactions / reach) * 100, 2)


# --- Commands ---

def cmd_log(args):
    """Log a post's performance metrics."""
    data = load_analytics()
    now = datetime.now().isoformat()

    likes = args.likes or 0
    comments = args.comments or 0
    shares = args.shares or 0
    saves = args.saves or 0
    reach = args.reach or 0

    engagement = calc_engagement_rate(likes, comments, shares, saves, reach)

    # Check if this post ID already exists (update it)
    existing = None
    for i, post in enumerate(data["posts"]):
        if post.get("post_id") == args.log:
            existing = i
            break

    entry = {
        "post_id": args.log,
        "account": args.account or "behikeai",
        "content_type": args.content_type or "",
        "topic": args.topic or "",
        "hook_style": args.hook_style or "",
        "hashtags": args.hashtags.split(",") if args.hashtags else [],
        "posted_at": args.posted_at or now,
        "logged_at": now,
        "metrics": {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "reach": reach,
        },
        "engagement_rate": engagement,
        "posting_hour": _extract_hour(args.posted_at or now),
        "posting_day": _extract_day(args.posted_at or now),
    }

    if existing is not None:
        data["posts"][existing] = entry
        print(f"[UPDATED] Post {args.log}")
    else:
        data["posts"].append(entry)
        print(f"[LOGGED] Post {args.log}")

    save_analytics(data)

    print(f"  Likes: {likes}, Comments: {comments}, Shares: {shares}, Saves: {saves}")
    print(f"  Reach: {reach}")
    print(f"  Engagement rate: {engagement}%")
    if engagement >= 5:
        print(f"  Performance: EXCELLENT")
    elif engagement >= 3:
        print(f"  Performance: GOOD")
    elif engagement >= 1:
        print(f"  Performance: AVERAGE")
    else:
        print(f"  Performance: BELOW AVERAGE")


def _extract_hour(iso_str: str) -> int:
    """Extract hour from ISO datetime string."""
    try:
        return datetime.fromisoformat(iso_str).hour
    except (ValueError, TypeError):
        return -1


def _extract_day(iso_str: str) -> str:
    """Extract day name from ISO datetime string."""
    try:
        return datetime.fromisoformat(iso_str).strftime("%A")
    except (ValueError, TypeError):
        return "Unknown"


def cmd_report(args):
    """Generate a performance report."""
    data = load_analytics()
    posts = data.get("posts", [])

    if not posts:
        print("No performance data logged yet.")
        print("Use: python3 performance_tracker.py --log POST_ID --likes N --comments N ...")
        return

    # Filter to this week if requested
    if args.weekly:
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        filtered = []
        for p in posts:
            try:
                logged = datetime.fromisoformat(p.get("logged_at", ""))
                if logged >= week_start:
                    filtered.append(p)
            except (ValueError, TypeError):
                continue
        posts = filtered
        period = f"This Week ({week_start.strftime('%b %d')} - {now.strftime('%b %d')})"
    else:
        period = "All Time"

    if not posts:
        print(f"No posts found for period: {period}")
        return

    # Aggregate metrics
    total_likes = sum(p["metrics"]["likes"] for p in posts)
    total_comments = sum(p["metrics"]["comments"] for p in posts)
    total_shares = sum(p["metrics"]["shares"] for p in posts)
    total_saves = sum(p["metrics"]["saves"] for p in posts)
    total_reach = sum(p["metrics"]["reach"] for p in posts)
    avg_engagement = sum(p.get("engagement_rate", 0) for p in posts) / len(posts)

    print()
    print("=" * 60)
    print(f"  PERFORMANCE REPORT. {period}")
    print("=" * 60)
    print()
    print(f"  Total posts:      {len(posts)}")
    print(f"  Total reach:      {total_reach:,}")
    print(f"  Total likes:      {total_likes:,}")
    print(f"  Total comments:   {total_comments:,}")
    print(f"  Total shares:     {total_shares:,}")
    print(f"  Total saves:      {total_saves:,}")
    print(f"  Avg engagement:   {avg_engagement:.2f}%")
    print()

    # Per account
    by_account = defaultdict(list)
    for p in posts:
        by_account[p.get("account", "unknown")].append(p)

    print("  BY ACCOUNT:")
    for account in sorted(by_account.keys()):
        acct_posts = by_account[account]
        acct_eng = sum(p.get("engagement_rate", 0) for p in acct_posts) / len(acct_posts)
        acct_reach = sum(p["metrics"]["reach"] for p in acct_posts)
        print(f"    @{account}: {len(acct_posts)} posts, {acct_reach:,} reach, {acct_eng:.2f}% avg engagement")

    # Per content type
    by_type = defaultdict(list)
    for p in posts:
        ct = p.get("content_type", "unknown")
        if ct:
            by_type[ct].append(p)

    if by_type:
        print()
        print("  BY CONTENT TYPE:")
        for ct in sorted(by_type.keys()):
            ct_posts = by_type[ct]
            ct_eng = sum(p.get("engagement_rate", 0) for p in ct_posts) / len(ct_posts)
            print(f"    {ct}: {len(ct_posts)} posts, {ct_eng:.2f}% avg engagement")

    # Best posting times
    by_hour = defaultdict(list)
    for p in posts:
        h = p.get("posting_hour", -1)
        if h >= 0:
            by_hour[h].append(p.get("engagement_rate", 0))

    if by_hour:
        print()
        print("  BEST POSTING HOURS:")
        hour_avgs = [(h, sum(rates) / len(rates)) for h, rates in by_hour.items()]
        hour_avgs.sort(key=lambda x: x[1], reverse=True)
        for h, avg in hour_avgs[:5]:
            period_label = "AM" if h < 12 else "PM"
            display_h = h if h <= 12 else h - 12
            if display_h == 0:
                display_h = 12
            print(f"    {display_h}:00 {period_label}: {avg:.2f}% avg engagement")

    # Top posts
    sorted_posts = sorted(posts, key=lambda p: p.get("engagement_rate", 0), reverse=True)
    print()
    print("  TOP 5 POSTS:")
    for i, p in enumerate(sorted_posts[:5], 1):
        topic = p.get("topic", p.get("post_id", "?"))[:40]
        eng = p.get("engagement_rate", 0)
        ct = p.get("content_type", "?")
        print(f"    {i}. [{ct}] {topic}. {eng}% engagement")

    # Bottom posts
    if len(sorted_posts) > 5:
        print()
        print("  BOTTOM 3 POSTS:")
        for i, p in enumerate(sorted_posts[-3:], 1):
            topic = p.get("topic", p.get("post_id", "?"))[:40]
            eng = p.get("engagement_rate", 0)
            ct = p.get("content_type", "?")
            print(f"    {i}. [{ct}] {topic}. {eng}% engagement")

    print()
    print("=" * 60)
    print()


def cmd_top(args):
    """Show top N posts by engagement rate."""
    data = load_analytics()
    posts = data.get("posts", [])

    if not posts:
        print("No performance data logged yet.")
        return

    n = args.top
    sorted_posts = sorted(posts, key=lambda p: p.get("engagement_rate", 0), reverse=True)

    print(f"\nTop {n} posts by engagement rate:\n")
    print(f"{'#':>3}  {'Engagement':>10}  {'Type':>10}  {'Account':>15}  {'Topic'}")
    print("-" * 75)

    for i, p in enumerate(sorted_posts[:n], 1):
        eng = f"{p.get('engagement_rate', 0):.2f}%"
        ct = p.get("content_type", "?")
        acct = p.get("account", "?")
        topic = p.get("topic", p.get("post_id", "?"))[:35]
        print(f"{i:3d}  {eng:>10}  {ct:>10}  {acct:>15}  {topic}")

    print()


def cmd_insights(args):
    """Generate insights for the script writer and content calendar."""
    data = load_analytics()
    posts = data.get("posts", [])

    if len(posts) < 3:
        print("Need at least 3 logged posts to generate insights.")
        print("Log more posts first.")
        return

    insights = {
        "generated_at": datetime.now().isoformat(),
        "total_posts_analyzed": len(posts),
    }

    # Best content types
    by_type = defaultdict(list)
    for p in posts:
        ct = p.get("content_type")
        if ct:
            by_type[ct].append(p.get("engagement_rate", 0))

    type_rankings = [(ct, sum(rates) / len(rates), len(rates))
                     for ct, rates in by_type.items()]
    type_rankings.sort(key=lambda x: x[1], reverse=True)
    insights["best_content_types"] = [
        {"type": ct, "avg_engagement": round(avg, 2), "sample_size": n}
        for ct, avg, n in type_rankings
    ]

    # Best hook styles
    by_hook = defaultdict(list)
    for p in posts:
        hs = p.get("hook_style")
        if hs:
            by_hook[hs].append(p.get("engagement_rate", 0))

    hook_rankings = [(hs, sum(rates) / len(rates), len(rates))
                     for hs, rates in by_hook.items()]
    hook_rankings.sort(key=lambda x: x[1], reverse=True)
    insights["best_hook_styles"] = [
        {"style": hs, "avg_engagement": round(avg, 2), "sample_size": n}
        for hs, avg, n in hook_rankings
    ]

    # Best topics (keywords)
    topic_words = Counter()
    topic_engagement = defaultdict(list)
    for p in posts:
        topic = p.get("topic", "")
        eng = p.get("engagement_rate", 0)
        for word in topic.lower().split():
            if len(word) > 3:  # skip short words
                topic_words[word] += 1
                topic_engagement[word].append(eng)

    best_topics = []
    for word, count in topic_words.most_common(20):
        if count >= 2:
            avg = sum(topic_engagement[word]) / len(topic_engagement[word])
            best_topics.append({"keyword": word, "avg_engagement": round(avg, 2), "count": count})

    best_topics.sort(key=lambda x: x["avg_engagement"], reverse=True)
    insights["best_topic_keywords"] = best_topics[:10]

    # Best posting times
    by_hour = defaultdict(list)
    for p in posts:
        h = p.get("posting_hour", -1)
        if h >= 0:
            by_hour[h].append(p.get("engagement_rate", 0))

    best_hours = [(h, sum(rates) / len(rates)) for h, rates in by_hour.items()]
    best_hours.sort(key=lambda x: x[1], reverse=True)
    insights["best_posting_hours"] = [{"hour": h, "avg_engagement": round(avg, 2)}
                                       for h, avg in best_hours[:5]]

    # Best posting days
    by_day = defaultdict(list)
    for p in posts:
        d = p.get("posting_day", "")
        if d and d != "Unknown":
            by_day[d].append(p.get("engagement_rate", 0))

    best_days = [(d, sum(rates) / len(rates)) for d, rates in by_day.items()]
    best_days.sort(key=lambda x: x[1], reverse=True)
    insights["best_posting_days"] = [{"day": d, "avg_engagement": round(avg, 2)}
                                      for d, avg in best_days]

    # Best hashtags
    hashtag_eng = defaultdict(list)
    for p in posts:
        eng = p.get("engagement_rate", 0)
        for tag in p.get("hashtags", []):
            hashtag_eng[tag].append(eng)

    best_hashtags = [(tag, sum(rates) / len(rates), len(rates))
                     for tag, rates in hashtag_eng.items() if len(rates) >= 2]
    best_hashtags.sort(key=lambda x: x[1], reverse=True)
    insights["best_hashtags"] = [{"hashtag": tag, "avg_engagement": round(avg, 2), "usage": n}
                                  for tag, avg, n in best_hashtags[:10]]

    # Recommendations
    recs = []
    if type_rankings:
        best_type = type_rankings[0]
        recs.append(f"Focus on {best_type[0]} content ({best_type[1]:.1f}% avg engagement)")
    if hook_rankings:
        best_hook = hook_rankings[0]
        recs.append(f"Use {best_hook[0]} hooks more often ({best_hook[1]:.1f}% avg engagement)")
    if best_hours:
        h = best_hours[0][0]
        period_label = "AM" if h < 12 else "PM"
        display_h = h if h <= 12 else h - 12
        if display_h == 0:
            display_h = 12
        recs.append(f"Post at {display_h}:00 {period_label} for best engagement")
    if best_days:
        recs.append(f"Best day to post: {best_days[0][0]}")

    insights["recommendations"] = recs

    # Save insights
    INSIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INSIGHTS_FILE, "w") as f:
        json.dump(insights, f, indent=2)

    # Display
    print()
    print("=" * 60)
    print("  CONTENT PERFORMANCE INSIGHTS")
    print("=" * 60)
    print()

    if insights["best_content_types"]:
        print("  Best content types:")
        for ct in insights["best_content_types"]:
            print(f"    {ct['type']}: {ct['avg_engagement']}% avg ({ct['sample_size']} posts)")

    if insights["best_hook_styles"]:
        print()
        print("  Best hook styles:")
        for hs in insights["best_hook_styles"]:
            print(f"    {hs['style']}: {hs['avg_engagement']}% avg ({hs['sample_size']} posts)")

    if insights["best_topic_keywords"]:
        print()
        print("  Best topic keywords:")
        for kw in insights["best_topic_keywords"][:5]:
            print(f"    '{kw['keyword']}': {kw['avg_engagement']}% avg ({kw['count']} posts)")

    print()
    print("  Recommendations:")
    for rec in recs:
        print(f"    - {rec}")

    print()
    print(f"  Saved to: {INSIGHTS_FILE}")
    print("=" * 60)
    print()


def cmd_export(args):
    """Export analytics data as CSV."""
    data = load_analytics()
    posts = data.get("posts", [])

    if not posts:
        print("No data to export.")
        return

    csv_path = NEWS_DIR / f"analytics-export-{datetime.now().strftime('%Y%m%d')}.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "post_id", "account", "content_type", "topic", "hook_style",
            "likes", "comments", "shares", "saves", "reach",
            "engagement_rate", "posting_hour", "posting_day", "posted_at"
        ])

        for p in posts:
            m = p.get("metrics", {})
            writer.writerow([
                p.get("post_id", ""),
                p.get("account", ""),
                p.get("content_type", ""),
                p.get("topic", ""),
                p.get("hook_style", ""),
                m.get("likes", 0),
                m.get("comments", 0),
                m.get("shares", 0),
                m.get("saves", 0),
                m.get("reach", 0),
                p.get("engagement_rate", 0),
                p.get("posting_hour", ""),
                p.get("posting_day", ""),
                p.get("posted_at", ""),
            ])

    print(f"Exported {len(posts)} posts to {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Performance Tracker. Track and analyze content performance. Copyright 2026 Behike."
    )

    # Logging
    parser.add_argument("--log", type=str, help="Post ID to log metrics for")
    parser.add_argument("--likes", type=int, default=0, help="Number of likes")
    parser.add_argument("--comments", type=int, default=0, help="Number of comments")
    parser.add_argument("--shares", type=int, default=0, help="Number of shares")
    parser.add_argument("--saves", type=int, default=0, help="Number of saves")
    parser.add_argument("--reach", type=int, default=0, help="Total reach")
    parser.add_argument("--content-type", choices=CONTENT_TYPES, help="Content type")
    parser.add_argument("--topic", type=str, help="Topic/subject of the post")
    parser.add_argument("--hook-style", choices=HOOK_STYLES, help="Hook style used")
    parser.add_argument("--hashtags", type=str, help="Comma-separated hashtags used")
    parser.add_argument("--account", choices=ACCOUNTS, default="behikeai", help="Account posted on")
    parser.add_argument("--posted-at", type=str, help="When it was posted (ISO format)")

    # Reports
    parser.add_argument("--report", action="store_true", help="Show performance report")
    parser.add_argument("--weekly", action="store_true", help="Filter report to this week")
    parser.add_argument("--top", type=int, help="Show top N posts by engagement")
    parser.add_argument("--insights", action="store_true", help="Generate insights for script writer")
    parser.add_argument("--export", action="store_true", help="Export data as CSV")

    args = parser.parse_args()

    if args.log:
        cmd_log(args)
    elif args.report:
        cmd_report(args)
    elif args.top:
        cmd_top(args)
    elif args.insights:
        cmd_insights(args)
    elif args.export:
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
