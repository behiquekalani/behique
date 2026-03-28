#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Matrix Disk Loader. Compiles knowledge from transcripts and web data into
structured "disks" that content generation tools can load as expert context.

Like loading skills in The Matrix ("I know kung fu"), this system turns raw
transcripts into compressed, structured expertise any tool can consume.

Usage:
    python3 matrix_loader.py --create ecommerce --source ~/behique/gym/transcripts/04-business-and-money/ecommerce
    python3 matrix_loader.py --create claude-code --source ~/behique/gym/transcripts/02-ai-and-machine-learning/claude-code-automating-daily-tasks
    python3 matrix_loader.py --load ecommerce
    python3 matrix_loader.py --list
    python3 matrix_loader.py --stats ecommerce
    python3 matrix_loader.py --enhance ecommerce --query "ebay dropshipping 2026 strategies"
    python3 matrix_loader.py --learn ecommerce
    python3 matrix_loader.py --build-presets
    python3 matrix_loader.py --help

Disk storage: Ceiba/matrix-disks/{name}.json
Requires: Ollama running at localhost:11434
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from collections import Counter
from datetime import datetime
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
DISKS_DIR = PROJECT_DIR / "Ceiba" / "matrix-disks"
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
ANALYTICS_FILE = NEWS_DIR / "analytics.json"
INSIGHTS_FILE = NEWS_DIR / "performance-insights.json"
GYM_DIR = PROJECT_DIR / "gym" / "transcripts"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

# Maximum characters to send per Ollama batch (model context window safety)
BATCH_CHAR_LIMIT = 12000

# --- Preset disk definitions ---
PRESETS = {
    "ecommerce": {
        "source": str(GYM_DIR / "04-business-and-money" / "ecommerce"),
        "description": "eBay dropshipping, Amazon FBA, product research, listing optimization, supplier management",
    },
    "gaming": {
        "source": str(GYM_DIR / "06-lifestyle" / "gaming"),
        "description": "Gaming content, Roblox development, cloth simulation, game design",
    },
    "claude-code": {
        "source": str(GYM_DIR / "02-ai-and-machine-learning" / "claude-code-automating-daily-tasks"),
        "description": "Claude Code automation, file management, report generation, web apps, invoice processing",
    },
    "ai-news": {
        "source": "_special:ai-news",
        "description": "AI industry trends, product launches, company moves compiled from news feed",
    },
}


# --- Ollama helpers ---

