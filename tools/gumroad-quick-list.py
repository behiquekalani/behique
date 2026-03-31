#!/usr/bin/env python3
"""
Gumroad Quick Lister - generates copy-paste ready listing text
for all products that aren't live yet.

Prints each product's listing info in a format ready to paste into Gumroad.
Also generates a master checklist for tracking what's been listed.
"""

import os
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
PRODUCTS_DIR = REPO / "READY-TO-SELL/products-organized"

# Products already live on Gumroad (don't list these)
ALREADY_LIVE = {
    "starter", "ecommerce", "ai-agency", "freelancer", "content-creator",
    "coaching", "consulting", "dropshipping", "saas",
    # Kalani may have listed more - add slugs here as they go live
}

# Original 17 that Kalani approved (list these first)
APPROVED_WAVE = {
    "youtube", "newsletter", "crypto", "etsy", "podcast",
    "ecommerce-es", "freelancer-es", "creator-es",
    "voice-bible", "blueprint-bundle",
    "first-dollar-guide", "gumroad-ai-guide",
    "ai-offline-content", "ai-social-media",
    "claude-code-builders", "claude-code-noncoders", "claude-cowork",
}


def main():
    print("=" * 60)
    print("  GUMROAD QUICK LISTER")
    print("  Copy-paste each listing into Gumroad")
    print("=" * 60)

    approved = []
    new_wave = []

    for product_dir in sorted(PRODUCTS_DIR.iterdir()):
        if not product_dir.is_dir():
            continue

        slug = product_dir.name
        info_file = product_dir / "GUMROAD_INFO.txt"

        if not info_file.exists():
            continue

        if slug in ALREADY_LIVE:
            continue

        info = info_file.read_text()

        if slug in APPROVED_WAVE:
            approved.append((slug, info, product_dir))
        else:
            new_wave.append((slug, info, product_dir))

    # Print approved products first
    print(f"\n{'='*60}")
    print(f"  APPROVED - LIST THESE NOW ({len(approved)} products)")
    print(f"{'='*60}")

    for i, (slug, info, path) in enumerate(approved, 1):
        files = list(path.glob("*.pdf")) + list(path.glob("*.zip"))
        file_name = files[0].name if files else "NO FILE FOUND"

        print(f"\n{'─'*60}")
        print(f"  [{i}/{len(approved)}] {slug}")
        print(f"  File: {path}/{file_name}")
        print(f"  Cover: {path}/cover.png")
        print(f"  Thumbnail: {path}/thumbnail.png")
        print(f"{'─'*60}")
        print(info)

    # Print new wave products
    if new_wave:
        print(f"\n{'='*60}")
        print(f"  NEW WAVE - NEEDS APPROVAL ({len(new_wave)} products)")
        print(f"{'='*60}")

        for slug, info, path in new_wave:
            # Just print name and price, not full info
            for line in info.split('\n'):
                if line.startswith('Name:'):
                    print(f"  {line.strip()}")
                elif line.startswith('Price:'):
                    print(f"    {line.strip()}")
                    break

    # Generate checklist
    checklist_path = REPO / "READY-TO-SELL/LISTING_CHECKLIST.md"
    with open(checklist_path, 'w') as f:
        f.write("# Gumroad Listing Checklist\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Already Live\n")
        for slug in sorted(ALREADY_LIVE):
            f.write(f"- [x] {slug}\n")

        f.write(f"\n## Approved - List Now ({len(approved)})\n")
        for slug, _, _ in approved:
            f.write(f"- [ ] {slug}\n")

        f.write(f"\n## New Wave - Needs Approval ({len(new_wave)})\n")
        for slug, _, _ in new_wave:
            f.write(f"- [ ] {slug}\n")

    print(f"\n{'='*60}")
    print(f"  Checklist saved: {checklist_path}")
    print(f"  Approved: {len(approved)} products ready to list")
    print(f"  New wave: {len(new_wave)} products need approval")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
