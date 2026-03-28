#!/usr/bin/env python3
"""
ebook_builder.py - Converts Gym knowledge base transcripts into formatted ebooks.

Usage:
    python3 tools/ebook_builder.py --kb-dir ~/behique/gym/ecommerce --title "The Ecommerce Playbook" --output ~/behique/ebooks/ecommerce-playbook.md
    python3 tools/ebook_builder.py --kb-dir ~/behique/gym/gaming --title "The Gaming Business Guide" --output ~/behique/ebooks/gaming-guide.md

Flow:
    1. Scan KB directory for transcript files (.txt, .md, .json)
    2. Group transcripts by module/category (folder structure or filename pattern)
    3. Clean and format each transcript (remove timestamps, filler, normalize)
    4. Generate table of contents
    5. Assemble into single Markdown ebook
    6. Output as .md (can be converted to PDF/EPUB with pandoc)

Pandoc conversion (after generating .md):
    pandoc ebook.md -o ebook.pdf --pdf-engine=wkhtmltopdf --css=ebook.css
    pandoc ebook.md -o ebook.epub --metadata title="Title" --metadata author="Kalani"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def find_transcripts(kb_dir: str) -> list[dict]:
    """Find and categorize all transcript files in a KB directory."""
    transcripts = []
    kb_path = Path(kb_dir)

    if not kb_path.exists():
        print(f"Error: KB directory not found: {kb_dir}")
        sys.exit(1)

    # Supported extensions
    extensions = {".txt", ".md", ".json", ".srt"}

    for root, dirs, files in os.walk(kb_path):
        # Sort dirs for consistent ordering
        dirs.sort()
        for filename in sorted(files):
            filepath = Path(root) / filename
            if filepath.suffix.lower() in extensions:
                # Determine module from folder structure or filename
                rel_path = filepath.relative_to(kb_path)
                parts = rel_path.parts

                module = parts[0] if len(parts) > 1 else "General"
                module = clean_module_name(module)

                transcripts.append({
                    "path": str(filepath),
                    "filename": filename,
                    "module": module,
                    "title": clean_title(filepath.stem),
                })

    return transcripts


def clean_module_name(name: str) -> str:
    """Clean module/folder name into readable chapter title."""
    # Remove leading numbers like "01_" or "1-"
    name = re.sub(r"^\d+[-_.\s]*", "", name)
    # Replace underscores and hyphens with spaces
    name = name.replace("_", " ").replace("-", " ")
    # Title case
    name = name.strip().title()
    return name if name else "General"


def clean_title(stem: str) -> str:
    """Clean filename stem into readable lesson title."""
    # Remove leading numbers
    title = re.sub(r"^\d+[-_.\s]*", "", stem)
    # Replace underscores and hyphens
    title = title.replace("_", " ").replace("-", " ")
    # Title case
    title = title.strip().title()
    return title if title else stem


def read_transcript(filepath: str) -> str:
    """Read and clean a transcript file."""
    path = Path(filepath)

    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return ""

    # Handle JSON format (Whisper output)
    if path.suffix == ".json":
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                # Whisper JSON format
                if "text" in data:
                    raw = data["text"]
                elif "segments" in data:
                    raw = " ".join(seg.get("text", "") for seg in data["segments"])
            elif isinstance(data, list):
                raw = " ".join(
                    item.get("text", str(item)) if isinstance(item, dict) else str(item)
                    for item in data
                )
        except json.JSONDecodeError:
            pass  # Treat as plain text

    # Handle SRT format
    if path.suffix == ".srt":
        raw = clean_srt(raw)

    # General cleaning
    text = clean_text(raw)
    return text


def clean_srt(text: str) -> str:
    """Strip SRT subtitle formatting, keep just the text."""
    lines = text.split("\n")
    clean_lines = []
    for line in lines:
        line = line.strip()
        # Skip sequence numbers
        if re.match(r"^\d+$", line):
            continue
        # Skip timestamps
        if re.match(r"\d{2}:\d{2}:\d{2}", line):
            continue
        if line:
            clean_lines.append(line)
    return " ".join(clean_lines)


def clean_text(text: str) -> str:
    """Clean transcript text for ebook readability."""
    # Remove excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove timestamp patterns like [00:05:23] or (5:23)
    text = re.sub(r"\[?\d{1,2}:\d{2}(:\d{2})?\]?", "", text)
    text = re.sub(r"\(\d{1,2}:\d{2}(:\d{2})?\)", "", text)
    # Remove common filler
    text = re.sub(r"\b(um|uh|like,?\s+you know|you know what I mean)\b", "", text, flags=re.IGNORECASE)
    # Collapse multiple spaces
    text = re.sub(r"  +", " ", text)
    # Trim lines
    text = "\n".join(line.strip() for line in text.split("\n"))

    return text.strip()


def build_ebook(
    transcripts: list[dict],
    title: str,
    author: str = "Kalani Andre Gomez Padin",
    description: str = "",
) -> str:
    """Assemble transcripts into a formatted Markdown ebook."""

    # Group by module
    modules: dict[str, list[dict]] = {}
    for t in transcripts:
        mod = t["module"]
        if mod not in modules:
            modules[mod] = []
        modules[mod].append(t)

    total_lessons = len(transcripts)
    total_modules = len(modules)

    # Build ebook
    lines = []

    # Title page
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**By {author}**")
    lines.append("")
    if description:
        lines.append(f"*{description}*")
        lines.append("")
    lines.append(f"{total_lessons} lessons across {total_modules} modules")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    chapter_num = 0
    for module_name, module_transcripts in modules.items():
        chapter_num += 1
        anchor = module_name.lower().replace(" ", "-")
        lines.append(f"{chapter_num}. [{module_name}](#{anchor}) ({len(module_transcripts)} lessons)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Chapters
    chapter_num = 0
    for module_name, module_transcripts in modules.items():
        chapter_num += 1
        lines.append(f"## Chapter {chapter_num}: {module_name}")
        lines.append("")

        lesson_num = 0
        for t in module_transcripts:
            lesson_num += 1
            content = read_transcript(t["path"])
            if not content:
                continue

            lines.append(f"### Lesson {lesson_num}: {t['title']}")
            lines.append("")

            # Split into paragraphs for readability
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if para:
                    lines.append(para)
                    lines.append("")

            lines.append("---")
            lines.append("")

    # Footer
    lines.append("## About This Book")
    lines.append("")
    lines.append(
        f"This book was compiled from {total_lessons} video course transcripts, "
        f"organized into {total_modules} modules. The content represents real course "
        f"material that was transcribed using AI (OpenAI Whisper) and formatted for "
        f"easy reading."
    )
    lines.append("")
    lines.append(f"Built with the Behique AI pipeline. {author}, Puerto Rico.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build ebook from Gym KB transcripts")
    parser.add_argument("--kb-dir", required=True, help="Path to KB transcript directory")
    parser.add_argument("--title", required=True, help="Ebook title")
    parser.add_argument("--author", default="Kalani Andre Gomez Padin", help="Author name")
    parser.add_argument("--description", default="", help="Book description/subtitle")
    parser.add_argument("--output", required=True, help="Output .md file path")
    parser.add_argument("--stats", action="store_true", help="Print stats only, don't build")

    args = parser.parse_args()

    print(f"Scanning: {args.kb_dir}")
    transcripts = find_transcripts(args.kb_dir)

    if not transcripts:
        print("No transcript files found.")
        sys.exit(1)

    # Group for stats
    modules: dict[str, int] = {}
    for t in transcripts:
        modules[t["module"]] = modules.get(t["module"], 0) + 1

    print(f"Found {len(transcripts)} transcripts in {len(modules)} modules:")
    for mod, count in modules.items():
        print(f"  {mod}: {count} lessons")

    if args.stats:
        return

    print(f"\nBuilding ebook: {args.title}")
    ebook = build_ebook(transcripts, args.title, args.author, args.description)

    # Ensure output directory exists
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ebook, encoding="utf-8")

    size_kb = out_path.stat().st_size / 1024
    word_count = len(ebook.split())
    print(f"\nDone: {args.output}")
    print(f"Size: {size_kb:.1f} KB")
    print(f"Words: {word_count:,}")
    print(f"\nTo convert to PDF:")
    print(f"  pandoc {args.output} -o {out_path.stem}.pdf --pdf-engine=wkhtmltopdf")
    print(f"To convert to EPUB:")
    print(f'  pandoc {args.output} -o {out_path.stem}.epub --metadata title="{args.title}"')


if __name__ == "__main__":
    main()
