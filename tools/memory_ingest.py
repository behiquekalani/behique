#!/usr/bin/env python3
"""
Memory Ingestion Protocol — Auto-tag and ingest sessions into the vault.

Scans session files, transcripts, and CMP data to:
  1. Extract decisions, ideas, blockers, and mood signals
  2. Auto-tag with project/tool/pattern links
  3. Store structured memories in CMP with correlation IDs
  4. Generate vault-linked summary files
  5. Update vault graph connections

Sources:
  - 06-Sessions/*.json (session tracker data)
  - 06-Sessions/SES_*.md (auto-generated session logs)
  - 07-Transcripts/TRANSCRIPT_*.md (conversation summaries)
  - 07-Transcripts/COMP2_*.md (Computer 2 session logs)
  - primer.md (live state snapshots)
  - git log (commit messages)

Usage:
    python3 memory_ingest.py                    # ingest today
    python3 memory_ingest.py --date 2026-03-16  # specific date
    python3 memory_ingest.py --all              # ingest all available dates
    python3 memory_ingest.py --dry-run          # preview without writing
    python3 memory_ingest.py --json             # machine-readable output
"""

import os
import sys
import json
import re
import sqlite3
import hashlib
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

BEHIQUE = os.path.expanduser("~/behique")
CEIBA = os.path.join(BEHIQUE, "Ceiba")
SESSIONS_DIR = os.path.join(CEIBA, "06-Sessions")
TRANSCRIPTS_DIR = os.path.join(CEIBA, "07-Transcripts")
CMP_DB = os.path.join(BEHIQUE, "tools", "ai_agent_kernel", "cmp.db")
PRIMER = os.path.join(BEHIQUE, "primer.md")
VAULT_GRAPH = os.path.join(CEIBA, "vault_graph.json")
INGESTION_LOG = os.path.join(CEIBA, "06-Sessions", "ingestion_log.json")

# ── Extraction patterns ────────────────────────────────────────────────────

# Decisions: lines that indicate a choice was made
DECISION_PATTERNS = [
    r"(?:decided|chose|switched|picked|selected|went with|using)\s+(.{10,80})",
    r"(?:DEC_\w+)",
    r"(?:decision|choice|trade-?off|pivot):\s*(.{10,80})",
]

# Ideas: lines that suggest new ideas or features
IDEA_PATTERNS = [
    r"(?:idea|concept|could|should|what if|maybe|consider)\s*:?\s*(.{10,100})",
    r"(?:TODO|FUTURE|NEXT|WANT):\s*(.{10,100})",
    r"(?:add|build|create|implement|make)\s+(?:a\s+)?(.{10,80})",
]

# Blockers: things preventing progress
BLOCKER_PATTERNS = [
    r"(?:blocked|stuck|waiting|need|can't|cannot|broken|failing)\s+(.{10,80})",
    r"(?:blocker|issue|problem|error|bug):\s*(.{10,80})",
]

# Mood signals: emotional state indicators
MOOD_PATTERNS = [
    r"(?:beautiful|amazing|perfect|love it|fire|sick|dope)",
    r"(?:frustrated|annoyed|confused|tired|overwhelmed|stuck)",
    r"(?:excited|motivated|pumped|ready|let's go|hyped)",
    r"(?:bored|meh|whatever|idk|eh)",
]

# Project keywords for auto-linking
PROJECT_KEYWORDS = {
    "eBay-Listing-Assistant": ["ebay", "listing", "publisher", "pricing", "shipping", "funko", "hello kitty"],
    "BehiqueBot": ["behiquebot", "telegram", "bot", "accountability", "railway"],
    "Google-Trends-Scraper": ["trends", "scraper", "google trends", "scraping"],
    "Shopify-Store": ["shopify", "store", "shop"],
    "n8n-Agency": ["n8n", "agency", "automation", "workflow"],
    "AI-Ebook": ["ebook", "ai ebook", "book"],
    "Telegram-Scraper-SaaS": ["telegram scraper", "saas"],
    "Computer-2": ["cobo", "comp2", "computer 2", "bridge", "syncthing"],
    "Spine-Architecture": ["spine", "vault", "graph", "ceiba", "memory"],
}

TOOL_KEYWORDS = {
    "TOOL_vault_grapher": ["vault graph", "grapher", "nodes", "edges", "vis.js"],
    "TOOL_morning_briefing": ["briefing", "morning", "jarvis"],
    "TOOL_session_tracker": ["session track", "planned", "drift", "forensics"],
    "TOOL_graph_query": ["graph query", "neighbors", "shortest path", "hubs"],
    "TOOL_ceiba_client": ["grpc", "ceiba client", "ccp"],
    "TOOL_cmp": ["cmp", "memory protocol", "sqlite"],
    "TOOL_prompt_guard": ["injection", "prompt guard", "security scan"],
    "TOOL_listing_pipeline": ["quick_list", "listing agent", "publisher"],
    "TOOL_vault_healer": ["vault heal", "orphan", "missing target", "dead link"],
    "TOOL_ceiba_cli": ["ceiba start", "ceiba status", "ceiba graph", "unified cli"],
}