def query_ollama(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Send a prompt to Ollama and return the response text."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 4096,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
            return result.get("message", {}).get("content", "")
    except urllib.error.URLError as e:
        print(f"[ERROR] Cannot connect to Ollama at {OLLAMA_URL}")
        print(f"  Make sure Ollama is running: ollama serve")
        print(f"  Error: {e}")
        return ""
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        return ""


def parse_json_response(raw: str) -> dict:
    """Extract JSON from an LLM response, handling markdown fences."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    # Try to find a JSON object
    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start >= 0 and brace_end > brace_start:
        try:
            return json.loads(cleaned[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    # Try to find a JSON array
    bracket_start = cleaned.find("[")
    bracket_end = cleaned.rfind("]")
    if bracket_start >= 0 and bracket_end > bracket_start:
        try:
            return {"items": json.loads(cleaned[bracket_start:bracket_end + 1])}
        except json.JSONDecodeError:
            pass

    return {}


# --- Transcript scanning ---

def scan_transcripts(source_dir: str) -> list:
    """Scan a directory for .md transcript files and return their contents."""
    source_path = Path(source_dir).expanduser()
    if not source_path.exists():
        print(f"[ERROR] Source directory not found: {source_dir}")
        return []

    transcripts = []
    md_files = sorted(source_path.rglob("*.md"))

    for md_file in md_files:
        # Skip README files
        if md_file.name.lower() == "readme.md":
            continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            # Extract frontmatter title if present
            title = md_file.stem
            title_match = re.search(r'^title:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)

            # Extract category from frontmatter
            category = ""
            cat_match = re.search(r'^category:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
            if cat_match:
                category = cat_match.group(1)

            # Strip frontmatter for content extraction
            body = re.sub(r"^---\n.*?\n---\n", "", content, count=1, flags=re.DOTALL)

            transcripts.append({
                "file": str(md_file),
                "title": title,
                "category": category,
                "content": body.strip(),
                "chars": len(body),
            })
        except Exception as e:
            print(f"  [!] Could not read {md_file}: {e}")

    return transcripts


def batch_transcripts(transcripts: list, char_limit: int = BATCH_CHAR_LIMIT) -> list:
    """Split transcripts into batches that fit within the char limit."""
    batches = []
    current_batch = []
    current_chars = 0

    for t in transcripts:
        # Truncate very long transcripts
        content = t["content"][:char_limit]
        chars = len(content)

        if current_chars + chars > char_limit and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_chars = 0

        current_batch.append({**t, "content": content})
        current_chars += chars

    if current_batch:
        batches.append(current_batch)

    return batches


# --- Disk structure ---

def empty_disk(name: str, source: str, description: str = "") -> dict:
    """Create an empty disk structure."""
    return {
        "name": name,
        "version": 1,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "source": source,
        "description": description,
        "transcript_count": 0,
        "topics": [],
        "frameworks": [],
        "vocabulary": {},
        "tips": [],
        "mistakes": [],
        "examples": [],
        "web_intel": [],
        "performance": {
            "top_topics": [],
            "top_hooks": [],
            "top_formats": [],
            "recommendations": [],
        },
    }


def load_disk(name: str) -> dict:
    """Load a disk from storage."""
    disk_path = DISKS_DIR / f"{name}.json"
    if not disk_path.exists():
        return {}
    with open(disk_path) as f:
        return json.load(f)


def save_disk(disk: dict):
    """Save a disk to storage."""
    DISKS_DIR.mkdir(parents=True, exist_ok=True)
    disk["updated"] = datetime.now().isoformat()
    disk_path = DISKS_DIR / f"{disk['name']}.json"
    with open(disk_path, "w") as f:
        json.dump(disk, f, indent=2, default=str)
    print(f"  [+] Disk saved: {disk_path}")


def list_disks() -> list:
    """List all available disks."""
    DISKS_DIR.mkdir(parents=True, exist_ok=True)
    disks = []
    for f in sorted(DISKS_DIR.glob("*.json")):
        try:
            with open(f) as fh:
                data = json.load(fh)
                disks.append({
                    "name": data.get("name", f.stem),
                    "file": str(f),
                    "topics": len(data.get("topics", [])),
                    "frameworks": len(data.get("frameworks", [])),
                    "tips": len(data.get("tips", [])),
                    "mistakes": len(data.get("mistakes", [])),
                    "examples": len(data.get("examples", [])),
                    "vocab": len(data.get("vocabulary", {})),
                    "web_intel": len(data.get("web_intel", [])),
                    "transcripts": data.get("transcript_count", 0),
                    "updated": data.get("updated", "unknown"),
                })
        except Exception:
            disks.append({"name": f.stem, "file": str(f), "error": True})
    return disks


# --- Extraction via Ollama ---

EXTRACTION_SYSTEM = """You are a knowledge extractor. Given transcript content, extract structured knowledge.
Return ONLY valid JSON. No markdown fences. No explanation.
Be specific and actionable. Pull real numbers, real strategies, real examples from the text.
Do not invent information. Only extract what is actually present."""

EXTRACTION_PROMPT = """Analyze these transcript excerpts and extract knowledge into this JSON structure:

{{
  "topics": ["list of specific topics covered"],
  "frameworks": ["named frameworks, systems, or step-by-step processes mentioned"],
  "vocabulary": {{"term": "definition from context"}},
  "tips": ["specific, actionable tips mentioned"],
  "mistakes": ["common mistakes or warnings mentioned"],
  "examples": ["concrete examples, case studies, or real scenarios described"]
}}

Transcripts:
{transcripts}

Extract everything useful. Be specific, not generic."""


def extract_from_batch(batch: list) -> dict:
    """Use Ollama to extract structured knowledge from a batch of transcripts."""
    # Format transcripts for the prompt
    formatted = []
    for t in batch:
        # Take first portion to stay within limits
        excerpt = t["content"][:3000]
        formatted.append(f"### {t['title']}\n{excerpt}")

    combined = "\n\n".join(formatted)
    prompt = EXTRACTION_PROMPT.format(transcripts=combined)

    raw = query_ollama(EXTRACTION_SYSTEM, prompt)
    if not raw:
        return {}

    return parse_json_response(raw)


def _safe_str(item):
    """Convert any item to string safely."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("name", item.get("title", str(item))))
    return str(item)


def merge_extractions(disk: dict, extraction: dict):
    """Merge an extraction result into the disk, deduplicating."""
    # Topics
    existing_topics = set(_safe_str(t).lower() for t in disk["topics"])
    for topic in extraction.get("topics", []):
        t = _safe_str(topic)
        if t.lower() not in existing_topics:
            disk["topics"].append(t)
            existing_topics.add(t.lower())

    # Frameworks
    existing_fw = set(_safe_str(f).lower() for f in disk["frameworks"])
    for fw in extraction.get("frameworks", []):
        f = _safe_str(fw)
        if f.lower() not in existing_fw:
            disk["frameworks"].append(f)
            existing_fw.add(f.lower())

    # Vocabulary
    vocab = extraction.get("vocabulary", {})
    if isinstance(vocab, dict):
        for term, definition in vocab.items():
            if str(term) not in disk["vocabulary"]:
                disk["vocabulary"][str(term)] = _safe_str(definition)
    elif isinstance(vocab, list):
        for item in vocab:
            t = _safe_str(item)
            if t not in disk["vocabulary"]:
                disk["vocabulary"][t] = ""

    # Tips
    existing_tips = set(_safe_str(t).lower()[:80] for t in disk["tips"])
    for tip in extraction.get("tips", []):
        t = _safe_str(tip)
        if t.lower()[:80] not in existing_tips:
            disk["tips"].append(t)
            existing_tips.add(t.lower()[:80])

    # Mistakes
    existing_mistakes = set(_safe_str(m).lower()[:80] for m in disk["mistakes"])
    for mistake in extraction.get("mistakes", []):
        m = _safe_str(mistake)
        if m.lower()[:80] not in existing_mistakes:
            disk["mistakes"].append(m)
            existing_mistakes.add(m.lower()[:80])

    # Examples
    existing_examples = set(_safe_str(e).lower()[:80] for e in disk["examples"])
    for example in extraction.get("examples", []):
        e = _safe_str(example)
        if e.lower()[:80] not in existing_examples:
            disk["examples"].append(e)
            existing_examples.add(e.lower()[:80])


# --- AI News special source ---

def extract_from_news() -> dict:
    """Extract knowledge from the AI news articles.json file."""
    articles_file = NEWS_DIR / "articles.json"
    if not articles_file.exists():
        print("[!] No articles.json found at Ceiba/news/articles.json")
        return empty_disk("ai-news", "_special:ai-news", PRESETS["ai-news"]["description"])

    with open(articles_file) as f:
        articles = json.load(f)

    disk = empty_disk("ai-news", "_special:ai-news", PRESETS["ai-news"]["description"])
    disk["transcript_count"] = len(articles)

    # Extract topics, companies, and patterns directly from article metadata
    topics = []
    companies = Counter()
    categories = Counter()
    high_impact = []

    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        impact = article.get("impact", "LOW")
        mentions = article.get("mentions", [])
        category = article.get("category", "")

        topics.append(title)
        categories[category] += 1

        for mention in mentions:
            companies[mention] += 1

        if impact in ("HIGH", "CRITICAL"):
            high_impact.append({
                "title": title,
                "summary": summary[:200],
                "impact": impact,
                "source": article.get("source", ""),
            })

    # Build disk from extracted data
    disk["topics"] = topics[:50]
    disk["vocabulary"] = {company: f"Mentioned {count} times in AI news" for company, count in companies.most_common(20)}
    disk["examples"] = [f"{item['title']}: {item['summary']}" for item in high_impact[:20]]
    disk["frameworks"] = [f"Category: {cat} ({count} articles)" for cat, count in categories.most_common()]

    # Use Ollama to find patterns if available
    if articles:
        titles_text = "\n".join(a.get("title", "") for a in articles[:40])
        pattern_prompt = f"""Analyze these AI news headlines and extract:
1. Recurring themes and trends
2. Actionable tips for content creators covering AI
3. Common mistakes in AI reporting to avoid

Headlines:
{titles_text}

Return JSON: {{"tips": [...], "mistakes": [...], "frameworks": [...]}}"""

        raw = query_ollama(EXTRACTION_SYSTEM, pattern_prompt)
        if raw:
            patterns = parse_json_response(raw)
            merge_extractions(disk, patterns)

    return disk


# --- Commands ---

def cmd_create(args):
    """Create a new knowledge disk from transcripts."""
    name = args.create
    source = args.source

    if not source:
        # Check presets
        if name in PRESETS:
            source = PRESETS[name]["source"]
        else:
            print(f"[ERROR] No --source provided and '{name}' is not a preset.")
            print(f"  Presets: {', '.join(PRESETS.keys())}")
            sys.exit(1)

    print(f"\n  MATRIX DISK COMPILER")
    print(f"  ====================")
    print(f"  Disk: {name}")
    print(f"  Source: {source}")

    # Special case for ai-news
    if source == "_special:ai-news":
        disk = extract_from_news()
        save_disk(disk)
        print(f"\n  Compiled {disk['transcript_count']} articles into {name}.json")
        _print_disk_summary(disk)
        return

    # Scan transcripts
    print(f"\n  Scanning transcripts...")
    transcripts = scan_transcripts(source)

    if not transcripts:
        print(f"  [!] No transcripts found in {source}")
        sys.exit(1)

    print(f"  Found {len(transcripts)} transcripts ({sum(t['chars'] for t in transcripts):,} chars total)")

    # Create or load existing disk
    description = PRESETS.get(name, {}).get("description", f"Knowledge disk from {source}")
    disk = empty_disk(name, source, description)
    disk["transcript_count"] = len(transcripts)

    # Batch and extract
    batches = batch_transcripts(transcripts)
    print(f"  Processing in {len(batches)} batches...\n")

    for i, batch in enumerate(batches, 1):
        batch_titles = [t["title"] for t in batch]
        print(f"  Batch {i}/{len(batches)}: {len(batch)} transcripts")
        for title in batch_titles[:3]:
            print(f"    - {title}")
        if len(batch_titles) > 3:
            print(f"    ... and {len(batch_titles) - 3} more")

        extraction = extract_from_batch(batch)
        if extraction:
            merge_extractions(disk, extraction)
            print(f"    Extracted: {len(extraction.get('topics', []))} topics, "
                  f"{len(extraction.get('tips', []))} tips, "
                  f"{len(extraction.get('vocabulary', {}))} terms")
        else:
            print(f"    [!] Extraction failed for this batch (Ollama may be offline)")

    # Save
    save_disk(disk)
    print(f"\n  Compilation complete.")
    _print_disk_summary(disk)


def cmd_load(args):
    """Load a disk and output it as a system prompt addition."""
    name = args.load
    disk = load_disk(name)

    if not disk:
        print(f"[ERROR] Disk '{name}' not found.")
        print(f"  Available: {', '.join(d['name'] for d in list_disks())}")
        sys.exit(1)

    prompt = format_disk_as_prompt(disk)
    print(prompt)


def format_disk_as_prompt(disk: dict) -> str:
    """Format a disk's knowledge as a system prompt injection."""
    sections = []

    sections.append(f"## Expert Knowledge: {disk['name'].upper()}")
    if disk.get("description"):
        sections.append(f"Domain: {disk['description']}")

    if disk.get("topics"):
        sections.append("\n### Key Topics")
        for topic in disk["topics"][:25]:
            sections.append(f"- {topic}")

    if disk.get("frameworks"):
        sections.append("\n### Frameworks and Systems")
        for fw in disk["frameworks"][:15]:
            sections.append(f"- {fw}")

    if disk.get("vocabulary"):
        sections.append("\n### Industry Vocabulary")
        for term, definition in list(disk["vocabulary"].items())[:20]:
            sections.append(f"- **{term}**: {definition}")

    if disk.get("tips"):
        sections.append("\n### Expert Tips (use these in content)")
        for tip in disk["tips"][:20]:
            sections.append(f"- {tip}")

    if disk.get("mistakes"):
        sections.append("\n### Common Mistakes (warn viewers about these)")
        for mistake in disk["mistakes"][:15]:
            sections.append(f"- {mistake}")

    if disk.get("examples"):
        sections.append("\n### Real Examples and Case Studies")
        for example in disk["examples"][:10]:
            sections.append(f"- {example}")

    if disk.get("web_intel"):
        sections.append("\n### Web Intelligence (current data)")
        for intel in disk["web_intel"][:10]:
            if isinstance(intel, dict):
                sections.append(f"- [{intel.get('source', 'web')}] {intel.get('insight', str(intel))}")
            else:
                sections.append(f"- {intel}")

    # Performance recommendations
    perf = disk.get("performance", {})
    recs = perf.get("recommendations", [])
    if recs:
        sections.append("\n### Performance-Optimized Recommendations")
        for rec in recs[:10]:
            sections.append(f"- {rec}")

    top_topics = perf.get("top_topics", [])
    if top_topics:
        sections.append("\n### Top-Performing Topics (prioritize these)")
        for t in top_topics[:5]:
            if isinstance(t, dict):
                sections.append(f"- {t.get('topic', str(t))} (engagement: {t.get('engagement', 'N/A')})")
            else:
                sections.append(f"- {t}")

    return "\n".join(sections)


def cmd_list(args):
    """List all available disks."""
    disks = list_disks()

    if not disks:
        print("\n  No disks found. Create one with:")
        print("    python3 matrix_loader.py --create DISK_NAME --source /path/to/transcripts/")
        print(f"\n  Or build presets: python3 matrix_loader.py --build-presets")
        return

    print(f"\n  MATRIX DISKS ({len(disks)} available)")
    print(f"  {'='*55}")

    for d in disks:
        if d.get("error"):
            print(f"  {d['name']:20s}  [ERROR reading disk]")
            continue

        print(f"  {d['name']:20s}  {d['topics']:3d} topics | {d['tips']:3d} tips | "
              f"{d['vocab']:3d} vocab | {d['transcripts']:3d} sources | "
              f"updated {d['updated'][:10]}")

    print(f"\n  Load with: python3 matrix_loader.py --load DISK_NAME")


def cmd_stats(args):
    """Show detailed stats for a disk."""
    name = args.stats
    disk = load_disk(name)

    if not disk:
        print(f"[ERROR] Disk '{name}' not found.")
        sys.exit(1)

    _print_disk_summary(disk)


def _print_disk_summary(disk: dict):
    """Print a formatted summary of a disk."""
    print(f"\n  DISK: {disk['name']}")
    print(f"  {'='*45}")
    print(f"  Description: {disk.get('description', 'N/A')}")
    print(f"  Source: {disk.get('source', 'N/A')}")
    print(f"  Transcripts: {disk.get('transcript_count', 0)}")
    print(f"  Created: {disk.get('created', 'N/A')[:19]}")
    print(f"  Updated: {disk.get('updated', 'N/A')[:19]}")
    print(f"  Version: {disk.get('version', 1)}")

    print(f"\n  Contents:")
    print(f"    Topics:      {len(disk.get('topics', []))}")
    print(f"    Frameworks:  {len(disk.get('frameworks', []))}")
    print(f"    Vocabulary:  {len(disk.get('vocabulary', {}))}")
    print(f"    Tips:        {len(disk.get('tips', []))}")
    print(f"    Mistakes:    {len(disk.get('mistakes', []))}")
    print(f"    Examples:    {len(disk.get('examples', []))}")
    print(f"    Web Intel:   {len(disk.get('web_intel', []))}")

    perf = disk.get("performance", {})
    if perf.get("recommendations"):
        print(f"    Perf Recs:   {len(perf['recommendations'])}")

    # Show sample content
    if disk.get("topics"):
        print(f"\n  Sample Topics:")
        for t in disk["topics"][:5]:
            print(f"    - {t}")

    if disk.get("tips"):
        print(f"\n  Sample Tips:")
        for t in disk["tips"][:3]:
            print(f"    - {t}")


def cmd_enhance(args):
    """Enhance a disk with web-scraped knowledge."""
    name = args.enhance
    query = args.query

    if not query:
        print("[ERROR] --query is required with --enhance")
        sys.exit(1)

    disk = load_disk(name)
    if not disk:
        print(f"[ERROR] Disk '{name}' not found.")
        sys.exit(1)

    print(f"\n  ENHANCING DISK: {name}")
    print(f"  Query: {query}")

    # Save the search query for manual or automated enhancement
    enhancement = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "source": "manual_query",
        "status": "pending",
        "insight": "",
    }

    # Try to use Ollama to generate search-informed knowledge
    enhance_prompt = f"""You are an expert researcher. Given this search query, generate useful
knowledge that would help someone creating content about this topic.

Search query: "{query}"
Existing disk topics: {json.dumps(disk.get('topics', [])[:10])}

Generate practical, specific knowledge in this JSON format:
{{
  "tips": ["actionable tips based on current best practices"],
  "vocabulary": {{"term": "definition"}},
  "frameworks": ["relevant frameworks or strategies"],
  "examples": ["real-world examples or case studies"]
}}

Be specific and current. No generic advice."""

    print("  Querying Ollama for knowledge synthesis...")
    raw = query_ollama(EXTRACTION_SYSTEM, enhance_prompt, temperature=0.5)

    if raw:
        result = parse_json_response(raw)
        if result:
            merge_extractions(disk, result)
            enhancement["status"] = "completed"
            enhancement["insight"] = f"Added {len(result.get('tips', []))} tips, {len(result.get('vocabulary', {}))} terms"
            print(f"  [+] Enhanced with: {enhancement['insight']}")
        else:
            enhancement["status"] = "parse_failed"
            print("  [!] Could not parse Ollama response")
    else:
        enhancement["status"] = "ollama_offline"
        print("  [!] Ollama offline. Query saved for later.")

    disk["web_intel"].append(enhancement)
    disk["version"] = disk.get("version", 1) + 1
    save_disk(disk)


