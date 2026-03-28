#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""Auto-journal: captures what was built each day in Kalani's voice."""

import json, os, subprocess
from datetime import datetime
from pathlib import Path

JOURNAL_DIR = Path(__file__).parent.parent / "Ceiba" / "journal"
JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
TOOLS = Path(__file__).parent
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def get_git_activity():
    """Get today's git commits."""
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={today}", "--oneline", "--no-merges"],
            capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def get_autonomous_log():
    """Read today's autonomous log entries."""
    log_file = Path(__file__).parent.parent / "Ceiba" / "AUTONOMOUS_LOG.md"
    if not log_file.exists():
        return ""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = log_file.read_text().split("\n")
    today_lines = [l for l in lines if today in l]
    return "\n".join(today_lines[:20])


def generate_entry(topic=None):
    """Generate a journal entry using Ollama."""
    import requests
    commits = get_git_activity()
    auto_log = get_autonomous_log()

    context = f"Git commits today: {len(commits)}\n"
    if commits:
        context += "\n".join(commits[:10]) + "\n"
    if auto_log:
        context += f"\nAutonomous activity:\n{auto_log}\n"

    prompt = f"""Write a personal journal entry (300-500 words) about today's building session.

Context of what was done:
{context}

Rules:
- Write as Kalani, a 21-year-old CS student in Puerto Rico building an AI business
- Short paragraphs, honest, raw
- Include feelings, not just facts
- Spanish words can bleed through naturally (dale, mira, para que)
- Do NOT reveal specific file paths, tool names, or proprietary details
- Keep it high-level: "built a financial app" not "created behike-finance.html"
- End with what's next or how you feel about tomorrow
- No em dashes, use periods or commas instead"""

    if topic:
        prompt += f"\n\nFocus on this angle: {topic}"

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 600}
        }, timeout=60)
        return resp.json().get("response", "")
    except Exception:
        return f"Today I built things. {len(commits)} commits. The machine keeps growing. Tomorrow we launch."


def save_entry(text, slug=None):
    """Save journal entry to file."""
    today = datetime.now().strftime("%Y-%m-%d")
    if not slug:
        slug = today
    filename = f"{slug}.md"
    path = JOURNAL_DIR / filename

    header = f"---\ndate: {today}\ntime: {datetime.now().strftime('%H:%M')}\nmood: building\n---\n\n"
    path.write_text(header + text)
    return path


def list_entries():
    """List all journal entries."""
    entries = sorted(JOURNAL_DIR.glob("*.md"), reverse=True)
    for e in entries[:20]:
        date = e.stem
        lines = e.read_text().split("\n")
        preview = ""
        for l in lines:
            if l.strip() and not l.startswith("---") and not l.startswith("date:") and not l.startswith("time:") and not l.startswith("mood:"):
                preview = l.strip()[:80]
                break
        print(f"  {date}: {preview}...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-journal writer")
    parser.add_argument("--generate", action="store_true", help="Generate today's entry")
    parser.add_argument("--topic", type=str, help="Focus the entry on a topic")
    parser.add_argument("--list", action="store_true", help="List all entries")
    parser.add_argument("--week", action="store_true", help="Show this week's entries")
    args = parser.parse_args()

    if args.list:
        list_entries()
    elif args.generate:
        text = generate_entry(args.topic)
        path = save_entry(text)
        print(f"  Journal saved: {path}")
        print(f"\n{text}")
    else:
        parser.print_help()
