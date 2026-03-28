#!/usr/bin/env python3
"""
Instagram Carousel Generator v2 -- Apple minimalist + Dan Koe style.

Design philosophy: Steve Jobs calligraphy aesthetic. Clean. Minimal.
No em dashes. Short, direct sentences. Adult reading level.
Occasional Robert Greene shaped text for variety.

Usage:
    python3 carousel_generator.py --from-tracker 1
    python3 carousel_generator.py --from-tracker 1 --theme bone
    python3 carousel_generator.py --from-tracker 1 --shape diamond
    python3 carousel_generator.py "Headline" --body "What happened" --source "TechCrunch"
    python3 carousel_generator.py --list
"""
import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Import text shaper for Robert Greene effect
sys.path.insert(0, str(Path(__file__).parent))
from text_shaper import shape_text

DATA_DIR = Path(__file__).parent.parent / "Ceiba" / "news"
ARTICLES_FILE = DATA_DIR / "articles.json"
CAROUSEL_DIR = DATA_DIR / "carousels"

THEMES = {
    "bone": {
        "bg": "#faf9f6",
        "card": "#ffffff",
        "accent": "#1d1d1f",
        "accent2": "#424245",
        "text": "#1d1d1f",
        "muted": "#86868b",
        "high": "#ff3b30",
        "medium": "#ff9500",
        "gradient": "linear-gradient(180deg, #faf9f6 0%, #f5f5f7 100%)",
        "font": "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    },
    "ink": {
        "bg": "#0a0a0a",
        "card": "#111111",
        "accent": "#f5f5f7",
        "accent2": "#a1a1a6",
        "text": "#f5f5f7",
        "muted": "#6e6e73",
        "high": "#ff453a",
        "medium": "#ff9f0a",
        "gradient": "linear-gradient(180deg, #0a0a0a 0%, #1d1d1f 100%)",
        "font": "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    },
    "slate": {
        "bg": "#1c1c1e",
        "card": "#2c2c2e",
        "accent": "#f5f5f7",
        "accent2": "#98989d",
        "text": "#f5f5f7",
        "muted": "#636366",
        "high": "#ff453a",
        "medium": "#ffd60a",
        "gradient": "linear-gradient(180deg, #1c1c1e 0%, #2c2c2e 100%)",
        "font": "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    },
    "warm": {
        "bg": "#f2efe8",
        "card": "#faf8f3",
        "accent": "#2d2926",
        "accent2": "#5c5650",
        "text": "#2d2926",
        "muted": "#8a8480",
        "high": "#c44536",
        "medium": "#d4a03c",
        "gradient": "linear-gradient(180deg, #f2efe8 0%, #e8e4db 100%)",
        "font": "'Georgia', 'Times New Roman', serif",
    },
}


def load_stories(n=15):
    if ARTICLES_FILE.exists():
        with open(ARTICLES_FILE) as f:
            articles = json.load(f)
        articles.sort(key=lambda a: a.get("impact_score", 0), reverse=True)
        return articles[:n]
    return []


def clean_text(text):
    """Clean HTML entities and em dashes."""
    replacements = {
        "&#160;": " ", "&#8217;": "'", "&#8220;": '"', "&#8221;": '"',
        "&#32;": " ", "&#8212;": ".", "&#8211;": ".", "&mdash;": ".",
        "&ndash;": ".", "\u2014": ".", "\u2013": ".",
        "&amp;": "&", "&lt;": "<", "&gt;": ">",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Clean double periods from em dash replacement
    while ".." in text:
        text = text.replace("..", ".")
    return text.strip()


def generate_shaped_slide_html(text, shape_name, t):
    """Generate a slide with Robert Greene shaped text."""
    shaped = shape_text(text, shape=shape_name, max_width=42, center=True)
    lines_html = ""
    for line in shaped.split("\n"):
        escaped = line.replace(" ", "&nbsp;")
        lines_html += f'<div class="shape-line">{escaped}</div>\n'

    return f"""
    <div class="slide shaped-slide">
        <div class="slide-inner">
            <div class="shaped-text">{lines_html}</div>
        </div>
        <div class="brand-mark"></div>
    </div>"""


def generate_carousel_html(headline, body="", source="", impact="HIGH",
                           why_matters="", key_players=None, theme_name="ink",
                           brand_name="", shape_text_content="", shape_name="diamond"):
    """Generate Apple-minimal carousel."""
    t = THEMES.get(theme_name, THEMES["ink"])
    CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)

    impact_color = t["high"] if impact == "HIGH" else t["medium"] if impact == "MEDIUM" else t["muted"]
    headline_clean = clean_text(headline)
    body_clean = clean_text(body)

    # Build players slide
    players_html = ""
    if key_players:
        # Sort longest to shortest for visual taper effect
        sorted_players = sorted(key_players, key=len, reverse=True)
        items = "".join(f'<div class="player-name">{p}</div>' for p in sorted_players)
        players_html = f"""
    <div class="slide">
        <div class="slide-inner">
            <div class="section-label">Who</div>
            <div class="players">{items}</div>
        </div>
        <div class="brand-mark"></div>
    </div>"""

    # Build why slide
    why_html = ""
    if why_matters:
        why_clean = clean_text(why_matters)
        why_html = f"""
    <div class="slide">
        <div class="slide-inner">
            <div class="section-label">Why it matters</div>
            <p class="body-text">{why_clean}</p>
        </div>
        <div class="brand-mark"></div>
    </div>"""

    # Build shaped text slide (Robert Greene style, occasional)
    shaped_html = ""
    if shape_text_content:
        shaped_html = generate_shaped_slide_html(shape_text_content, shape_name, t)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{headline_clean[:50]}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
    font-family:{t['font']};
    background:#000;
    display:flex;flex-wrap:wrap;gap:24px;padding:24px;justify-content:center;
}}

.slide{{
    width:1080px;height:1080px;
    background:{t['gradient']};
    position:relative;
    display:flex;align-items:center;justify-content:center;
    flex-shrink:0;
}}
.slide-inner{{
    padding:100px;
    width:100%;
    z-index:1;
}}

/* Typography - Apple style, readable on mobile */
.headline{{
    font-family:'Playfair Display','Georgia',serif;
    font-size:64px;
    font-weight:700;
    color:{t['text']};
    line-height:1.15;
    letter-spacing:-0.5px;
    margin-bottom:40px;
}}
.impact-dot{{
    display:inline-block;
    width:12px;height:12px;
    border-radius:50%;
    background:{impact_color};
    margin-right:16px;
    vertical-align:middle;
}}
.source-text{{
    font-family:'Inter',sans-serif;
    font-size:14px;
    color:{t['muted']};
    letter-spacing:2px;
    text-transform:uppercase;
    margin-bottom:48px;
}}
.section-label{{
    font-family:'Inter',sans-serif;
    font-size:13px;
    color:{t['muted']};
    letter-spacing:3px;
    text-transform:uppercase;
    margin-bottom:32px;
}}
.body-text{{
    font-size:34px;
    color:{t['text']};
    line-height:1.6;
    font-weight:400;
}}
.swipe-hint{{
    position:absolute;
    bottom:60px;right:100px;
    font-family:'Inter',sans-serif;
    font-size:13px;
    color:{t['muted']};
    letter-spacing:2px;
}}

/* Players */
.players{{
    display:flex;flex-direction:column;gap:20px;
}}
.player-name{{
    font-size:38px;
    font-weight:600;
    color:{t['text']};
    padding:20px 0;
    border-bottom:1px solid {t['muted']}30;
}}

/* CTA */
.cta-text{{
    font-family:'Playfair Display','Georgia',serif;
    font-size:48px;
    font-weight:500;
    color:{t['accent']};
    line-height:1.3;
    margin-bottom:24px;
}}
.cta-sub{{
    font-size:18px;
    color:{t['muted']};
    line-height:1.8;
    font-weight:300;
}}

/* Brand mark */
.brand-mark{{
    position:absolute;
    top:50px;left:100px;
    width:8px;height:8px;
    border-radius:50%;
    background:{t['accent']};
}}

/* Shaped text (Robert Greene) */
.shaped-text{{
    font-family:'Playfair Display','Georgia',serif;
    font-size:20px;
    color:{t['text']};
    line-height:1.8;
    white-space:pre;
    text-align:center;
}}
.shape-line{{
    font-size:22px;
    letter-spacing:0.5px;
}}
.shaped-slide .slide-inner{{
    display:flex;align-items:center;justify-content:center;
}}

@media print{{
    body{{background:#000}}
    .slide{{page-break-after:always;margin:0}}
}}
</style>
</head>
<body>

<!-- SLIDE 1: HOOK -->
<div class="slide">
    <div class="slide-inner">
        <div class="source-text"><span class="impact-dot"></span>{source}</div>
        <h1 class="headline">{headline_clean}</h1>
    </div>
    <div class="brand-mark"></div>
    <div class="swipe-hint">SWIPE</div>
</div>

<!-- SLIDE 2: WHAT HAPPENED -->
<div class="slide">
    <div class="slide-inner">
        <div class="section-label">What happened</div>
        <p class="body-text">{body_clean if body_clean else 'Details still emerging.'}</p>
    </div>
    <div class="brand-mark"></div>
</div>

{players_html}
{why_html}
{shaped_html}

<!-- SLIDE FINAL: CTA -->
<div class="slide">
    <div class="slide-inner" style="display:flex;flex-direction:column;justify-content:center;height:100%">
        <div class="cta-text">Follow for<br>daily AI news.</div>
        <p class="cta-sub">Short. Direct. No hype.<br>Just what matters.</p>
    </div>
    <div class="brand-mark"></div>
</div>

</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Instagram Carousel Generator v2 (Apple minimal)")
    parser.add_argument("headline", nargs="?", help="Carousel headline")
    parser.add_argument("--body", default="", help="What happened")
    parser.add_argument("--source", default="", help="News source")
    parser.add_argument("--impact", default="HIGH", choices=["HIGH", "MEDIUM", "LOW"])
    parser.add_argument("--why", default="", help="Why it matters")
    parser.add_argument("--players", nargs="*", help="Key players")
    parser.add_argument("--theme", default="ink", choices=list(THEMES.keys()))
    parser.add_argument("--brand", default="", help="Brand name")
    parser.add_argument("--shape", default="", help="Robert Greene shape for one slide (diamond, hourglass, vase)")
    parser.add_argument("--shape-text", default="", help="Text to shape (Robert Greene style)")
    parser.add_argument("--from-tracker", type=int, help="Story # from news tracker")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--open", action="store_true")

    args = parser.parse_args()

    if args.list:
        stories = load_stories(15)
        print(f"\n  Stories available:\n")
        for i, s in enumerate(stories, 1):
            m = "!!!" if s["impact"] == "HIGH" else "**" if s["impact"] == "MEDIUM" else "--"
            print(f"  {i:2d}. [{m}] {s['title'][:70]}")
            print(f"      {s['source']}")
        return

    headline = args.headline
    body = args.body
    source = args.source
    impact = args.impact
    players = args.players
    why = args.why

    if args.from_tracker:
        stories = load_stories(20)
        if args.from_tracker < 1 or args.from_tracker > len(stories):
            print(f"  Story {args.from_tracker} not found.")
            return
        story = stories[args.from_tracker - 1]
        headline = story["title"]
        body = story.get("summary", "")
        source = story["source"]
        impact = story["impact"]
        players = story.get("mentions", []) or None

    if not headline:
        parser.print_help()
        return

    CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)

    html = generate_carousel_html(
        headline=headline, body=body, source=source, impact=impact,
        why_matters=why, key_players=players, theme_name=args.theme,
        brand_name=args.brand,
        shape_text_content=args.shape_text, shape_name=args.shape or "diamond",
    )

    slug = headline[:40].lower().replace(" ", "-").replace("/", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = CAROUSEL_DIR / f"carousel-{today}-{slug}.html"

    with open(filepath, "w") as f:
        f.write(html)

    print(f"\n  Carousel: {filepath}")
    print(f"  Theme: {args.theme}")
    if args.shape_text:
        print(f"  Shape: {args.shape or 'diamond'}")
    print(f"  Open in browser, screenshot each 1080x1080 slide")

    if args.open:
        os.system(f"open '{filepath}'")


if __name__ == "__main__":
    main()
