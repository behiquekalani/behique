#!/usr/bin/env python3
"""
Content Repurposer - Takes one piece of content and converts it into 5+ platform formats.

Uses Ollama (localhost:11434) for intelligent repurposing with rule-based fallback.

Usage:
    python3 tools/repurposer.py --input path/to/post.md --output output/repurposed/
    python3 tools/repurposer.py --input path/to/post.md --platform twitter
    python3 tools/repurposer.py --input path/to/post.md --dry-run
"""

import argparse
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # change if you have a different model loaded

PLATFORMS = [
    "twitter",
    "instagram",
    "tiktok",
    "linkedin",
    "pinterest",
    "newsletter",
    "youtube_shorts",
]

PLATFORM_HASHTAGS = {
    "twitter": ["#Thread", "#ContentCreator", "#ValueBomb"],
    "instagram": ["#ContentCreator", "#DigitalMarketing", "#Carousel", "#ValuePost", "#GrowthMindset"],
    "tiktok": ["#LearnOnTikTok", "#ContentTips", "#ValueDrop", "#FYP", "#Viral"],
    "linkedin": ["#ProfessionalDevelopment", "#Leadership", "#CareerGrowth", "#BusinessTips"],
    "pinterest": [],  # SEO keywords instead, added dynamically
    "newsletter": [],
    "youtube_shorts": ["#Shorts", "#QuickTips", "#LearnSomethingNew"],
}

# ---------------------------------------------------------------------------
# Ollama integration
# ---------------------------------------------------------------------------

def ollama_available() -> bool:
    """Check if Ollama is running."""
    try:
        if HAS_REQUESTS:
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            return r.status_code == 200
        else:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
    except Exception:
        return False


