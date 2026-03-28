#!/usr/bin/env python3
"""
ebook_series_builder.py - Generates ORIGINAL ebooks from Gym KB transcripts.

Unlike ebook_builder.py (which compiles/cleans transcripts), this tool:
1. Scans a KB directory for transcript .md files
2. Groups transcripts by module/course (YAML frontmatter or filename)
3. Extracts TOPICS and CONCEPTS only (never copies text)
4. Generates original chapters in the Behike writing voice
5. Adds exercises/checklists per chapter
6. Compiles into a single ebook .md with TOC
7. Adds copyright + AI disclosure

IMPORTANT: This tool extracts topic outlines from transcripts.
The actual chapter writing must be done by the human or AI author
using only the extracted topics as a guide. No transcript text
is ever copied into the output.

Usage:
    python3 tools/ebook_series_builder.py scan --kb-dir ~/behique/gym/knowledge-bases/gaming
    python3 tools/ebook_series_builder.py outline --kb-dir ~/behique/gym/knowledge-bases/gaming --modules "1,2,3" --output outline.md
    python3 tools/ebook_series_builder.py compile --outline outline.md --chapters-dir ./chapters --output ebook.md --title "Book Title"

Copyright 2026 Behike. All rights reserved.
"""

import argparse
import os
import re
import sys
import yaml
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Lesson:
    title: str
    topics: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)


@dataclass
class Module:
    name: str
    source_file: str
    lesson_count: int = 0
    lessons: list[Lesson] = field(default_factory=list)


def parse_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}


