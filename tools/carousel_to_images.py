#!/usr/bin/env python3
"""
Carousel to Images -- Screenshots each slide from carousel HTML files.

Takes carousel HTML files and produces 1080x1080 PNG images for each slide,
ready for Instagram upload.

Usage:
    python3 carousel_to_images.py                          # all carousels
    python3 carousel_to_images.py carousel-2026-03-20-*.html  # specific file
    python3 carousel_to_images.py --latest 5               # last 5 carousels
"""
import sys
import argparse
import asyncio
from pathlib import Path

CAROUSEL_DIR = Path(__file__).parent.parent / "Ceiba" / "news" / "carousels"
IMAGES_DIR = Path(__file__).parent.parent / "Ceiba" / "news" / "carousel-images"


async def screenshot_carousel(html_path, output_dir):
    """Open carousel HTML and screenshot each 1080x1080 slide."""
    from playwright.async_api import async_playwright

    stem = Path(html_path).stem
    slide_dir = output_dir / stem
    slide_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080})

        await page.goto(f"file://{html_path}")
        await page.wait_for_timeout(1000)

        # Find all slides
        slides = await page.query_selector_all(".slide")
        print(f"  {stem}: {len(slides)} slides found")

        for i, slide in enumerate(slides):
            # Scroll slide into view
            await slide.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)

            # Screenshot just the slide element
            img_path = slide_dir / f"slide_{i+1}.png"
            await slide.screenshot(path=str(img_path))
            print(f"    slide_{i+1}.png saved")

        await browser.close()

    return len(slides)


async def process_carousels(files, output_dir):
    """Process multiple carousel files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    total_slides = 0

    for f in files:
        try:
            count = await screenshot_carousel(str(f), output_dir)
            total_slides += count
        except Exception as e:
            print(f"  ERROR: {f.name}: {e}")

    return total_slides


def main():
    parser = argparse.ArgumentParser(description="Carousel to Images")
    parser.add_argument("files", nargs="*", help="Carousel HTML files")
    parser.add_argument("--latest", type=int, help="Process N most recent carousels")
    parser.add_argument("--all", action="store_true", help="Process all carousels")
    parser.add_argument("--output", default=str(IMAGES_DIR), help="Output directory")

    args = parser.parse_args()
    output_dir = Path(args.output)

    if args.files:
        files = [Path(f) for f in args.files]
    elif args.latest:
        files = sorted(CAROUSEL_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:args.latest]
    elif args.all:
        files = sorted(CAROUSEL_DIR.glob("*.html"))
    else:
        # Default: today's carousels
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        files = sorted(CAROUSEL_DIR.glob(f"carousel-{today}-*.html"))

    if not files:
        print("  No carousel files found.")
        return

    print(f"\n  Processing {len(files)} carousels...\n")
    total = asyncio.run(process_carousels(files, output_dir))
    print(f"\n  Done. {total} slides saved to {output_dir}")


if __name__ == "__main__":
    main()
