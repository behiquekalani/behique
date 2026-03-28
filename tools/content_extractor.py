#!/usr/bin/env python3
"""
Content Extractor - Gym Transcript Pipeline
Reads gym transcripts and extracts video topics, hooks, and content ideas.
Does NOT copy transcript text. Generates original hooks in Kalani's voice.

Copyright 2026 Behike.

Usage:
    python3 content_extractor.py --scan           Full scan of all transcripts
    python3 content_extractor.py --kb ecommerce   Scan specific knowledge base
    python3 content_extractor.py --list            Show all extracted topics
    python3 content_extractor.py --random          Pick a random topic for today
"""

import argparse
import json
import os
import random
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
GYM_DIR = Path(__file__).resolve().parent.parent / "gym"
TRANSCRIPTS_DIR = GYM_DIR / "transcripts"
OUTPUT_JSON = Path(__file__).resolve().parent.parent / "Ceiba" / "news" / "content-ideas.json"
OUTPUT_MD = Path(__file__).resolve().parent.parent / "Ceiba" / "news" / "content-ideas.md"

# Knowledge base folder name -> top-level transcript folder mapping
# Transcripts live under transcripts/<category>/<subcategory>/<course>/
# Knowledge bases are named by course slug
KB_NAMES = {
    "ecommerce": "04-business-and-money",
    "gaming": "06-lifestyle",
    "claude-code-automating-daily-tasks": "02-ai-and-machine-learning",
}

# -------------------------------------------------------------------
# Frontmatter parser
# -------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def strip_frontmatter(text: str) -> str:
    """Return text without the YAML frontmatter block."""
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)


# -------------------------------------------------------------------
# Content analysis (local, no API calls)
# -------------------------------------------------------------------

def file_id(filepath: str) -> str:
    """Stable unique ID from file path."""
    return hashlib.md5(filepath.encode()).hexdigest()[:12]


def detect_difficulty(text: str) -> str:
    """Heuristic difficulty based on vocabulary and length."""
    lower = text.lower()
    advanced_signals = [
        "api", "algorithm", "optimization", "scaling", "architecture",
        "advanced", "deep dive", "technical", "framework", "infrastructure",
        "private label", "ppc", "sponsored", "analytics", "metrics",
    ]
    beginner_signals = [
        "beginner", "intro", "getting started", "basics", "first",
        "step by step", "how to start", "what is", "welcome",
        "setup", "set up", "overview",
    ]

    adv_count = sum(1 for s in advanced_signals if s in lower)
    beg_count = sum(1 for s in beginner_signals if s in lower)

    if adv_count >= 3:
        return "advanced"
    if beg_count >= 2 or adv_count == 0:
        return "beginner"
    return "intermediate"


def suggest_content_type(title: str, text: str, word_count: int) -> list:
    """Suggest content formats based on the transcript characteristics."""
    suggestions = []
    lower_title = title.lower()
    lower_text = text.lower()

    # Short, actionable topics work as reels
    if word_count < 1500 or any(w in lower_title for w in ["how to", "tip", "hack", "quick", "fast"]):
        suggestions.append("reel")

    # List-style or multi-step content works as carousels
    if any(w in lower_title for w in ["top", "best", "ways", "steps", "methods", "tips"]):
        suggestions.append("carousel")

    # Deep topics work as blog posts
    if word_count > 2000:
        suggestions.append("blog post")

    # Very deep or tutorial-style content works as YouTube videos
    if word_count > 3000 or "tutorial" in lower_title or "course" in lower_text:
        suggestions.append("youtube video")

    if not suggestions:
        suggestions.append("reel")

    return suggestions