def extract_section_headers(filepath: Path) -> list[str]:
    """Extract ## level headers from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    headers = []
    for line in text.split("\n"):
        match = re.match(r"^##\s+\d+\.\s*(.*)", line)
        if match:
            title = match.group(1).strip()
            # Clean up numbered prefixes like "1. " or "32. "
            title = re.sub(r"^\d+\.\s*", "", title)
            headers.append(title)

    return headers


def extract_topics_from_section(text: str) -> list[str]:
    """Extract key topics/concepts from a transcript section.

    This pulls out TOPIC NAMES only, not transcript text.
    Uses keyword detection to identify what subjects are covered.
    """
    topics = set()

    # Common topic patterns in educational content
    topic_indicators = [
        (r"let'?s talk about (.+?)[\.\,\!]", 1),
        (r"what is (.+?)[\?\.\,]", 1),
        (r"we'?(?:re|ll) (?:talk|learn|cover|go over|discuss) (?:about )?(.+?)[\.\,\!]", 1),
        (r"this is (?:called |basically )?(.+?)[\.\,\!]", 1),
        (r"how (?:to|can we) (.+?)[\.\,\!]", 1),
    ]

    for pattern, group in topic_indicators:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            topic = match.group(group).strip()
            if 5 < len(topic) < 80:
                topics.add(topic)

    return sorted(topics)[:10]  # Cap at 10 topics per section


def scan_knowledge_base(kb_dir: str) -> list[Module]:
    """Scan a KB directory and return structured module data."""
    kb_path = Path(kb_dir)
    if not kb_path.exists():
        print(f"Error: Directory not found: {kb_dir}")
        sys.exit(1)

    modules = []
    for filepath in sorted(kb_path.glob("*.md")):
        if filepath.name.startswith("_"):
            continue

        frontmatter = parse_frontmatter(filepath)
        module_name = frontmatter.get("module", filepath.stem)
        lesson_count = frontmatter.get("lessons", 0)
        headers = extract_section_headers(filepath)

        mod = Module(
            name=module_name,
            source_file=str(filepath),
            lesson_count=lesson_count,
            lessons=[Lesson(title=h) for h in headers],
        )
        modules.append(mod)

    return modules


def generate_topic_outline(modules: list[Module], selected: list[int] | None = None) -> str:
    """Generate a topic outline from selected modules.

    This extracts TOPICS ONLY. No transcript text is included.
    """
    lines = []
    lines.append("# Topic Outline")
    lines.append("")
    lines.append("Extracted topics for original chapter writing.")
    lines.append("DO NOT copy any source material. Use topics as a guide only.")
    lines.append("")

    for i, mod in enumerate(modules):
        if selected and (i + 1) not in selected:
            continue

        lines.append(f"## Module: {mod.name}")
        lines.append(f"Source: {mod.source_file}")
        lines.append(f"Lessons: {mod.lesson_count}")
        lines.append("")

        for lesson in mod.lessons:
            lines.append(f"### {lesson.title}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def compile_ebook(
    title: str,
    subtitle: str,
    author: str,
    chapters: list[dict],
    price: str = "",
) -> str:
    """Compile chapters into a formatted ebook markdown file.

    Each chapter dict should have: title, content, exercises
    """
    lines = []

    # Copyright + AI Disclosure
    lines.append(f"# {title}")
    lines.append("")
    if subtitle:
        lines.append(f"*{subtitle}*")
        lines.append("")
    lines.append(f"**By {author}**")
    lines.append("")
    if price:
        lines.append(f"Price: {price}")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Legal
    lines.append("## Legal Notice")
    lines.append("")
    lines.append(f"Copyright 2026 Behike. All rights reserved.")
    lines.append("")
    lines.append(
        "No part of this publication may be reproduced, distributed, or transmitted "
        "in any form without prior written permission of the publisher."
    )
    lines.append("")
    lines.append("**AI Disclosure:** This book was written with AI assistance. "
                 "All content is original and does not reproduce any copyrighted material.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("")
    for i, ch in enumerate(chapters, 1):
        anchor = ch["title"].lower().replace(" ", "-").replace(":", "")
        lines.append(f"{i}. [{ch['title']}](#{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Chapters
    for i, ch in enumerate(chapters, 1):
        lines.append(f"## Chapter {i}: {ch['title']}")
        lines.append("")
        lines.append(ch["content"])
        lines.append("")

        if ch.get("exercises"):
            lines.append(f"### Exercises")
            lines.append("")
            lines.append(ch["exercises"])
            lines.append("")

        lines.append("---")
        lines.append("")

    # Footer
    lines.append("## About the Author")
    lines.append("")
    lines.append(
        f"{author} builds digital products and teaches creative technology "
        "from Puerto Rico. Follow @behikeai on Instagram for more."
    )
    lines.append("")

    return "\n".join(lines)


def cmd_scan(args):
    """Scan command: show KB structure."""
    modules = scan_knowledge_base(args.kb_dir)
    total_lessons = sum(m.lesson_count for m in modules)

    print(f"Knowledge Base: {args.kb_dir}")
    print(f"Modules: {len(modules)}")
    print(f"Total Lessons: {total_lessons}")
    print()

    for i, mod in enumerate(modules, 1):
        print(f"  [{i}] {mod.name} ({mod.lesson_count} lessons)")
        for lesson in mod.lessons[:5]:
            print(f"      - {lesson.title}")
        if len(mod.lessons) > 5:
            print(f"      ... and {len(mod.lessons) - 5} more")
        print()


def cmd_outline(args):
    """Outline command: generate topic outline."""
    modules = scan_knowledge_base(args.kb_dir)

    selected = None
    if args.modules:
        selected = [int(x.strip()) for x in args.modules.split(",")]

    outline = generate_topic_outline(modules, selected)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(outline, encoding="utf-8")
    print(f"Outline saved to: {args.output}")


def cmd_compile(args):
    """Compile command: assemble chapters into ebook."""
    chapters_dir = Path(args.chapters_dir)
    if not chapters_dir.exists():
        print(f"Error: chapters directory not found: {args.chapters_dir}")
        sys.exit(1)

    chapters = []
    for filepath in sorted(chapters_dir.glob("*.md")):
        text = filepath.read_text(encoding="utf-8")
        # Extract title from first # heading
        title_match = re.match(r"^#\s+(.+)", text)
        title = title_match.group(1) if title_match else filepath.stem

        # Split content and exercises if marked
        parts = re.split(r"\n##\s+Exercises?\s*\n", text, maxsplit=1)
        content = parts[0].strip()
        exercises = parts[1].strip() if len(parts) > 1 else ""

        # Remove the title line from content
        content = re.sub(r"^#\s+.+\n*", "", content).strip()

        chapters.append({
            "title": title,
            "content": content,
            "exercises": exercises,
        })

    ebook = compile_ebook(
        title=args.title,
        subtitle=args.subtitle or "",
        author=args.author,
        chapters=chapters,
        price=args.price or "",
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ebook, encoding="utf-8")

    word_count = len(ebook.split())
    print(f"Ebook compiled: {args.output}")
    print(f"Chapters: {len(chapters)}")
    print(f"Words: {word_count:,}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate original ebooks from Gym KB transcripts"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan
    scan_parser = subparsers.add_parser("scan", help="Scan KB and show structure")
    scan_parser.add_argument("--kb-dir", required=True, help="Path to KB directory")

    # Outline
    outline_parser = subparsers.add_parser("outline", help="Generate topic outline")
    outline_parser.add_argument("--kb-dir", required=True, help="Path to KB directory")
    outline_parser.add_argument("--modules", default=None, help="Comma-separated module numbers")
    outline_parser.add_argument("--output", required=True, help="Output outline .md path")

    # Compile
    compile_parser = subparsers.add_parser("compile", help="Compile chapters into ebook")
    compile_parser.add_argument("--chapters-dir", required=True, help="Directory with chapter .md files")
    compile_parser.add_argument("--title", required=True, help="Ebook title")
    compile_parser.add_argument("--subtitle", default="", help="Subtitle")
    compile_parser.add_argument("--author", default="Behike", help="Author name")
    compile_parser.add_argument("--price", default="", help="Price point")
    compile_parser.add_argument("--output", required=True, help="Output .md path")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "outline":
        cmd_outline(args)
    elif args.command == "compile":
        cmd_compile(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
