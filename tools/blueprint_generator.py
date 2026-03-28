#!/usr/bin/env python3
"""
SVG Blueprint Generator — runs on Cobo/Naboria with Ollama.
Generates sellable business blueprint SVGs without using Claude credits.

Usage:
    python3 tools/blueprint_generator.py "Real Estate Investing"
    python3 tools/blueprint_generator.py "Podcast Business"
    python3 tools/blueprint_generator.py --batch niches.txt
    python3 tools/blueprint_generator.py --list  # show built-in niches
"""

import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "READY-TO-SELL"
OUTPUT_DIR.mkdir(exist_ok=True)

# Ollama endpoints to try (Ceiba first, then Cobo)
OLLAMA_URLS = [
    "http://localhost:11434",
    "http://192.168.0.145:11434",
    "http://192.168.0.151:11434",
]

BUILT_IN_NICHES = [
    "Real Estate Investing",
    "Podcast Business",
    "Print on Demand",
    "Affiliate Marketing",
    "Online Course Creator",
    "Social Media Agency",
    "Mobile App Business",
    "Consulting Practice",
    "Etsy Store",
    "Amazon FBA",
    "Photography Business",
    "Fitness Coaching",
    "Wedding Planning",
    "Food Truck Business",
    "Property Management",
    "Bookkeeping Service",
    "Virtual Assistant Agency",
    "Web Design Agency",
    "Stock Trading",
    "Crypto Trading",
]


def find_ollama():
    """Find a working Ollama instance."""
    for url in OLLAMA_URLS:
        try:
            req = Request(f"{url}/api/tags", headers={"User-Agent": "BIOS/1.0"})
            with urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return url
        except Exception:
            continue
    return None