def extract_key_themes(text: str) -> list:
    """Pull out the main themes/concepts from transcript body text."""
    # Split into sentences
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    # Score sentences by information density (unique nouns, action verbs)
    scored = []
    for s in sentences:
        words = s.split()
        if len(words) < 6 or len(words) > 40:
            continue
        # Skip filler sentences
        filler_starts = ["so ", "and ", "but ", "okay ", "um ", "uh ", "like ",
                         "you know", "i mean", "anyways", "alright"]
        if any(s.lower().startswith(f) for f in filler_starts):
            continue
        # Prefer sentences with concrete/instructional language
        score = 0
        instructional = ["important", "key", "strategy", "method", "technique",
                         "profit", "margin", "product", "build", "create",
                         "system", "process", "tool", "automate", "sell",
                         "customer", "revenue", "growth", "brand", "market",
                         "design", "develop", "launch", "test", "optimize"]
        for word in instructional:
            if word in s.lower():
                score += 1
        if score > 0:
            scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    # Return top themes as condensed one-liners
    themes = []
    seen_starts = set()
    for _, s in scored[:10]:
        # Deduplicate by first 5 words
        start = " ".join(s.split()[:5]).lower()
        if start in seen_starts:
            continue
        seen_starts.add(start)
        # Truncate to one clean sentence
        clean = s.strip()
        if len(clean) > 120:
            clean = clean[:117] + "..."
        themes.append(clean)
        if len(themes) >= 5:
            break

    return themes


def generate_hooks(title: str, themes: list, category: str) -> list:
    """Generate original attention-grabbing hooks in Kalani's voice.
    Direct, builder-to-builder, no hype. No em dashes."""
    hooks = []
    clean_title = re.sub(r"^\d+[\.\-]\d*\s*", "", title).strip()

    # Hook templates by category
    if "ecommerce" in category.lower() or "business" in category.lower():
        templates = [
            f"Most people get {clean_title.lower()} wrong. Here is what actually works.",
            f"I tested this {clean_title.lower()} strategy so you do not have to guess.",
            f"Stop overthinking {clean_title.lower()}. Do this instead.",
            f"The thing nobody tells you about {clean_title.lower()}.",
            f"This one change in {clean_title.lower()} doubled my results.",
        ]
    elif "gaming" in category.lower() or "lifestyle" in category.lower():
        templates = [
            f"You are building {clean_title.lower()} the hard way. Let me show you the shortcut.",
            f"I broke down {clean_title.lower()} into steps anyone can follow.",
            f"Here is what {clean_title.lower()} looks like when you actually understand it.",
            f"Stop watching tutorials and start building. {clean_title} in practice.",
            f"The fastest way to learn {clean_title.lower()} is not what you think.",
        ]
    else:
        templates = [
            f"Everyone talks about {clean_title.lower()} but nobody shows you how. Until now.",
            f"I automated {clean_title.lower()} and it changed everything.",
            f"{clean_title} is simpler than you think. Here is proof.",
            f"Forget the theory. This is {clean_title.lower()} in the real world.",
            f"What I learned building {clean_title.lower()} from scratch.",
        ]

    # Pick 2-3 hooks, vary them
    random.seed(hash(title))  # Deterministic per title
    chosen = random.sample(templates, min(3, len(templates)))

    # If we have themes, create one hook based on the top theme
    if themes:
        theme_hook = f"{themes[0].split(',')[0].strip()}. That is the part everyone skips."
        chosen[-1] = theme_hook

    return chosen


