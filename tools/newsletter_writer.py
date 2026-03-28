#!/usr/bin/env python3
"""
Weekly Newsletter Generator for Behike.
Generates HTML newsletters using Ollama, loads the Voice Bible for tone.

Usage:
    python tools/newsletter_writer.py --generate
    python tools/newsletter_writer.py --preview
    python tools/newsletter_writer.py --list

Copyright 2026 Behike.
"""

import argparse
import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

# -- Config --

BASE_DIR = Path(__file__).resolve().parent.parent
NEWSLETTERS_DIR = BASE_DIR / "Ceiba" / "newsletters"
VOICE_BIBLE = BASE_DIR / "Ceiba" / "projects" / "content-empire" / "voice-bible.md"
AI_NEWS_DIR = BASE_DIR / "Ceiba" / "projects" / "content-empire" / "ai-news"
PRODUCTS_DIR = BASE_DIR / "Ceiba" / "projects" / "content-empire" / "products"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


# -- HTML Template --

NEWSLETTER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject_line}</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    background: #000;
    color: #f5f5f7;
    font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{
    max-width: 600px;
    margin: 0 auto;
    padding: 40px 24px;
  }}
  .header {{
    text-align: center;
    padding-bottom: 32px;
    border-bottom: 1px solid rgba(245,245,247,0.08);
    margin-bottom: 32px;
  }}
  .header h1 {{
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 4px;
  }}
  .header .date {{
    font-size: 13px;
    color: #86868b;
  }}
  .section {{
    margin-bottom: 36px;
  }}
  .section-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #0a84ff;
    margin-bottom: 12px;
  }}
  .section h2 {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 12px;
  }}
  .section p {{
    font-size: 15px;
    line-height: 1.6;
    color: #d1d1d6;
    margin: 0 0 12px;
  }}
  .story {{
    background: rgba(29,29,31,0.6);
    border: 1px solid rgba(245,245,247,0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
  }}
  .story h3 {{
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 8px;
  }}
  .story p {{
    font-size: 14px;
    color: #86868b;
    margin: 0;
    line-height: 1.5;
  }}
  .spotlight {{
    background: rgba(10,132,255,0.08);
    border: 1px solid rgba(10,132,255,0.2);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
  }}
  .spotlight h3 {{
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 8px;
  }}
  .spotlight p {{
    font-size: 14px;
    color: #86868b;
    margin: 0 0 16px;
  }}
  .spotlight a {{
    display: inline-block;
    background: #0a84ff;
    color: #fff;
    padding: 10px 24px;
    border-radius: 980px;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
  }}
  .tip {{
    background: rgba(52,199,89,0.08);
    border-left: 3px solid #34c759;
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
  }}
  .tip h3 {{
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 8px;
    color: #34c759;
  }}
  .tip p {{
    font-size: 14px;
    color: #d1d1d6;
    margin: 0;
    line-height: 1.5;
  }}
  .footer {{
    border-top: 1px solid rgba(245,245,247,0.08);
    padding-top: 24px;
    text-align: center;
    font-size: 12px;
    color: #86868b;
  }}
  .footer a {{
    color: #0a84ff;
    text-decoration: none;
  }}
  .unsubscribe {{
    margin-top: 12px;
  }}
  .unsubscribe a {{
    color: #86868b;
    font-size: 11px;
  }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>Behike Weekly</h1>
    <div class="date">{date_display}</div>
  </div>

  <!-- Personal Update -->
  <div class="section">
    <div class="section-label">From Kalani</div>
    <p>{personal_update}</p>
  </div>

  <!-- Top 3 AI Stories -->
  <div class="section">
    <div class="section-label">This Week in AI</div>
    {stories_html}
  </div>

  <!-- Product Spotlight -->
  <div class="section">
    <div class="section-label">Product Spotlight</div>
    <div class="spotlight">
      <h3>{spotlight_title}</h3>
      <p>{spotlight_desc}</p>
      <a href="{spotlight_link}">Check it out</a>
    </div>
  </div>

  <!-- Weekly Tip -->
  <div class="section">
    <div class="section-label">Quick Tip</div>
    <div class="tip">
      <h3>{tip_title}</h3>
      <p>{tip_body}</p>
    </div>
  </div>

  <div class="footer">
    <p>Built by <a href="https://instagram.com/behikeai">@behikeai</a> in Puerto Rico.</p>
    <p>Copyright 2026 Behike. All rights reserved.</p>
    <div class="unsubscribe">
      <a href="{{{{unsubscribe_url}}}}">Unsubscribe</a>
    </div>
  </div>

</div>
</body>
</html>"""


# -- Helpers --

def load_voice_bible() -> str:
    """Load the voice bible for tone guidance."""
    if VOICE_BIBLE.exists():
        return VOICE_BIBLE.read_text()[:2000]
    return "Tone: direct, honest, zero fluff. Apple minimalism. Dan Koe influence. Short sentences. Builder mentality."


def load_recent_news() -> str:
    """Load recent AI news if tracker output exists."""
    if AI_NEWS_DIR.exists():
        news_files = sorted(AI_NEWS_DIR.glob("*.md"), reverse=True)[:3]
        content = []
        for f in news_files:
            content.append(f.read_text()[:1000])
        return "\n---\n".join(content) if content else "No recent news files found."
    return "No AI news directory found. Use placeholder stories."


def load_product_info() -> str:
    """Load product info for spotlight section."""
    if PRODUCTS_DIR.exists():
        product_files = sorted(PRODUCTS_DIR.glob("*.md"), reverse=True)[:5]
        content = []
        for f in product_files:
            content.append(f"## {f.stem}\n{f.read_text()[:500]}")
        return "\n".join(content) if content else "Products: AI Employee Guide, Behike Method, Solopreneur OS, Budget Template, Shopify Themes."
    return "Products: AI Employee Guide ($19.99), Behike Method ($14.99), Solopreneur OS ($12.99), Budget Template ($9.99), Shopify Theme Bundle ($69.99)."


def query_ollama(prompt: str) -> str:
    """Query Ollama for content generation."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 2000},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        print(f"Ollama error: {e}")
        print("Falling back to placeholder content.")
        return ""


def generate_subject_lines() -> list[str]:
    """Generate 5 subject line options."""
    voice = load_voice_bible()
    prompt = f"""You write newsletter subject lines for Behike, a digital tools brand for builders and solopreneurs.

Voice guide: {voice[:500]}

Generate exactly 5 subject lines for this week's newsletter. Keep them under 60 characters. Make them curiosity-driven, not clickbait. No emojis. No em dashes.

Format: one per line, numbered 1-5."""

    result = query_ollama(prompt)
    if result:
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        # Clean numbering
        cleaned = []
        for line in lines:
            line = line.lstrip("0123456789.)- ").strip()
            if line and len(line) > 5:
                cleaned.append(line)
        return cleaned[:5] if cleaned else default_subjects()
    return default_subjects()


def default_subjects() -> list[str]:
    today = datetime.now().strftime("%B %d")
    return [
        f"What builders need to know this week ({today})",
        "3 AI tools that actually save time",
        "The one thing slowing down your business",
        "Build faster. Ship more. Here's how.",
        "This week's best AI finds, no fluff",
    ]


def generate_newsletter_content() -> dict:
    """Generate all newsletter sections using Ollama."""
    voice = load_voice_bible()
    news = load_recent_news()
    products = load_product_info()

    prompt = f"""You are writing the weekly Behike newsletter. Behike is a digital tools brand for builders and solopreneurs, run by Kalani, a computer engineering student in Puerto Rico.

VOICE GUIDE:
{voice[:1000]}

RECENT AI NEWS (use for story summaries):
{news[:2000]}

PRODUCTS (pick one for spotlight):
{products[:1500]}

Generate the following sections in JSON format. No em dashes anywhere. Keep it direct, honest, zero fluff.

{{
  "personal_update": "2-3 sentences from Kalani's perspective. What he's been working on, what he learned. Honest, not polished. Write [FILL IN] as placeholder for Kalani to customize.",
  "stories": [
    {{"title": "Story 1 headline", "summary": "2-3 sentence summary"}},
    {{"title": "Story 2 headline", "summary": "2-3 sentence summary"}},
    {{"title": "Story 3 headline", "summary": "2-3 sentence summary"}}
  ],
  "spotlight_title": "Product name",
  "spotlight_desc": "One compelling sentence about the product",
  "spotlight_link": "https://behike.com",
  "tip_title": "Short tip title",
  "tip_body": "2-3 sentence actionable tip for builders"
}}

Return ONLY valid JSON. No markdown code blocks."""

    result = query_ollama(prompt)

    # Try to parse JSON from response
    if result:
        # Strip markdown code blocks if present
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1] if "\n" in result else result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            import re
            match = re.search(r'\{[\s\S]*\}', result)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

    # Fallback content
    return {
        "personal_update": "[FILL IN] Write a quick personal update here. What you shipped, what you learned, what's next.",
        "stories": [
            {"title": "AI story placeholder", "summary": "Replace with this week's top AI news story."},
            {"title": "AI story placeholder", "summary": "Replace with this week's second story."},
            {"title": "AI story placeholder", "summary": "Replace with this week's third story."},
        ],
        "spotlight_title": "AI Employee Guide",
        "spotlight_desc": "20-chapter blueprint for building your own multi-machine AI system. No cloud subscriptions needed.",
        "spotlight_link": "https://behike.com",
        "tip_title": "Start with one automation",
        "tip_body": "Don't try to automate everything at once. Pick the one task you repeat most often. Automate that first. Build from there.",
    }


def build_stories_html(stories: list[dict]) -> str:
    """Build HTML for story cards."""
    html = ""
    for story in stories[:3]:
        html += f"""    <div class="story">
      <h3>{story.get('title', 'Story')}</h3>
      <p>{story.get('summary', '')}</p>
    </div>\n"""
    return html


def build_newsletter(content: dict, subject: str) -> str:
    """Assemble the full newsletter HTML."""
    today = datetime.now()
    date_display = today.strftime("%B %d, %Y")
    stories_html = build_stories_html(content.get("stories", []))

    html = NEWSLETTER_TEMPLATE.format(
        subject_line=subject,
        date_display=date_display,
        personal_update=content.get("personal_update", "[FILL IN]"),
        stories_html=stories_html,
        spotlight_title=content.get("spotlight_title", ""),
        spotlight_desc=content.get("spotlight_desc", ""),
        spotlight_link=content.get("spotlight_link", "https://behike.com"),
        tip_title=content.get("tip_title", ""),
        tip_body=content.get("tip_body", ""),
    )
    return html


# -- CLI Commands --

def cmd_generate():
    """Generate this week's newsletter."""
    NEWSLETTERS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = NEWSLETTERS_DIR / f"{today}.html"

    print("Generating subject lines...")
    subjects = generate_subject_lines()
    print("\nSubject line options (A/B test ready):")
    for i, s in enumerate(subjects, 1):
        print(f"  {i}. {s}")

    print("\nGenerating newsletter content...")
    content = generate_newsletter_content()

    # Use first subject as default
    subject = subjects[0] if subjects else f"Behike Weekly - {today}"
    html = build_newsletter(content, subject)

    output_file.write_text(html)
    print(f"\nNewsletter saved: {output_file}")
    print(f"Subject lines saved alongside.")

    # Save subject lines
    subjects_file = NEWSLETTERS_DIR / f"{today}-subjects.json"
    subjects_file.write_text(json.dumps(subjects, indent=2))

    # Remind about personal update
    if "[FILL IN]" in html:
        print("\nREMINDER: Open the HTML and fill in the personal update section.")


def cmd_preview():
    """Open the most recent newsletter in the browser."""
    NEWSLETTERS_DIR.mkdir(parents=True, exist_ok=True)
    html_files = sorted(NEWSLETTERS_DIR.glob("*.html"), reverse=True)

    if not html_files:
        print("No newsletters found. Run --generate first.")
        return

    latest = html_files[0]
    print(f"Opening: {latest}")
    webbrowser.open(f"file://{latest}")


def cmd_list():
    """List all past newsletters."""
    NEWSLETTERS_DIR.mkdir(parents=True, exist_ok=True)
    html_files = sorted(NEWSLETTERS_DIR.glob("*.html"), reverse=True)

    if not html_files:
        print("No newsletters yet.")
        return

    print("Past newsletters:")
    for f in html_files:
        size = f.stat().st_size
        print(f"  {f.stem}  ({size:,} bytes)")


# -- Main --

def main():
    parser = argparse.ArgumentParser(description="Behike Newsletter Writer")
    parser.add_argument("--generate", action="store_true", help="Generate this week's newsletter")
    parser.add_argument("--preview", action="store_true", help="Open latest newsletter in browser")
    parser.add_argument("--list", action="store_true", help="List past newsletters")

    args = parser.parse_args()

    if args.generate:
        cmd_generate()
    elif args.preview:
        cmd_preview()
    elif args.list:
        cmd_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
