#!/usr/bin/env python3
"""
Behike Idea Capture — Your second brain's intake valve.

Capture ideas from anywhere. They get cleaned, tagged, connected,
and routed to the right place automatically.

INPUT: raw messy thoughts (text, voice transcripts, screenshots)
OUTPUT: clean, tagged, connected ideas in the pipeline

Usage:
    python3 capture.py "i want to vlog like casey neistat about building with AI"
    python3 capture.py --voice recording.wav
    python3 capture.py --file ideas.txt
    python3 capture.py --review              # Review and route pending ideas
    python3 capture.py --pipeline            # Show the full pipeline
    python3 capture.py --search "youtube"    # Search captured ideas
    echo "idea here" | python3 capture.py -  # Pipe from stdin
"""

import json
import os
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IDEAS_DIR = BASE_DIR / "tools" / "idea-capture"
PIPELINE_FILE = IDEAS_DIR / "pipeline.json"
ARCHIVE_FILE = IDEAS_DIR / "archive.json"
STATUS_FILE = BASE_DIR / "mem" / "status.md"
BACKLOG_FILE = BASE_DIR / "Ceiba" / "IDEAS_BACKLOG.md"

IDEAS_DIR.mkdir(parents=True, exist_ok=True)


def color(t, c): return f"\033[{c}m{t}\033[0m"
def green(t): return color(t, "32")
def cyan(t): return color(t, "36")
def gold(t): return color(t, "33")
def dim(t): return color(t, "90")
def red(t): return color(t, "31")
def purple(t): return color(t, "35")


# ── IDEA PROCESSOR ──────────────────────────────────────────

