#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Ceiba Morning Brief. The smarter daily briefing.

Shows what the autonomous system did overnight, today's content plan,
captured ideas, product metrics, and the 3 things Kalani should focus on.

Written in Voice Bible tone. Not robot status updates.

Usage:
    python3 ceiba_morning_brief.py               # full morning brief
    python3 ceiba_morning_brief.py --short        # just priorities
    python3 ceiba_morning_brief.py --overnight    # just autonomous log
    python3 ceiba_morning_brief.py --calendar     # just today's content
    python3 ceiba_morning_brief.py --json         # machine-readable output
    python3 ceiba_morning_brief.py --help
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
CEIBA_DIR = PROJECT_DIR / "Ceiba"
NEWS_DIR = CEIBA_DIR / "news"
PRIMER = PROJECT_DIR / "primer.md"

TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_DISPLAY = datetime.now().strftime("%A, %B %d")
HOUR = datetime.now().hour

AUTONOMOUS_LOG = CEIBA_DIR / "AUTONOMOUS_LOG.md"
MASTER_TODO = CEIBA_DIR / "MASTER_TODO.md"
IDEAS_BACKLOG = CEIBA_DIR / "IDEAS_BACKLOG.md"
CALENDAR_JSON = NEWS_DIR / f"calendar-{TODAY}.json"
CALENDAR_MD = NEWS_DIR / f"calendar-{TODAY}.md"
ANALYTICS_FILE = NEWS_DIR / "analytics.json"
INSIGHTS_FILE = NEWS_DIR / "performance-insights.json"
ARTICLES_FILE = NEWS_DIR / "articles.json"


def greeting():
    """Time-appropriate greeting in Voice Bible tone."""
    if HOUR < 12:
        return "Buenos dias."
    elif HOUR < 17:
        return "Buenas tardes."
    else:
        return "Buenas noches."


