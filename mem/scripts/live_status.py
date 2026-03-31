#!/usr/bin/env python3
"""
Ceiba Live Status Monitor - tiny terminal dashboard.

Shows real-time status of all active Claude sessions.
Run this in a small terminal window while other sessions build.

Usage:
    python3 live_status.py              # Live refresh (every 2s)
    python3 live_status.py --once       # Single snapshot
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
MEM = REPO / "mem"
SESSIONS_FILE = MEM / "sessions.json"
STATUS_FILE = MEM / "status.md"
PRIMER_FILE = MEM / "primer.md"
LOCKS_DIR = MEM / "locks"

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def c(text, code):
    return f"\033[{code}m{text}\033[0m"

def render():
    """Render one frame of the status dashboard."""
    now = datetime.now()
    lines = []

    # Header
    lines.append(c("╔══════════════════════════════════════════╗", "36"))
    lines.append(c("║      CEIBA LIVE STATUS                   ║", "36"))
    lines.append(c(f"║      {now.strftime('%Y-%m-%d %H:%M:%S')}                    ║", "36"))
    lines.append(c("╚══════════════════════════════════════════╝", "36"))
    lines.append("")

    # Sessions
    sessions = []
    if SESSIONS_FILE.exists():
        try:
            data = json.loads(SESSIONS_FILE.read_text())
            sessions = data.get("sessions", [])
            claimed = data.get("claimed_tasks", {})
        except:
            sessions = []
            claimed = {}

    # Clean stale
    active = [s for s in sessions if time.time() - s.get("last_heartbeat", 0) < 300]

    lines.append(c(f" SESSIONS ({len(active)} active)", "1"))
    lines.append(c(" ─────────────────────────────────────────", "90"))

    if active:
        for s in active:
            age = int(time.time() - s.get("last_heartbeat", 0))
            if age < 30:
                status = c("●", "32")  # green
            elif age < 120:
                status = c("●", "33")  # yellow
            else:
                status = c("●", "31")  # red

            # Find tasks claimed by this session
            tasks = [k for k, v in claimed.items() if v == s["id"]]
            task_str = f" → {tasks[0][:30]}" if tasks else ""

            lines.append(f" {status} {c(s['id'][:15], '36'):20s} {s['focus'][:20]:20s}{task_str}")
    else:
        lines.append(c("   No active sessions", "90"))

    lines.append("")

    # Git activity (last 5 commits)
    lines.append(c(" RECENT COMMITS", "1"))
    lines.append(c(" ─────────────────────────────────────────", "90"))

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--format=%h %s"],
            capture_output=True, text=True, cwd=REPO, timeout=5
        )
        for line in result.stdout.strip().split("\n")[:5]:
            if line:
                parts = line.split(" ", 1)
                hash_str = c(parts[0], "33")
                msg = parts[1][:45] if len(parts) > 1 else ""
                lines.append(f" {hash_str} {msg}")
    except:
        lines.append(c("   git unavailable", "90"))

    lines.append("")

    # Product count
    try:
        product_count = len(list((REPO / "READY-TO-SELL/products-organized").iterdir()))
    except:
        product_count = "?"

    # File locks
    locks = list(LOCKS_DIR.glob("*.lock")) if LOCKS_DIR.exists() else []

    lines.append(c(" SYSTEM", "1"))
    lines.append(c(" ─────────────────────────────────────────", "90"))
    lines.append(f" Products ready:  {c(str(product_count), '32')}")
    lines.append(f" Live on Gumroad: {c('11', '33')}")
    lines.append(f" Active locks:    {c(str(len(locks)), '31' if locks else '32')}")

    # Memory file ages
    mem_files = [
        ("primer.md", PRIMER_FILE),
        ("status.md", STATUS_FILE),
        ("sessions.json", SESSIONS_FILE),
    ]
    for name, path in mem_files:
        if path.exists():
            age = (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds()
            age_str = f"{int(age)}s" if age < 60 else f"{int(age/60)}m" if age < 3600 else f"{int(age/3600)}h"
            lines.append(f" {name:18s} {c(age_str, '90')} ago")

    lines.append("")

    # Claimed tasks
    if claimed:
        lines.append(c(" CLAIMED TASKS", "1"))
        lines.append(c(" ─────────────────────────────────────────", "90"))
        for task, sid in claimed.items():
            lines.append(f" {c('▸', '33')} {task[:35]:35s} → {c(sid[:12], '36')}")
        lines.append("")

    # Active/Todo from status.md
    try:
        content = STATUS_FILE.read_text()
        import re
        current_name = None
        active_items = []
        todo_items = []
        for line in content.split('\n'):
            name_match = re.search(r'name:\s*"(.+)"', line)
            status_match = re.search(r'status:\s*(\w+)', line)
            if name_match:
                current_name = name_match.group(1)
            elif status_match and current_name:
                if status_match.group(1) == 'active':
                    active_items.append(current_name)
                elif status_match.group(1) == 'todo':
                    todo_items.append(current_name)
                current_name = None

        lines.append(c(f" PRIORITY TASKS", "1"))
        lines.append(c(" ─────────────────────────────────────────", "90"))
        for item in active_items[:5]:
            lines.append(f" {c('▸', '32')} {item[:42]}")
        for item in todo_items[:3]:
            lines.append(f" {c('○', '90')} {item[:42]}")
    except:
        pass

    lines.append("")
    lines.append(c(" Press Ctrl+C to exit", "90"))

    return "\n".join(lines)


def main():
    once = "--once" in sys.argv

    if once:
        print(render())
        return

    try:
        while True:
            clear()
            print(render())
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n  Bye.")


if __name__ == "__main__":
    main()
