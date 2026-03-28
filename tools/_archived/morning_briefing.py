#!/usr/bin/env python3
"""
Jarvis Morning Briefing — Daily Intelligence Digest

"Good morning Ceiba" → overnight summary, project status, priorities,
blockers cleared, what Cobo did. Like the Jarvis reel.

Reads from:
  - primer.md (current focus, live state)
  - Vault graph (node counts, recent changes)
  - Git log (overnight activity)
  - CMP database (task events, errors)
  - Bridge tasks (Cobo delegation status)
  - Session tracker (yesterday's report)
  - IDEAS_BACKLOG.md (ready items count)

Usage:
    python3 morning_briefing.py              # full briefing
    python3 morning_briefing.py --short      # compact version
    python3 morning_briefing.py --json       # machine-readable
"""

import os
import sys
import json
import subprocess
import sqlite3
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ============ Config ============
BEHIQUE = os.path.expanduser("~/behique")
PRIMER = os.path.join(BEHIQUE, "primer.md")
VAULT_GRAPH = os.path.join(BEHIQUE, "Ceiba", "vault_graph.json")
CMP_DB = os.path.join(BEHIQUE, "tools", "ai_agent_kernel", "cmp.db")
BRIDGE_TASKS = os.path.join(BEHIQUE, "bridge", "tasks.md")
IDEAS_BACKLOG = os.path.join(BEHIQUE, "Ceiba", "IDEAS_BACKLOG.md")
SESSIONS_DIR = os.path.join(BEHIQUE, "Ceiba", "06-Sessions")
OBSERVATIONS = os.path.join(BEHIQUE, "Ceiba", "04-Patterns", "observations.md")
COBO_IP = "192.168.0.151"


# ============ Data Collectors ============
def collect_primer():
    """Extract key info from primer.md."""
    if not os.path.exists(PRIMER):
        return {"exists": False}
    try:
        with open(PRIMER) as f:
            content = f.read()
        age_hours = (os.path.getmtime(PRIMER) - datetime.now().timestamp()) / -3600

        # Extract sections
        focus = ""
        next_action = ""
        blockers = ""
        lines = content.split("\n")
        current_section = None
        for line in lines:
            lower = line.lower().strip()
            if "focus" in lower or "current" in lower:
                current_section = "focus"
            elif "next" in lower and ("action" in lower or "step" in lower):
                current_section = "next"
            elif "blocker" in lower:
                current_section = "blockers"
            elif line.startswith("#"):
                current_section = None

            if current_section == "focus" and line.strip() and not line.startswith("#"):
                focus += line.strip() + " "
            elif current_section == "next" and line.strip() and not line.startswith("#"):
                next_action += line.strip() + " "
            elif current_section == "blockers" and line.strip() and not line.startswith("#"):
                blockers += line.strip() + " "

        return {
            "exists": True,
            "age_hours": round(age_hours, 1),
            "focus": focus.strip()[:200] or "(could not extract)",
            "next_action": next_action.strip()[:200] or "(could not extract)",
            "blockers": blockers.strip()[:200] or "none detected",
            "stale": age_hours > 24,
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def collect_git():
    """Git activity since yesterday."""
    try:
        # Last 24h commits
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=24 hours ago",
             "--format=%s|%ai|%an"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 2)
                commits.append({
                    "message": parts[0],
                    "time": parts[1][:16] if len(parts) > 1 else "",
                })

        # Uncommitted changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        )
        uncommitted = len([l for l in status.stdout.strip().split("\n") if l])

        # Current branch
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip()

        return {
            "commits_24h": len(commits),
            "recent_commits": commits[:5],
            "uncommitted_files": uncommitted,
            "branch": branch,
        }
    except Exception as e:
        return {"error": str(e)}


