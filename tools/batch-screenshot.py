#!/usr/bin/env python3
"""
Batch Screenshot - Convert cover.html and thumbnail.html to PNGs using Brave.
Uses --screenshot flag for headless rendering at 2x resolution.
"""

import os
import subprocess
import time
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
PRODUCTS_DIR = REPO / "READY-TO-SELL/products-organized"

# Try different Brave paths
BRAVE_PATHS = [
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Brave Browser Beta.app/Contents/MacOS/Brave Browser Beta",
    "brave-browser",
]

def find_brave():
    for path in BRAVE_PATHS:
        if os.path.exists(path):
            return path
    # Try which
    try:
        result = subprocess.run(["which", "brave-browser"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def screenshot_html(brave_path, html_file, output_png, width, height):
    """Take a screenshot of an HTML file using Brave headless."""
    file_url = f"file://{html_file.absolute()}"

    cmd = [
        brave_path,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        "--force-device-scale-factor=2",
        f"--screenshot={output_png.absolute()}",
        file_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0 and output_png.exists()
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"    Error: {e}")
        return False


def main():
    brave = find_brave()
    if not brave:
        print("Brave Browser not found. Install it or add to PATH.")
        print("\nAlternative: Open each .html file in Brave manually and take screenshots.")
        print("Or use the manual approach:")
        print('  for f in READY-TO-SELL/products-organized/*/cover.html; do')
        print('    open "$f"')
        print('  done')
        return

    print(f"\n{'='*50}")
    print(f"  BATCH SCREENSHOT - Brave Headless")
    print(f"{'='*50}")
    print(f"  Brave: {brave}\n")

    covers_done = 0
    thumbs_done = 0
    errors = 0

    for product_dir in sorted(PRODUCTS_DIR.iterdir()):
        if not product_dir.is_dir():
            continue

        slug = product_dir.name

        # Screenshot cover
        cover_html = product_dir / "cover.html"
        cover_png = product_dir / "cover.png"
        if cover_html.exists() and not cover_png.exists():
            print(f"  COVER: {slug}...", end=" ", flush=True)
            if screenshot_html(brave, cover_html, cover_png, 1280, 720):
                print("OK")
                covers_done += 1
            else:
                print("FAILED")
                errors += 1

        # Screenshot thumbnail
        thumb_html = product_dir / "thumbnail.html"
        thumb_png = product_dir / "thumbnail.png"
        if thumb_html.exists() and not thumb_png.exists():
            print(f"  THUMB: {slug}...", end=" ", flush=True)
            if screenshot_html(brave, thumb_html, thumb_png, 600, 600):
                print("OK")
                thumbs_done += 1
            else:
                print("FAILED")
                errors += 1

    print(f"\n  Covers: {covers_done}")
    print(f"  Thumbnails: {thumbs_done}")
    print(f"  Errors: {errors}")

    if errors > 0:
        print(f"\n  For failed items, open the .html files manually in Brave")
        print(f"  and use Cmd+Shift+4 to screenshot them.")


if __name__ == "__main__":
    main()