class IdeaProcessor:
    """Clean, tag, and route raw ideas."""

    # Project keywords → project mapping
    PROJECT_MAP = {
        "youtube": "youtube-content",
        "vlog": "youtube-content",
        "video": "youtube-content",
        "casey": "youtube-content",
        "record": "youtube-content",
        "instagram": "instagram",
        "reel": "instagram",
        "post": "instagram",
        "gumroad": "gumroad-store",
        "product": "gumroad-store",
        "list": "gumroad-store",
        "sell": "gumroad-store",
        "barber": "innova-barber",
        "luis": "innova-barber",
        "anexis": "innova-barber",
        "hogar": "hogar-ana-gabriel",
        "mum": "hogar-ana-gabriel",
        "mom": "hogar-ana-gabriel",
        "ancianos": "hogar-ana-gabriel",
        "behike": "behike-core",
        "ceiba": "ceiba-system",
        "memory": "ceiba-system",
        "bot": "behiquebot",
        "telegram": "behiquebot",
        "naboria": "infrastructure",
        "cobo": "infrastructure",
        "server": "infrastructure",
        "deploy": "infrastructure",
        "website": "local-biz",
        "client": "local-biz",
        "seo": "local-biz",
        "saas": "hogar-saas",
        "compliance": "hogar-saas",
        "music": "music-apps",
        "beat": "music-apps",
        "adhd": "adhd-products",
        "focus": "adhd-products",
        "wellness": "adhd-products",
        "money": "finance",
        "budget": "finance",
        "polymarket": "polymarket",
        "ebay": "ebay",
    }

    # Category detection
    CATEGORIES = {
        "product": ["build", "create", "make", "product", "app", "tool", "guide", "blueprint"],
        "content": ["video", "post", "reel", "youtube", "instagram", "content", "vlog", "script"],
        "business": ["client", "sell", "revenue", "price", "pitch", "contract", "service"],
        "technical": ["code", "deploy", "server", "api", "fix", "bug", "script", "database"],
        "personal": ["feel", "want", "think", "wish", "remember", "call", "mom", "mum"],
        "creative": ["design", "style", "aesthetic", "brand", "logo", "vibe", "casey"],
    }

    # Priority signals
    URGENCY_SIGNALS = ["now", "today", "asap", "urgent", "important", "first", "before", "deadline"]
    MONEY_SIGNALS = ["revenue", "sell", "client", "pay", "charge", "income", "profit", "$"]

    @classmethod
    def process(cls, raw_text):
        """Process raw idea text into structured idea."""
        idea_id = f"IDEA-{hashlib.md5(f'{raw_text}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        text = raw_text.strip()
        words = text.lower().split()

        # Split multi-idea messages
        ideas = cls._split_ideas(text)

        processed = []
        for idea_text in ideas:
            idea_lower = idea_text.lower()

            # Detect project
            project = "uncategorized"
            for keyword, proj in cls.PROJECT_MAP.items():
                if keyword in idea_lower:
                    project = proj
                    break

            # Detect category
            category = "general"
            max_score = 0
            for cat, keywords in cls.CATEGORIES.items():
                score = sum(1 for k in keywords if k in idea_lower)
                if score > max_score:
                    max_score = score
                    category = cat

            # Detect priority
            priority = "normal"
            if any(s in idea_lower for s in cls.URGENCY_SIGNALS):
                priority = "high"
            if any(s in idea_lower for s in cls.MONEY_SIGNALS):
                priority = "high"

            # Detect actionability
            actionable = any(w in idea_lower for w in ["build", "create", "make", "fix", "add", "set up", "write", "record", "post", "deploy", "launch"])

            # Extract tags
            tags = []
            if project != "uncategorized":
                tags.append(project)
            tags.append(category)
            # Add any @mentions or #hashtags
            tags.extend(re.findall(r'#(\w+)', idea_text))
            tags.extend(re.findall(r'@(\w+)', idea_text))

            # Clean the idea text
            clean_text = cls._clean(idea_text)

            # Determine route
            if actionable and priority == "high":
                route = "todo"
            elif actionable:
                route = "backlog"
            elif category == "creative":
                route = "explore"
            elif category == "personal":
                route = "journal"
            else:
                route = "capture"

            processed.append({
                "id": f"{idea_id}-{len(processed)}",
                "raw": idea_text,
                "clean": clean_text,
                "project": project,
                "category": category,
                "priority": priority,
                "actionable": actionable,
                "route": route,
                "tags": list(set(tags)),
                "captured_at": datetime.now().isoformat(),
                "status": "pending",  # pending → reviewed → routed → done
                "connections": [],  # filled in by connection engine
            })

        return processed

    @classmethod
    def _split_ideas(cls, text):
        """Split a message into discrete ideas."""
        # Split on common delimiters
        splitters = [
            r'\n\n+',           # Double newlines
            r'\.\s+(?=[A-Z])',  # Period + capital letter
            r'\balso\b',
            r'\bplus\b',
            r'\band also\b',
            r'\boh and\b',
            r'\bbtw\b',
            r'\banother thing\b',
        ]

        parts = [text]
        for pattern in splitters:
            new_parts = []
            for part in parts:
                splits = re.split(pattern, part, flags=re.IGNORECASE)
                new_parts.extend([s.strip() for s in splits if s.strip()])
            parts = new_parts

        # Filter out tiny fragments
        return [p for p in parts if len(p) > 10]

    @classmethod
    def _clean(cls, text):
        """Clean up raw idea text."""
        # Remove filler words at start
        text = re.sub(r'^(like|so|um|uh|ok|okay|hey|yo|man|bro|dude)\s+', '', text, flags=re.IGNORECASE)
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        # Remove trailing filler
        text = re.sub(r'\s+(idk|lol|lmao|haha|like yeah)\s*$', '', text, flags=re.IGNORECASE)
        return text


# ── CONNECTION ENGINE ──────────────────────────────────────────

class ConnectionEngine:
    """Connect new ideas to existing projects and ideas."""

    @staticmethod
    def find_connections(idea, existing_ideas):
        """Find related ideas in the pipeline."""
        connections = []
        idea_words = set(idea["clean"].lower().split())

        for existing in existing_ideas:
            existing_words = set(existing["clean"].lower().split())
            overlap = idea_words & existing_words - {"the", "a", "an", "is", "to", "in", "for", "and", "or", "but", "i", "my", "we"}
            if len(overlap) >= 3 or idea["project"] == existing["project"]:
                connections.append({
                    "id": existing["id"],
                    "reason": f"shared: {', '.join(list(overlap)[:5])}" if overlap else f"same project: {idea['project']}",
                    "strength": len(overlap)
                })

        # Sort by strength
        connections.sort(key=lambda c: -c["strength"])
        return connections[:5]


# ── PIPELINE ──────────────────────────────────────────

def load_pipeline():
    if PIPELINE_FILE.exists():
        return json.loads(PIPELINE_FILE.read_text())
    return {"ideas": [], "stats": {"total": 0, "routed": 0, "done": 0}}

def save_pipeline(data):
    PIPELINE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ── CLI ──────────────────────────────────────────