def ollama_generate(prompt: str, max_tokens: int = 2048) -> str | None:
    """Send a prompt to Ollama and return the response text."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.7},
    }
    try:
        if HAS_REQUESTS:
            r = requests.post(OLLAMA_URL, json=payload, timeout=120)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        else:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body.get("response", "").strip()
    except Exception as e:
        print(f"  [warn] Ollama request failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Content parsing helpers
# ---------------------------------------------------------------------------

def parse_markdown(text: str) -> dict:
    """Extract structured pieces from markdown content."""
    lines = text.strip().splitlines()

    title = ""
    paragraphs = []
    bullet_points = []
    current_para = []

    for line in lines:
        stripped = line.strip()
        # Title from first heading
        if not title and stripped.startswith("#"):
            title = re.sub(r"^#+\s*", "", stripped)
            continue
        # Bullet points
        if re.match(r"^[-*]\s+", stripped):
            bullet_points.append(re.sub(r"^[-*]\s+", "", stripped))
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
            continue
        # Numbered list items
        if re.match(r"^\d+[.)]\s+", stripped):
            bullet_points.append(re.sub(r"^\d+[.)]\s+", "", stripped))
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
            continue
        # Empty line ends paragraph
        if not stripped:
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
            continue
        # Skip images/links-only lines
        if stripped.startswith("!["):
            continue
        current_para.append(stripped)

    if current_para:
        paragraphs.append(" ".join(current_para))

    # Extract key sentences (first sentence of each paragraph)
    key_sentences = []
    for p in paragraphs:
        first_sent = re.split(r"(?<=[.!?])\s+", p)[0]
        if len(first_sent) > 20:
            key_sentences.append(first_sent)

    return {
        "title": title,
        "paragraphs": paragraphs,
        "bullet_points": bullet_points,
        "key_sentences": key_sentences,
        "full_text": text.strip(),
        "word_count": len(text.split()),
    }


def extract_keywords(parsed: dict, n: int = 8) -> list[str]:
    """Pull rough keywords from the content for SEO/hashtags."""
    text = parsed["full_text"].lower()
    # Remove markdown syntax
    text = re.sub(r"[#*_\[\]()>`~]", " ", text)
    words = re.findall(r"\b[a-z]{4,}\b", text)
    # Simple frequency count, skip common words
    stopwords = {
        "this", "that", "with", "from", "have", "will", "your", "they",
        "been", "were", "their", "about", "would", "could", "should",
        "into", "also", "just", "than", "then", "when", "what", "which",
        "more", "most", "some", "very", "much", "each", "every", "make",
        "like", "even", "because", "through", "after", "before", "being",
        "other", "over", "such", "only", "does", "doing", "done",
    }
    freq = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_kw = sorted(freq, key=freq.get, reverse=True)
    return sorted_kw[:n]


# ---------------------------------------------------------------------------
# Rule-based generators (fallback)
# ---------------------------------------------------------------------------

def rule_twitter(parsed: dict) -> str:
    """Generate a Twitter/X thread from parsed content."""
    title = parsed["title"] or "Key Insights"
    points = parsed["bullet_points"] or parsed["key_sentences"]
    hashtags = " ".join(PLATFORM_HASHTAGS["twitter"])

    tweets = []
    # Tweet 1: Hook
    hook = parsed["paragraphs"][0] if parsed["paragraphs"] else title
    hook = textwrap.shorten(hook, width=250, placeholder="...")
    tweets.append(f"1/ {hook}")

    # Middle tweets from bullet points or key sentences
    for i, point in enumerate(points[:5], start=2):
        tweet = textwrap.shorten(point, width=260, placeholder="...")
        tweets.append(f"{i}/ {tweet}")

    # Closing tweet
    n = len(tweets) + 1
    tweets.append(f"{n}/ If this thread helped you, repost the first tweet.\n\nFollow for more.\n\n{hashtags}")

    return "\n\n---\n\n".join(tweets)


def rule_instagram(parsed: dict) -> str:
    """Generate Instagram carousel text (10 slides)."""
    title = parsed["title"] or "Key Insights"
    points = parsed["bullet_points"] or parsed["key_sentences"]
    paragraphs = parsed["paragraphs"]
    hashtags = " ".join(PLATFORM_HASHTAGS["instagram"])

    slides = []
    # Slide 1: Hook
    slides.append(f"SLIDE 1 (HOOK):\n{title}")

    # Slides 2-8: Value points
    for i, point in enumerate(points[:7], start=2):
        slides.append(f"SLIDE {i}:\n{textwrap.shorten(point, width=200, placeholder='...')}")

    # Fill remaining slides from paragraphs if needed
    slide_num = len(slides) + 1
    para_idx = 1
    while len(slides) < 9 and para_idx < len(paragraphs):
        text = textwrap.shorten(paragraphs[para_idx], width=200, placeholder="...")
        slides.append(f"SLIDE {slide_num}:\n{text}")
        slide_num += 1
        para_idx += 1

    # Pad if still short
    while len(slides) < 9:
        slides.append(f"SLIDE {len(slides) + 1}:\n[Add supporting point or stat here]")

    # Slide 10: CTA
    slides.append(f"SLIDE 10 (CTA):\nSave this post. Share with someone who needs it.\nFollow for more.\n\n{hashtags}")

    return "\n\n".join(slides)


def rule_tiktok(parsed: dict) -> str:
    """Generate a TikTok script (30-60 seconds)."""
    title = parsed["title"] or "Quick Tip"
    first_para = parsed["paragraphs"][0] if parsed["paragraphs"] else ""
    points = parsed["bullet_points"][:3] or parsed["key_sentences"][:3]
    hashtags = " ".join(PLATFORM_HASHTAGS["tiktok"])

    hook = textwrap.shorten(first_para, width=150, placeholder="...") if first_para else title

    body_lines = "\n".join(f"  - {textwrap.shorten(p, 100, placeholder='...')}" for p in points)

    script = f"""HOOK (0-5s):
"{hook}"

