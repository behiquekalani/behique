#!/usr/bin/env python3
"""
Session Finish-Tracker — Planned vs Completed Accountability Engine

Tracks what was planned at session start vs what actually got done.
Reads primer.md, git log, CMP events, and session logs to produce
an honest forensic report.

Usage:
    python3 session_tracker.py start "Fix bugs, implement skills, paste eBay listing"
    python3 session_tracker.py log "Implemented ebay_research skill" --type completed
    python3 session_tracker.py log "iOS calendar setup" --type deferred
    python3 session_tracker.py report
    python3 session_tracker.py drift

Data stored in: ~/behique/Ceiba/06-Sessions/YYYY-MM-DD.json
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime, timezone
from pathlib import Path


# ============ Config ============
BEHIQUE_DIR = os.path.expanduser("~/behique")
SESSIONS_DIR = os.path.join(BEHIQUE_DIR, "Ceiba", "06-Sessions")
PRIMER_PATH = os.path.join(BEHIQUE_DIR, "primer.md")
CMP_DB = os.path.join(BEHIQUE_DIR, "tools", "ai_agent_kernel", "cmp.db")

# Ensure sessions directory exists
os.makedirs(SESSIONS_DIR, exist_ok=True)


def today_file() -> str:
    return os.path.join(SESSIONS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.json")


def load_session() -> dict:
    """Load today's session data, or create empty structure."""
    path = today_file()
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "started_at": None,
        "planned_tasks": [],
        "execution_log": [],
        "primer_snapshot": "",
        "git_commits_at_start": 0,
        "metadata": {},
    }


def save_session(data: dict):
    with open(today_file(), "w") as f:
        json.dump(data, f, indent=2)


# ============ Git Integration ============
def git_commits_today() -> list:
    """Get all git commits from today."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=midnight", "--format=%H|%s|%ai"],
            capture_output=True, text=True, cwd=BEHIQUE_DIR, timeout=5
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 2)
                commits.append({
                    "hash": parts[0][:8],
                    "message": parts[1],
                    "time": parts[2] if len(parts) > 2 else "",
                })
        return commits
    except Exception:
        return []


def git_files_changed_today() -> int:
    """Count files changed in today's commits."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR",
             f"--since=midnight", "HEAD"],
            capture_output=True, text=True, cwd=BEHIQUE_DIR, timeout=5
        )
        return len([l for l in result.stdout.strip().split("\n") if l])
    except Exception:
        return 0


# ============ CMP Integration ============
def cmp_events_today() -> int:
    """Count CMP memory entries created today."""
    if not os.path.exists(CMP_DB):
        return 0
    try:
        import sqlite3
        conn = sqlite3.connect(CMP_DB)
        count = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE date(timestamp) = date('now')"
        ).fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


# ============ Primer Snapshot ============
def read_primer_focus() -> str:
    """Extract current focus / next action from primer.md."""
    if not os.path.exists(PRIMER_PATH):
        return "(primer.md not found)"
    try:
        with open(PRIMER_PATH) as f:
            content = f.read()
        # Extract key lines
        lines = content.split("\n")
        focus_lines = []
        capture = False
        for line in lines:
            lower = line.lower().strip()
            if any(kw in lower for kw in ["focus", "next action", "next step",
                                           "current work", "what's next", "priorities"]):
                capture = True
            if capture:
                focus_lines.append(line)
                if len(focus_lines) > 5:
                    break
            if capture and line.strip() == "":
                break
        return "\n".join(focus_lines[:5]) if focus_lines else content[:300]
    except Exception:
        return "(error reading primer.md)"


# ============ Commands ============
def cmd_start(args):
    """Start tracking a session with planned tasks."""
    session = load_session()
    session["started_at"] = datetime.now(timezone.utc).isoformat()
    session["primer_snapshot"] = read_primer_focus()
    session["git_commits_at_start"] = len(git_commits_today())

    # Parse planned tasks
    if args.tasks:
        tasks_str = " ".join(args.tasks)
        planned = [t.strip() for t in tasks_str.split(",") if t.strip()]
        session["planned_tasks"] = [
            {"task": t, "status": "pending", "added_at": datetime.now(timezone.utc).isoformat()}
            for t in planned
        ]

    save_session(session)

    print(f"\n📋 Session started — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Planned tasks: {len(session['planned_tasks'])}")
    for i, t in enumerate(session["planned_tasks"], 1):
        print(f"   {i}. {t['task']}")
    print(f"\n   Primer focus: {session['primer_snapshot'][:100]}...")
    print(f"   Commits so far today: {session['git_commits_at_start']}")
    print()