def cmd_learn(args):
    """Learn from performance data to improve disk recommendations."""
    name = args.learn
    disk = load_disk(name)

    if not disk:
        print(f"[ERROR] Disk '{name}' not found.")
        sys.exit(1)

    print(f"\n  LEARNING FROM PERFORMANCE: {name}")

    # Load analytics data
    if not ANALYTICS_FILE.exists():
        print("  [!] No analytics data found. Log some posts first with performance_tracker.py")
        print("  Saving placeholder for future learning.")
        disk["performance"]["last_learn"] = datetime.now().isoformat()
        save_disk(disk)
        return

    with open(ANALYTICS_FILE) as f:
        analytics = json.load(f)

    posts = analytics.get("posts", [])
    if not posts:
        print("  [!] No posts in analytics data yet.")
        return

    # Also load insights if available
    insights = {}
    if INSIGHTS_FILE.exists():
        with open(INSIGHTS_FILE) as f:
            insights = json.load(f)

    # Analyze which topics related to this disk performed best
    disk_topics = set(t.lower() for t in disk.get("topics", []))
    disk_name_lower = name.lower()

    relevant_posts = []
    for post in posts:
        post_topic = post.get("topic", "").lower()
        post_tags = [t.lower() for t in post.get("tags", [])]
        content_category = post.get("category", "").lower()

        # Check if this post is relevant to the disk
        is_relevant = False
        if disk_name_lower in post_topic or disk_name_lower in content_category:
            is_relevant = True
        for dt in disk_topics:
            if dt in post_topic or any(dt in tag for tag in post_tags):
                is_relevant = True
                break

        if is_relevant:
            relevant_posts.append(post)

    print(f"  Found {len(relevant_posts)} relevant posts out of {len(posts)} total")

    if not relevant_posts:
        # Use general insights instead
        print("  No directly relevant posts found. Using general performance patterns.")

        if insights:
            general_recs = []
            top_hooks = insights.get("top_hook_styles", [])
            if top_hooks:
                general_recs.append(f"Best hook styles overall: {', '.join(h.get('style', str(h)) if isinstance(h, dict) else str(h) for h in top_hooks[:3])}")

            top_formats = insights.get("top_content_types", [])
            if top_formats:
                general_recs.append(f"Best content formats: {', '.join(f.get('type', str(f)) if isinstance(f, dict) else str(f) for f in top_formats[:3])}")

            disk["performance"]["recommendations"] = general_recs
            disk["performance"]["last_learn"] = datetime.now().isoformat()
            save_disk(disk)
            print(f"  [+] Applied {len(general_recs)} general recommendations")
        return

    # Sort by engagement
    relevant_posts.sort(key=lambda p: p.get("engagement_rate", 0), reverse=True)

    # Extract patterns from top performers
    top_posts = relevant_posts[:10]
    top_topics = []
    top_hooks = Counter()
    top_formats = Counter()

    for post in top_posts:
        topic = post.get("topic", "")
        hook = post.get("hook_style", "")
        fmt = post.get("content_type", "")
        engagement = post.get("engagement_rate", 0)

        if topic:
            top_topics.append({"topic": topic, "engagement": engagement})
        if hook:
            top_hooks[hook] += 1
        if fmt:
            top_formats[fmt] += 1

    # Build recommendations
    recommendations = []

    if top_topics:
        best_topic = top_topics[0]
        recommendations.append(f"Highest engagement topic: '{best_topic['topic']}' ({best_topic['engagement']}% engagement)")

    for hook, count in top_hooks.most_common(3):
        recommendations.append(f"High-performing hook style: {hook} (used in {count} top posts)")

    for fmt, count in top_formats.most_common(3):
        recommendations.append(f"Best content format: {fmt} (used in {count} top posts)")

    # Synthesize with Ollama
    if top_topics:
        learn_prompt = f"""Analyze these performance results for {name} content and give actionable recommendations:

Top performing topics: {json.dumps(top_topics[:5])}
Best hook styles: {json.dumps(dict(top_hooks.most_common(5)))}
Best formats: {json.dumps(dict(top_formats.most_common(5)))}

Give 5 specific recommendations for improving future {name} content.
Return JSON: {{"recommendations": ["rec1", "rec2", ...]}}"""

        raw = query_ollama(EXTRACTION_SYSTEM, learn_prompt)
        if raw:
            result = parse_json_response(raw)
            llm_recs = result.get("recommendations", [])
            recommendations.extend(llm_recs)

    # Update disk
    disk["performance"]["top_topics"] = top_topics[:10]
    disk["performance"]["top_hooks"] = [{"style": h, "count": c} for h, c in top_hooks.most_common(5)]
    disk["performance"]["top_formats"] = [{"type": f, "count": c} for f, c in top_formats.most_common(5)]
    disk["performance"]["recommendations"] = recommendations
    disk["performance"]["last_learn"] = datetime.now().isoformat()
    disk["performance"]["posts_analyzed"] = len(relevant_posts)
    disk["version"] = disk.get("version", 1) + 1

    save_disk(disk)
    print(f"  [+] Applied {len(recommendations)} performance recommendations")

    for rec in recommendations[:5]:
        print(f"    - {rec}")