def cmd_capture(text):
    """Capture a new idea."""
    pipeline = load_pipeline()
    ideas = IdeaProcessor.process(text)

    # Find connections
    for idea in ideas:
        idea["connections"] = ConnectionEngine.find_connections(idea, pipeline["ideas"])

    pipeline["ideas"].extend(ideas)
    pipeline["stats"]["total"] += len(ideas)
    save_pipeline(pipeline)

    print(cyan(f"\n  CAPTURED {len(ideas)} idea(s)"))
    print(f"  {'─'*50}")

    for idea in ideas:
        route_colors = {"todo": "31", "backlog": "33", "explore": "35", "journal": "36", "capture": "90"}
        route_c = route_colors.get(idea["route"], "90")

        print(f"\n  {cyan(idea['id'])}")
        print(f"    {idea['clean']}")
        print(f"    Project: {gold(idea['project'])}  Category: {idea['category']}  Priority: {idea['priority']}")
        print(f"    Route: {color(idea['route'].upper(), route_c)}  Tags: {', '.join(idea['tags'])}")
        if idea["connections"]:
            print(f"    Connected to: {dim(idea['connections'][0]['id'])} ({idea['connections'][0]['reason']})")

    print(f"\n  Pipeline: {pipeline['stats']['total']} ideas total")


def cmd_review(args):
    """Review pending ideas and route them."""
    pipeline = load_pipeline()
    pending = [i for i in pipeline["ideas"] if i["status"] == "pending"]

    if not pending:
        print(f"\n  No pending ideas. Pipeline is clean.")
        return

    print(cyan(f"\n  PENDING IDEAS ({len(pending)})"))
    print(f"  {'─'*50}")

    by_route = {}
    for idea in pending:
        by_route.setdefault(idea["route"], []).append(idea)

    for route in ["todo", "backlog", "explore", "capture", "journal"]:
        items = by_route.get(route, [])
        if not items:
            continue

        route_colors = {"todo": "31", "backlog": "33", "explore": "35", "journal": "36", "capture": "90"}
        print(f"\n  {color(route.upper(), route_colors.get(route, '90'))} ({len(items)})")
        for idea in items:
            print(f"    {dim(idea['id'])} [{gold(idea['project'])}] {idea['clean'][:60]}")


def cmd_pipeline(args):
    """Show full pipeline status."""
    pipeline = load_pipeline()
    ideas = pipeline["ideas"]

    print(cyan(f"\n  IDEA PIPELINE"))
    print(f"  {'─'*50}")

    # Stats
    by_status = {}
    by_project = {}
    by_route = {}
    for idea in ideas:
        by_status[idea["status"]] = by_status.get(idea["status"], 0) + 1
        by_project[idea["project"]] = by_project.get(idea["project"], 0) + 1
        by_route[idea["route"]] = by_route.get(idea["route"], 0) + 1

    print(f"\n  Total: {green(str(len(ideas)))}")
    print(f"\n  By status:")
    for s, n in sorted(by_status.items()):
        print(f"    {s:12s} {n}")
    print(f"\n  By project:")
    for p, n in sorted(by_project.items(), key=lambda x: -x[1]):
        print(f"    {p:20s} {n}")
    print(f"\n  By route:")
    for r, n in sorted(by_route.items(), key=lambda x: -x[1]):
        print(f"    {r:12s} {n}")


def cmd_search(args):
    """Search captured ideas."""
    query = " ".join(args).lower()
    pipeline = load_pipeline()

    matches = [i for i in pipeline["ideas"] if query in i["clean"].lower() or query in i["project"] or query in " ".join(i["tags"])]

    print(cyan(f"\n  SEARCH: '{query}' ({len(matches)} results)"))
    print(f"  {'─'*50}")
    for idea in matches:
        print(f"  {dim(idea['id'])} [{gold(idea['project'])}] {idea['clean'][:60]}")
        print(f"    Route: {idea['route']} | Tags: {', '.join(idea['tags'])} | {dim(idea['captured_at'][:10])}")


def main():
    if len(sys.argv) < 2:
        print(cyan("""
  Behike Idea Capture
  ====================

  Capture:
    python3 capture.py "your idea here"
    python3 capture.py --review
    python3 capture.py --pipeline
    python3 capture.py --search "keyword"
    echo "idea" | python3 capture.py -
        """))
        return

    arg = sys.argv[1]

    if arg == "--review":
        cmd_review(sys.argv[2:])
    elif arg == "--pipeline":
        cmd_pipeline(sys.argv[2:])
    elif arg == "--search":
        cmd_search(sys.argv[2:])
    elif arg == "-":
        text = sys.stdin.read().strip()
        if text:
            cmd_capture(text)
    else:
        text = " ".join(sys.argv[1:])
        cmd_capture(text)


if __name__ == "__main__":
    main()