def read_overnight_activity():
    """Parse the autonomous log for activity since last session."""
    if not AUTONOMOUS_LOG.exists():
        return []

    content = AUTONOMOUS_LOG.read_text()
    entries = []

    # Parse log entries
    pattern = r"### \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+): (.+?)(?:\n\n|\n---)"
    for match in re.finditer(pattern, content, re.DOTALL):
        ts, status, rest = match.groups()
        entry_date = ts.split(" ")[0]

        # Only show today's and yesterday's entries
        if entry_date >= (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
            # Extract task name (first line of rest)
            task_name = rest.split("\n")[0].strip()
            entries.append({
                "timestamp": ts,
                "status": status,
                "task": task_name,
            })

    return entries


def read_content_calendar():
    """Read today's content calendar."""
    if CALENDAR_JSON.exists():
        try:
            return json.loads(CALENDAR_JSON.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    if CALENDAR_MD.exists():
        return {"raw": CALENDAR_MD.read_text()[:500]}

    return None


def read_new_ideas():
    """Check for recently captured ideas."""
    ideas = []

    # Check IDEAS_BACKLOG for today's additions
    if IDEAS_BACKLOG.exists():
        content = IDEAS_BACKLOG.read_text()
        # Look for entries with today's date
        for line in content.split("\n"):
            if TODAY in line and line.strip().startswith("-"):
                ideas.append(line.strip().lstrip("- "))

    # Check for RSS/Reddit captures
    reddit_dir = NEWS_DIR / "reddit"
    if reddit_dir.exists():
        for f in reddit_dir.glob(f"*{TODAY}*"):
            ideas.append(f"Reddit capture: {f.stem}")

    return ideas[:10]


def read_performance_insights():
    """Get latest content performance data."""
    if not INSIGHTS_FILE.exists():
        return None

    try:
        data = json.loads(INSIGHTS_FILE.read_text())
        return data
    except (json.JSONDecodeError, OSError):
        return None


def count_news_articles():
    """Count today's fetched news articles."""
    if not ARTICLES_FILE.exists():
        return 0

    try:
        mtime = datetime.fromtimestamp(ARTICLES_FILE.stat().st_mtime)
        if mtime.date() != datetime.now().date():
            return 0
        articles = json.loads(ARTICLES_FILE.read_text())
        if isinstance(articles, list):
            return len(articles)
        return 0
    except (json.JSONDecodeError, OSError):
        return 0


def determine_priorities():
    """
    Figure out the 3 most important things for today.
    Revenue > audience > infrastructure. Always.
    """
    priorities = []

    # Read primer for current state
    if PRIMER.exists():
        primer = PRIMER.read_text()

        # Check for revenue blockers
        if "revenue = $0" in primer.lower() or "blocker" in primer.lower():
            # Find the next non-blocked revenue action
            if "llc" in primer.lower() and "done" not in primer.lower().split("llc")[0][-50:]:
                priorities.append({
                    "priority": 1,
                    "category": "REVENUE",
                    "task": "File the LLC. Everything else waits on this.",
                    "why": "Can't accept money without it. $150 to unlock the entire pipeline.",
                })

    # Check if content was generated
    if not (NEWS_DIR / "daily-bundles").exists() or not list(
        (NEWS_DIR / "daily-bundles").glob(f"*{TODAY}*")
    ):
        priorities.append({
            "priority": 2,
            "category": "AUDIENCE",
            "task": "Generate and post today's content.",
            "why": "Consistency builds audience. One day missed is momentum lost.",
        })

    # Check for buildable product ideas
    missed = CEIBA_DIR / f"MISSED_IDEAS_{TODAY}.md"
    if missed.exists():
        content = missed.read_text()
        if "buildable now? yes" in content.lower():
            priorities.append({
                "priority": 2,
                "category": "REVENUE",
                "task": "Build one product from the missed ideas list.",
                "why": "Every unbuilt idea is revenue sitting on the table.",
            })

    # Check Gumroad listing status
    if MASTER_TODO.exists():
        todo = MASTER_TODO.read_text()
        if "list products on gumroad" in todo.lower() and "done" not in todo.lower().split("gumroad")[0][-50:]:
            priorities.append({
                "priority": 1,
                "category": "REVENUE",
                "task": "List products on Gumroad. Account exists. Products are built.",
                "why": "Products without a store page make $0.",
            })

    # Infrastructure check
    priorities.append({
        "priority": 3,
        "category": "INFRA",
        "task": "Review the autonomous log. See what got built while you were away.",
        "why": "Ceiba worked. Check the results.",
    })

    # Sort and cap at 3
    priorities.sort(key=lambda p: p["priority"])
    return priorities[:3]


def format_brief(overnight, calendar, ideas, insights, news_count, priorities, short=False):
    """Format the full morning brief in Voice Bible tone."""
    output = []

    # Header
    output.append(f"\n  {greeting()} {TODAY_DISPLAY}.\n")

    if short:
        output.append("  YOUR 3 PRIORITIES TODAY:\n")
        for i, p in enumerate(priorities, 1):
            output.append(f"  {i}. [{p['category']}] {p['task']}")
            output.append(f"     {p['why']}\n")
        return "\n".join(output)

    # Overnight activity
    output.append("  WHAT GOT DONE WHILE YOU WERE AWAY")
    output.append("  " + "-" * 40)
    if overnight:
        completed = [e for e in overnight if e["status"] == "COMPLETED"]
        failed = [e for e in overnight if e["status"] == "FAILED"]
        output.append(f"  {len(completed)} tasks completed. {len(failed)} failed.\n")
        for entry in overnight[:8]:
            status_icon = "+" if entry["status"] == "COMPLETED" else "x"
            output.append(f"  [{status_icon}] {entry['task']}")
    else:
        output.append("  Autonomous system hasn't run yet. Set up the cron or run:")
        output.append("  python3 tools/ceiba_autonomous.py --continuous\n")
    output.append("")

    # Content calendar
    output.append("  TODAY'S CONTENT")
    output.append("  " + "-" * 40)
    if calendar:
        if isinstance(calendar, dict) and "raw" in calendar:
            # Markdown calendar, show first few lines
            lines = calendar["raw"].split("\n")[:10]
            for line in lines:
                if line.strip():
                    output.append(f"  {line.strip()}")
        elif isinstance(calendar, dict):
            posts = calendar.get("posts", calendar.get("schedule", []))
            if isinstance(posts, list):
                for post in posts[:5]:
                    if isinstance(post, dict):
                        t = post.get("time", "")
                        acct = post.get("account", "")
                        ctype = post.get("type", "")
                        topic = post.get("topic", post.get("title", ""))
                        output.append(f"  {t} @{acct} [{ctype}] {topic}")
    else:
        output.append("  No calendar generated yet. Run:")
        output.append("  python3 tools/content_calendar.py --generate")
    output.append("")

    # News
    if news_count > 0:
        output.append(f"  NEWS: {news_count} articles fetched and scored.")
    else:
        output.append("  NEWS: Not fetched yet. Run: python3 tools/ai_news_pipeline.py")
    output.append("")

    # New ideas
    if ideas:
        output.append("  NEW IDEAS CAPTURED")
        output.append("  " + "-" * 40)
        for idea in ideas[:5]:
            output.append(f"  - {idea}")
        if len(ideas) > 5:
            output.append(f"  ... and {len(ideas) - 5} more")
        output.append("")

    # Performance insights
    if insights:
        output.append("  CONTENT PERFORMANCE")
        output.append("  " + "-" * 40)
        if isinstance(insights, dict):
            top_type = insights.get("best_content_type", "")
            best_hook = insights.get("best_hook_style", "")
            best_topic = insights.get("best_topic", "")
            if top_type:
                output.append(f"  Best performing type: {top_type}")
            if best_hook:
                output.append(f"  Best hook style: {best_hook}")
            if best_topic:
                output.append(f"  Top topic: {best_topic}")
        output.append("")

    # Priorities (always last, always visible)
    output.append("  YOUR 3 PRIORITIES TODAY")
    output.append("  " + "-" * 40)
    for i, p in enumerate(priorities, 1):
        output.append(f"\n  {i}. [{p['category']}] {p['task']}")
        output.append(f"     {p['why']}")

    output.append("\n")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Ceiba Morning Brief. What happened, what's planned, what matters.",
    )
    parser.add_argument("--short", action="store_true", help="Just show priorities")
    parser.add_argument("--overnight", action="store_true", help="Just show autonomous log")
    parser.add_argument("--calendar", action="store_true", help="Just show today's content")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    # Gather data
    overnight = read_overnight_activity()
    calendar = read_content_calendar()
    ideas = read_new_ideas()
    insights = read_performance_insights()
    news_count = count_news_articles()
    priorities = determine_priorities()

    if args.json:
        data = {
            "date": TODAY,
            "overnight_tasks": overnight,
            "calendar": calendar,
            "new_ideas": ideas,
            "news_articles_count": news_count,
            "priorities": priorities,
        }
        print(json.dumps(data, indent=2, default=str))
        return

    if args.overnight:
        for entry in overnight:
            status = entry["status"]
            print(f"  [{status}] {entry['timestamp']} {entry['task']}")
        if not overnight:
            print("  No overnight activity.")
        return

    if args.calendar:
        cal = read_content_calendar()
        if cal:
            if isinstance(cal, dict) and "raw" in cal:
                print(cal["raw"])
            else:
                print(json.dumps(cal, indent=2))
        else:
            print("  No calendar for today.")
        return

    # Full brief
    brief = format_brief(overnight, calendar, ideas, insights, news_count, priorities, short=args.short)
    print(brief)


if __name__ == "__main__":
    main()
