#!/usr/bin/env python3
"""
AI News to Instagram Post Generator.

Takes high-impact articles from ai_news_tracker and generates
ready-to-post content: caption, hashtags, carousel text slides.

Usage:
    python3 news_to_post.py                     # generate from today's top stories
    python3 news_to_post.py --story 3           # pick story #3 from digest
    python3 news_to_post.py --custom "headline"  # write post from custom headline
    python3 news_to_post.py --carousel           # generate carousel slide text
    python3 news_to_post.py --list               # list today's stories to pick from
"""
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
DATA_DIR = TOOLS_DIR.parent / "Ceiba" / "news"
ARTICLES_FILE = DATA_DIR / "articles.json"
POSTS_DIR = DATA_DIR / "posts"


def _voice_check_caption(caption: str) -> str:
    """Run Voice Bible check on generated caption text and auto-fix violations."""
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        from voice_checker import fix_text
        fixed, changes = fix_text(caption)
        if changes:
            total = sum(c.get("count", 0) for c in changes)
            print(f"  [VOICE] Fixed {total} banned word violations in caption")
        return fixed
    except ImportError:
        return caption


def load_articles():
    if ARTICLES_FILE.exists():
        with open(ARTICLES_FILE) as f:
            return json.load(f)
    return []


def get_top_stories(n=10):
    articles = load_articles()
    today = datetime.now().strftime("%Y-%m-%d")
    # Prefer today's articles, fall back to most recent
    today_articles = [a for a in articles if a.get("fetched", "")[:10] == today]
    if not today_articles:
        today_articles = articles
    # Sort by impact
    today_articles.sort(key=lambda a: a.get("impact_score", 0), reverse=True)
    return today_articles[:n]


