#!/usr/bin/env python3
"""
Ceiba Session Manager - Multi-terminal coordination.

Handles concurrent Claude Code sessions sharing the same memory files.
Each terminal registers itself, claims tasks, and coordinates writes.

Usage:
    python3 session_manager.py register "building products"    # Register this session
    python3 session_manager.py status                          # Show all active sessions
    python3 session_manager.py claim "task name"               # Claim a task
    python3 session_manager.py release "task name"             # Release a task
    python3 session_manager.py heartbeat                       # Update session heartbeat
    python3 session_manager.py deregister                      # End this session
    python3 session_manager.py primer                          # Read primer safely
    python3 session_manager.py update-primer "key" "value"     # Update primer field
    python3 session_manager.py sync                            # Sync all sessions
"""

import fcntl
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
MEM = REPO / "mem"
SESSIONS_FILE = MEM / "sessions.json"
LOCKS_DIR = MEM / "locks"
PRIMER = MEM / "primer.md"
STATUS = MEM / "status.md"

LOCKS_DIR.mkdir(parents=True, exist_ok=True)

# Session ID from PID + terminal
SESSION_ID = f"s-{os.getpid()}-{int(time.time()) % 10000}"


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t): return color(t, "32")
def yellow(t): return color(t, "33")
def cyan(t): return color(t, "36")
def red(t): return color(t, "31")
def dim(t): return color(t, "90")


class FileLock:
    """Simple file-based lock for coordinating writes."""

    def __init__(self, name):
        self.path = LOCKS_DIR / f"{name}.lock"
        self.fd = None

    def acquire(self, timeout=5):
        """Try to acquire lock, return True if successful."""
        self.fd = open(self.path, 'w')
        start = time.time()
        while time.time() - start < timeout:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.fd.write(f"{SESSION_ID}\n{datetime.now().isoformat()}\n")
                self.fd.flush()
                return True
            except IOError:
                time.sleep(0.1)
        self.fd.close()
        self.fd = None
        return False

    def release(self):
        if self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            except:
                pass
            self.fd = None
            try:
                self.path.unlink()
            except:
                pass

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock: {self.path.name}")
        return self

    def __exit__(self, *args):
        self.release()


def load_sessions():
    """Load sessions registry with file locking."""
    if not SESSIONS_FILE.exists():
        return {"sessions": [], "claimed_tasks": {}}
    try:
        return json.loads(SESSIONS_FILE.read_text())
    except:
        return {"sessions": [], "claimed_tasks": {}}


def save_sessions(data):
    """Save sessions registry with file locking."""
    lock = FileLock("sessions")
    if lock.acquire():
        try:
            SESSIONS_FILE.write_text(json.dumps(data, indent=2))
        finally:
            lock.release()


def cleanup_stale(data, max_age_seconds=300):
    """Remove sessions that haven't heartbeated in 5 minutes."""
    now = time.time()
    active = []
    for s in data["sessions"]:
        if now - s.get("last_heartbeat", 0) < max_age_seconds:
            active.append(s)
        else:
            # Release any tasks claimed by stale session
            stale_id = s["id"]
            data["claimed_tasks"] = {
                k: v for k, v in data["claimed_tasks"].items()
                if v != stale_id
            }
    data["sessions"] = active
    return data


def cmd_register(args):
    """Register a new session."""
    focus = " ".join(args) if args else "general"
    data = load_sessions()
    data = cleanup_stale(data)

    session = {
        "id": SESSION_ID,
        "pid": os.getpid(),
        "focus": focus,
        "started": datetime.now().isoformat(),
        "last_heartbeat": time.time(),
        "status": "active"
    }

    # Remove any existing session with same PID
    data["sessions"] = [s for s in data["sessions"] if s["pid"] != os.getpid()]
    data["sessions"].append(session)

    save_sessions(data)
    print(green(f"  Session registered: {SESSION_ID}"))
    print(f"  Focus: {focus}")
    print(f"  Active sessions: {len(data['sessions'])}")

    # Show other active sessions
    others = [s for s in data["sessions"] if s["id"] != SESSION_ID]
    if others:
        print(f"\n  Other active sessions:")
        for s in others:
            print(f"    {cyan(s['id'])} — {s['focus']} (pid {s['pid']})")


