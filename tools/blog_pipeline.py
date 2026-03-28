#!/usr/bin/env python3
"""
Blog Pipeline - Converts journal entries to polished blog posts.

Reads from Ceiba/journal/*.md, uses Ollama to expand short journal entries
into full blog posts with SEO metadata and headline options.

Usage:
    python blog_pipeline.py --from-journal 2026-03-22
    python blog_pipeline.py --from-journal 2026-03-22-adhd-superpower
    python blog_pipeline.py --week
    python blog_pipeline.py --list

Copyright 2026 Behike.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

# -- Paths --
BASE_DIR = Path(__file__).resolve().parent.parent
JOURNAL_DIR = BASE_DIR / "Ceiba" / "journal"
BLOG_DIR = BASE_DIR / "Ceiba" / "blog"
BLOG_INDEX = BASE_DIR / "themes" / "behike-store" / "landing-pages" / "blog-index.json"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

# Patterns to strip from journal entries before sending to LLM
STRIP_PATTERNS = [
    r"~/[\w/\-\.]+",              # File paths like ~/behique/tools/
    r"/Users/[\w/\-\.]+",         # Absolute paths
    r"\b(?:n8n|Ollama|Railway|Warp|Cursor)\b",  # Internal tool names
    r"\bgit\s+(?:commit|push|pull|merge)\b",     # Git commands
    r"```[\s\S]*?```",            # Code blocks
    r"\b[A-Z_]{3,}(?:_[A-Z]+)+\b",  # ENV_VAR_NAMES
]

SYSTEM_PROMPT = """You are a blog writer for Behike, a brand run by a computer engineering student in Puerto Rico.

Voice rules:
- Direct, confident, no fluff
- Active voice. Numbers. Pattern interrupts.
- Never use em dashes. Use periods or commas instead.
- Short paragraphs. One idea per paragraph.
- First person. Real stories. Honest about struggles.
- Dan Koe tone: minimalist, confident, clear
- Mix English with occasional Spanish phrases naturally
- Hit at least two of: educate, entertain, inspire

Structure:
- Strong opening line that hooks immediately
- 800-1500 words total
- Break into clear sections with subheadings
- End with a takeaway or call to reflection
- No generic CTAs like "drop your take below"

You will receive a raw journal entry. Expand it into a polished blog post.
Strip any internal details about tools, file paths, or technical infrastructure.
Keep the authentic voice and real stories. Add depth, not fluff."""

SEO_PROMPT = """Given this blog post, generate SEO metadata as JSON:
{
  "title": "the blog post title (60 chars max)",
  "description": "meta description (155 chars max)",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "headlines": [
    "Headline option 1",
    "Headline option 2",
    "Headline option 3"
  ],
  "reading_time": "X min",
  "tags": ["tag1", "tag2"]
}

Tags must be from: ai, business, adhd, building, personal

Respond with ONLY the JSON. No markdown. No explanation."""


def ollama_generate(prompt, system=None, temperature=0.7):
    """Call Ollama API for text generation."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system

    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.ConnectionError:
        print(f"ERROR: Cannot connect to Ollama at {OLLAMA_URL}")
        print("Start Ollama or set OLLAMA_URL environment variable.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Ollama request failed: {e}")
        sys.exit(1)


def strip_internal_details(text):
    """Remove file paths, tool names, and internal references."""
    cleaned = text
    for pattern in STRIP_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    # Clean up double spaces and blank lines
    cleaned = re.sub(r"  +", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def parse_frontmatter(content):
    """Extract YAML frontmatter and body from markdown."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content

    fm_text = match.group(1)
    body = match.group(2).strip()

    frontmatter = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            frontmatter[key.strip()] = val.strip()

    return frontmatter, body


def read_journal(path):
    """Read and parse a journal entry."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    frontmatter, body = parse_frontmatter(content)
    return frontmatter, body


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:60]


def generate_blog_post(journal_path):
    """Convert a journal entry into a full blog post."""
    frontmatter, body = read_journal(journal_path)
    date = frontmatter.get("date", datetime.now().strftime("%Y-%m-%d"))
    word_count = len(body.split())

    print(f"\nProcessing: {journal_path.name}")
    print(f"  Date: {date}")
    print(f"  Words: {word_count}")

    # Strip internal details
    cleaned_body = strip_internal_details(body)

    # Generate expanded blog post
    print("  Expanding with Ollama...")
    blog_content = ollama_generate(
        f"Journal entry ({word_count} words):\n\n{cleaned_body}",
        system=SYSTEM_PROMPT,
        temperature=0.7,
    )

    if not blog_content:
        print("  ERROR: Empty response from Ollama")
        return None

    # Generate SEO metadata
    print("  Generating SEO metadata...")
    seo_raw = ollama_generate(
        f"Blog post:\n\n{blog_content[:2000]}",
        system=SEO_PROMPT,
        temperature=0.3,
    )

    # Parse SEO JSON
    seo = {}
    try:
        # Find JSON in response
        json_match = re.search(r"\{[\s\S]*\}", seo_raw)
        if json_match:
            seo = json.loads(json_match.group())
    except json.JSONDecodeError:
        print("  WARNING: Could not parse SEO metadata, using defaults")

    title = seo.get("title", journal_path.stem.replace("-", " ").title())
    slug = slugify(title)
    headlines = seo.get("headlines", [title])
    tags = seo.get("tags", ["building"])
    reading_time = seo.get("reading_time", f"{max(3, len(blog_content.split()) // 250)} min")
    description = seo.get("description", blog_content[:155])
    keywords = seo.get("keywords", [])

    # Build output markdown
    output = f"""---
title: "{title}"
date: {date}
slug: {slug}
tags: {json.dumps(tags)}
reading_time: "{reading_time}"
description: "{description}"
keywords: {json.dumps(keywords)}
headlines:
  - "{headlines[0] if len(headlines) > 0 else title}"
  - "{headlines[1] if len(headlines) > 1 else ''}"
  - "{headlines[2] if len(headlines) > 2 else ''}"
source: {journal_path.name}
generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

{blog_content}
"""

    # Save
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    output_filename = f"{date}-{slug}.md"
    output_path = BLOG_DIR / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"  Saved: {output_path}")
    print(f"  Headlines:")
    for i, h in enumerate(headlines[:3], 1):
        print(f"    {i}. {h}")

    # Update blog index
    update_blog_index(output_path, seo, blog_content)

    return output_path