def collect_cmp():
    """CMP database stats."""
    if not os.path.exists(CMP_DB):
        return {"exists": False}
    try:
        conn = sqlite3.connect(CMP_DB)
        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        today = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE date(timestamp) = date('now')"
        ).fetchone()[0]
        yesterday = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE date(timestamp) = date('now', '-1 day')"
        ).fetchone()[0]

        # Recent errors
        errors = conn.execute(
            "SELECT payload FROM memories WHERE type='error' ORDER BY timestamp DESC LIMIT 3"
        ).fetchall()
        recent_errors = []
        for e in errors:
            try:
                payload = json.loads(e[0])
                recent_errors.append(payload.get("message", "unknown")[:80])
            except Exception:
                pass

        # Task completion stats
        tasks = conn.execute(
            "SELECT payload FROM memories WHERE type='task' AND date(timestamp) >= date('now', '-1 day')"
        ).fetchall()
        task_statuses = {}
        for t in tasks:
            try:
                payload = json.loads(t[0])
                status = payload.get("status", "unknown")
                task_statuses[status] = task_statuses.get(status, 0) + 1
            except Exception:
                pass

        conn.close()
        return {
            "exists": True,
            "total_entries": total,
            "today": today,
            "yesterday": yesterday,
            "recent_errors": recent_errors,
            "task_statuses": task_statuses,
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def collect_vault():
    """Vault graph stats including typed relationships."""
    if not os.path.exists(VAULT_GRAPH):
        return {"exists": False}
    try:
        with open(VAULT_GRAPH) as f:
            data = json.load(f)
        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        typed_edges = data.get("typed_edges", [])
        stats = data.get("stats", {})

        # Count by type
        node_types = {}
        for name, n in nodes.items():
            t = n.get("type", "unknown")
            node_types[t] = node_types.get(t, 0) + 1

        # Typed relationship stats
        rel_types = stats.get("relationship_types", {})
        typed_count = sum(v for k, v in rel_types.items() if k != "wiki_link")

        age_hours = (os.path.getmtime(VAULT_GRAPH) - datetime.now().timestamp()) / -3600

        return {
            "exists": True,
            "nodes": len(nodes),
            "edges": len(edges),
            "typed_relationships": typed_count,
            "relationship_types": {k: v for k, v in rel_types.items() if k != "wiki_link"},
            "types": node_types,
            "orphans": stats.get("orphans", 0),
            "missing_targets": stats.get("missing_targets", 0),
            "age_hours": round(age_hours, 1),
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def collect_bridge():
    """Bridge task status."""
    if not os.path.exists(BRIDGE_TASKS):
        return {"exists": False}
    try:
        with open(BRIDGE_TASKS) as f:
            content = f.read()
        pending = content.lower().count("[pending]")
        in_progress = content.lower().count("[in progress]")
        done = content.lower().count("[done]")
        return {
            "exists": True,
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def collect_backlog():
    """IDEAS_BACKLOG.md stats."""
    if not os.path.exists(IDEAS_BACKLOG):
        return {"exists": False}
    try:
        with open(IDEAS_BACKLOG) as f:
            content = f.read()
        # Count by section
        sections = {"DONE": 0, "READY": 0, "BLOCKED": 0, "FUTURE": 0, "KILLED": 0}
        current = None
        for line in content.split("\n"):
            if "## DONE" in line:
                current = "DONE"
            elif "## READY" in line:
                current = "READY"
            elif "## BLOCKED" in line:
                current = "BLOCKED"
            elif "## FUTURE" in line:
                current = "FUTURE"
            elif "## KILLED" in line:
                current = "KILLED"
            elif line.strip().startswith("|") and current and "---" not in line and "Idea" not in line:
                sections[current] = sections.get(current, 0) + 1

        return {"exists": True, **sections}
    except Exception as e:
        return {"exists": True, "error": str(e)}


def collect_cobo():
    """Quick Cobo health check."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", COBO_IP],
            capture_output=True, timeout=5
        )
        online = result.returncode == 0
        return {"online": online}
    except Exception:
        return {"online": False}


def collect_yesterday_session():
    """Yesterday's session report if it exists."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    for date_str in [today, yesterday]:
        report_path = os.path.join(SESSIONS_DIR, f"{date_str}-report.md")
        session_path = os.path.join(SESSIONS_DIR, f"{date_str}.json")

        if os.path.exists(session_path):
            try:
                with open(session_path) as f:
                    data = json.load(f)
                planned = len(data.get("planned_tasks", []))
                completed = len([t for t in data.get("planned_tasks", []) if t.get("status") == "completed"])
                return {
                    "exists": True,
                    "date": date_str,
                    "planned": planned,
                    "completed": completed,
                    "completion_rate": round(completed / planned * 100) if planned > 0 else 0,
                }
            except Exception:
                pass

    return {"exists": False}


# ============ Briefing Generator ============
def generate_briefing(short=False):
    """Generate the morning briefing."""
    now = datetime.now()
    hour = now.hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

    # Collect all data
    primer = collect_primer()
    git = collect_git()
    cmp = collect_cmp()
    vault = collect_vault()
    bridge = collect_bridge()
    backlog = collect_backlog()
    cobo = collect_cobo()
    last_session = collect_yesterday_session()

    briefing = {
        "timestamp": now.isoformat(),
        "primer": primer,
        "git": git,
        "cmp": cmp,
        "vault": vault,
        "bridge": bridge,
        "backlog": backlog,
        "cobo": cobo,
        "last_session": last_session,
    }

    # ============ Print ============
    print()
    print("╔══════════════════════════════════════════════════╗")
    print(f"║  🌳 {greeting}, Kalani.                        ║")
    print(f"║  Ceiba Intelligence Briefing — {now.strftime('%b %d, %H:%M')}     ║")
    print("╚══════════════════════════════════════════════════╝")

    # --- Cluster Status ---
    print(f"\n── Cluster Status ──")
    print(f"  Ceiba (Mac):  🟢 Online")
    print(f"  Cobo (Win):   {'🟢 Online' if cobo['online'] else '🔴 Offline'}")
    if cmp.get("exists"):
        print(f"  CMP Memory:   {cmp.get('total_entries', 0)} entries ({cmp.get('today', 0)} today)")
    if vault.get("exists"):
        typed = vault.get("typed_relationships", 0)
        orphans = vault.get("orphans", 0)
        vault_health = "🟢" if orphans < 5 else "🟡" if orphans < 15 else "🔴"
        print(f"  Vault Graph:  {vault.get('nodes', 0)} nodes, {vault.get('edges', 0)} wiki + {typed} typed edges {vault_health}")
        if orphans > 0:
            print(f"                {orphans} orphans, {vault.get('missing_targets', 0)} missing targets")

    # --- Last Session Recap ---
    if last_session.get("exists"):
        print(f"\n── Last Session ({last_session['date']}) ──")
        rate = last_session["completion_rate"]
        emoji = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "🚩"
        print(f"  {emoji} Completed {last_session['completed']}/{last_session['planned']} planned tasks ({rate}%)")

    # --- Git Activity ---
    if not short:
        print(f"\n── Git Activity (24h) ──")
        print(f"  Commits: {git.get('commits_24h', 0)} | Uncommitted: {git.get('uncommitted_files', 0)} | Branch: {git.get('branch', '?')}")
        for c in git.get("recent_commits", [])[:3]:
            print(f"    • {c['message'][:60]}")

    # --- Current Focus ---
    print(f"\n── Current Focus ──")
    if primer.get("stale"):
        print(f"  ⚠️  primer.md is {primer.get('age_hours', '?')}h old — needs update")
    print(f"  {primer.get('focus', 'unknown')[:120]}")
    if primer.get("next_action") and primer["next_action"] != "(could not extract)":
        print(f"  Next: {primer['next_action'][:120]}")

    # --- Bridge Tasks ---
    if bridge.get("exists") and (bridge.get("pending", 0) > 0 or bridge.get("in_progress", 0) > 0):
        print(f"\n── Bridge Tasks (Cobo) ──")
        print(f"  Pending: {bridge['pending']} | In Progress: {bridge['in_progress']} | Done: {bridge['done']}")

    # --- CMP Errors ---
    if cmp.get("recent_errors") and not short:
        print(f"\n── Recent Errors ──")
        for err in cmp["recent_errors"][:3]:
            print(f"  🔴 {err}")

    # --- Backlog ---
    if backlog.get("exists"):
        print(f"\n── Ideas Backlog ──")
        print(f"  Done: {backlog.get('DONE', 0)} | Ready: {backlog.get('READY', 0)} | Blocked: {backlog.get('BLOCKED', 0)} | Future: {backlog.get('FUTURE', 0)}")

    # --- Revenue Check ---
    print(f"\n── Revenue Status ──")
    print(f"  💰 Current revenue: $0")
    print(f"  📦 Funko Pop listing: READY — paste it on eBay")
    print(f"  🔑 eBay OAuth: needs completion → run ebay_oauth_token.py")

    # --- Today's Priorities ---
    print(f"\n── Recommended Priorities ──")
    priorities = []
    if backlog.get("READY", 0) > 0:
        priorities.append("Chip away at READY backlog items")
    priorities.append("Paste Funko Pop listing on eBay → $0 → $27.99")
    priorities.append("Complete eBay OAuth flow for V2 auto-publishing")
    if bridge.get("pending", 0) > 0:
        priorities.append(f"Clear {bridge['pending']} pending bridge tasks")
    if primer.get("stale"):
        priorities.append("Update primer.md with current state")

    for i, p in enumerate(priorities[:5], 1):
        print(f"  {i}. {p}")

    print()
    print("══════════════════════════════════════════════════")
    print(f"  Run 'bash bridge/wake.sh' for full system check")
    print("══════════════════════════════════════════════════")
    print()

    return briefing


# ============ CLI ============
def main():
    parser = argparse.ArgumentParser(description="Jarvis Morning Briefing")
    parser.add_argument("--short", action="store_true", help="Compact briefing")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    briefing = generate_briefing(short=args.short)

    if args.json:
        # Clean up non-serializable data
        print(json.dumps(briefing, indent=2, default=str))


if __name__ == "__main__":
    main()
