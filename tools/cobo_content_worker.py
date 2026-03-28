#!/usr/bin/env python3
"""
Cobo Content Worker - Dispatch content generation to Cobo's Ollama.
Uses the bridge to send prompts and collect responses.

Usage:
    python3 tools/cobo_content_worker.py hooks 10      # Generate 10 hooks
    python3 tools/cobo_content_worker.py captions 5    # Generate 5 captions
    python3 tools/cobo_content_worker.py threads 3     # Generate 3 thread ideas
    python3 tools/cobo_content_worker.py scripts 2     # Generate 2 reel scripts
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://192.168.0.151:11434/api/generate"
MODEL = "llama3.2"
OUTPUT_DIR = Path(os.path.expanduser("~/behique/Ceiba/projects/content-empire/ai-generated"))

BRAND_CONTEXT = """You are writing content for Behike, an AI automation brand.
Voice: Direct, calm authority. Dan Koe style. Philosophical but practical.
Audience: Young entrepreneurs, small business owners, side hustlers.
Rules: Never use em dashes. Use periods or commas instead. No emojis. No hype words like "revolutionary" or "game-changing". Be real, not salesy.
Founder: Kalani, a computer engineering student in Puerto Rico who built an AI system with 6 agents on 3 computers for $0/month."""

PROMPTS = {
    "hooks": f"""{BRAND_CONTEXT}

Generate {{count}} Instagram hook ideas. Each hook should:
- Be exactly 1 sentence
- Stop someone from scrolling
- Use curiosity, fear, or results as the trigger
- Sound like something a real person would say, not a brand

Format: numbered list, one per line.""",

    "captions": f"""{BRAND_CONTEXT}

Generate {{count}} Instagram captions about AI automation. Each caption should:
- Be 50-100 words
- Start with a hook (first line = scroll stopper)
- Include 1 key insight
- End with a call to action (save, follow, or link in bio)
- Include 5 relevant hashtags

Separate each caption with ---""",

    "threads": f"""{BRAND_CONTEXT}

Generate {{count}} X/Twitter thread ideas. For each, provide:
- Hook tweet (must stand alone and make people want to read more)
- 3 bullet points of what the thread would cover
- CTA tweet

Separate each thread idea with ---""",

    "scripts": f"""{BRAND_CONTEXT}

Generate {{count}} 60-second reel scripts. Each script should:
- Start with a hook in the first 3 seconds
- Deliver one clear insight about AI automation
- End with "save this" or "follow for more"
- Include [VISUAL] notes for what should be on screen
- Be written as a voiceover script

Separate each script with ---""",
}


def generate(content_type, count=5):
    """Send prompt to Cobo's Ollama and get response."""
    if content_type not in PROMPTS:
        print(f"  Unknown type: {content_type}")
        print(f"  Available: {', '.join(PROMPTS.keys())}")
        return None

    prompt = PROMPTS[content_type].format(count=count)

    print(f"  Dispatching to Cobo: {content_type} x{count}...")

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        }, timeout=120)

        if resp.status_code == 200:
            result = resp.json().get("response", "")
            return result
        else:
            print(f"  Error: {resp.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("  Cobo is offline. Cannot dispatch.")
        return None
    except requests.exceptions.Timeout:
        print("  Timeout. Cobo took too long.")
        return None


def save_output(content_type, content, count):
    """Save generated content to file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{content_type}_{count}x_{timestamp}.md"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w") as f:
        f.write(f"# AI-Generated {content_type.title()}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"# Model: {MODEL} on Cobo (192.168.0.151)\n")
        f.write(f"# Status: DRAFT - needs human review before use\n\n")
        f.write("---\n\n")
        f.write(content)

    print(f"  Saved: {filepath}")
    return filepath


def main():
    if len(sys.argv) < 2:
        print("  Cobo Content Worker")
        print(f"  Types: {', '.join(PROMPTS.keys())}")
        print("  Usage: python3 tools/cobo_content_worker.py <type> [count]")
        return

    content_type = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    result = generate(content_type, count)
    if result:
        save_output(content_type, result, count)
        print(f"\n  Preview (first 500 chars):\n")
        print(f"  {result[:500]}")
    else:
        print("  Generation failed.")


if __name__ == "__main__":
    main()