def cmd_status(args):
    """Show all active sessions."""
    data = load_sessions()
    data = cleanup_stale(data)
    save_sessions(data)

    print(cyan(f"\n{'='*50}"))
    print(cyan(f"  CEIBA SESSION MANAGER"))
    print(cyan(f"{'='*50}"))

    if not data["sessions"]:
        print(f"\n  No active sessions.")
        return

    print(f"\n  Active Sessions ({len(data['sessions'])}):")
    for s in data["sessions"]:
        age = int(time.time() - s["last_heartbeat"])
        status = green("ACTIVE") if age < 60 else yellow(f"IDLE {age}s")
        print(f"    {cyan(s['id'])} [{status}]")
        print(f"      Focus: {s['focus']}")
        print(f"      PID: {s['pid']} | Started: {s['started'][:19]}")

    if data["claimed_tasks"]:
        print(f"\n  Claimed Tasks:")
        for task, session_id in data["claimed_tasks"].items():
            print(f"    {yellow(task)} → {session_id}")


def cmd_claim(args):
    """Claim a task for this session."""
    if not args:
        print(red("  Usage: claim <task name>"))
        return

    task = " ".join(args)
    data = load_sessions()
    data = cleanup_stale(data)

    if task in data["claimed_tasks"]:
        owner = data["claimed_tasks"][task]
        if owner == SESSION_ID:
            print(yellow(f"  Already claimed by you: {task}"))
        else:
            print(red(f"  BLOCKED: '{task}' claimed by {owner}"))
        return

    data["claimed_tasks"][task] = SESSION_ID
    save_sessions(data)
    print(green(f"  Claimed: {task}"))


def cmd_release(args):
    """Release a claimed task."""
    if not args:
        print(red("  Usage: release <task name>"))
        return

    task = " ".join(args)
    data = load_sessions()

    if task in data["claimed_tasks"]:
        if data["claimed_tasks"][task] == SESSION_ID:
            del data["claimed_tasks"][task]
            save_sessions(data)
            print(green(f"  Released: {task}"))
        else:
            print(red(f"  Can't release: owned by {data['claimed_tasks'][task]}"))
    else:
        print(dim(f"  Not claimed: {task}"))


def cmd_heartbeat(args):
    """Update session heartbeat."""
    data = load_sessions()
    for s in data["sessions"]:
        if s["id"] == SESSION_ID or s["pid"] == os.getpid():
            s["last_heartbeat"] = time.time()
            break
    save_sessions(data)
    print(dim(f"  Heartbeat: {SESSION_ID}"))


def cmd_deregister(args):
    """End this session."""
    data = load_sessions()

    # Remove session
    data["sessions"] = [s for s in data["sessions"] if s["pid"] != os.getpid()]

    # Release all tasks claimed by this session
    data["claimed_tasks"] = {
        k: v for k, v in data["claimed_tasks"].items()
        if v != SESSION_ID
    }

    save_sessions(data)
    print(green(f"  Session ended: {SESSION_ID}"))
    print(f"  Remaining sessions: {len(data['sessions'])}")


def cmd_primer(args):
    """Read primer with lock."""
    lock = FileLock("primer")
    if lock.acquire(timeout=3):
        try:
            content = PRIMER.read_text()
            print(content)
        finally:
            lock.release()
    else:
        print(red("  Could not acquire primer lock"))


def cmd_update_primer(args):
    """Update a specific field in primer."""
    if len(args) < 2:
        print(red("  Usage: update-primer <key> <value>"))
        return

    key = args[0]
    value = " ".join(args[1:])

    lock = FileLock("primer")
    if lock.acquire(timeout=5):
        try:
            content = PRIMER.read_text()
            # Simple key-value update in YAML frontmatter
            import re
            pattern = rf'{key}:\s*.*'
            if re.search(pattern, content):
                content = re.sub(pattern, f'{key}: {value}', content)
            else:
                # Add after last frontmatter key
                content = content.replace('---\n\n', f'{key}: {value}\n---\n\n', 1)
            PRIMER.write_text(content)
            print(green(f"  Updated: {key} = {value}"))
        finally:
            lock.release()
    else:
        print(red("  Could not acquire primer lock"))