def clean_html(text):
    """Clean HTML entities, tags, em dashes, and Reddit formatting from text."""
    import re
    if not text:
        return ""
    # Strip ALL HTML tags first
    text = re.sub(r'<[^>]+>', ' ', text)
    # HTML entities
    replacements = {
        "&#160;": " ", "&#8217;": "'", "&#8220;": '"', "&#8221;": '"',
        "&#32;": " ", "&#8212;": ".", "&#8211;": ".", "&mdash;": ".",
        "&ndash;": ".", "\u2014": ".", "\u2013": ".",
        "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&#8230;": "...", "&hellip;": "...",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Clean Reddit tags: [R], [D], [P], [N], [Discussion], etc.
    text = re.sub(r'^\s*:?\s*\[([RDPN]|Discussion|Research|Project|News)\]\s*', '', text)
    # Clean trailing metadata in parens at end: (275 obs, 97% cost...)
    text = re.sub(r'\s*\(\d+\s*obs[^)]*\)\s*$', '', text)
    # Clean Reddit markdown: **bold**, *italic*, ~~strike~~
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    # Clean multiple spaces
    text = re.sub(r'\s+', ' ', text)
    while ".." in text:
        text = text.replace("..", ".")
    return text.strip()


## OPB Content Templates (Dan Koe framework)
## Each template maps to a different content angle.

OPB_TEMPLATES = {
    "importance": {
        "name": "Importance",
        "desc": "Why this matters for builders",
        "format": "Why {topic} matters for builders:\n\n{reasons}\n\n{closer}",
    },
    "harsh_truth": {
        "name": "Harsh Truth",
        "desc": "Call out what people are missing",
        "format": "{hook}\n\n{body}\n\n{closer}",
    },
    "principles": {
        "name": "Principles",
        "desc": "Break down what happened and what it means",
        "format": "{hook}\n\n{points}\n\n{closer}",
    },
    "pain_resolution": {
        "name": "Pain Resolution",
        "desc": "Connect news to reader's problem, offer filter",
        "format": "{audience_callout}\n\n{pains}\n\n{solution}",
    },
    "confident_advice": {
        "name": "Confident Advice",
        "desc": "Step-by-step what to do with this info",
        "format": "{hook}\n\n{steps}\n\n{nuance}\n\n{summary}",
    },
}


def _build_tags(article):
    """Build focused hashtag set. Max 10, no spam."""
    mentions = article.get("mentions", [])
    tags = ["#AI", "#technews"]

    for m in mentions[:5]:
        tag = "#" + m.replace(" ", "").replace("-", "").lower()
        if tag not in tags:
            tags.append(tag)

    cat = article.get("category", "")
    cat_tags = {
        "releases": ["#aitools", "#newrelease"],
        "hardware": ["#nvidia", "#gpu"],
        "research": ["#airesearch", "#machinelearning"],
        "regulation": ["#airegulation", "#policy"],
        "business": ["#startup", "#venture"],
    }
    for t in cat_tags.get(cat, []):
        if t not in tags:
            tags.append(t)

    filler = ["#artificialintelligence", "#deeplearning", "#tech", "#innovation", "#coding", "#future"]
    for t in filler:
        if len(tags) >= 10:
            break
        if t not in tags:
            tags.append(t)

    return " ".join(tags)


def _extract_key_facts(summary):
    """Pull 3-5 key facts from a summary for list-style posts."""
    if not summary:
        return []
    import re
    # Better sentence splitting that handles abbreviations
    sentences = re.split(r'(?<=[.!?])\s+', summary)
    # Filter out fragments (less than 20 chars) and clean each
    facts = [s.strip() for s in sentences if len(s.strip()) >= 20]
    # Cap each fact at 200 chars, break at word boundary
    clean_facts = []
    for f in facts[:5]:
        if len(f) > 200:
            f = f[:200].rsplit(' ', 1)[0]
            if not f.endswith('.'):
                f += '.'
        clean_facts.append(f)
    # Sort longest to shortest (Dan Koe visual taper)
    clean_facts.sort(key=len, reverse=True)
    return clean_facts


def generate_caption(article, template="principles"):
    """Generate Instagram caption using OPB framework templates.

    Templates: importance, harsh_truth, principles, pain_resolution, confident_advice
    """
    title = clean_html(article["title"])
    summary = clean_html(article.get("summary", ""))
    source = article["source"]
    mentions = article.get("mentions", [])
    tags = _build_tags(article)
    facts = _extract_key_facts(summary)

    # If no facts extracted, fall back to simple "principles" format
    if not facts and template != "principles":
        template = "principles"

    lines = []

    if template == "importance":
        # WHY THIS MATTERS format
        # Shorten title for hook if it's too long
        short_title = title.split(",")[0].split(".")[0].strip()
        if len(short_title) > 50:
            short_title = short_title[:47] + "..."
        lines.append(f"Why {short_title} matters for builders:")
        lines.append("")
        for f in facts[:5]:
            # Clean up truncated facts
            fact = f.strip()
            if fact and not fact.endswith("."):
                fact += "."
            lines.append(f"- {fact}")
        lines.append("")
        lines.append("News without context is noise.")
        lines.append("Context without action is philosophy.")
        lines.append("Build accordingly.")

    elif template == "harsh_truth":
        # HARSH TRUTH format
        short_title = title.split(",")[0].split(".")[0].strip()
        if len(short_title) > 50:
            short_title = short_title[:47] + "..."
        lines.append(f"Everyone is talking about {short_title}.")
        lines.append("")
        if facts:
            lines.append(f"What they're missing: {facts[0]}")
            lines.append("")
        if len(facts) > 1:
            lines.append(facts[1])
            lines.append("")
        lines.append("Pay attention to what changes. Ignore the noise.")

    elif template == "principles":
        # PRINCIPLES format (default)
        lines.append(title)
        lines.append("")
        if facts:
            for f in facts[:4]:
                lines.append(f"- {f}")
            lines.append("")
        if mentions:
            players = ", ".join(mentions[:3])
            lines.append(f"Key players: {players}")
            lines.append("")
        lines.append(f"via {source}")

    elif template == "pain_resolution":
        # PAIN RESOLUTION format
        lines.append("If you're struggling to keep up with AI news:")
        lines.append("")
        lines.append(title)
        lines.append("")
        if facts:
            lines.append(facts[0])
        lines.append("")
        lines.append("Here's your filter: follow the money, follow the builders.")
        lines.append("Everything else is commentary.")

    elif template == "confident_advice":
        # CONFIDENT ADVICE format
        lines.append(f"What to do about {title}:")
        lines.append("")
        actions = [
            "Read the actual announcement, not the headline",
            "Ask: does this change what I'm building?",
            "If yes, adapt now. If no, keep shipping.",
        ]
        for i, a in enumerate(actions, 1):
            lines.append(f"{i}. {a}")
        lines.append("")
        if facts:
            lines.append(f"Context: {facts[0]}")
            lines.append("")
        lines.append("The best response to any AI news is shipping your own work.")

    else:
        # Fallback: simple format
        lines.append(title)
        lines.append("")
        if summary:
            lines.append(summary[:280])
        lines.append("")
        lines.append(f"via {source}")

    lines.append("")
    lines.append(tags)

    caption = "\n".join(lines)

    # Post-generation Voice Bible check: scan and fix banned words
    caption = _voice_check_caption(caption)

    return caption


def generate_carousel(article):
    """Generate carousel slide text for a news story."""
    title = article["title"]
    summary = article.get("summary", "")
    source = article["source"]
    mentions = article.get("mentions", [])

    slides = []

    # Slide 1: Hook
    slides.append({
        "slide": 1,
        "type": "hook",
        "headline": title.upper() if len(title) < 60 else title[:57].upper() + "...",
        "subtext": "Swipe to learn more ->",
        "label": "NEWS" if article["impact"] == "HIGH" else "UPDATE",
    })

    # Slide 2: What happened
    clean_summary = summary.replace("&#160;", " ").replace("&#8217;", "'").replace("&#32;", " ")
    slides.append({
        "slide": 2,
        "type": "context",
        "headline": "WHAT HAPPENED",
        "body": clean_summary[:250] if clean_summary else "Details emerging. Check the source for the full story.",
    })

    # Slide 3: Who's involved
    if mentions:
        slides.append({
            "slide": 3,
            "type": "players",
            "headline": "KEY PLAYERS",
            "body": "\n".join([f"- {m}" for m in mentions]),
        })

    # Slide 4: Why it matters
    slides.append({
        "slide": len(slides) + 1,
        "type": "analysis",
        "headline": "WHY IT MATTERS",
        "body": "[Add your take. 1-2 sentences on what this means for builders.]",
    })

    # Slide 5: CTA
    slides.append({
        "slide": len(slides) + 1,
        "type": "cta",
        "headline": "Follow for daily AI news.",
        "body": "Short. Direct. No hype.\nJust what matters.",
    })

    return slides


def list_stories():
    """List today's top stories for selection."""
    stories = get_top_stories(15)
    print(f"\n  Today's Top Stories ({datetime.now().strftime('%Y-%m-%d')})\n")
    for i, s in enumerate(stories, 1):
        impact_marker = "!!!" if s["impact"] == "HIGH" else "**" if s["impact"] == "MEDIUM" else "--"
        mentions = f" [{', '.join(s['mentions'])}]" if s.get("mentions") else ""
        print(f"  {i:2d}. [{impact_marker}] {s['title'][:80]}{mentions}")
        print(f"      {s['source']}")
    print()


def save_post(article, caption, carousel=None):
    """Save generated post to disk."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    slug = article["id"]

    post_data = {
        "article": article,
        "caption": caption,
        "carousel": carousel,
        "generated": datetime.now().isoformat(),
    }

    path = POSTS_DIR / f"post-{today}-{slug}.json"
    with open(path, "w") as f:
        json.dump(post_data, f, indent=2)

    return path


def main():
    parser = argparse.ArgumentParser(description="AI News to Instagram Post Generator (OPB Framework)")
    parser.add_argument("--list", action="store_true", help="List today's stories")
    parser.add_argument("--story", type=int, help="Generate post from story number")
    parser.add_argument("--template", choices=list(OPB_TEMPLATES.keys()), default="principles",
                        help="OPB template: importance, harsh_truth, principles, pain_resolution, confident_advice")
    parser.add_argument("--all-templates", action="store_true", help="Generate all 5 OPB templates for a story")
    parser.add_argument("--carousel", action="store_true", help="Include carousel slides")
    parser.add_argument("--all-high", action="store_true", help="Generate posts for all HIGH impact stories")
    parser.add_argument("--save", action="store_true", help="Save post to disk")

    args = parser.parse_args()

    if args.list:
        list_stories()
        return

    stories = get_top_stories(15)

    # Cycle templates for batch generation
    template_names = list(OPB_TEMPLATES.keys())

    if args.all_high:
        high_stories = [s for s in stories if s["impact"] == "HIGH"]
        print(f"\n  Generating OPB posts for {len(high_stories)} HIGH impact stories...\n")
        for i, story in enumerate(high_stories, 1):
            # Rotate through templates for variety
            tmpl = template_names[i % len(template_names)]
            print(f"  {'=' * 60}")
            print(f"  POST {i}: {story['title'][:55]} [{OPB_TEMPLATES[tmpl]['name']}]")
            print(f"  {'=' * 60}")
            caption = generate_caption(story, template=tmpl)
            print(caption)
            if args.carousel:
                carousel = generate_carousel(story)
                print(f"\n  CAROUSEL SLIDES:")
                for slide in carousel:
                    print(f"  [Slide {slide['slide']}] {slide['headline']}")
                    if slide.get('body'):
                        print(f"  {slide['body'][:100]}")
                    print()
            if args.save:
                path = save_post(story, caption, generate_carousel(story) if args.carousel else None)
                print(f"  Saved: {path}")
            print()
        return

    if args.story:
        if args.story < 1 or args.story > len(stories):
            print(f"  Story {args.story} not found. Use --list to see available stories.")
            return
        story = stories[args.story - 1]
    else:
        if not stories:
            print("  No stories found. Run: python3 ai_news_tracker.py --fetch")
            return
        story = stories[0]

    print(f"\n  {'=' * 60}")
    print(f"  {story['title']}")
    print(f"  {story['source']} | {story['impact']} impact")
    print(f"  {'=' * 60}\n")

    if args.all_templates:
        # Generate all 5 OPB templates for one story
        for tmpl_key, tmpl_info in OPB_TEMPLATES.items():
            print(f"  [{tmpl_info['name'].upper()}] {tmpl_info['desc']}")
            print("  " + "-" * 40)
            caption = generate_caption(story, template=tmpl_key)
            print(caption)
            print()
        if args.save:
            # Save all templates as one post bundle
            all_captions = {k: generate_caption(story, template=k) for k in OPB_TEMPLATES}
            POSTS_DIR.mkdir(parents=True, exist_ok=True)
            path = POSTS_DIR / f"post-{datetime.now().strftime('%Y-%m-%d')}-{story['id']}-all.json"
            with open(path, "w") as f:
                json.dump({"article": story, "templates": all_captions, "generated": datetime.now().isoformat()}, f, indent=2)
            print(f"  Saved all templates: {path}")
    else:
        caption = generate_caption(story, template=args.template)
        print(f"  CAPTION [{OPB_TEMPLATES[args.template]['name']}]:")
        print("  " + "-" * 40)
        print(caption)

        if args.carousel:
            carousel = generate_carousel(story)
            print(f"\n  CAROUSEL SLIDES:")
            print("  " + "-" * 40)
            for slide in carousel:
                print(f"\n  [Slide {slide['slide']} - {slide['type'].upper()}]")
                print(f"  {slide['headline']}")
                if slide.get("body"):
                    for line in slide["body"].split("\n"):
                        print(f"  {line}")
                if slide.get("subtext"):
                    print(f"  {slide['subtext']}")

        if args.save:
            path = save_post(story, caption, generate_carousel(story) if args.carousel else None)
            print(f"\n  Saved: {path}")


if __name__ == "__main__":
    main()