def cmd_log(args):
    """Log a task event (completed, deferred, started, abandoned, drift)."""
    session = load_session()
    event = {
        "task": args.description,
        "type": args.type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": args.attribution or "self-directed",
        "notes": args.notes or "",
    }
    session["execution_log"].append(event)

    # Update planned task status if it matches (fuzzy: any 2+ significant words overlap)
    desc_words = set(args.description.lower().split())
    stopwords = {"the", "a", "an", "and", "or", "in", "on", "to", "for", "of", "with", "is", "was"}
    desc_significant = desc_words - stopwords
    for pt in session["planned_tasks"]:
        plan_words = set(pt["task"].lower().split()) - stopwords
        overlap = desc_significant & plan_words
        if len(overlap) >= 2 or (len(plan_words) <= 2 and len(overlap) >= 1):
            if args.type in ("completed", "deferred", "abandoned"):
                pt["status"] = args.type

    save_session(session)

    icons = {"completed": "✅", "started": "🔄", "deferred": "⏸️",
             "abandoned": "❌", "drift": "↗️", "pivot": "🔀"}
    icon = icons.get(args.type, "📝")
    print(f"  {icon} [{args.type.upper()}] {args.description}")
    if args.attribution:
        print(f"     Attribution: {args.attribution}")


def cmd_report(args):
    """Generate the session forensics report."""
    session = load_session()

    if not session["started_at"]:
        print("⚠️  No session started today. Run: session_tracker.py start \"task1, task2\"")
        return

    # Gather data
    commits = git_commits_today()
    commits_during = len(commits) - session.get("git_commits_at_start", 0)
    cmp_count = cmp_events_today()
    execution = session.get("execution_log", [])
    planned = session.get("planned_tasks", [])

    # Calculate stats
    completed = [e for e in execution if e["type"] == "completed"]
    deferred = [e for e in execution if e["type"] == "deferred"]
    abandoned = [e for e in execution if e["type"] == "abandoned"]
    drifts = [e for e in execution if e["type"] == "drift"]
    self_directed = [e for e in execution if e.get("attribution") == "self-directed"]

    planned_completed = [p for p in planned if p["status"] == "completed"]
    planned_pending = [p for p in planned if p["status"] == "pending"]

    # Revenue check
    revenue_tasks = [e for e in execution
                     if any(kw in e["task"].lower() for kw in
                            ["ebay", "listing", "sell", "revenue", "price", "sale", "shopify"])]

    # Completion rate
    total_planned = len(planned)
    completion_rate = (len(planned_completed) / total_planned * 100) if total_planned > 0 else 0

    # Build report
    print("\n" + "=" * 60)
    print("  SESSION FORENSICS REPORT")
    print(f"  Date: {session['date']} | Started: {session['started_at'][:16]}")
    print("=" * 60)

    print(f"\n── Plan vs Reality ──")
    print(f"  Planned tasks: {total_planned}")
    print(f"  Completed:     {len(planned_completed)} ({completion_rate:.0f}%)")
    print(f"  Still pending: {len(planned_pending)}")
    if planned_pending:
        for p in planned_pending:
            print(f"    ⬜ {p['task']}")

    print(f"\n── Execution Log ({len(execution)} events) ──")
    for e in execution:
        icons = {"completed": "✅", "started": "🔄", "deferred": "⏸️",
                 "abandoned": "❌", "drift": "↗️", "pivot": "🔀"}
        icon = icons.get(e["type"], "📝")
        attr = f" [{e.get('attribution', '?')}]" if e.get('attribution') else ""
        print(f"  {icon} {e['task']}{attr}")

    print(f"\n── Drift Report ──")
    print(f"  Self-directed tasks: {len(self_directed)}")
    print(f"  Unplanned drifts:    {len(drifts)}")
    print(f"  Revenue tasks:       {len(revenue_tasks)}")

    if len(self_directed) > 3:
        print(f"\n  🚩 RED FLAG: {len(self_directed)} self-directed tasks without Kalani asking")

    if len(revenue_tasks) == 0 and len(execution) > 3:
        print(f"\n  🚩 RED FLAG: 0 revenue tasks out of {len(execution)} total — infrastructure creep?")

    print(f"\n── System Stats ──")
    print(f"  Git commits this session: {commits_during}")
    print(f"  CMP entries today:        {cmp_count}")
    if commits_during > 0:
        print(f"  Recent commits:")
        for c in commits[:5]:
            print(f"    {c['hash']} {c['message']}")

    print(f"\n── Honest Assessment ──")
    if completion_rate >= 80:
        print(f"  ✅ Strong execution — {completion_rate:.0f}% of plan completed")
    elif completion_rate >= 50:
        print(f"  ⚠️  Partial execution — {completion_rate:.0f}% of plan completed")
    else:
        print(f"  🚩 Low execution — only {completion_rate:.0f}% of plan completed")

    if planned_pending:
        print(f"\n  Unfinished items carry forward to next session:")
        for p in planned_pending:
            print(f"    → {p['task']}")

    print("\n" + "=" * 60)

    # Save report to markdown
    report_path = os.path.join(SESSIONS_DIR, f"{session['date']}-report.md")
    with open(report_path, "w") as f:
        f.write(f"# Session Report — {session['date']}\n\n")
        f.write(f"## Plan\n")
        for p in planned:
            status = "✅" if p["status"] == "completed" else "⬜"
            f.write(f"- {status} {p['task']}\n")
        f.write(f"\n## Execution ({len(execution)} events)\n")
        for e in execution:
            f.write(f"- [{e['type'].upper()}] {e['task']} ({e.get('attribution', '?')})\n")
        f.write(f"\n## Stats\n")
        f.write(f"- Completion rate: {completion_rate:.0f}%\n")
        f.write(f"- Git commits: {commits_during}\n")
        f.write(f"- CMP entries: {cmp_count}\n")
        f.write(f"- Revenue tasks: {len(revenue_tasks)}\n")
        f.write(f"- Self-directed: {len(self_directed)}\n")
        f.write(f"- Drifts: {len(drifts)}\n")
    print(f"  Report saved: {report_path}")
    print()


