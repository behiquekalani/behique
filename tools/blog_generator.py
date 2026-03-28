#!/usr/bin/env python3
"""
SEO Blog Post Generator - Generates long-form blog posts optimized for search.

Drives organic traffic to behike.co products via keyword-targeted content.
Uses Ollama for AI generation, falls back to structured templates if offline.

Usage:
    python3 blog_generator.py --topic "solopreneur business blueprint"
    python3 blog_generator.py --batch
    python3 blog_generator.py --topic "AI tools" --model mistral

Copyright 2026 Behike.
"""

import argparse
import json
import os
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

# -- Config --
BASE_DIR = Path(__file__).resolve().parent.parent
BLOG_DIR = BASE_DIR / "Ceiba" / "projects" / "content-empire" / "blog"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
SITE_URL = "https://behike.co"

BATCH_KEYWORDS = [
    "solopreneur business blueprint",
    "how to start a one person business",
    "business operating system template",
    "AI tools for solopreneurs",
    "digital product business plan",
]

# Products to link internally
PRODUCTS = [
    {"name": "Business Operating System", "url": f"{SITE_URL}/products/business-os", "keywords": ["operating system", "business system", "organize", "workflow", "productivity"]},
    {"name": "Solopreneur Blueprint", "url": f"{SITE_URL}/products/solopreneur-blueprint", "keywords": ["solopreneur", "one person business", "solo founder", "bootstrap"]},
    {"name": "AI Automation Toolkit", "url": f"{SITE_URL}/products/ai-toolkit", "keywords": ["AI tools", "automation", "artificial intelligence", "automate"]},
    {"name": "Digital Product Launch Guide", "url": f"{SITE_URL}/products/launch-guide", "keywords": ["digital product", "launch", "product business", "info product"]},
    {"name": "Content System Template", "url": f"{SITE_URL}/products/content-system", "keywords": ["content", "content creation", "writing", "publishing", "newsletter"]},
]


# -- Ollama --

def ollama_generate(prompt, model=None):
    """Call Ollama API. Returns generated text or None on failure."""
    model = model or OLLAMA_MODEL
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"[warn] Ollama unavailable ({e}). Using template fallback.")
        return None


def ollama_available():
    """Quick health check."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# -- SEO helpers --

def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def pick_product_links(topic):
    """Select 2-3 relevant products to link based on topic keywords."""
    topic_lower = topic.lower()
    scored = []
    for prod in PRODUCTS:
        score = sum(1 for kw in prod["keywords"] if kw in topic_lower)
        if score > 0:
            scored.append((score, prod))
    scored.sort(key=lambda x: x[0], reverse=True)
    # Always return at least 1, max 3
    if not scored:
        return PRODUCTS[:2]
    return [p for _, p in scored[:3]]


def generate_meta_description(topic, title):
    """Generate a meta description under 160 chars."""
    base = f"Learn how to build a {topic}. Practical strategies, tools, and templates to help you succeed as a solopreneur."
    if len(base) > 160:
        base = base[:157] + "..."
    return base


# -- Blog generation with Ollama --

def build_ollama_prompt(topic):
    """Build the prompt for Ollama to generate a full blog post."""
    products = pick_product_links(topic)
    product_refs = "\n".join(
        f"- {p['name']}: {p['url']}" for p in products
    )

    return f"""You are an expert SEO content writer for behike.co, a brand that helps solopreneurs build one-person businesses using AI, automation, and systems thinking.

Write a comprehensive blog post about: "{topic}"

REQUIREMENTS:
1. SEO-optimized title under 60 characters
2. Meta description under 160 characters
3. 1500-2000 words
4. Use H2 and H3 headers to structure the content
5. Write in a direct, practical tone. No fluff. Like Dan Koe meets James Clear.
6. Include actionable steps, not just theory
7. Naturally reference these products where relevant (do not force them):
{product_refs}
8. End with a clear call-to-action directing readers to behike.co
9. Include a "Key Takeaways" section before the CTA
10. Do NOT use em dashes. Use periods or commas instead.