def update_blog_index(post_path, seo, content):
    """Add or update the post in blog-index.json for the web frontend."""
    # Load existing index
    index = {"posts": []}
    if BLOG_INDEX.exists():
        try:
            with open(BLOG_INDEX, "r", encoding="utf-8") as f:
                index = json.load(f)
                if isinstance(index, list):
                    index = {"posts": index}
        except json.JSONDecodeError:
            pass

    frontmatter, body = parse_frontmatter(post_path.read_text(encoding="utf-8"))

    # Build excerpt from first paragraph
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    excerpt = paragraphs[0] if paragraphs else content[:200]
    body_paragraphs = paragraphs[1:] if len(paragraphs) > 1 else paragraphs

    post_entry = {
        "id": frontmatter.get("slug", post_path.stem),
        "title": frontmatter.get("title", post_path.stem),
        "date": frontmatter.get("date", ""),
        "readingTime": frontmatter.get("reading_time", "3 min"),
        "tags": json.loads(frontmatter.get("tags", '["building"]')),
        "excerpt": excerpt[:300],
        "body": body_paragraphs[:10],
    }

    # Replace if exists, otherwise append
    existing_ids = [p["id"] for p in index["posts"]]
    if post_entry["id"] in existing_ids:
        idx = existing_ids.index(post_entry["id"])
        index["posts"][idx] = post_entry
    else:
        index["posts"].append(post_entry)

    # Sort reverse chronological
    index["posts"].sort(key=lambda p: p.get("date", ""), reverse=True)

    # Save
    BLOG_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"  Updated blog index: {BLOG_INDEX}")


def find_journals(date_filter=None):
    """Find journal entries matching a date or slug."""
    if not JOURNAL_DIR.exists():
        print(f"Journal directory not found: {JOURNAL_DIR}")
        return []

    entries = sorted(JOURNAL_DIR.glob("*.md"))

    if date_filter:
        entries = [e for e in entries if date_filter in e.stem]

    return entries


def list_journals():
    """List all available journal entries."""
    entries = find_journals()
    if not entries:
        print("No journal entries found.")
        return

    print(f"\nJournal entries in {JOURNAL_DIR}:\n")
    for entry in entries:
        frontmatter, body = read_journal(entry)
        word_count = len(body.split())
        date = frontmatter.get("date", "unknown")
        mood = frontmatter.get("mood", "")
        print(f"  {entry.name}")
        print(f"    Date: {date}  Mood: {mood}  Words: {word_count}")

    # Also list existing blog posts
    if BLOG_DIR.exists():
        blog_posts = sorted(BLOG_DIR.glob("*.md"))
        if blog_posts:
            print(f"\nExisting blog posts in {BLOG_DIR}:\n")
            for bp in blog_posts:
                print(f"  {bp.name}")


def process_week():
    """Process all journal entries from the past 7 days."""
    today = datetime.now()
    entries = []

    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        found = find_journals(date)
        entries.extend(found)

    if not entries:
        print("No journal entries found in the past 7 days.")
        return

    print(f"Found {len(entries)} entries from the past week.")
    results = []
    for entry in entries:
        result = generate_blog_post(entry)
        if result:
            results.append(result)

    print(f"\nDone. Generated {len(results)} blog posts.")


def main():
    parser = argparse.ArgumentParser(
        description="Convert journal entries to blog posts using Ollama."
    )
    parser.add_argument(
        "--from-journal",
        metavar="DATE_OR_SLUG",
        help="Process journal entry matching this date (YYYY-MM-DD) or filename slug",
    )
    parser.add_argument(
        "--week",
        action="store_true",
        help="Process all journal entries from the past 7 days",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available journal entries",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Ollama model to use (default: {OLLAMA_MODEL})",
    )

    args = parser.parse_args()

    if args.model:
        global OLLAMA_MODEL
        OLLAMA_MODEL = args.model

    if args.list:
        list_journals()
    elif args.week:
        process_week()
    elif args.from_journal:
        entries = find_journals(args.from_journal)
        if not entries:
            print(f"No journal entries matching: {args.from_journal}")
            sys.exit(1)
        for entry in entries:
            generate_blog_post(entry)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
