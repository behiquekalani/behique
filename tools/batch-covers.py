#!/usr/bin/env python3
"""
Batch Cover/Thumbnail Generator
Creates cover.html and thumbnail.html for products missing them.
Screenshot with Brave --force-device-scale-factor=2 to get 2x images.
"""

import os
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
PRODUCTS_DIR = REPO / "READY-TO-SELL/products-organized"

# Product display names for covers (slug -> display info)
PRODUCT_INFO = {
    "roblox-guide": {"title": "ROBLOX\nBUILDER'S\nGUIDE", "modules": ["Roblox Studio", "Lua Scripting", "UI Design", "Game Mechanics", "Monetization"], "quote": "Build games. Make money. On Roblox."},
    "3d-fashion": {"title": "3D FASHION\nDESIGN\nGUIDE", "modules": ["Marvelous Designer", "ZBrush", "Retopology", "Texturing", "Export"], "quote": "Design clothes for games, VTubers, and fashion."},
    "self-hosted-store": {"title": "SELF-HOSTED\nSTORE\nGUIDE", "modules": ["HTML Pages", "Gumroad Payments", "Free Hosting", "No Monthly Fees"], "quote": "Stop paying $29/month for Shopify."},
    "social-pipeline": {"title": "SOCIAL MEDIA\nPIPELINE\nGUIDE", "modules": ["RSS Automation", "Instagram Posts", "Carousel Gen", "Hashtags"], "quote": "Automate your content. Post forever."},
    "ai-news-tracker": {"title": "AI NEWS\nTRACKER\nGUIDE", "modules": ["18 RSS Feeds", "Impact Scoring", "Entity Tracking", "HTML Digests"], "quote": "Build your own AI news system."},
    "solopreneur-os": {"title": "SOLOPRENEUR\nOPERATING\nSYSTEM", "modules": ["Vision Builder", "Domain Stack", "Content Engine", "Monetization", "Daily Ops"], "quote": "The system for ADHD builders."},
    "behike-method": {"title": "THE BEHIKE\nMETHOD\nV2", "modules": ["Vision Layer", "Domain Stacking", "ADHD Edge", "Content Waterfall", "AI Engine", "Value Ladder", "Ship It"], "quote": "100+ products in 2 weeks. This is how."},
    "ai-copywriting": {"title": "AI\nCOPYWRITING\nPLAYBOOK", "modules": ["Headlines", "Emails", "Product Desc", "Social Posts", "Ad Copy"], "quote": "Write copy that sells. With AI."},
    "fl-studio-ai": {"title": "FL STUDIO\nAI PRODUCTION\nGUIDE", "modules": ["Sample Gen", "Melody Creation", "Mixing", "Mastering", "Workflow"], "quote": "Make beats faster with AI."},
    "niche-sniper": {"title": "NICHE\nSNIPER\nGUIDE", "modules": ["Research Framework", "Validation", "Competition Analysis", "Data-First"], "quote": "Find profitable niches before everyone."},
    "prompt-cheatsheet": {"title": "PROMPT\nENGINEERING\nCHEAT SHEET", "modules": ["Chain of Thought", "Few-Shot", "Role-Playing", "System Prompts", "Templates"], "quote": "Every prompt framework. One sheet."},
    "linkedin-growth": {"title": "LINKEDIN\nGROWTH\nPLAYBOOK", "modules": ["Profile Optimization", "Content Strategy", "Connections", "Engagement"], "quote": "Grow on LinkedIn without being cringe."},
    "personal-brand": {"title": "PERSONAL\nBRAND\nBLUEPRINT", "modules": ["Positioning", "Content Pillars", "Audience Building", "Monetization"], "quote": "A brand that makes money, not just likes."},
    "email-list": {"title": "EMAIL LIST\nACCELERATOR", "modules": ["Lead Magnets", "Opt-in Pages", "Welcome Sequence", "Monetization"], "quote": "The list is the asset."},
    "faceless-creator": {"title": "FACELESS\nCREATOR\nBLUEPRINT", "modules": ["AI Voiceovers", "Stock Footage", "Auto Editing", "Faceless YouTube"], "quote": "Create without showing your face."},
    "gumroad-playbook": {"title": "GUMROAD\nSELLER'S\nPLAYBOOK", "modules": ["Product Creation", "Pricing", "Descriptions", "Covers", "SEO", "Promotions"], "quote": "What actually works on Gumroad."},
    "freelance-clients": {"title": "FREELANCE\nCLIENT\nACQUISITION", "modules": ["Inbound Strategy", "Portfolio", "Pricing", "Proposals"], "quote": "Get clients. Not anxiety."},
    "amazon-fba": {"title": "AMAZON FBA\nSTARTER\nGUIDE", "modules": ["Product Research", "Suppliers", "Listings", "PPC Basics"], "quote": "Start your Amazon business."},
    "affiliate-marketing": {"title": "AFFILIATE\nMARKETING\nBLUEPRINT", "modules": ["Niche Selection", "Content Strategy", "Link Optimization", "Traffic"], "quote": "Earn while you recommend."},
}