def cmd_build_presets(args):
    """Build all preset disks."""
    print(f"\n  BUILDING PRESET DISKS")
    print(f"  =====================")
    print(f"  Presets: {', '.join(PRESETS.keys())}\n")

    for name, config in PRESETS.items():
        print(f"\n  --- Building: {name} ---")

        # Check if source exists
        source = config["source"]
        if source != "_special:ai-news" and not Path(source).exists():
            print(f"  [!] Source not found: {source}. Skipping.")
            continue

        # Build args namespace
        build_args = argparse.Namespace(
            create=name,
            source=source,
        )
        try:
            cmd_create(build_args)
        except SystemExit:
            print(f"  [!] Failed to build {name}")
        except Exception as e:
            print(f"  [!] Error building {name}: {e}")

    print(f"\n  Preset build complete. Run --list to see results.")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Matrix Disk Loader. Compile knowledge into loadable disks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 matrix_loader.py --create ecommerce --source ~/behique/gym/transcripts/04-business-and-money/ecommerce
  python3 matrix_loader.py --load ecommerce
  python3 matrix_loader.py --list
  python3 matrix_loader.py --stats ecommerce
  python3 matrix_loader.py --enhance ecommerce --query "ebay dropshipping trends 2026"
  python3 matrix_loader.py --learn ecommerce
  python3 matrix_loader.py --build-presets
""",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", metavar="DISK_NAME", help="Create a new disk from transcripts")
    group.add_argument("--load", metavar="DISK_NAME", help="Load disk as system prompt context")
    group.add_argument("--list", action="store_true", help="List all available disks")
    group.add_argument("--stats", metavar="DISK_NAME", help="Show disk statistics")
    group.add_argument("--enhance", metavar="DISK_NAME", help="Enhance disk with web knowledge")
    group.add_argument("--learn", metavar="DISK_NAME", help="Learn from performance data")
    group.add_argument("--build-presets", action="store_true", help="Build all preset disks")

    parser.add_argument("--source", help="Source directory for transcript scanning")
    parser.add_argument("--query", help="Search query for --enhance mode")

    args = parser.parse_args()

    if args.create:
        cmd_create(args)
    elif args.load:
        cmd_load(args)
    elif args.list:
        cmd_list(args)
    elif args.stats:
        cmd_stats(args)
    elif args.enhance:
        cmd_enhance(args)
    elif args.learn:
        cmd_learn(args)
    elif args.build_presets:
        cmd_build_presets(args)


if __name__ == "__main__":
    main()