PATTERN_KEYWORDS = {
    "PAT_Revenue_Avoidance": ["revenue", "$0", "no sales", "hasn't sold", "revenue avoidance"],
    "PAT_Infrastructure_Creep": ["infrastructure", "over-engineering", "should ship", "too many tools"],
    "PAT_Event_Driven": ["event driven", "hook", "trigger", "reactive"],
    "avoidance-pattern": ["avoiding", "procrastinating", "putting off", "not doing"],
}


# ── Source readers ──────────────────────────────────────────────────────────

def read_session_json(date_str):
    """Read session tracker JSON for a date."""
    path = os.path.join(SESSIONS_DIR, f"{date_str}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def read_session_md(date_str):
    """Read SES_ markdown for a date."""
    filename = f"SES_{date_str.replace('-', '')}.md"
    path = os.path.join(SESSIONS_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def read_transcripts(date_str):
    """Read all transcript files for a date."""
    transcripts = []
    if not os.path.isdir(TRANSCRIPTS_DIR):
        return transcripts
    for f in os.listdir(TRANSCRIPTS_DIR):
        if date_str in f and f.endswith(".md"):
            path = os.path.join(TRANSCRIPTS_DIR, f)
            with open(path) as fh:
                transcripts.append({"filename": f, "content": fh.read()})
    return transcripts


def read_primer():
    """Read current primer.md."""
    if os.path.exists(PRIMER):
        with open(PRIMER) as f:
            return f.read()
    return ""


def get_git_commits(date_str):
    """Get commit messages for a date."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline",
             f"--since={date_str} 00:00:00",
             f"--until={date_str} 23:59:59",
             "--format=%s"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=10
        )
        return [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
    except Exception:
        return []


# ── Extraction engine ───────────────────────────────────────────────────────

def extract_signals(text):
    """Extract decisions, ideas, blockers, and mood from text."""
    signals = {
        "decisions": [],
        "ideas": [],
        "blockers": [],
        "mood": [],
        "projects": [],
        "tools": [],
        "patterns": [],
    }

    text_lower = text.lower()

    # Decisions
    for pattern in DECISION_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1) if match.lastindex else match.group(0)
            val = val.strip().rstrip(".,;:")
            if len(val) > 8 and val not in signals["decisions"]:
                signals["decisions"].append(val)

    # Ideas
    for pattern in IDEA_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1) if match.lastindex else match.group(0)
            val = val.strip().rstrip(".,;:")
            if len(val) > 8 and val not in signals["ideas"]:
                signals["ideas"].append(val)

    # Blockers
    for pattern in BLOCKER_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(1) if match.lastindex else match.group(0)
            val = val.strip().rstrip(".,;:")
            if len(val) > 8 and val not in signals["blockers"]:
                signals["blockers"].append(val)

    # Mood
    for pattern in MOOD_PATTERNS:
        if re.search(pattern, text_lower):
            mood_word = re.search(pattern, text_lower).group(0)
            if mood_word not in signals["mood"]:
                signals["mood"].append(mood_word)

    # Auto-link projects
    for project, keywords in PROJECT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            signals["projects"].append(project)

    # Auto-link tools
    for tool, keywords in TOOL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            signals["tools"].append(tool)

    # Auto-link patterns
    for pattern_name, keywords in PATTERN_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            signals["patterns"].append(pattern_name)

    # Deduplicate and limit
    for key in signals:
        signals[key] = list(dict.fromkeys(signals[key]))[:15]

    return signals


def classify_session_mood(signals):
    """Classify overall session mood from extracted signals."""
    positive = {"beautiful", "amazing", "perfect", "love it", "fire", "sick",
                "dope", "excited", "motivated", "pumped", "ready", "let's go", "hyped"}
    negative = {"frustrated", "annoyed", "confused", "tired", "overwhelmed", "stuck"}
    neutral = {"bored", "meh", "whatever", "idk", "eh"}

    moods = set(signals.get("mood", []))
    if moods & positive:
        return "positive"
    if moods & negative:
        return "negative"
    if moods & neutral:
        return "neutral"
    return "unknown"


# ── CMP integration ─────────────────────────────────────────────────────────

def write_to_cmp(memories, dry_run=False):
    """Write extracted memories to CMP database."""
    if dry_run or not os.path.exists(CMP_DB):
        return 0

    conn = sqlite3.connect(CMP_DB)
    cursor = conn.cursor()
    written = 0

    for mem in memories:
        mem_id = hashlib.sha256(
            json.dumps(mem, sort_keys=True).encode()
        ).hexdigest()[:16]

        # Check if already ingested
        cursor.execute("SELECT id FROM memories WHERE id = ?", (mem_id,))
        if cursor.fetchone():
            continue

        now = datetime.now().isoformat()
        payload = json.dumps(mem.get("payload", {}))
        tags = json.dumps(mem.get("tags", []))
        mem_hash = hashlib.sha256(payload.encode()).hexdigest()

        try:
            import time
            cursor.execute(
                """INSERT INTO memories (id, type, timestamp, payload, author, version, tags, permissions, hash, correlation_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (mem_id, mem["type"], now, payload, "memory_ingest", 1, tags,
                 "{}", mem_hash, mem.get("correlation_id", ""), time.time())
            )
            written += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    return written


# ── Ingestion pipeline ──────────────────────────────────────────────────────

def ingest_date(date_str, dry_run=False):
    """Run full ingestion pipeline for a date."""
    result = {
        "date": date_str,
        "sources_found": [],
        "signals": {
            "decisions": [],
            "ideas": [],
            "blockers": [],
            "mood": [],
            "projects": [],
            "tools": [],
            "patterns": [],
        },
        "memories_written": 0,
        "session_type": "unknown",
        "commit_count": 0,
    }

    all_text = ""

    # 1. Session tracker JSON
    session_json = read_session_json(date_str)
    if session_json:
        result["sources_found"].append(f"06-Sessions/{date_str}.json")
        # Extract planned tasks and execution log as text
        for task in session_json.get("planned_tasks", []):
            all_text += f" {task.get('task', '')}"
        for event in session_json.get("execution_log", []):
            all_text += f" {event.get('task', '')}"
            if event.get("notes"):
                all_text += f" {event['notes']}"

    # 2. Session markdown
    session_md = read_session_md(date_str)
    if session_md:
        result["sources_found"].append(f"06-Sessions/SES_{date_str.replace('-','')}.md")
        all_text += f" {session_md}"

    # 3. Transcripts
    transcripts = read_transcripts(date_str)
    for t in transcripts:
        result["sources_found"].append(f"07-Transcripts/{t['filename']}")
        all_text += f" {t['content']}"

    # 4. Git commits
    commits = get_git_commits(date_str)
    result["commit_count"] = len(commits)
    for c in commits:
        all_text += f" {c}"

    # 5. Primer snapshot (only for today)
    if date_str == datetime.now().strftime("%Y-%m-%d"):
        primer = read_primer()
        if primer:
            result["sources_found"].append("primer.md")
            all_text += f" {primer}"

    if not all_text.strip():
        result["error"] = "No sources found for this date"
        return result

    # Extract signals
    signals = extract_signals(all_text)
    result["signals"] = signals
    result["session_mood"] = classify_session_mood(signals)

    # Determine session type from session JSON or markdown
    if session_json:
        planned = session_json.get("planned_tasks", [])
        completed = [t for t in planned if t.get("status") == "completed"]
        if planned:
            pct = len(completed) / len(planned) * 100
            result["completion_pct"] = round(pct)
    if session_md:
        if "session_type:" in session_md:
            match = re.search(r"session_type:\s*(\w+)", session_md)
            if match:
                result["session_type"] = match.group(1)

    # Build CMP memories
    memories = []
    correlation_id = f"session-{date_str}"

    # Session summary memory
    memories.append({
        "type": "event",
        "payload": {
            "desc": f"Session {date_str}: {result['session_type']}",
            "date": date_str,
            "commits": result["commit_count"],
            "sources": result["sources_found"],
            "projects": signals["projects"],
            "tools": signals["tools"],
            "mood": result.get("session_mood", "unknown"),
        },
        "tags": ["session", "ingested", date_str] + signals["projects"][:3],
        "correlation_id": correlation_id,
    })

    # Decision memories
    for dec in signals["decisions"][:5]:
        memories.append({
            "type": "metadata",
            "payload": {"desc": f"Decision: {dec}", "date": date_str, "context": "auto-extracted"},
            "tags": ["decision", "ingested", date_str],
            "correlation_id": correlation_id,
        })

    # Blocker memories
    for blk in signals["blockers"][:5]:
        memories.append({
            "type": "state",
            "payload": {"desc": f"Blocker: {blk}", "date": date_str, "context": "auto-extracted"},
            "tags": ["blocker", "ingested", date_str],
            "correlation_id": correlation_id,
        })

    # Idea memories
    for idea in signals["ideas"][:5]:
        memories.append({
            "type": "task",
            "payload": {"desc": f"Idea: {idea}", "date": date_str, "context": "auto-extracted"},
            "tags": ["idea", "ingested", date_str],
            "correlation_id": correlation_id,
        })

    # Write to CMP
    result["memories_written"] = write_to_cmp(memories, dry_run)
    result["memories_generated"] = len(memories)

    return result


def load_ingestion_log():
    """Load record of previously ingested dates."""
    if os.path.exists(INGESTION_LOG):
        with open(INGESTION_LOG) as f:
            return json.load(f)
    return {"ingested_dates": [], "last_run": None}


def save_ingestion_log(log):
    """Save ingestion log."""
    os.makedirs(os.path.dirname(INGESTION_LOG), exist_ok=True)
    with open(INGESTION_LOG, "w") as f:
        json.dump(log, f, indent=2)


def find_all_dates():
    """Find all dates that have session data."""
    dates = set()
    if os.path.isdir(SESSIONS_DIR):
        for f in os.listdir(SESSIONS_DIR):
            # Match YYYY-MM-DD.json
            match = re.match(r"(\d{4}-\d{2}-\d{2})\.json$", f)
            if match:
                dates.add(match.group(1))
            # Match SES_YYYYMMDD.md
            match = re.match(r"SES_(\d{4})(\d{2})(\d{2})\.md$", f)
            if match:
                dates.add(f"{match.group(1)}-{match.group(2)}-{match.group(3)}")
    if os.path.isdir(TRANSCRIPTS_DIR):
        for f in os.listdir(TRANSCRIPTS_DIR):
            match = re.search(r"(\d{4}-\d{2}-\d{2})", f)
            if match:
                dates.add(match.group(1))
    return sorted(dates)


# ── Output ──────────────────────────────────────────────────────────────────

def print_report(result):
    """Pretty-print ingestion report."""
    print()
    print("╔══════════════════════════════════════════════╗")
    print(f"║  🧠 Memory Ingestion Report                  ║")
    print(f"║  📅 {result['date']}                              ║")
    print("╚══════════════════════════════════════════════╝")

    if result.get("error"):
        print(f"\n  ❌ {result['error']}")
        return

    print(f"\n  📊 Sources: {len(result['sources_found'])}")
    for s in result["sources_found"]:
        print(f"     • {s}")

    print(f"\n  🎯 Session: {result['session_type']} | "
          f"Commits: {result['commit_count']} | "
          f"Mood: {result.get('session_mood', '?')}")

    signals = result["signals"]

    if signals["decisions"]:
        print(f"\n  🔑 Decisions ({len(signals['decisions'])}):")
        for d in signals["decisions"][:5]:
            print(f"     • {d}")

    if signals["ideas"]:
        print(f"\n  💡 Ideas ({len(signals['ideas'])}):")
        for i in signals["ideas"][:5]:
            print(f"     • {i}")

    if signals["blockers"]:
        print(f"\n  🚧 Blockers ({len(signals['blockers'])}):")
        for b in signals["blockers"][:5]:
            print(f"     • {b}")

    if signals["mood"]:
        print(f"\n  😊 Mood signals: {', '.join(signals['mood'][:5])}")

    if signals["projects"]:
        print(f"\n  📁 Projects: {', '.join(signals['projects'])}")
    if signals["tools"]:
        print(f"  🔧 Tools: {', '.join(signals['tools'])}")
    if signals["patterns"]:
        print(f"  🔄 Patterns: {', '.join(signals['patterns'])}")

    print(f"\n  💾 CMP: {result['memories_written']}/{result['memories_generated']} memories written")

    if result.get("completion_pct") is not None:
        print(f"  📋 Completion: {result['completion_pct']}%")

    print(f"\n  {'─' * 40}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Memory Ingestion Protocol")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Date to ingest (YYYY-MM-DD)")
    parser.add_argument("--all", action="store_true", help="Ingest all available dates")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    log = load_ingestion_log()

    if args.all:
        dates = find_all_dates()
        results = []
        for date_str in dates:
            if date_str in log.get("ingested_dates", []) and not args.dry_run:
                continue  # Skip already ingested
            result = ingest_date(date_str, args.dry_run)
            results.append(result)
            if not args.dry_run and not result.get("error"):
                log["ingested_dates"].append(date_str)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print_report(r)
            print(f"\n  📊 Total: {len(results)} dates processed, "
                  f"{sum(r['memories_written'] for r in results)} memories written")
    else:
        result = ingest_date(args.date, args.dry_run)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_report(result)

        if not args.dry_run and not result.get("error"):
            if args.date not in log.get("ingested_dates", []):
                log["ingested_dates"].append(args.date)

    log["last_run"] = datetime.now().isoformat()
    if not args.dry_run:
        save_ingestion_log(log)


if __name__ == "__main__":
    main()
