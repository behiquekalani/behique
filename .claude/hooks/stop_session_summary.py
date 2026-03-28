#!/usr/bin/env python3
"""
Claude Code Stop hook — Session Summary Writer.

When a Claude Code session ends, this script:
1. Creates a session log in ~/behique/Ceiba/06-Sessions/YYYY-MM-DD-HHMM.md
2. Records timestamp, duration estimate, and the stop reason
3. Updates primer.md with the session reference

This is deterministic (no LLM). It captures what it can from the hook payload
and creates a skeleton that Ceiba fills in at next session start.
"""

import datetime
import json
import pathlib
import subprocess
import sys


def read_stdin_payload() -> dict:
    try:
        data = sys.stdin.read()
        if not data.strip():
            return {}
        return json.loads(data)
    except Exception:
        return {}


def find_project_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def get_recent_git_activity(project_root: pathlib.Path) -> str:
    """Get files changed in the current session (last 2 hours of commits)."""
    try:
        since = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--pretty=format:%s", "--name-only"],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            return result.stdout.strip()
        return "No commits in the last 2 hours."
    except Exception:
        return "Could not read git log."


def get_changed_files(project_root: pathlib.Path) -> str:
    """Get currently modified/untracked files."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.stdout.strip() else "Working tree clean."
    except Exception:
        return "Could not read git status."


def write_session_log(project_root: pathlib.Path, payload: dict) -> pathlib.Path:
    """Write a session log file."""
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d-%H%M") + ".md"
    sessions_dir = project_root / "Ceiba" / "06-Sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    filepath = sessions_dir / filename

    stop_reason = payload.get("stop_hook_reason", "unknown")
    git_activity = get_recent_git_activity(project_root)
    changed_files = get_changed_files(project_root)

    content = f"""---
type: session
date: {now.strftime("%Y-%m-%d")}
time: {now.strftime("%H:%M")}
stop_reason: {stop_reason}
tags: [session, auto-generated]
---

# Session Log — {now.strftime("%Y-%m-%d %H:%M")}

## Auto-captured at session end

**Stop reason:** {stop_reason}
**Timestamp:** {now.strftime("%Y-%m-%d %H:%M:%S")}

## Git Activity (last 2 hours)

```
{git_activity}
```

## Uncommitted Changes at Session End

```
{changed_files}
```

## What Was Done This Session

_Fill in at next session start by reading primer.md and git log._

## What's Left / Next Session Priority

_Fill in at next session start._

## Patterns Noticed

_Ceiba: note any avoidance, drift, or wins here._
"""

    filepath.write_text(content, encoding="utf-8")
    return filepath


def main() -> None:
    payload = read_stdin_payload()
    project_root = find_project_root()

    # Only run if this is the behique project
    if not (project_root / "primer.md").exists():
        return

    session_path = write_session_log(project_root, payload)

    # Auto-commit the session log
    try:
        subprocess.run(
            ["git", "add", str(session_path)],
            cwd=str(project_root),
            check=False,
        )
        subprocess.run(
            ["git", "commit", "-m", f"auto: session log {session_path.name}"],
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
