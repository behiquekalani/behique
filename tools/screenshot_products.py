#!/usr/bin/env python3
"""
screenshot_products.py — Generate Gumroad product preview images from HTML files.

Uses headless Brave Browser to screenshot each product landing page at:
  - 1280x720 (Gumroad cover)
  - 600x600 (Gumroad thumbnail)

Zero dependencies beyond Brave Browser.
"""

import os
import subprocess
import glob

BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
READY_TO_SELL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "READY-TO-SELL")

# Match *-v3.html and behike-os-v3.html
PATTERNS = ["*-v3.html", "behike-os-v3.html"]

SIZES = [
    {"suffix": "-preview.png", "width": 1280, "height": 720, "label": "cover"},
    {"suffix": "-thumb.png", "width": 600, "height": 600, "label": "thumbnail"},
]


def find_html_files():
    """Find all matching HTML files, deduplicated."""
    found = set()
    for pattern in PATTERNS:
        for path in glob.glob(os.path.join(READY_TO_SELL, pattern)):
            found.add(path)
    return sorted(found)


def screenshot(html_path, output_path, width, height):
    """Take a screenshot of an HTML file using headless Brave."""
    file_url = f"file://{html_path}"
    cmd = [
        BRAVE,
        "--headless",
        "--disable-gpu",
        f"--screenshot={output_path}",
        f"--window-size={width},{height}",
        file_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0


def file_size_str(path):
    """Human-readable file size."""
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def main():
    if not os.path.isfile(BRAVE):
        print(f"ERROR: Brave Browser not found at {BRAVE}")
        return

    html_files = find_html_files()
    if not html_files:
        print(f"No matching HTML files found in {READY_TO_SELL}")
        return

    print(f"Found {len(html_files)} HTML files in {READY_TO_SELL}\n")

    generated = []

    for html_path in html_files:
        name = os.path.basename(html_path)
        base = html_path.rsplit(".html", 1)[0]
        print(f"Processing: {name}")

        for size in SIZES:
            output = base + size["suffix"]
            ok = screenshot(html_path, output, size["width"], size["height"])
            if ok and os.path.isfile(output):
                generated.append(output)
                print(f"  {size['label']} ({size['width']}x{size['height']}): OK")
            else:
                print(f"  {size['label']} ({size['width']}x{size['height']}): FAILED")

    # Summary
    print(f"\n{'='*60}")
    print(f"Generated {len(generated)} screenshots:\n")
    for path in generated:
        print(f"  {os.path.basename(path):50s} {file_size_str(path)}")


if __name__ == "__main__":
    main()