CONTENT (5-45s):
Here's what you need to know:
{body_lines}

CTA (45-60s):
Follow for more. Drop a comment if this helped.

{hashtags}"""
    return script


def rule_linkedin(parsed: dict) -> str:
    """Generate a LinkedIn post (200-300 words, professional tone)."""
    title = parsed["title"] or ""
    paragraphs = parsed["paragraphs"]
    points = parsed["bullet_points"]
    hashtags = " ".join(PLATFORM_HASHTAGS["linkedin"])

    parts = []
    # Opening hook
    if paragraphs:
        parts.append(textwrap.shorten(paragraphs[0], width=300, placeholder="..."))
    parts.append("")

    # Body
    if points:
        for p in points[:5]:
            parts.append(f"-> {textwrap.shorten(p, 200, placeholder='...')}")
        parts.append("")

    if len(paragraphs) > 1:
        parts.append(textwrap.shorten(paragraphs[-1], width=300, placeholder="..."))
        parts.append("")

    parts.append("What are your thoughts? Drop them below.")
    parts.append("")
    parts.append(hashtags)

    return "\n".join(parts)


def rule_pinterest(parsed: dict) -> str:
    """Generate a Pinterest pin description (~100 words, SEO-heavy)."""
    title = parsed["title"] or "Helpful Guide"
    keywords = extract_keywords(parsed, 10)
    first_para = parsed["paragraphs"][0] if parsed["paragraphs"] else ""

    desc = textwrap.shorten(first_para, width=400, placeholder="...")
    kw_line = " | ".join(keywords)
    kw_hashtags = " ".join(f"#{k}" for k in keywords[:6])

    return f"""{title}

{desc}

Keywords: {kw_line}

{kw_hashtags}"""


def rule_newsletter(parsed: dict) -> str:
    """Generate a newsletter snippet (3 paragraphs + link placeholder)."""
    title = parsed["title"] or "This Week's Insight"
    paragraphs = parsed["paragraphs"]

    p1 = paragraphs[0] if len(paragraphs) > 0 else "[Opening paragraph]"
    p2 = paragraphs[1] if len(paragraphs) > 1 else "[Key insight paragraph]"
    # Summarize closing
    p3 = paragraphs[-1] if len(paragraphs) > 2 else "[Closing paragraph]"

    p1 = textwrap.shorten(p1, width=400, placeholder="...")
    p2 = textwrap.shorten(p2, width=400, placeholder="...")
    p3 = textwrap.shorten(p3, width=400, placeholder="...")

    return f"""Subject: {title}

{p1}

{p2}

{p3}

Read the full post here: [LINK]

Hit reply if this resonated. I read every response."""


def rule_youtube_shorts(parsed: dict) -> str:
    """Generate a YouTube Shorts script (under 60 seconds)."""
    title = parsed["title"] or "Quick Tip"
    first_para = parsed["paragraphs"][0] if parsed["paragraphs"] else ""
    points = parsed["bullet_points"][:3] or parsed["key_sentences"][:3]
    hashtags = " ".join(PLATFORM_HASHTAGS["youtube_shorts"])

    hook = textwrap.shorten(first_para, width=150, placeholder="...") if first_para else title
    body_lines = "\n".join(f"  {i}. {textwrap.shorten(p, 100, placeholder='...')}" for i, p in enumerate(points, 1))

    return f"""HOOK (0-3s):
"{hook}"

CONTENT (3-50s):
{body_lines}

CTA (50-60s):
Subscribe for more. Like if this was useful.

{hashtags}"""


RULE_GENERATORS = {
    "twitter": rule_twitter,
    "instagram": rule_instagram,
    "tiktok": rule_tiktok,
    "linkedin": rule_linkedin,
    "pinterest": rule_pinterest,
    "newsletter": rule_newsletter,
    "youtube_shorts": rule_youtube_shorts,
}

# ---------------------------------------------------------------------------
# AI-powered generators (Ollama)
# ---------------------------------------------------------------------------

PLATFORM_PROMPTS = {
    "twitter": """Convert the following content into a Twitter/X thread of 5-7 tweets.
