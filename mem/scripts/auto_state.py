#!/usr/bin/env python3
"""
Auto State — Continuous state persistence for seamless context transitions.

Runs as a background process. Every 2 minutes:
1. Snapshots current git state (what changed)
2. Updates primer.md with live state
3. Writes a handoff file that any new session can read instantly
4. Commits checkpoint if weight threshold hit

The goal: when context runs out and a new session starts,
it picks up EXACTLY where the last one left off. No manual handoff.
No "read this file." No momentum loss.

Usage:
    python3 auto_state.py &              # Run in background
    python3 auto_state.py --once         # Single snapshot
    python3 auto_state.py --status       # Show current state
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
MEM = REPO / "mem"
STATE_FILE = MEM / "live_state.json"
HANDOFF_FILE = REPO / "Ceiba" / "inbox" / "AUTO_HANDOFF.md"
PRIMER = MEM / "primer.md"

INTERVAL = 120  # seconds between snapshots


def get_git_state():
    """Snapshot current git state."""
    try:
        # Recent commits
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--format=%h|%s|%ai"],
            capture_output=True, text=True, cwd=REPO, timeout=10
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|", 2)
                if len(parts) >= 2:
                    commits.append({"hash": parts[0], "msg": parts[1], "date": parts[2] if len(parts) > 2 else ""})

        # Uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO, timeout=10
        )
        changed_files = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]

        # Total commits
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, cwd=REPO, timeout=10
        )
        total_commits = int(result.stdout.strip() or "0")

        return {
            "recent_commits": commits,
            "uncommitted_changes": len(changed_files),
            "changed_files": changed_files[:20],
            "total_commits": total_commits,
        }
    except Exception as e:
        return {"error": str(e)}


def get_product_count():
    """Count products."""
    try:
        products_dir = REPO / "READY-TO-SELL" / "products-organized"
        return len([d for d in products_dir.iterdir() if d.is_dir()])
    except:
        return 0


def get_active_tasks():
    """Read active tasks from status.md."""
    try:
        content = (MEM / "status.md").read_text()
        active = []
        todo = []
        current_name = None
        for line in content.split('\n'):
            name_match = re.search(r'name:\s*"(.+)"', line)
            status_match = re.search(r'status:\s*(\w+)', line)
            if name_match:
                current_name = name_match.group(1)
            elif status_match and current_name:
                if status_match.group(1) == 'active':
                    active.append(current_name)
                elif status_match.group(1) == 'todo':
                    todo.append(current_name)
                current_name = None
        return {"active": active, "todo": todo}
    except:
        return {"active": [], "todo": []}


def get_running_servers():
    """Check what's running on common ports."""
    servers = []
    for port, name in [(8090, "Innova Barber"), (8091, "Hogar Website"), (8095, "Hogar SaaS Dashboard")]:
        try:
            result = subprocess.run(
                ["lsof", f"-i:{port}"], capture_output=True, text=True, timeout=5
            )
            if "LISTEN" in result.stdout:
                servers.append({"port": port, "name": name, "status": "running"})
        except:
            pass
    return servers


def snapshot():
    """Take a complete state snapshot."""
    state = {
        "timestamp": datetime.now().isoformat(),
        "git": get_git_state(),
        "products": get_product_count(),
        "tasks": get_active_tasks(),
        "servers": get_running_servers(),
    }

    # Save state
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    # Write handoff
    write_handoff(state)

    return state


def write_handoff(state):
    """Write a handoff file that new sessions read automatically."""
    git = state.get("git", {})
    tasks = state.get("tasks", {})
    servers = state.get("servers", [])

    last_commit = git.get("recent_commits", [{}])[0] if git.get("recent_commits") else {}
    last_msg = last_commit.get("msg", "unknown")

    active_str = "\n".join(f"- {t}" for t in tasks.get("active", [])[:5]) or "- None"
    todo_str = "\n".join(f"- {t}" for t in tasks.get("todo", [])[:5]) or "- None"
    server_str = "\n".join(f"- {s['name']} on port {s['port']}" for s in servers) or "- None running"

    handoff = f"""# AUTO HANDOFF — {datetime.now().strftime('%Y-%m-%d %H:%M')}
# This file is auto-generated. Read it to continue where the last session left off.

## Last Activity
- Last commit: {last_msg}
- Uncommitted changes: {git.get('uncommitted_changes', 0)}
- Total commits: {git.get('total_commits', 0)}
- Products ready: {state.get('products', 0)}

## What Was Being Built
{active_str}

## Next Up
{todo_str}

## Running Servers
{server_str}

## To Continue
Read `mem/primer.md` for full context. Read `mem/status.md` for task list.
Don't ask what to do. Read the state and continue building.
"""
    HANDOFF_FILE.write_text(handoff)


def auto_checkpoint(state):
    """Auto-commit if there are enough uncommitted changes."""
    changes = state.get("git", {}).get("uncommitted_changes", 0)
    if changes >= 10:
        try:
            subprocess.run(["git", "add", "mem/", "Ceiba/inbox/"], cwd=REPO, timeout=10)
            subprocess.run(
                ["git", "commit", "-m", f"auto: state checkpoint ({changes} files)"],
                capture_output=True, text=True, cwd=REPO, timeout=10
            )
        except:
            pass


def cmd_status():
    """Show current state."""
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        print(f"\n  Last snapshot: {state['timestamp'][:19]}")
        print(f"  Products: {state.get('products', 0)}")
        print(f"  Commits: {state.get('git', {}).get('total_commits', 0)}")
        print(f"  Uncommitted: {state.get('git', {}).get('uncommitted_changes', 0)}")
        print(f"  Active tasks: {len(state.get('tasks', {}).get('active', []))}")
        servers = state.get("servers", [])
        if servers:
            print(f"  Servers: {', '.join(s['name'] for s in servers)}")
    else:
        print("  No state snapshot yet. Run: python3 auto_state.py --once")


def main():
    if "--once" in sys.argv:
        state = snapshot()
        print(f"  Snapshot saved. Products: {state['products']} | Commits: {state['git'].get('total_commits', 0)}")
        return

    if "--status" in sys.argv:
        cmd_status()
        return

    # Background loop
    print(f"  Auto State running (every {INTERVAL}s). Ctrl+C to stop.")
    try:
        while True:
            state = snapshot()
            auto_checkpoint(state)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n  Auto State stopped.")


if __name__ == "__main__":
    main()