def ask_ollama(url, prompt, model="qwen2.5:7b"):
    """Send prompt to Ollama and get response."""
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2000}
    }).encode()
    req = Request(f"{url}/api/generate", data=data,
                  headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    return result.get("response", "")


def generate_sections(ollama_url, niche):
    """Use Ollama to generate 8 business sections for the niche."""
    prompt = f"""Generate exactly 8 business sections for a "{niche}" business blueprint.
For each section, provide:
- Section title (2-4 words)
- 4-6 bullet points of key items

Format as JSON array:
[{{"title": "SECTION NAME", "items": ["item 1", "item 2", "item 3", "item 4"]}}]

Only output the JSON, nothing else. Keep items short (under 40 chars each)."""

    response = ask_ollama(ollama_url, prompt)

    # Try to parse JSON from response
    try:
        # Find JSON in response
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception:
        pass

    # Fallback: generic sections
    return [
        {"title": "GETTING STARTED", "items": ["Define your niche", "Set up accounts", "Initial investment", "Legal requirements"]},
        {"title": "PRODUCT/SERVICE", "items": ["Core offering", "Pricing strategy", "Unique value prop", "Quality standards"]},
        {"title": "MARKETING", "items": ["Social media", "Content strategy", "Paid ads", "Referrals", "SEO"]},
        {"title": "OPERATIONS", "items": ["Daily workflow", "Tools needed", "Automation", "Quality control"]},
        {"title": "FINANCES", "items": ["Startup costs", "Revenue streams", "Break-even point", "Profit margins"]},
        {"title": "GROWTH", "items": ["Scaling strategy", "Hiring plan", "Partnerships", "New markets"]},
        {"title": "METRICS", "items": ["KPIs to track", "Monthly goals", "Quarterly review", "Annual targets"]},
        {"title": "SCHEDULE", "items": ["Daily tasks", "Weekly reviews", "Monthly planning", "Quarterly strategy"]},
    ]


def build_svg(niche, sections):
    """Generate the SVG file from sections."""
    slug = niche.lower().replace(" ", "-").replace("/", "-")
    title = niche.upper()

    # Layout positions for 8 sections (2 rows of 4)
    positions = [
        (80, 180, 520, 380),    # top-left
        (680, 180, 520, 380),   # top-center-left
        (1280, 180, 520, 380),  # top-center-right
        (1880, 180, 520, 380),  # top-right (narrower to fit)
        (80, 700, 520, 380),    # bottom-left
        (680, 700, 520, 380),   # bottom-center-left
        (1280, 700, 520, 380),  # bottom-center-right
        (1880, 700, 520, 380),  # bottom-right
    ]

    svg_parts = []
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 1800" width="2400" height="1800">
<style>
  text {{ font-family: 'Courier New', monospace; fill: #ffffff; }}
  .title {{ font-size: 42px; font-weight: bold; letter-spacing: 4px; }}
  .subtitle {{ font-size: 14px; fill: #999999; }}
  .section-title {{ font-size: 16px; font-weight: bold; letter-spacing: 2px; }}
  .item {{ font-size: 11px; fill: #cccccc; }}
  .checkbox {{ font-size: 11px; fill: #666666; }}
  rect.section {{ fill: none; stroke: #ffffff; stroke-width: 1; }}
  rect.bg {{ fill: #000000; }}
  line.connector {{ stroke: #333333; stroke-width: 0.5; stroke-dasharray: 4,4; }}
  .tracker-header {{ font-size: 10px; fill: #666666; font-weight: bold; }}
  .tracker-cell {{ font-size: 9px; fill: #444444; }}
</style>
<rect class="bg" width="2400" height="1800"/>

<!-- Title -->
<text class="title" x="1200" y="70" text-anchor="middle">{title}</text>
<text class="subtitle" x="1200" y="95" text-anchor="middle">BUSINESS BLUEPRINT</text>
<line x1="400" y1="110" x2="2000" y2="110" stroke="#333" stroke-width="0.5"/>
''')

    # Render sections
    for i, section in enumerate(sections[:8]):
        x, y, w, h = positions[i]
        sect_title = section.get("title", f"SECTION {i+1}").upper()
        items = section.get("items", [])

        svg_parts.append(f'''
<!-- Section {i+1}: {sect_title} -->
<rect class="section" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>
<text class="section-title" x="{x+15}" y="{y+25}">{sect_title}</text>
<line x1="{x+15}" y1="{y+32}" x2="{x+w-15}" y2="{y+32}" stroke="#333" stroke-width="0.5"/>
''')
        for j, item in enumerate(items[:8]):
            iy = y + 50 + j * 22
            item_text = item[:45].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            svg_parts.append(f'<text class="checkbox" x="{x+15}" y="{iy}">[ ]</text>')
            svg_parts.append(f'<text class="item" x="{x+40}" y="{iy}">{item_text}</text>')

    # Connecting lines between sections
    for i in range(3):
        x1 = positions[i][0] + positions[i][2]
        y1 = positions[i][1] + positions[i][3] // 2
        x2 = positions[i+1][0]
        y2 = positions[i+1][1] + positions[i+1][3] // 2
        svg_parts.append(f'<line class="connector" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    for i in range(4, 7):
        x1 = positions[i][0] + positions[i][2]
        y1 = positions[i][1] + positions[i][3] // 2
        x2 = positions[i+1][0]
        y2 = positions[i+1][1] + positions[i+1][3] // 2
        svg_parts.append(f'<line class="connector" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    # Vertical connectors
    for i in range(4):
        x1 = positions[i][0] + positions[i][2] // 2
        y1 = positions[i][1] + positions[i][3]
        x2 = positions[i+4][0] + positions[i+4][2] // 2
        y2 = positions[i+4][1]
        svg_parts.append(f'<line class="connector" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    # Revenue tracker
    svg_parts.append('''
<!-- Revenue Tracker -->
<text class="section-title" x="80" y="1160">REVENUE TRACKER</text>
<line x1="80" y1="1168" x2="2320" y2="1168" stroke="#333" stroke-width="0.5"/>
''')
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    for i, m in enumerate(months):
        mx = 200 + i * 175
        svg_parts.append(f'<text class="tracker-header" x="{mx}" y="1190">{m}</text>')
        svg_parts.append(f'<text class="tracker-cell" x="{mx}" y="1210">$_____</text>')

    # Legend
    svg_parts.append('''
<text class="subtitle" x="2300" y="1760" text-anchor="end">[ ] Not started   [x] Done</text>
<text class="subtitle" x="2300" y="1780" text-anchor="end">behike.co</text>
''')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts), slug


def main():
    if "--list" in sys.argv:
        print("Built-in niches:")
        for n in BUILT_IN_NICHES:
            print(f"  - {n}")
        return

    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        if idx + 1 < len(sys.argv):
            batch_file = Path(sys.argv[idx + 1])
            if batch_file.exists():
                niches = [l.strip() for l in batch_file.read_text().splitlines() if l.strip()]
            else:
                print(f"File not found: {batch_file}")
                return
        else:
            niches = BUILT_IN_NICHES
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        niches = [" ".join(sys.argv[1:])]
    else:
        print("Usage:")
        print('  python3 tools/blueprint_generator.py "Niche Name"')
        print('  python3 tools/blueprint_generator.py --batch niches.txt')
        print('  python3 tools/blueprint_generator.py --list')
        return

    # Find Ollama
    ollama_url = find_ollama()
    use_ai = ollama_url is not None

    if use_ai:
        print(f"  Ollama found at {ollama_url}")
    else:
        print("  No Ollama found. Using template sections (still produces valid SVGs).")

    for niche in niches:
        print(f"\n  Building: {niche}")

        if use_ai:
            try:
                sections = generate_sections(ollama_url, niche)
                print(f"    AI generated {len(sections)} sections")
            except Exception as e:
                print(f"    AI failed ({e}), using template")
                sections = None
        else:
            sections = None

        if not sections:
            sections = generate_sections(None, niche) if not use_ai else None
            if not sections:
                sections = [
                    {"title": "GETTING STARTED", "items": ["Define scope", "Set up accounts", "Initial budget", "Legal setup"]},
                    {"title": "CORE OFFERING", "items": ["Main product/service", "Pricing", "Value proposition", "Delivery method"]},
                    {"title": "MARKETING", "items": ["Social media", "Content", "Paid ads", "Referrals", "SEO"]},
                    {"title": "OPERATIONS", "items": ["Daily workflow", "Tools", "Automation", "Quality"]},
                    {"title": "FINANCES", "items": ["Costs", "Revenue streams", "Break-even", "Margins"]},
                    {"title": "GROWTH", "items": ["Scale plan", "Hiring", "Partnerships", "Expansion"]},
                    {"title": "METRICS", "items": ["KPIs", "Monthly goals", "Reviews", "Targets"]},
                    {"title": "SCHEDULE", "items": ["Daily", "Weekly", "Monthly", "Quarterly"]},
                ]

        svg_content, slug = build_svg(niche, sections)
        output_file = OUTPUT_DIR / f"blueprint-{slug}.svg"
        output_file.write_text(svg_content)
        print(f"    Saved: {output_file.name}")

    print(f"\n  Done. {len(niches)} blueprint(s) generated.")


if __name__ == "__main__":
    main()


def export_llm_ready(niche, sections, output_dir=None):
    """Export blueprint data as LLM-ready markdown for enhancement by Claude/Gemini/ChatGPT."""
    slug = niche.lower().replace(" ", "-").replace("/", "-")
    out = output_dir or OUTPUT_DIR
    llm_file = Path(out) / f"blueprint-{slug}-llm-enhance.md"

    lines = [
        f"# {niche.upper()} BUSINESS BLUEPRINT",
        f"# LLM Enhancement Prompt",
        f"# Generated: {datetime.now().isoformat()}",
        "",
        "## Instructions for LLM",
        "Enhance this business blueprint into a premium, detailed guide.",
        "For each section, expand the bullet points into 2-3 sentences of actionable advice.",
        "Add specific tools, metrics, and examples. Keep tone direct, no fluff.",
        "Output as clean markdown ready to convert to PDF.",
        "",
        "## Blueprint Data",
        "",
    ]

    for i, section in enumerate(sections[:8]):
        title = section.get("title", f"SECTION {i+1}").upper()
        items = section.get("items", [])
        lines.append(f"### {title}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend([
        "## Enhancement Requirements",
        f"- Target audience: solopreneurs starting a {niche.lower()} business",
        "- Include specific dollar amounts, tools, and timelines",
        "- Add a 90-day launch plan at the end",
        "- Add a monthly revenue projection table",
        "- Keep under 3000 words total",
        f"- Title the output: '{niche} Business Blueprint - Complete Guide'",
    ])

    llm_file.write_text("\n".join(lines))
    return llm_file


# Patch main to also generate LLM files
_original_main = main

def patched_main():
    _original_main()
    # Also generate LLM-ready files for batch runs
    if "--llm" in sys.argv:
        ollama_url = find_ollama()
        niches = BUILT_IN_NICHES if "--batch" in sys.argv else [" ".join(a for a in sys.argv[1:] if not a.startswith("--"))]
        for niche in niches:
            if not niche:
                continue
            sections = generate_sections(ollama_url, niche) if ollama_url else None
            if not sections:
                sections = [{"title": "SECTION", "items": ["item"]}]
            f = export_llm_ready(niche, sections)
            print(f"  LLM file: {f.name}")

main = patched_main