Rules:
- Number each tweet (1/, 2/, etc.)
- First tweet is the hook, must grab attention
- Each tweet under 280 characters
- Last tweet is a CTA (follow, repost)
- Add 2-3 relevant hashtags to the last tweet only
- Separate tweets with ---

Content:
{content}""",

    "instagram": """Convert the following content into Instagram carousel text with exactly 10 slides.
Rules:
- Slide 1 is the hook (bold, attention-grabbing title)
- Slides 2-9 deliver value (one key point per slide, keep each under 50 words)
- Slide 10 is a CTA (save, share, follow)
- Label each slide: SLIDE 1:, SLIDE 2:, etc.
- Add 5-8 relevant hashtags at the end

Content:
{content}""",

    "tiktok": """Convert the following content into a TikTok script for a 30-60 second video.
Rules:
- HOOK (0-5s): One punchy line to stop the scroll
- CONTENT (5-45s): 3 key points, conversational tone, spoken language
- CTA (45-60s): Follow + comment prompt
- Add 4-5 TikTok hashtags at the end
- Include timing markers

Content:
{content}""",

    "linkedin": """Convert the following content into a LinkedIn post (200-300 words).
Rules:
- Professional but human tone
- Start with a hook line (pattern interrupt or bold statement)
- Use line breaks for readability
- Include bullet points or arrows for key takeaways
- End with a question to drive engagement
- Add 3-5 professional hashtags

Content:
{content}""",

    "pinterest": """Convert the following content into a Pinterest pin description (~100 words).
Rules:
- SEO-optimized, keyword-rich
- Describe the value of the content clearly
- Include a list of 8-10 relevant keywords at the bottom
- Add 5-6 hashtags from those keywords
- Keep it scannable

Content:
{content}""",

    "newsletter": """Convert the following content into a newsletter snippet (3 short paragraphs).
Rules:
- Paragraph 1: Hook the reader with the key insight
- Paragraph 2: Deliver the core value/takeaway
- Paragraph 3: Tease the full post and include [LINK] placeholder
- Add a subject line at the top
- Casual, direct tone
- End with a "reply to this" CTA

Content:
{content}""",

    "youtube_shorts": """Convert the following content into a YouTube Shorts script (under 60 seconds).
Rules:
- HOOK (0-3s): Attention-grabbing opener
- CONTENT (3-50s): 2-3 key points, spoken naturally, numbered
- CTA (50-60s): Subscribe + like prompt
- Include timing markers
- Add #Shorts and 2-3 relevant hashtags

