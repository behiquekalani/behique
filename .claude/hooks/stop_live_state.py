#!/usr/bin/env python3
"""
Claude Code Stop hook for Ceiba.

When a Claude Code session ends, this script:
1. Updates the LIVE STATE block in primer.md with a fresh timestamp.
2. Creates a lightweight git commit so the checkpoint is saved.

This is v1: deterministic, no LLM. It can be upgraded later to summarize
the transcript and modify more fields in LIVE STATE using Ollama.
"""

import datetime
import json
import os
import pathlib
import subprocess
import sys
from typing import List


def read_stdin_payload() -> dict:
    try:
        data = sys.stdin.read()
        if not data.strip():
            return {}
        return json.loads(data)
    except Exception:
        return {}


def find_project_root() -> pathlib.Path:
    # This file lives in <project>/.claude/hooks/stop_live_state.py
    return pathlib.Path(__file__).resolve().parents[2]


def load_lines(path: pathlib.Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def save_lines(path: pathlib.Path, lines: List[str]) -> None:
    path.write_text("".join(lines), encoding="utf-8")


def update_live_state_block(primer_path: pathlib.Path) -> bool:
    """
    Find the LIVE STATE block in primer.md and update the timestamp line.
    Returns True if a change was made.
    """
    lines = load_lines(primer_path)

    # Locate the LIVE STATE section header and comment line
    header_idx = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("## ⚡ LIVE STATE"):
            header_idx = i
            break

    if header_idx is None:
        return False

    # Expect the comment line immediately after header
    if header_idx + 1 >= len(lines):
        return False

    # LIVE STATE block starts two lines after header (after the HTML comment)
    start_idx = header_idx + 2

    # We expect 5 lines: Last update, Focus, Next action, Blocker, Session status
    if start_idx + 5 > len(lines):
        return False

    # Only change the "Last update" line to keep v1 simple and safe
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    new_last_update = (
        f"Last update: {date_str} — Auto checkpoint via Claude Code stop hook.\n"
    )

    if lines[start_idx] == new_last_update:
        return False

    lines[start_idx] = new_last_update
    save_lines(primer_path, lines)
    return True


def git_commit_if_needed(project_root: pathlib.Path) -> None:
    """Stage primer.md and create an auto checkpoint commit if there are changes."""
    try:
        # Check if primer.md has changes
        result = subprocess.run(
            ["git", "status", "--porcelain", "primer.md"],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        if not result.stdout.strip():
            return

        subprocess.run(
            ["git", "add", "primer.md"],
            cwd=str(project_root),
            check=False,
        )

        now = datetime.datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S")
        msg = f"auto: session checkpoint {ts}"

        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        # Never let git issues break the stop hook
        pass


def main() -> None:
    _payload = read_stdin_payload()

    project_root = find_project_root()
    primer_path = project_root / "primer.md"

    if not primer_path.exists():
        return

    changed = update_live_state_block(primer_path)
    if changed:
        git_commit_if_needed(project_root)


if __name__ == "__main__":
    main()

