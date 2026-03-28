#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Matrix Writer. Expert content generator powered by Matrix Disks.

Takes a knowledge disk + topic + format and generates content using Ollama,
with the disk providing genuine domain expertise instead of generic surface
knowledge. Loads the Voice Bible for style, performance insights for
optimization, and disk knowledge for depth.

Usage:
    python3 matrix_writer.py --disk ecommerce --topic "product research tips" --format script
    python3 matrix_writer.py --disk ecommerce --topic "supplier negotiation" --format caption
    python3 matrix_writer.py --disk ai-news --topic "latest AI tools" --format carousel
    python3 matrix_writer.py --disk claude-code --topic "automating workflows" --format article
    python3 matrix_writer.py --disk ecommerce --topic "listing optimization" --format script --language es
    python3 matrix_writer.py --available                    # show available disks and formats
    python3 matrix_writer.py --help

Output formats:
  script    - Video script JSON (reel-pipeline compatible)
  caption   - Instagram caption text
  article   - Long-form article/thread
  carousel  - Carousel slide data JSON

Requires: Ollama running at localhost:11434
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
DISKS_DIR = PROJECT_DIR / "Ceiba" / "matrix-disks"
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
SCRIPTS_DIR = NEWS_DIR / "scripts"
VOICE_BIBLE = PROJECT_DIR / "Ceiba" / "VOICE_BIBLE.md"
ANALYTICS_FILE = NEWS_DIR / "analytics.json"
INSIGHTS_FILE = NEWS_DIR / "performance-insights.json"
OUTPUT_DIR = NEWS_DIR / "matrix-output"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

# --- Output format definitions ---
FORMATS = {
    "script": {
        "name": "Video Script",
        "description": "30-60s video script for Reels/TikTok/Shorts",
        "output_ext": ".json",
        "schema": {
            "title": "slug-format-title",
            "hook": "Opening line (first 3 seconds)",
            "narration": "Full narration text",
            "scenes": [
                {
                    "text": "Scene narration",
                    "image_prompt": "Visual description for AI image gen",
                    "overlay_text": "Short overlay (max 60 chars)",
                    "duration": 5,
                }
            ],
            "tags": ["relevant", "hashtags"],
            "category": "content-category",
            "cta": "Call to action",
        },
    },
    "caption": {
        "name": "Instagram Caption",
        "description": "Instagram post caption with hooks and hashtags",
        "output_ext": ".txt",
        "schema": {
            "hook": "First line that stops the scroll",
            "body": "Main caption body (3-5 short paragraphs)",
            "cta": "Call to action",
            "hashtags": "15-20 relevant hashtags",
        },
    },
    "article": {
        "name": "Long-Form Article",
        "description": "Blog post, newsletter, or Twitter/X thread",
        "output_ext": ".md",
        "schema": {
            "title": "Article title",
            "subtitle": "One-line subtitle",
            "sections": [
                {"heading": "Section heading", "content": "Section content"}
            ],
            "key_takeaway": "One sentence summary",
            "cta": "Call to action",
        },
    },
    "carousel": {
        "name": "Carousel Post",
        "description": "Multi-slide Instagram/LinkedIn carousel",
        "output_ext": ".json",
        "schema": {
            "title": "Carousel title",
            "slides": [
                {
                    "heading": "Slide heading",
                    "body": "Slide body text (2-3 sentences max)",
                    "slide_number": 1,
                }
            ],
            "caption": "Post caption",
            "hashtags": "Relevant hashtags",
        },
    },
}


# --- Helpers ---

