#!/usr/bin/env python3
"""
Gumroad Product Upload Helper
Scans READY-TO-SELL/, categorizes products, assigns pricing,
and generates upload manifests for manual Gumroad listing.

Usage: python3 tools/gumroad_uploader.py
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

READY_DIR = Path(__file__).resolve().parent.parent / "READY-TO-SELL"
MANIFEST_PATH = READY_DIR / "GUMROAD_UPLOAD_MANIFEST.md"
QUICK_LIST_PATH = READY_DIR / "QUICK_LIST_ORDER.md"

# Files to skip (not products)
SKIP_FILES = {
    ".audit-note", "README.md", "GUMROAD_BLUEPRINT_LISTING.md",
    "GUMROAD_UPLOAD_MANIFEST.md", "QUICK_LIST_ORDER.md", ".DS_Store",
}

SELLABLE_EXTENSIONS = {".pdf", ".svg", ".xlsx", ".zip"}


# --- Pricing rules (order matters, first match wins) ---

def get_price(filename):
    fl = filename.lower()
    if fl.startswith("behike-operating-system"):
        return 97.00
    if fl.startswith("blueprint-") and (fl.endswith(".pdf") or fl.endswith(".svg")):
        return 19.99
    if fl.endswith("-kit.pdf"):
        return 19.99
    if fl.endswith("-guide.pdf"):
        return 9.99
    if fl.endswith("-playbook.pdf"):
        return 9.99
    if fl.endswith("-checklist.pdf"):
        return 0.00
    if fl.endswith(".xlsx"):
        return 7.99
    return 4.99


# --- Category detection ---

def get_category(filename):
    fl = filename.lower()
    if fl.startswith("behike-operating-system"):
        return "operating-system"
    if fl.startswith("blueprint-"):
        return "blueprint"
    if "-kit" in fl:
        return "kit"
    if "-guide" in fl:
        return "guide"
    if "-playbook" in fl:
        return "playbook"
    if "-checklist" in fl:
        return "free"
    if "-template" in fl or fl.endswith(".xlsx"):
        return "template"
    if "-blueprint" in fl:
        return "blueprint"
    if "-course" in fl:
        return "course"
    if fl.endswith(".zip"):
        return "template"
    return "guide"


# --- Title cleaning ---

def clean_title(filename):
    name = Path(filename).stem
    # Remove version suffixes like -v2, -v3
    # Keep -es suffix for Spanish versions
    words = name.replace("-", " ").replace("_", " ").split()
    titled = []
    # Acronyms and special words to keep uppercase
    upper_words = {"ai", "os", "fba", "diy", "n8n", "3d", "fl", "adhd", "saas", "seo", "npc"}
    keep_lower = {"for", "and", "the", "to", "of", "a", "in", "on", "with"}
    for i, w in enumerate(words):
        if w.lower() in upper_words:
            titled.append(w.upper())
        elif w.lower() == "es" and i == len(words) - 1:
            titled.append("(Espanol)")
        elif w.lower() == "v2":
            titled.append("V2")
        elif w.lower() == "v3":
            titled.append("V3")
        elif w.lower() == "behike":
            titled.append("Behike")
        elif w.lower() == "ebay":
            titled.append("eBay")
        elif w.lower() == "facebook" or w.lower() == "fb" or w.lower() == "fbmarketplace":
            titled.append("FB Marketplace" if "marketplace" in w.lower() or w.lower() == "fbmarketplace" else w.capitalize())
        elif w.lower() == "linkedin":
            titled.append("LinkedIn")
        elif w.lower() == "youtube":
            titled.append("YouTube")
        elif w.lower() == "roblox":
            titled.append("Roblox")
        elif w.lower() == "claude":
            titled.append("Claude")
        elif w.lower() == "gumroad":
            titled.append("Gumroad")
        elif w.lower() == "etsy":
            titled.append("Etsy")
        elif w.lower() == "polymarket":
            titled.append("Polymarket")
        elif i == 0 or w.lower() not in keep_lower:
            titled.append(w.capitalize())
        else:
            titled.append(w.lower())
    return " ".join(titled)


# --- Description generator ---

DESCRIPTIONS = {
    "operating-system": "The complete Behike Operating System. A visual framework that maps your entire business, content engine, and revenue streams into one actionable system. Print it, pin it, build from it.",
    "blueprint": "A step-by-step visual blueprint you can follow from zero to launch. Every phase, every milestone, every tool mapped out so you never wonder what comes next.",
    "kit": "A ready-to-use kit packed with templates, frameworks, and action steps. Stop planning, start executing.",
    "guide": "A practical, no-fluff guide that walks you through exactly what to do, what tools to use, and how to get results fast.",
    "playbook": "A tactical playbook with proven strategies and real examples. Follow the plays, skip the guesswork.",
    "free": "A free resource to get you started. Download it, use it, share it.",
    "template": "A plug-and-play template you can customize immediately. Save hours of setup time.",
    "course": "A structured learning path that takes you from beginner to confident practitioner.",
}


def generate_description(title, category, filename):
    base = DESCRIPTIONS.get(category, DESCRIPTIONS["guide"])
    return base


# --- Tag generator ---

def generate_tags(filename, category):
    tags = set()
    fl = filename.lower()

    # Always add category
    tags.add(category)

    # Topic detection
    topic_map = {
        "ai": ["ai", "artificial intelligence", "automation"],
        "ecommerce": ["ecommerce", "online store", "selling"],
        "ebay": ["ebay", "dropshipping", "reselling"],
        "content": ["content creation", "social media"],
        "freelance": ["freelancing", "clients", "services"],
        "youtube": ["youtube", "video", "creator"],
        "newsletter": ["newsletter", "email", "subscribers"],
        "saas": ["saas", "software", "startup"],
        "podcast": ["podcast", "audio", "creator"],
        "crypto": ["crypto", "investing", "trading"],
        "real-estate": ["real estate", "investing", "property"],
        "coaching": ["coaching", "consulting", "services"],
        "dropshipping": ["dropshipping", "ecommerce", "selling"],
        "brand": ["personal brand", "branding", "marketing"],
        "budget": ["budget", "finance", "money"],
        "adhd": ["adhd", "productivity", "focus"],
        "automation": ["automation", "n8n", "workflows"],
        "copywriting": ["copywriting", "writing", "marketing"],
        "linkedin": ["linkedin", "networking", "professional"],
        "telegram": ["telegram", "bot", "automation"],
        "roblox": ["roblox", "gaming", "kids"],
        "polymarket": ["polymarket", "prediction", "trading"],
        "gumroad": ["gumroad", "digital products", "selling"],
        "prompt": ["prompt engineering", "ai", "chatgpt"],
        "music": ["music", "fl studio", "production"],
        "security": ["ai safety", "security", "privacy"],
    }

    for keyword, tag_list in topic_map.items():
        if keyword in fl:
            tags.update(tag_list)

    # Spanish content
    if fl.endswith("-es.pdf") or fl.endswith("-es.svg"):
        tags.add("spanish")
        tags.add("espanol")

    # Accessibility
    if "colorblind" in fl:
        tags.add("accessibility")
        tags.add("colorblind")

    # General tags
    tags.add("digital product")
    if category == "blueprint":
        tags.add("visual guide")
    if category == "free":
        tags.add("free")
        tags.add("lead magnet")

    return sorted(tags)[:8]  # Gumroad allows limited tags


# --- Deduplicate SVG/PDF pairs (group them) ---

def scan_products():
    """Scan READY-TO-SELL and return list of product dicts, grouping SVG+PDF pairs."""
    files = []
    for f in sorted(READY_DIR.iterdir()):
        if f.name in SKIP_FILES or f.name.startswith("."):
            continue
        if f.suffix.lower() not in SELLABLE_EXTENSIONS:
            continue
        files.append(f)

    # Group SVG+PDF pairs by stem
    stems = {}
    for f in files:
        stem = f.stem
        ext = f.suffix.lower()
        if stem not in stems:
            stems[stem] = {}
        stems[stem][ext] = f

    products = []
    seen_stems = set()

    for stem, ext_map in sorted(stems.items()):
        if stem in seen_stems:
            continue
        seen_stems.add(stem)

        # Pick the primary file (PDF preferred for pricing, but include both)
        primary = ext_map.get(".pdf") or ext_map.get(".svg") or ext_map.get(".xlsx") or ext_map.get(".zip")
        if not primary:
            continue

        all_files = sorted(ext_map.values(), key=lambda x: x.name)
        filename = primary.name
        price = get_price(filename)
        category = get_category(filename)
        title = clean_title(filename)
        desc = generate_description(title, category, filename)
        tags = generate_tags(filename, category)
        size_kb = sum(f.stat().st_size for f in all_files) / 1024

        products.append({
            "title": title,
            "price": price,
            "category": category,
            "description": desc,
            "files": [f.name for f in all_files],
            "primary_file": filename,
            "tags": tags,
            "size_kb": round(size_kb, 1),
            "stem": stem,
        })

    return products


def priority_score(p):
    """Higher score = list first. Combines price and category weight."""
    cat_weight = {
        "operating-system": 100,
        "blueprint": 50,
        "kit": 40,
        "course": 35,
        "playbook": 30,
        "guide": 20,
        "template": 15,
        "free": 5,
    }
    return p["price"] * 10 + cat_weight.get(p["category"], 10)


def estimate_list_time(p):
    """Estimate minutes to list on Gumroad."""
    if len(p["files"]) > 1:
        return 4  # Multiple files to upload
    if p["price"] == 0:
        return 2  # Free = quick
    if p["category"] == "operating-system":
        return 5  # Flagship, more care
    return 3


def write_manifest(products):
    total = len(products)
    total_revenue_all = sum(p["price"] for p in products)
    total_revenue_10pct = total_revenue_all * 0.10

    paid = [p for p in products if p["price"] > 0]
    free = [p for p in products if p["price"] == 0]

    lines = []
    lines.append("# Gumroad Upload Manifest")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total products:** {total}")
    lines.append(f"- **Paid products:** {len(paid)}")
    lines.append(f"- **Free lead magnets:** {len(free)}")
    lines.append(f"- **Total catalog value (1 sale each):** ${total_revenue_all:,.2f}")
    lines.append(f"- **Revenue projection (10% sell month 1):** ${total_revenue_10pct:,.2f}")
    lines.append("")

    # Price breakdown
    lines.append("## Price Breakdown")
    lines.append("")
    price_groups = {}
    for p in products:
        key = f"${p['price']:.2f}"
        if key not in price_groups:
            price_groups[key] = 0
        price_groups[key] += 1
    for price_str in sorted(price_groups.keys(), key=lambda x: -float(x.replace("$", ""))):
        lines.append(f"- {price_str}: {price_groups[price_str]} products")
    lines.append("")

    # Category breakdown
    lines.append("## Category Breakdown")
    lines.append("")
    cat_groups = {}
    for p in products:
        cat = p["category"]
        if cat not in cat_groups:
            cat_groups[cat] = 0
        cat_groups[cat] += 1
    for cat in sorted(cat_groups.keys()):
        lines.append(f"- {cat}: {cat_groups[cat]}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Product Listings")
    lines.append("")

    for i, p in enumerate(sorted(products, key=lambda x: -priority_score(x)), 1):
        lines.append(f"### {i}. {p['title']}")
        lines.append("")
        lines.append(f"- **Price:** ${p['price']:.2f}" + (" (FREE)" if p['price'] == 0 else ""))
        lines.append(f"- **Category:** {p['category']}")
        lines.append(f"- **File(s):** {', '.join(p['files'])}")
        lines.append(f"- **Size:** {p['size_kb']:.0f} KB")
        lines.append(f"- **Tags:** {', '.join(p['tags'])}")
        lines.append(f"- **Description:**")
        lines.append(f"  {p['description']}")
        lines.append("")

    MANIFEST_PATH.write_text("\n".join(lines))
    print(f"  Wrote {MANIFEST_PATH.name} ({total} products)")


def write_quick_list(products):
    sorted_products = sorted(products, key=lambda x: -priority_score(x))
    top10 = sorted_products[:10]
    rest = sorted_products[10:]

    total_time_top10 = sum(estimate_list_time(p) for p in top10)
    total_time_all = sum(estimate_list_time(p) for p in sorted_products)

    lines = []
    lines.append("# Quick List Order - Gumroad Upload Priority")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## TOP 10 - List These First")
    lines.append(f"Estimated time: ~{total_time_top10} minutes")
    lines.append("")

    for i, p in enumerate(top10, 1):
        t = estimate_list_time(p)
        lines.append(f"- [ ] **{i}. {p['title']}** - ${p['price']:.2f} (~{t} min)")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Remaining Products")
    lines.append(f"Estimated time for all remaining: ~{total_time_all - total_time_top10} minutes")
    lines.append("")

    for i, p in enumerate(rest, 11):
        t = estimate_list_time(p)
        lines.append(f"- [ ] **{i}. {p['title']}** - ${p['price']:.2f} (~{t} min)")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Upload Checklist (per product)")
    lines.append("")
    lines.append("1. Go to gumroad.com/dashboard > New Product")
    lines.append("2. Set product name (copy title from manifest)")
    lines.append("3. Upload file(s)")
    lines.append("4. Set price")
    lines.append("5. Paste description")
    lines.append("6. Add tags")
    lines.append("7. Add cover image (use product-covers.html generator or screenshot)")
    lines.append("8. Set to Published")
    lines.append("9. Copy link, save to tracking sheet")
    lines.append("")
    lines.append(f"**Total products:** {len(sorted_products)}")
    lines.append(f"**Total estimated time:** ~{total_time_all} minutes ({total_time_all // 60}h {total_time_all % 60}m)")

    QUICK_LIST_PATH.write_text("\n".join(lines))
    print(f"  Wrote {QUICK_LIST_PATH.name} (top 10 + {len(rest)} remaining)")


def main():
    print()
    print("=" * 50)
    print("  GUMROAD UPLOAD MANIFEST GENERATOR")
    print("=" * 50)
    print()

    if not READY_DIR.exists():
        print(f"ERROR: {READY_DIR} not found")
        return

    products = scan_products()
    if not products:
        print("No sellable products found.")
        return

    paid = [p for p in products if p["price"] > 0]
    free = [p for p in products if p["price"] == 0]

    print(f"  Found {len(products)} products ({len(paid)} paid, {len(free)} free)")
    print(f"  Catalog value: ${sum(p['price'] for p in products):,.2f}")
    print()

    write_manifest(products)
    write_quick_list(products)

    print()
    print("  Done. Open the files in READY-TO-SELL/:")
    print(f"    - {MANIFEST_PATH.name}")
    print(f"    - {QUICK_LIST_PATH.name}")
    print()


if __name__ == "__main__":
    main()