OUTPUT FORMAT (follow exactly):
TITLE: [your title here]
META: [your meta description here]
---
[full blog post content in markdown with ## for H2 and ### for H3]

Write the post now."""


def generate_with_ollama(topic, model=None):
    """Generate a blog post using Ollama."""
    prompt = build_ollama_prompt(topic)
    raw = ollama_generate(prompt, model=model)
    if not raw:
        return None

    # Parse title and meta from output
    title = ""
    meta = ""
    body = raw

    lines = raw.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip().strip('"')
        elif line.startswith("META:"):
            meta = line.replace("META:", "").strip().strip('"')
        elif line.strip() == "---":
            body_start = i + 1
            break

    if body_start > 0:
        body = "\n".join(lines[body_start:])

    if not title:
        title = f"The Complete Guide to {topic.title()}"
    if len(title) > 60:
        title = title[:57] + "..."

    if not meta:
        meta = generate_meta_description(topic, title)
    if len(meta) > 160:
        meta = meta[:157] + "..."

    return {"title": title, "meta": meta, "body": body.strip()}


# -- Template fallback --

def generate_from_template(topic):
    """Generate a structured blog post from templates when Ollama is offline."""
    products = pick_product_links(topic)
    title = f"The Complete Guide to {topic.title()}"
    if len(title) > 60:
        title = f"How to Master {topic.title()}"
    if len(title) > 60:
        title = title[:57] + "..."

    meta = generate_meta_description(topic, title)

    product_links_html = "\n".join(
        f'<li><a href="{p["url"]}">{p["name"]}</a></li>' for p in products
    )

    body = f"""## Why {topic.title()} Matters in 2026

The landscape of online business is shifting. Solopreneurs who build systems win. Those who hustle without structure burn out.

If you have been searching for a way to build a {topic}, you are in the right place. This guide breaks down the exact steps, tools, and frameworks you need.

## What is a {topic.title()}?

A {topic} is more than a plan. It is a repeatable system that lets you operate a profitable business without a team of 50 people. The best solopreneurs in 2026 are not working harder. They are building smarter.

The core idea is simple: design once, execute repeatedly. Automate what you can. Focus your energy on the 20% that drives 80% of results.

## The Foundation: Systems Over Hustle

Most people fail at building a business because they treat it like a job. They trade time for output instead of building assets that compound.

Here is the shift you need to make:

### 1. Define Your Core Offer

Every successful one-person business starts with one clear offer. Not five. Not ten. One.

Ask yourself: what problem can you solve better than most people? What do people already come to you for? That is your starting point.

### 2. Build Your Operating System

Your business needs a central operating system. A place where tasks, projects, content, and revenue all connect. Without this, you are just reacting to whatever feels urgent.

A good operating system covers four areas:
- **Task management** (what needs to happen today)
- **Content pipeline** (what you are publishing and when)
- **Revenue tracking** (what is making money)
- **Growth metrics** (what is moving the needle)

### 3. Automate the Repetitive Work

AI tools have made it possible for one person to do the work of a small team. Content generation, email sequences, social media scheduling, data analysis. All of these can be partially or fully automated.

The key is knowing which tasks to automate and which ones need your personal touch. Automate distribution. Keep creation human.

## The Execution Framework

Theory without execution is entertainment. Here is how to actually implement this.

### Step 1: Audit Your Current Workflow

Spend one day tracking every task you do. Categorize each one:
- **Create** (writing, designing, building)
- **Distribute** (posting, emailing, outreach)
- **Admin** (invoicing, scheduling, organizing)
- **Strategy** (planning, researching, deciding)

Most solopreneurs spend 60% of their time on admin and distribution. That needs to flip.

### Step 2: Pick Your Stack

You do not need 30 tools. You need 5-7 that work together. Here is a solid starting stack:

- **Notion or Obsidian** for your operating system
- **Beehiiv or ConvertKit** for email
- **Gumroad or Shopify** for products
- **Buffer or Hypefury** for social scheduling
- **n8n or Zapier** for automation

### Step 3: Create a 30-Day Sprint

Do not plan for a year. Plan for 30 days. Set one revenue goal, one content goal, and one systems goal. Execute daily. Review weekly.

## Common Mistakes to Avoid

**Building in silence.** Share your work before it is perfect. The market will tell you what to improve.

**Tool hopping.** Pick your stack and commit for 90 days minimum. Switching tools every week is a form of procrastination.

**Ignoring distribution.** The best product in the world fails if nobody sees it. Spend at least 30% of your time on getting eyeballs on your work.

**Skipping the system.** Motivation fades. Systems persist. Build the system first.

## Key Takeaways

- A {topic} is your competitive advantage as a solopreneur
- Start with one core offer and build systems around it
- Automate distribution, keep creation human
- Use a 30-day sprint model instead of annual planning
- Pick 5-7 tools and commit to them for 90 days

## Resources to Get Started

{product_links_html}

## Ready to Build Your System?

Stop reading about business systems and start building one. The difference between where you are now and where you want to be is one decision followed by consistent action.

Check out <a href="{SITE_URL}">behike.co</a> for templates, tools, and frameworks built specifically for solopreneurs who want to build real businesses without burning out.

Your future self will thank you for starting today.
"""
    return {"title": title, "meta": meta, "body": body.strip()}


# -- HTML output --

def to_html(post, topic):
    """Convert a blog post dict to clean, pasteable HTML."""
    title = post["title"]
    meta = post["meta"]
    body = post["body"]
    slug = slugify(topic)
    date_str = datetime.now().strftime("%Y-%m-%d")
    products = pick_product_links(topic)

    # Convert markdown headers to HTML
    lines = body.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Close list if we are leaving one
        if in_list and not stripped.startswith("- ") and not stripped.startswith("* "):
            html_lines.append("</ul>")
            in_list = False

        if stripped.startswith("### "):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = stripped[2:]
            # Convert **bold** to <strong>
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            # Convert [text](url) to <a>
            item = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', item)
            html_lines.append(f"  <li>{item}</li>")
        elif stripped == "":
            html_lines.append("")
        else:
            # Convert inline markdown
            p = stripped
            p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
            p = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', p)
            html_lines.append(f"<p>{p}</p>")

    if in_list:
        html_lines.append("</ul>")

    body_html = "\n".join(html_lines)

    # Build product JSON-LD references
    product_jsonld = []
    for p in products:
        product_jsonld.append(f'    {{"@type": "Product", "name": "{p["name"]}", "url": "{p["url"]}"}}')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{SITE_URL}/blog/{slug}">

    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_URL}/blog/{slug}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta}">

    <!-- Structured Data -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "{title}",
        "description": "{meta}",
        "datePublished": "{date_str}",
        "author": {{
            "@type": "Person",
            "name": "Kalani",
            "url": "{SITE_URL}"
        }},
        "publisher": {{
            "@type": "Organization",
            "name": "Behike",
            "url": "{SITE_URL}"
        }},
        "mainEntityOfPage": "{SITE_URL}/blog/{slug}",
        "mentions": [
{",\\n".join(product_jsonld)}
        ]
    }}
    </script>

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 720px;
            margin: 0 auto;
            padding: 2rem 1rem;
            line-height: 1.7;
            color: #1a1a1a;
            background: #fff;
        }}
        h1 {{ font-size: 2rem; line-height: 1.2; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 1.5rem; margin-top: 2.5rem; margin-bottom: 1rem; }}
        h3 {{ font-size: 1.2rem; margin-top: 2rem; margin-bottom: 0.75rem; }}
        p {{ margin-bottom: 1.2rem; }}
        ul {{ margin-bottom: 1.2rem; padding-left: 1.5rem; }}
        li {{ margin-bottom: 0.5rem; }}
        a {{ color: #2563eb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 2rem; }}
        .cta-box {{
            background: #f0f4ff;
            border: 1px solid #d0d8f0;
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 2rem;
            text-align: center;
        }}
        .cta-box a {{
            display: inline-block;
            background: #2563eb;
            color: #fff;
            padding: 0.75rem 2rem;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        .cta-box a:hover {{ background: #1d4ed8; text-decoration: none; }}
    </style>
</head>
<body>
    <article>
        <h1>{title}</h1>
        <div class="meta">By Kalani | {datetime.now().strftime("%B %d, %Y")} | behike.co</div>

{body_html}

        <div class="cta-box">
            <p><strong>Ready to build your system?</strong></p>
            <p>Get the tools, templates, and frameworks at behike.co</p>
            <a href="{SITE_URL}">Visit Behike</a>
        </div>
    </article>
</body>
</html>"""

    return html


# -- Save --

def save_post(html, topic):
    """Save HTML to blog directory. Returns file path."""
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(topic)
    filename = f"{date_str}-{slug}.html"
    filepath = BLOG_DIR / filename
    filepath.write_text(html, encoding="utf-8")
    return filepath


# -- Main --

def generate_post(topic, model=None):
    """Generate a single blog post. Returns (filepath, post_dict)."""
    print(f"\n>> Generating: {topic}")

    post = None
    if ollama_available():
        print(f"   Using Ollama ({model or OLLAMA_MODEL})...")
        post = generate_with_ollama(topic, model=model)

    if not post:
        print("   Using template fallback...")
        post = generate_from_template(topic)

    html = to_html(post, topic)
    filepath = save_post(html, topic)

    print(f"   Title: {post['title']}")
    print(f"   Meta:  {post['meta']}")
    print(f"   Saved: {filepath}")
    return filepath, post


def main():
    parser = argparse.ArgumentParser(
        description="SEO Blog Post Generator for behike.co"
    )
    parser.add_argument(
        "--topic", type=str, help="Keyword/topic to generate a post for"
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="Generate posts for all predefined high-value keywords"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help=f"Ollama model to use (default: {OLLAMA_MODEL})"
    )
    parser.add_argument(
        "--template-only", action="store_true",
        help="Skip Ollama, use template fallback only"
    )
    args = parser.parse_args()

    if not args.topic and not args.batch:
        parser.print_help()
        sys.exit(1)

    results = []

    if args.template_only:
        # Monkey-patch to force template mode
        global ollama_available
        _orig = ollama_available
        ollama_available = lambda: False

    if args.batch:
        print(f"=== Batch mode: generating {len(BATCH_KEYWORDS)} posts ===")
        for kw in BATCH_KEYWORDS:
            filepath, post = generate_post(kw, model=args.model)
            results.append({"topic": kw, "title": post["title"], "file": str(filepath)})
    elif args.topic:
        filepath, post = generate_post(args.topic, model=args.model)
        results.append({"topic": args.topic, "title": post["title"], "file": str(filepath)})

    if args.template_only:
        ollama_available = _orig

    # Summary
    print(f"\n=== Done: {len(results)} post(s) generated ===")
    for r in results:
        print(f"  [{r['topic']}] -> {r['file']}")

    # Save manifest
    manifest_path = BLOG_DIR / "manifest.json"
    existing = []
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text())
        except Exception:
            existing = []

    for r in results:
        r["date"] = datetime.now().strftime("%Y-%m-%d")
    existing.extend(results)
    manifest_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"  Manifest updated: {manifest_path}")


if __name__ == "__main__":
    main()