def process_transcript(filepath: Path) -> Optional[dict]:
    """Process a single transcript file and extract content ideas."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  [SKIP] Could not read {filepath}: {e}")
        return None

    if len(text.strip()) < 100:
        return None

    meta = parse_frontmatter(text)
    body = strip_frontmatter(text)
    word_count = len(body.split())

    title = meta.get("title", filepath.stem.replace("-", " ").title())
    category = meta.get("category", "GENERAL")
    course = meta.get("course", "Unknown")
    module_info = meta.get("module", "")

    # Determine which knowledge base this belongs to
    rel_path = str(filepath.relative_to(TRANSCRIPTS_DIR))
    parts = rel_path.split(os.sep)
    kb_folder = parts[0] if parts else "unknown"

    # Extract content
    themes = extract_key_themes(body)
    difficulty = detect_difficulty(body)
    content_types = suggest_content_type(title, body, word_count)
    hooks = generate_hooks(title, themes, category)

    return {
        "id": file_id(str(filepath)),
        "title": title,
        "category": category,
        "course": course,
        "knowledge_base": kb_folder,
        "module": module_info,
        "file": str(filepath),
        "word_count": word_count,
        "difficulty": difficulty,
        "content_types": content_types,
        "key_takeaways": themes[:5],
        "hooks": hooks[:3],
        "extracted_at": datetime.now().isoformat(),
    }


# -------------------------------------------------------------------
# Scanning
# -------------------------------------------------------------------

def find_transcripts(kb_filter: Optional[str] = None) -> list:
    """Find all transcript files, optionally filtered by knowledge base."""
    if not TRANSCRIPTS_DIR.exists():
        print(f"[ERROR] Transcripts directory not found: {TRANSCRIPTS_DIR}")
        sys.exit(1)

    files = sorted(TRANSCRIPTS_DIR.rglob("*.md"))

    if kb_filter:
        # Map kb name to transcript folder
        folder_filter = KB_NAMES.get(kb_filter, kb_filter)
        files = [f for f in files if folder_filter in str(f)]
        if not files:
            # Try matching directly against path
            files = sorted(TRANSCRIPTS_DIR.rglob("*.md"))
            files = [f for f in files if kb_filter.lower() in str(f).lower()]

    return files


def run_scan(kb_filter: Optional[str] = None):
    """Scan transcripts and extract content ideas."""
    files = find_transcripts(kb_filter)
    total = len(files)
    scope = f"knowledge base '{kb_filter}'" if kb_filter else "all knowledge bases"
    print(f"\n[SCAN] Found {total} transcripts in {scope}\n")

    if total == 0:
        print("[WARN] No transcripts found. Check the path or knowledge base name.")
        print(f"  Available KBs: {', '.join(KB_NAMES.keys())}")
        return

    # Load existing data to merge
    existing = {}
    if OUTPUT_JSON.exists():
        try:
            existing_data = json.loads(OUTPUT_JSON.read_text())
            existing = {item["id"]: item for item in existing_data.get("ideas", [])}
        except Exception:
            pass

    results = []
    skipped = 0
    for i, fp in enumerate(files, 1):
        if i % 50 == 0 or i == total:
            print(f"  Processing {i}/{total}...")
        idea = process_transcript(fp)
        if idea:
            existing[idea["id"]] = idea
            results.append(idea)
        else:
            skipped += 1

    # Merge all ideas
    all_ideas = list(existing.values())

    # Save JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_ideas": len(all_ideas),
        "scan_scope": scope,
        "knowledge_bases": list(KB_NAMES.keys()),
        "ideas": all_ideas,
    }
    OUTPUT_JSON.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n[SAVED] {len(all_ideas)} ideas to {OUTPUT_JSON}")

    # Save markdown summary
    generate_markdown(all_ideas)
    print(f"[SAVED] Summary to {OUTPUT_MD}")

    # Stats
    print(f"\n--- Scan Results ---")
    print(f"  Processed: {len(results)}")
    print(f"  Skipped:   {skipped}")
    print(f"  Total DB:  {len(all_ideas)}")

    # Breakdown by KB
    kb_counts = {}
    for idea in all_ideas:
        kb = idea.get("knowledge_base", "unknown")
        kb_counts[kb] = kb_counts.get(kb, 0) + 1
    print(f"\n  By knowledge base:")
    for kb, count in sorted(kb_counts.items()):
        print(f"    {kb}: {count}")

    # Breakdown by difficulty
    diff_counts = {}
    for idea in all_ideas:
        d = idea.get("difficulty", "unknown")
        diff_counts[d] = diff_counts.get(d, 0) + 1
    print(f"\n  By difficulty:")
    for d, count in sorted(diff_counts.items()):
        print(f"    {d}: {count}")


def generate_markdown(ideas: list):
    """Generate a human-readable markdown summary."""
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Content Ideas Extracted from Gym Transcripts",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total ideas: {len(ideas)}",
        "",
    ]

    # Group by knowledge base
    by_kb = {}
    for idea in ideas:
        kb = idea.get("knowledge_base", "unknown")
        by_kb.setdefault(kb, []).append(idea)

    for kb in sorted(by_kb.keys()):
        kb_ideas = by_kb[kb]
        lines.append(f"## {kb.replace('-', ' ').title()} ({len(kb_ideas)} topics)")
        lines.append("")

        # Group by difficulty within KB
        for difficulty in ["beginner", "intermediate", "advanced"]:
            diff_ideas = [i for i in kb_ideas if i.get("difficulty") == difficulty]
            if not diff_ideas:
                continue
            lines.append(f"### {difficulty.title()} ({len(diff_ideas)})")
            lines.append("")

            for idea in diff_ideas:
                lines.append(f"**{idea['title']}**")
                lines.append(f"- Course: {idea.get('course', 'N/A')}")
                lines.append(f"- Content types: {', '.join(idea.get('content_types', []))}")

                takeaways = idea.get("key_takeaways", [])
                if takeaways:
                    lines.append(f"- Key takeaways:")
                    for t in takeaways:
                        lines.append(f"  - {t}")

                hooks = idea.get("hooks", [])
                if hooks:
                    lines.append(f"- Hooks:")
                    for h in hooks:
                        lines.append(f"  - \"{h}\"")

                lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


# -------------------------------------------------------------------
# List and Random commands
# -------------------------------------------------------------------

def run_list():
    """Show all extracted topics."""
    if not OUTPUT_JSON.exists():
        print("[ERROR] No content ideas found. Run --scan first.")
        sys.exit(1)

    data = json.loads(OUTPUT_JSON.read_text())
    ideas = data.get("ideas", [])
    print(f"\n[LIST] {len(ideas)} content ideas extracted\n")

    # Group by KB
    by_kb = {}
    for idea in ideas:
        kb = idea.get("knowledge_base", "unknown")
        by_kb.setdefault(kb, []).append(idea)

    for kb in sorted(by_kb.keys()):
        kb_ideas = by_kb[kb]
        print(f"  {kb.replace('-', ' ').upper()} ({len(kb_ideas)} topics)")
        for idea in kb_ideas:
            difficulty_tag = f"[{idea.get('difficulty', '?')[0].upper()}]"
            types = ", ".join(idea.get("content_types", []))
            print(f"    {difficulty_tag} {idea['title']}  ({types})")
        print()


def run_random():
    """Pick a random topic and display it as today's content suggestion."""
    if not OUTPUT_JSON.exists():
        print("[ERROR] No content ideas found. Run --scan first.")
        sys.exit(1)

    data = json.loads(OUTPUT_JSON.read_text())
    ideas = data.get("ideas", [])

    if not ideas:
        print("[ERROR] No ideas in database.")
        sys.exit(1)

    idea = random.choice(ideas)

    print(f"\n{'=' * 60}")
    print(f"  TODAY'S CONTENT PICK")
    print(f"{'=' * 60}")
    print(f"\n  Title:      {idea['title']}")
    print(f"  Category:   {idea.get('category', 'N/A')}")
    print(f"  Course:     {idea.get('course', 'N/A')}")
    print(f"  Difficulty: {idea.get('difficulty', 'N/A')}")
    print(f"  Format:     {', '.join(idea.get('content_types', []))}")

    takeaways = idea.get("key_takeaways", [])
    if takeaways:
        print(f"\n  Key Takeaways:")
        for i, t in enumerate(takeaways, 1):
            print(f"    {i}. {t}")

    hooks = idea.get("hooks", [])
    if hooks:
        print(f"\n  Content Hooks:")
        for i, h in enumerate(hooks, 1):
            print(f"    {i}. \"{h}\"")

    print(f"\n  Source: {idea.get('file', 'N/A')}")
    print(f"{'=' * 60}\n")


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Content Extractor - Extract video topics and hooks from gym transcripts"
    )
    parser.add_argument("--scan", action="store_true", help="Full scan of all transcripts")
    parser.add_argument("--kb", type=str, help="Scan specific knowledge base (ecommerce, gaming, claude-code-automating-daily-tasks)")
    parser.add_argument("--list", action="store_true", help="Show all extracted topics")
    parser.add_argument("--random", action="store_true", help="Pick a random topic for today")

    args = parser.parse_args()

    if args.scan:
        run_scan()
    elif args.kb:
        run_scan(kb_filter=args.kb)
    elif args.list:
        run_list()
    elif args.random:
        run_random()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