def cmd_drift(args):
    """Quick drift check — what's off-plan right now?"""
    session = load_session()
    planned = session.get("planned_tasks", [])
    execution = session.get("execution_log", [])

    pending = [p for p in planned if p["status"] == "pending"]
    drifts = [e for e in execution if e["type"] == "drift"]
    self_directed = [e for e in execution if e.get("attribution") == "self-directed"]

    print(f"\n📊 Quick Drift Check")
    if pending:
        print(f"\n  Still pending ({len(pending)}):")
        for p in pending:
            print(f"    ⬜ {p['task']}")
    else:
        print(f"  ✅ All planned tasks addressed")

    if drifts:
        print(f"\n  Unplanned work ({len(drifts)}):")
        for d in drifts:
            print(f"    ↗️  {d['task']}")

    if len(self_directed) > 3:
        print(f"\n  🚩 {len(self_directed)} self-directed tasks — ask Kalani if this is OK")

    print()


# ============ CLI ============
def main():
    parser = argparse.ArgumentParser(description="Session Finish-Tracker")
    sub = parser.add_subparsers(dest="command")

    # start
    sp = sub.add_parser("start", help="Start tracking with planned tasks")
    sp.add_argument("tasks", nargs="*", help="Comma-separated planned tasks")

    # log
    lp = sub.add_parser("log", help="Log a task event")
    lp.add_argument("description", help="What happened")
    lp.add_argument("--type", default="completed",
                    choices=["completed", "started", "deferred", "abandoned", "drift", "pivot"])
    lp.add_argument("--attribution", default="", help="assigned, self-directed, or drift")
    lp.add_argument("--notes", default="", help="Additional context")

    # report
    sub.add_parser("report", help="Generate session forensics")

    # drift
    sub.add_parser("drift", help="Quick drift check")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "start":
        cmd_start(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "drift":
        cmd_drift(args)


if __name__ == "__main__":
    main()