def generate_cover_html(slug, info):
    """Generate cover HTML (1280x720)."""
    title_lines = info["title"].split("\n")
    title_html = "<br>".join(title_lines)
    modules_html = "".join(f'<span class="mod">{m}</span>' for m in info["modules"])
    quote = info["quote"]

    # Create strikethrough pain points based on product
    pains = [
        "Another 40-hour course",
        "Generic advice that doesn't work",
        "Overpriced fluff with no system"
    ]

    pains_html = "".join(f'<div class="pain">{p}</div>' for p in pains)

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1280px; height: 720px; background: #0a0a0a; color: #e0e0e0;
    font-family: 'Inter', sans-serif; display: flex; flex-direction: column;
    justify-content: center; padding: 60px 80px; overflow: hidden; position: relative;
  }}
  .quote {{ font-size: 18px; color: #888; font-style: italic; margin-bottom: 16px; }}
  .pain {{ text-decoration: line-through; color: #555; font-size: 15px; margin: 3px 0; }}
  .title {{ font-size: 38px; font-weight: 900; color: #fff; margin: 16px 0 8px; line-height: 1.1; }}
  .cyan-line {{ width: 80px; height: 3px; background: #00e5ff; margin-bottom: 16px; }}
  .modules {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .mod {{ background: #111; border: 1px solid #1a1a1a; padding: 5px 12px; border-radius: 4px; font-size: 12px; color: #aaa; }}
  .brand {{ position: absolute; bottom: 30px; right: 40px; font-size: 11px; color: #333; letter-spacing: 3px; text-transform: uppercase; }}
</style></head><body>
  <div class="quote">"{quote}"</div>
  {pains_html}
  <div class="title">{title_html}</div>
  <div class="cyan-line"></div>
  <div class="modules">{modules_html}</div>
  <div class="brand">BEHIKE</div>
</body></html>"""


def generate_thumbnail_html(slug, info):
    """Generate thumbnail HTML (600x600)."""
    # Use first 2-3 words of title for thumbnail
    title_lines = info["title"].split("\n")
    title_html = "<br>".join(title_lines[:2])  # Max 2 lines for thumbnail

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;900&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 600px; height: 600px; background: #0a0a0a; color: #fff;
    font-family: 'Inter', sans-serif; display: flex; flex-direction: column;
    justify-content: center; align-items: center; text-align: center;
    padding: 60px; overflow: hidden;
  }}
  .title {{ font-size: 36px; font-weight: 900; line-height: 1.15; margin-bottom: 16px; }}
  .cyan-line {{ width: 60px; height: 3px; background: #00e5ff; margin-bottom: 20px; }}
  .brand {{ font-size: 11px; color: #333; letter-spacing: 4px; text-transform: uppercase; }}
</style></head><body>
  <div class="title">{title_html}</div>
  <div class="cyan-line"></div>
  <div class="brand">BEHIKE</div>
</body></html>"""


def main():
    print(f"\n{'='*50}")
    print(f"  BATCH COVER/THUMBNAIL GENERATOR")
    print(f"{'='*50}\n")

    created_covers = 0
    created_thumbs = 0

    for slug, info in PRODUCT_INFO.items():
        folder = PRODUCTS_DIR / slug
        if not folder.exists():
            print(f"  SKIP: {slug} (folder missing)")
            continue

        # Generate cover
        cover_html = folder / "cover.html"
        if not (folder / "cover.png").exists():
            cover_html.write_text(generate_cover_html(slug, info))
            created_covers += 1
            print(f"  COVER: {slug}")

        # Generate thumbnail
        thumb_html = folder / "thumbnail.html"
        if not (folder / "thumbnail.png").exists():
            thumb_html.write_text(generate_thumbnail_html(slug, info))
            created_thumbs += 1
            print(f"  THUMB: {slug}")

    print(f"\n  Covers created: {created_covers}")
    print(f"  Thumbnails created: {created_thumbs}")
    print(f"\n  To render PNGs, open each .html in Brave and screenshot at 2x:")
    print(f"  /Applications/Brave\\ Browser.app/Contents/MacOS/Brave\\ Browser --force-device-scale-factor=2 <file>")
    print(f"\n  Or use the batch screenshot script:")
    print(f"  python3 tools/batch-screenshot.py")


if __name__ == "__main__":
    main()
