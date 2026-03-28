#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""Content waterfall: one blog post becomes 5 content pieces."""
import json, os, re, requests
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path(__file__).parent.parent / "Ceiba" / "blog"
DERIV_DIR = BLOG_DIR / "derivatives"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def ask_ollama(prompt, max_tokens=500):
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": "qwen2.5:7b", "prompt": prompt,
            "stream": False, "options": {"num_predict": max_tokens}
        }, timeout=60)
        return resp.json().get("response", "")
    except: return ""

def waterfall(blog_file):
    path = Path(blog_file)
    text = path.read_text()
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    title = title_match.group(1) if title_match else path.stem
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3: text = parts[2].strip()
    date = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:40]
    out_dir = DERIV_DIR / f"{date}-{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    generators = [
        ("carousel.md", f"Convert to 5 Instagram slides. Slide 1=hook, 2-4=points, 5=CTA. No em dashes.\n\n{title}\n{text[:2000]}"),
        ("tweets.md", f"Convert to 4-tweet thread. Under 280 chars each. No em dashes.\n\n{title}\n{text[:1500]}"),
        ("linkedin.md", f"Convert to 200-word LinkedIn post. Professional but personal. No em dashes.\n\n{title}\n{text[:2000]}"),
        ("newsletter.md", f"Write 100-word newsletter snippet. End with 'Read the full post'. No em dashes.\n\n{title}\n{text[:1000]}"),
        ("reel-script.md", f"Convert to 30-second reel script with [CAMERA]/[SCREEN] markers. No em dashes.\n\n{title}\n{text[:1000]}"),
    ]
    for filename, prompt in generators:
        content = ask_ollama(prompt, 500)
        if content: (out_dir / filename).write_text(f"# {title}\n\n{content}")
    print(f"  Waterfall complete: {out_dir}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--from-blog", help="Blog file to convert")
    p.add_argument("--list", action="store_true")
    a = p.parse_args()
    if a.list:
        if DERIV_DIR.exists():
            for d in sorted(DERIV_DIR.iterdir(), reverse=True):
                if d.is_dir(): print(f"  {d.name}: {len(list(d.glob('*.md')))} pieces")
    elif a.from_blog: waterfall(a.from_blog)
    else: p.print_help()