Content:
{content}""",
}


def ai_generate(platform: str, content: str) -> str | None:
    """Use Ollama to generate platform-specific content."""
    prompt_template = PLATFORM_PROMPTS.get(platform)
    if not prompt_template:
        return None
    prompt = prompt_template.format(content=content[:3000])  # cap input length
    return ollama_generate(prompt)


# ---------------------------------------------------------------------------
# Main repurposing logic
# ---------------------------------------------------------------------------

def repurpose(input_path: str, output_dir: str, platforms: list[str] | None = None, dry_run: bool = False) -> dict:
    """Repurpose a markdown file into multiple platform formats."""
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    content = input_file.read_text(encoding="utf-8")
    if not content.strip():
        print(f"Error: Input file is empty: {input_path}")
        sys.exit(1)

    parsed = parse_markdown(content)
    print(f"Loaded: {input_file.name} ({parsed['word_count']} words)")
    print(f"Title: {parsed['title'] or '(no title found)'}")
    print(f"Paragraphs: {len(parsed['paragraphs'])}, Bullet points: {len(parsed['bullet_points'])}")
    print()

    # Determine output directory
    if output_dir:
        out_path = Path(output_dir)
    else:
        stem = input_file.stem
        out_path = input_file.parent / f"{stem}_repurposed"

    target_platforms = platforms or PLATFORMS
    use_ai = ollama_available()

    if use_ai:
        print(f"Using Ollama ({OLLAMA_MODEL}) for intelligent repurposing")
    else:
        print("Ollama not available. Using rule-based extraction")
    print()

    results = {}

    for platform in target_platforms:
        print(f"  Generating: {platform}...", end=" ", flush=True)

        output_text = None

        # Try AI first
        if use_ai:
            output_text = ai_generate(platform, content)

        # Fallback to rules
        if not output_text:
            generator = RULE_GENERATORS.get(platform)
            if generator:
                output_text = generator(parsed)
                if use_ai:
                    print("(fallback) ", end="")
            else:
                output_text = f"[No generator available for {platform}]"

        results[platform] = output_text
        print("done")

    if dry_run:
        print("\n--- DRY RUN OUTPUT ---\n")
        for platform, text in results.items():
            print(f"{'=' * 60}")
            print(f"  {platform.upper()}")
            print(f"{'=' * 60}")
            print(text)
            print()
        print(f"Would save to: {out_path}/")
        return results

    # Save outputs
    out_path.mkdir(parents=True, exist_ok=True)

    file_extensions = {
        "twitter": "twitter_thread.md",
        "instagram": "instagram_carousel.md",
        "tiktok": "tiktok_script.md",
        "linkedin": "linkedin_post.md",
        "pinterest": "pinterest_pin.md",
        "newsletter": "newsletter_snippet.md",
        "youtube_shorts": "youtube_shorts_script.md",
    }

    for platform, text in results.items():
        filename = file_extensions.get(platform, f"{platform}.md")
        filepath = out_path / filename
        header = f"# {platform.replace('_', ' ').title()} - Repurposed Content\n"
        header += f"# Source: {input_file.name}\n"
        header += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        filepath.write_text(header + text, encoding="utf-8")

    # Write a summary manifest
    manifest = {
        "source": str(input_file.resolve()),
        "generated": datetime.now().isoformat(),
        "word_count": parsed["word_count"],
        "title": parsed["title"],
        "platforms": list(results.keys()),
        "method": "ollama" if use_ai else "rule-based",
        "files": {p: str(out_path / file_extensions.get(p, f"{p}.md")) for p in results},
    }
    manifest_path = out_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"\nSaved {len(results)} formats to: {out_path}/")
    for platform in results:
        print(f"  - {file_extensions.get(platform, f'{platform}.md')}")
    print(f"  - manifest.json")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Content Repurposer - One piece of content into 7 platform formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python3 tools/repurposer.py --input blog/my-post.md
              python3 tools/repurposer.py --input blog/my-post.md --output output/repurposed/
              python3 tools/repurposer.py --input blog/my-post.md --platform twitter
              python3 tools/repurposer.py --input blog/my-post.md --platform twitter --platform linkedin
              python3 tools/repurposer.py --input blog/my-post.md --dry-run
        """),
    )
    parser.add_argument("--input", "-i", required=True, help="Path to markdown file (blog post, newsletter, etc.)")
    parser.add_argument("--output", "-o", default="", help="Output directory (default: <input_stem>_repurposed/)")
    parser.add_argument(
        "--platform", "-p", action="append", choices=PLATFORMS,
        help="Generate for a single platform only (can be repeated)",
    )
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview output without saving files")
    parser.add_argument("--model", "-m", default=None, help="Ollama model to use (default: llama3.2)")

    args = parser.parse_args()

    global OLLAMA_MODEL
    if args.model:
        OLLAMA_MODEL = args.model

    print("=" * 50)
    print("  Content Repurposer")
    print("=" * 50)
    print()

    repurpose(
        input_path=args.input,
        output_dir=args.output,
        platforms=args.platform,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