def cmd_sync(args):
    """Show sync status across all memory files."""
    print(cyan(f"\n  MEMORY SYNC STATUS"))
    print(f"  {'─'*40}")

    files = [
        ("primer.md", PRIMER),
        ("status.md", STATUS),
        ("context_graph.md", MEM / "context_graph.md"),
        ("verifier.md", MEM / "verifier.md"),
        ("fleet.md", MEM / "fleet.md"),
        ("voice-bible.md", MEM / "voice-bible.md"),
        ("sessions.json", SESSIONS_FILE),
    ]

    for name, path in files:
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age = (datetime.now() - mtime).total_seconds()
            age_str = f"{int(age)}s" if age < 60 else f"{int(age/60)}m" if age < 3600 else f"{int(age/3600)}h"
            lock_exists = (LOCKS_DIR / f"{name.split('.')[0]}.lock").exists()
            lock_str = red("LOCKED") if lock_exists else green("free")
            print(f"    {name:25s} {dim(age_str):>8s} ago  [{lock_str}]")
        else:
            print(f"    {name:25s} {red('MISSING')}")

    # Show active locks
    locks = list(LOCKS_DIR.glob("*.lock"))
    if locks:
        print(f"\n  Active locks:")
        for l in locks:
            content = l.read_text().strip().split("\n")
            owner = content[0] if content else "unknown"
            print(f"    {l.stem} → {owner}")


def cmd_assign(args):
    """Auto-assign work to sessions based on priority."""
    data = load_sessions()
    data = cleanup_stale(data)

    if not data["sessions"]:
        print(red("  No active sessions to assign work to"))
        return

    # Read status.md for active/todo items
    try:
        status_content = STATUS.read_text()
        import re
        items = []
        current = {}
        for line in status_content.split('\n'):
            name_match = re.search(r'name:\s*"(.+)"', line)
            status_match = re.search(r'status:\s*(\w+)', line)
            priority_match = re.search(r'priority:\s*(\d+)', line)
            if name_match:
                current['name'] = name_match.group(1)
            elif status_match and current.get('name'):
                current['status'] = status_match.group(1)
            elif priority_match and current.get('name'):
                current['priority'] = int(priority_match.group(1))
                items.append(current)
                current = {}

        # Get unclaimed active/todo items
        claimed = set(data["claimed_tasks"].keys())
        available = [i for i in items
                     if i.get('status') in ('active', 'todo')
                     and i['name'] not in claimed]
        available.sort(key=lambda x: x.get('priority', 99))

        print(f"\n  Available tasks ({len(available)}):")
        for i, item in enumerate(available):
            print(f"    {i+1}. [{item['status']}] {item['name']} (P{item.get('priority', '?')})")

        # Auto-suggest assignments
        sessions = data["sessions"]
        if available and sessions:
            print(f"\n  Suggested assignments:")
            for i, session in enumerate(sessions):
                if i < len(available):
                    print(f"    {cyan(session['id'])} → {available[i]['name']}")

    except Exception as e:
        print(red(f"  Error reading status: {e}"))


def main():
    if len(sys.argv) < 2:
        print(cyan("""
  Ceiba Session Manager
  =====================

  Commands:
    register <focus>         Register this terminal
    status                   Show all active sessions
    claim <task>             Claim a task (prevents duplicates)
    release <task>           Release a claimed task
    heartbeat                Update session heartbeat
    deregister               End this session
    primer                   Read primer safely
    update-primer <k> <v>    Update primer field
    sync                     Show memory sync status
    assign                   Auto-suggest task assignments
        """))
        return

    commands = {
        "register": cmd_register,
        "status": cmd_status,
        "claim": cmd_claim,
        "release": cmd_release,
        "heartbeat": cmd_heartbeat,
        "deregister": cmd_deregister,
        "primer": cmd_primer,
        "update-primer": cmd_update_primer,
        "sync": cmd_sync,
        "assign": cmd_assign,
    }

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd in commands:
        commands[cmd](args)
    else:
        print(red(f"  Unknown command: {cmd}"))


if __name__ == "__main__":
    main()