def query_ollama(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
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
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        sys.exit(1)


def parse_json_response(raw: str) -> dict:
    """Extract JSON from an LLM response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start >= 0 and brace_end > brace_start:
        try:
            return json.loads(cleaned[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass
    return {}


def load_disk(name: str) -> dict:
    """Load a matrix disk."""
    disk_path = DISKS_DIR / f"{name}.json"
    if not disk_path.exists():
        return {}
    with open(disk_path) as f:
        return json.load(f)


def load_voice_bible() -> str:
    """Load the Voice Bible as style context."""
    if not VOICE_BIBLE.exists():
        return ""
    return VOICE_BIBLE.read_text(encoding="utf-8", errors="replace")


def load_performance_insights() -> str:
    """Load performance insights for optimization context."""
    if not INSIGHTS_FILE.exists():
        return ""
    try:
        with open(INSIGHTS_FILE) as f:
            data = json.load(f)
        # Summarize key insights
        lines = []
        if data.get("top_hook_styles"):
            hooks = data["top_hook_styles"]
            if isinstance(hooks, list) and hooks:
                lines.append(f"Best hook styles: {', '.join(str(h.get('style', h) if isinstance(h, dict) else h) for h in hooks[:3])}")
        if data.get("top_content_types"):
            types = data["top_content_types"]
            if isinstance(types, list) and types:
                lines.append(f"Best formats: {', '.join(str(t.get('type', t) if isinstance(t, dict) else t) for t in types[:3])}")
        if data.get("best_posting_times"):
            times = data["best_posting_times"]
            if isinstance(times, list) and times:
                lines.append(f"Best posting times: {', '.join(str(t) for t in times[:3])}")
        return "\n".join(lines)
    except Exception:
        return ""


def format_disk_context(disk: dict) -> str:
    """Format disk knowledge for the system prompt."""
    # Import the formatter from matrix_loader
    sys.path.insert(0, str(TOOLS_DIR))
    try:
        from matrix_loader import format_disk_as_prompt
        return format_disk_as_prompt(disk)
    except ImportError:
        # Fallback: manual formatting
        sections = [f"## Expert Knowledge: {disk.get('name', 'unknown').upper()}"]

        if disk.get("topics"):
            sections.append("\nKey Topics: " + ", ".join(disk["topics"][:15]))

        if disk.get("tips"):
            sections.append("\nExpert Tips:")
            for tip in disk["tips"][:10]:
                sections.append(f"- {tip}")

        if disk.get("mistakes"):
            sections.append("\nCommon Mistakes:")
            for m in disk["mistakes"][:8]:
                sections.append(f"- {m}")

        if disk.get("vocabulary"):
            sections.append("\nKey Terms:")
            for term, defn in list(disk["vocabulary"].items())[:10]:
                sections.append(f"- {term}: {defn}")

        perf = disk.get("performance", {})
        if perf.get("recommendations"):
            sections.append("\nPerformance Recommendations:")
            for r in perf["recommendations"][:5]:
                sections.append(f"- {r}")

        return "\n".join(sections)


# --- System prompt builder ---

def build_system_prompt(disk: dict, voice_bible: str, perf_insights: str, fmt: str) -> str:
    """Build the complete system prompt with all context layers."""
    format_info = FORMATS[fmt]

    parts = []

    # Layer 1: Core identity
    parts.append(f"""You are an expert content creator specializing in {disk.get('name', 'this topic')}.
You create {format_info['name']} content that demonstrates genuine expertise, not surface-level generic advice.
You have deep knowledge from studying real courses, transcripts, and case studies.""")

    # Layer 2: Voice Bible (trimmed to essentials)
    if voice_bible:
        # Extract key rules only
        voice_section = []
        in_rules = False
        for line in voice_bible.split("\n"):
            if "TONE RULES" in line or "BANNED WORDS" in line or "COPYWRITING RULES" in line:
                in_rules = True
            if in_rules:
                voice_section.append(line)
            if len(voice_section) > 60:
                break

        if voice_section:
            parts.append("\n## VOICE AND STYLE RULES\n" + "\n".join(voice_section))

    # Layer 3: Disk knowledge
    disk_context = format_disk_context(disk)
    if disk_context:
        parts.append(f"\n{disk_context}")

    # Layer 4: Performance optimization
    if perf_insights:
        parts.append(f"\n## PERFORMANCE OPTIMIZATION\n{perf_insights}")

    perf = disk.get("performance", {})
    if perf.get("recommendations"):
        parts.append("\nApply these performance-tested recommendations:")
        for rec in perf["recommendations"][:5]:
            parts.append(f"- {rec}")

    # Layer 5: Format rules
    parts.append(f"""
## OUTPUT RULES
- Return ONLY valid JSON matching the schema provided. No markdown fences. No explanation.
- No em dashes. Use periods or commas instead.
- No emojis in scripts or article text.
- Every sentence must earn its place. Cut filler.
- Use specific examples and numbers from your expert knowledge.
- Sound like a builder who has done this, not a guru who read about it.""")

    return "\n\n".join(parts)


def build_user_prompt(topic: str, fmt: str, language: str, disk: dict) -> str:
    """Build the user prompt for content generation."""
    format_info = FORMATS[fmt]
    lang_label = "Spanish (Latin American)" if language == "es" else "English"

    # Pull relevant tips for this specific topic
    relevant_tips = []
    topic_lower = topic.lower()
    for tip in disk.get("tips", []):
        tip_lower = tip.lower()
        # Check for word overlap
        topic_words = set(topic_lower.split())
        tip_words = set(tip_lower.split())
        if len(topic_words & tip_words) >= 1:
            relevant_tips.append(tip)

    tip_injection = ""
    if relevant_tips:
        tip_injection = "\n\nIncorporate these specific expert insights:\n" + "\n".join(f"- {t}" for t in relevant_tips[:5])

    schema_str = json.dumps(format_info["schema"], indent=2)

    prompt = f"""Create a {format_info['name']} about: "{topic}"

Language: {lang_label}
Format: {format_info['description']}
{tip_injection}

Use your expert knowledge to provide specific, actionable insights.
Reference real strategies, real numbers, real examples from your training.
Do NOT be generic. The audience can tell when content is surface-level.

Return a JSON object matching this schema:
{schema_str}"""

    return prompt


# --- Output handlers ---

def save_output(content: dict, raw: str, disk_name: str, topic: str, fmt: str, language: str):
    """Save generated content to disk in the appropriate format."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:40].strip("-")
    base_name = f"{disk_name}_{slug}_{timestamp}"

    format_info = FORMATS[fmt]
    ext = format_info["output_ext"]

    if fmt == "script":
        # Save as reel-pipeline compatible JSON
        output_path = OUTPUT_DIR / f"{base_name}{ext}"
        script_data = content if content else {"raw": raw}
        script_data["_matrix"] = {
            "disk": disk_name,
            "topic": topic,
            "format": fmt,
            "language": language,
            "generated": datetime.now().isoformat(),
        }
        with open(output_path, "w") as f:
            json.dump(script_data, f, indent=2, default=str)

        # Also save to scripts dir for script_writer compatibility
        SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        compat_path = SCRIPTS_DIR / f"matrix-{base_name}{ext}"
        with open(compat_path, "w") as f:
            json.dump(script_data, f, indent=2, default=str)

        print(f"  [+] Script: {output_path}")
        print(f"  [+] Compat: {compat_path}")

    elif fmt == "caption":
        output_path = OUTPUT_DIR / f"{base_name}.txt"
        if content:
            text_parts = []
            if content.get("hook"):
                text_parts.append(content["hook"])
            if content.get("body"):
                text_parts.append(f"\n{content['body']}")
            if content.get("cta"):
                text_parts.append(f"\n{content['cta']}")
            if content.get("hashtags"):
                text_parts.append(f"\n\n{content['hashtags']}")
            caption_text = "\n".join(text_parts)
        else:
            caption_text = raw

        with open(output_path, "w") as f:
            f.write(caption_text)
        print(f"  [+] Caption: {output_path}")

    elif fmt == "article":
        output_path = OUTPUT_DIR / f"{base_name}.md"
        if content:
            md_parts = []
            if content.get("title"):
                md_parts.append(f"# {content['title']}")
            if content.get("subtitle"):
                md_parts.append(f"*{content['subtitle']}*")
            for section in content.get("sections", []):
                if isinstance(section, dict):
                    md_parts.append(f"\n## {section.get('heading', '')}")
                    md_parts.append(section.get("content", ""))
            if content.get("key_takeaway"):
                md_parts.append(f"\n**Key takeaway:** {content['key_takeaway']}")
            if content.get("cta"):
                md_parts.append(f"\n{content['cta']}")
            article_text = "\n\n".join(md_parts)
        else:
            article_text = raw

        with open(output_path, "w") as f:
            f.write(article_text)
        print(f"  [+] Article: {output_path}")

    elif fmt == "carousel":
        output_path = OUTPUT_DIR / f"{base_name}{ext}"
        carousel_data = content if content else {"raw": raw}
        carousel_data["_matrix"] = {
            "disk": disk_name,
            "topic": topic,
            "format": fmt,
            "language": language,
            "generated": datetime.now().isoformat(),
        }
        with open(output_path, "w") as f:
            json.dump(carousel_data, f, indent=2, default=str)
        print(f"  [+] Carousel: {output_path}")

    return str(output_path)


# --- Main generate function ---

def generate(disk_name: str, topic: str, fmt: str, language: str = "en") -> str:
    """Generate expert content using a Matrix Disk. Returns path to output file."""
    # Load disk
    disk = load_disk(disk_name)
    if not disk:
        print(f"[ERROR] Disk '{disk_name}' not found at {DISKS_DIR}")
        available = [f.stem for f in DISKS_DIR.glob("*.json")] if DISKS_DIR.exists() else []
        if available:
            print(f"  Available disks: {', '.join(available)}")
        else:
            print("  No disks found. Build some with: python3 matrix_loader.py --build-presets")
        sys.exit(1)

    # Validate format
    if fmt not in FORMATS:
        print(f"[ERROR] Unknown format '{fmt}'. Available: {', '.join(FORMATS.keys())}")
        sys.exit(1)

    print(f"\n  MATRIX WRITER")
    print(f"  =============")
    print(f"  Disk: {disk_name} ({len(disk.get('topics', []))} topics, {len(disk.get('tips', []))} tips)")
    print(f"  Topic: {topic}")
    print(f"  Format: {FORMATS[fmt]['name']}")
    print(f"  Language: {'Spanish' if language == 'es' else 'English'}")

    # Load context layers
    print(f"\n  Loading context...")
    voice_bible = load_voice_bible()
    perf_insights = load_performance_insights()

    context_loaded = []
    if voice_bible:
        context_loaded.append("Voice Bible")
    if perf_insights:
        context_loaded.append("Performance Insights")
    context_loaded.append(f"Disk: {disk_name}")
    print(f"  Context: {', '.join(context_loaded)}")

    # Build prompts
    system_prompt = build_system_prompt(disk, voice_bible, perf_insights, fmt)
    user_prompt = build_user_prompt(topic, fmt, language, disk)

    # Generate
    print(f"\n  Generating {FORMATS[fmt]['name']}...")
    raw = query_ollama(system_prompt, user_prompt)

    if not raw:
        print("  [!] No response from Ollama")
        sys.exit(1)

    # Parse
    content = parse_json_response(raw)

    if not content:
        print("  [!] Could not parse JSON response. Saving raw output.")

    # Save
    output_path = save_output(content, raw, disk_name, topic, fmt, language)

    # Preview
    print(f"\n  --- Preview ---")
    if content:
        if fmt == "script":
            print(f"  Hook: {content.get('hook', 'N/A')}")
            scenes = content.get("scenes", [])
            print(f"  Scenes: {len(scenes)}")
            if scenes and isinstance(scenes[0], dict):
                print(f"  First scene: {scenes[0].get('text', '')[:100]}")

        elif fmt == "caption":
            print(f"  Hook: {content.get('hook', 'N/A')}")
            body = content.get("body", "")
            print(f"  Body: {body[:150]}...")

        elif fmt == "article":
            print(f"  Title: {content.get('title', 'N/A')}")
            sections = content.get("sections", [])
            print(f"  Sections: {len(sections)}")

        elif fmt == "carousel":
            print(f"  Title: {content.get('title', 'N/A')}")
            slides = content.get("slides", [])
            print(f"  Slides: {len(slides)}")
    else:
        print(f"  Raw output (first 200 chars): {raw[:200]}")

    print(f"\n  Done. Output: {output_path}")
    return output_path


def cmd_available(args):
    """Show available disks and formats."""
    print(f"\n  MATRIX WRITER - AVAILABLE RESOURCES")
    print(f"  ====================================")

    # Disks
    print(f"\n  Disks:")
    DISKS_DIR.mkdir(parents=True, exist_ok=True)
    disk_files = sorted(DISKS_DIR.glob("*.json"))
    if disk_files:
        for f in disk_files:
            try:
                with open(f) as fh:
                    data = json.load(fh)
                    topics = len(data.get("topics", []))
                    tips = len(data.get("tips", []))
                    print(f"    {f.stem:20s}  {topics:3d} topics, {tips:3d} tips")
            except Exception:
                print(f"    {f.stem:20s}  [error reading]")
    else:
        print("    None found. Run: python3 matrix_loader.py --build-presets")

    # Formats
    print(f"\n  Formats:")
    for key, info in FORMATS.items():
        print(f"    {key:12s}  {info['description']}")

    # Context
    print(f"\n  Context layers:")
    print(f"    Voice Bible:  {'found' if VOICE_BIBLE.exists() else 'NOT FOUND'}")
    print(f"    Performance:  {'found' if INSIGHTS_FILE.exists() else 'no data yet'}")
    print(f"    Analytics:    {'found' if ANALYTICS_FILE.exists() else 'no data yet'}")

    print(f"\n  Usage:")
    print(f"    python3 matrix_writer.py --disk DISK --topic 'your topic' --format FORMAT")


# --- Integration function for auto_content_engine ---

def matrix_generate(disk_name: str, topic: str, fmt: str, language: str = "en") -> str:
    """
    Public API for other tools to call matrix_writer.
    Returns the path to the generated output file, or empty string on failure.

    This function can be imported by auto_content_engine.py:
        from matrix_writer import matrix_generate
        output = matrix_generate("ecommerce", "product research", "script")
    """
    try:
        return generate(disk_name, topic, fmt, language)
    except SystemExit:
        return ""
    except Exception as e:
        print(f"[matrix_writer] Error: {e}")
        return ""


def has_disk(name: str) -> bool:
    """Check if a disk exists. Used by auto_content_engine to decide routing."""
    return (DISKS_DIR / f"{name}.json").exists()


def best_disk_for_topic(topic: str) -> str:
    """
    Find the best matching disk for a given topic.
    Returns disk name or empty string if no match.

    Used by auto_content_engine.py to auto-route:
        from matrix_writer import best_disk_for_topic
        disk = best_disk_for_topic("ebay listing tips")
        if disk:
            matrix_generate(disk, topic, "script")
    """
    DISKS_DIR.mkdir(parents=True, exist_ok=True)
    topic_lower = topic.lower()
    best_match = ""
    best_score = 0

    for disk_file in DISKS_DIR.glob("*.json"):
        try:
            with open(disk_file) as f:
                disk = json.load(f)

            score = 0
            disk_name = disk.get("name", disk_file.stem).lower()

            # Check name match
            if disk_name in topic_lower:
                score += 10

            # Check topic overlap
            for dt in disk.get("topics", []):
                dt_lower = dt.lower()
                topic_words = set(topic_lower.split())
                dt_words = set(dt_lower.split())
                overlap = len(topic_words & dt_words)
                if overlap >= 2:
                    score += 5
                elif overlap >= 1:
                    score += 1

            # Check vocabulary match
            for term in disk.get("vocabulary", {}).keys():
                if term.lower() in topic_lower:
                    score += 3

            if score > best_score:
                best_score = score
                best_match = disk.get("name", disk_file.stem)

        except Exception:
            continue

    return best_match if best_score >= 3 else ""


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Matrix Writer. Generate expert content powered by Matrix Disks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 matrix_writer.py --disk ecommerce --topic "product research tips" --format script
  python3 matrix_writer.py --disk ai-news --topic "latest AI developments" --format carousel
  python3 matrix_writer.py --disk claude-code --topic "automating file organization" --format article
  python3 matrix_writer.py --available
""",
    )

    parser.add_argument("--disk", help="Matrix disk to load as expert context")
    parser.add_argument("--topic", help="Content topic")
    parser.add_argument("--format", choices=list(FORMATS.keys()), help="Output format")
    parser.add_argument("--language", choices=["en", "es"], default="en", help="Content language (default: en)")
    parser.add_argument("--available", action="store_true", help="Show available disks and formats")

    args = parser.parse_args()

    if args.available:
        cmd_available(args)
        return

    if not args.disk or not args.topic or not args.format:
        parser.print_help()
        print("\n[ERROR] --disk, --topic, and --format are all required.")
        sys.exit(1)

    generate(args.disk, args.topic, args.format, args.language)


if __name__ == "__main__":
    main()
