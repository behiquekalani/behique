#!/usr/bin/env python3
"""
Session Auto-Generator — Creates structured vault session files.

Generates SES_ files in the vault with links to projects, tools,
decisions, and patterns from the session. Integrates with
session_tracker.py for planned/completed data and git for changes.

Usage:
    python3 session_logger.py                    # generate for today
    python3 session_logger.py --date 2026-03-15  # generate for specific date
    python3 session_logger.py --dry-run          # preview without writing
"""

import os
import json
import subprocess
import argparse
from datetime import datetime, timezone
from pathlib import Path


BEHIQUE = os.path.expanduser("~/behique")
VAULT_DIR = os.path.join(BEHIQUE, "Ceiba")
SESSIONS_DIR = os.path.join(VAULT_DIR, "06-Sessions")
TRACKER_DIR = os.path.join(VAULT_DIR, "06-Sessions")  # session_tracker.py data
VAULT_GRAPH = os.path.join(VAULT_DIR, "vault_graph.json")

# Known project/tool mappings for auto-linking
PROJECT_KEYWORDS = {
    "eBay-Listing-Assistant": ["ebay", "listing", "publisher", "pricing", "shipping", "funko"],
    "BehiqueBot": ["behiquebot", "telegram", "bot", "accountability"],
    "Google-Trends-Scraper": ["trends", "scraper", "google trends", "scraping"],
    "Shopify-Store": ["shopify", "store", "shop"],
    "n8n-Agency": ["n8n", "agency", "automation", "workflow"],
    "AI-Ebook": ["ebook", "ai ebook", "book"],
    "Telegram-Scraper-SaaS": ["telegram scraper", "saas"],
}

TOOL_KEYWORDS = {
    "vault_grapher": ["vault", "graph", "grapher", "nodes", "edges"],
    "morning_briefing": ["briefing", "morning", "jarvis"],
    "session_tracker": ["session", "tracker", "planned", "drift"],
    "graph_query": ["graph query", "neighbors", "shortest path", "hubs"],
    "ceiba_client": ["grpc", "ceiba client", "cobo", "ccp"],
    "cmp": ["cmp", "memory protocol", "sqlite", "conflict"],
    "prompt_guard": ["injection", "prompt guard", "security scan"],
}


def get_git_activity(date_str: str) -> dict:
    """Get git commits and changed files for a specific date."""
    try:
        # Commits on that date
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str} 00:00:00",
             f"--until={date_str} 23:59:59", "--format=%s"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=10
        )
        commits = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]

        # Files changed
        result2 = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:",
             f"--since={date_str} 00:00:00", f"--until={date_str} 23:59:59"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=10
        )
        files = list(set(l.strip() for l in result2.stdout.strip().split("\n") if l.strip()))

        return {"commits": commits, "files_changed": files}
    except Exception:
        return {"commits": [], "files_changed": []}


def get_tracker_data(date_str: str) -> dict:
    """Load session tracker data for a date."""
    tracker_file = os.path.join(TRACKER_DIR, f"{date_str}.json")
    if os.path.exists(tracker_file):
        with open(tracker_file) as f:
            return json.load(f)
    return {}


def detect_links(text: str) -> dict:
    """Auto-detect vault links from text content."""
    text_lower = text.lower()
    projects = []
    tools = []

    for project, keywords in PROJECT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            projects.append(project)

    for tool, keywords in TOOL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tools.append(tool)

    return {"projects": projects, "tools": tools}


def generate_session_file(date_str: str, dry_run: bool = False) -> str:
    """Generate a structured session vault file."""
    git = get_git_activity(date_str)
    tracker = get_tracker_data(date_str)

    # Build text blob for link detection
    text_blob = " ".join(git.get("commits", []))
    for event in tracker.get("execution_log", []):
        text_blob += " " + event.get("task", "")
    for task in tracker.get("planned_tasks", []):
        text_blob += " " + task.get("task", "")

    links = detect_links(text_blob)

    # Session stats
    planned = tracker.get("planned_tasks", [])
    completed = [t for t in planned if t.get("status") == "completed"]
    execution = tracker.get("execution_log", [])
    commit_count = len(git.get("commits", []))
    files_count = len(git.get("files_changed", []))

    # Determine session type
    session_type = "build"  # default
    if any("fix" in c.lower() or "bug" in c.lower() for c in git.get("commits", [])):
        session_type = "fix"
    if any("refactor" in c.lower() for c in git.get("commits", [])):
        session_type = "refactor"
    if len(planned) > 0 and len(completed) == 0:
        session_type = "planning"

    # Generate markdown
    filename = f"SES_{date_str.replace('-', '')}.md"
    filepath = os.path.join(SESSIONS_DIR, filename)

    content = f"""---
type: session
date: {date_str}
session_type: {session_type}
commits: {commit_count}
files_changed: {files_count}
planned: {len(planned)}
completed: {len(completed)}
completion_rate: {round(len(completed) / len(planned) * 100) if planned else 0}%
---

# Session — {date_str}

## Summary
- **Type:** {session_type}
- **Commits:** {commit_count}
- **Files touched:** {files_count}
- **Planned:** {len(planned)} tasks
- **Completed:** {len(completed)} tasks ({round(len(completed) / len(planned) * 100) if planned else 0}%)

## Planned Tasks
"""

    if planned:
        for t in planned:
            status_icon = "✅" if t.get("status") == "completed" else "⬜"
            content += f"- {status_icon} {t['task']}\n"
    else:
        content += "- (no session plan recorded)\n"

    content += "\n## Execution Log\n"
    if execution:
        for e in execution:
            type_icon = {"completed": "✅", "started": "🔄", "deferred": "⏸️",
                         "abandoned": "❌", "drift": "↗️"}.get(e.get("type"), "📝")
            attr = f" [{e.get('attribution', '')}]" if e.get("attribution") else ""
            content += f"- {type_icon} {e['task']}{attr}\n"
    else:
        content += "- (no execution log)\n"

    content += "\n## Git Activity\n"
    if git["commits"]:
        for c in git["commits"][:15]:
            content += f"- {c}\n"
        if len(git["commits"]) > 15:
            content += f"- ... ({len(git['commits']) - 15} more)\n"
    else:
        content += "- (no commits)\n"

    # Auto-linked vault nodes
    content += "\n## Links\n\n### Projects\n"
    if links["projects"]:
        for p in links["projects"]:
            content += f"- [[01-Projects/{p}]]\n"
    else:
        content += "- (none detected)\n"

    content += "\n### Tools\n"
    if links["tools"]:
        for t in links["tools"]:
            content += f"- [[05-Tools/{t}]]\n"
    else:
        content += "- (none detected)\n"

    content += f"""
### Key Files Changed
"""
    if git["files_changed"]:
        for f in sorted(git["files_changed"])[:20]:
            content += f"- `{f}`\n"
    else:
        content += "- (none)\n"

    content += f"""
---
*Auto-generated by session_logger.py on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    if dry_run:
        print(content)
        return filepath

    # Write file
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)

    print(f"  ✅ Generated: {filepath}")
    print(f"     Type: {session_type} | Commits: {commit_count} | Files: {files_count}")
    print(f"     Plan: {len(completed)}/{len(planned)} completed")
    print(f"     Projects: {', '.join(links['projects']) or 'none'}")
    print(f"     Tools: {', '.join(links['tools']) or 'none'}")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Session Auto-Generator")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Date to generate for (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    generate_session_file(args.date, args.dry_run)


if __name__ == "__main__":
    main()
