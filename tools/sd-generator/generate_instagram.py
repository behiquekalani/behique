"""
Instagram Batch Image Generator
Reads instagram-batch.json and generates all images via SD WebUI API.

Usage:
  python generate_instagram.py                  # Generate all 20 images
  python generate_instagram.py --dry-run        # Print prompts only
  python generate_instagram.py --post 5         # Generate single post
  python generate_instagram.py --post 1-10      # Generate range
  python generate_instagram.py --dry-run --post 3
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

# --- Configuration ---
SD_API_URL = "http://localhost:7860"
SCRIPT_DIR = Path(__file__).parent
BATCH_FILE = SCRIPT_DIR / "instagram-batch.json"
OUTPUT_DIR = SCRIPT_DIR / "output" / "instagram"

DEFAULT_SAMPLER = "DPM++ 2M Karras"


def check_api():
    """Check if SD WebUI API is running."""
    try:
        r = requests.get(f"{SD_API_URL}/sdapi/v1/sd-models", timeout=5)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def load_batch():
    """Load the instagram batch JSON file."""
    if not BATCH_FILE.exists():
        print(f"[ERROR] Batch file not found: {BATCH_FILE}")
        sys.exit(1)

    with open(BATCH_FILE) as f:
        return json.load(f)


def parse_dimensions(dim_str):
    """Parse '1080x1080' into (width, height)."""
    parts = dim_str.lower().split("x")
    return int(parts[0]), int(parts[1])


def generate_image(post, output_dir):
    """Generate a single image from a post config dict."""
    width, height = parse_dimensions(post["dimensions"])

    payload = {
        "prompt": post["prompt"],
        "negative_prompt": post["negative_prompt"],
        "width": width,
        "height": height,
        "steps": post["steps"],
        "cfg_scale": post["cfg_scale"],
        "sampler_name": DEFAULT_SAMPLER,
        "seed": -1,
        "batch_size": 1,
    }

    try:
        r = requests.post(
            f"{SD_API_URL}/sdapi/v1/txt2img",
            json=payload,
            timeout=300,
        )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Generation failed: {e}")
        return None

    result = r.json()

    if not result.get("images"):
        print("  [ERROR] No images returned from API")
        return None

    # Save image
    img_bytes = base64.b64decode(result["images"][0])
    filepath = output_dir / post["output_filename"]
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    # Save generation metadata alongside
    info = json.loads(result.get("info", "{}"))
    meta_file = output_dir / post["output_filename"].replace(".png", "_meta.json")
    with open(meta_file, "w") as f:
        json.dump(
            {
                "post_number": post["post_number"],
                "post_title": post["post_title"],
                "prompt": post["prompt"],
                "negative_prompt": post["negative_prompt"],
                "dimensions": post["dimensions"],
                "steps": post["steps"],
                "cfg_scale": post["cfg_scale"],
                "seed": info.get("seed", -1),
                "sampler": DEFAULT_SAMPLER,
                "output_file": str(filepath),
            },
            f,
            indent=2,
        )

    return str(filepath)


def dry_run(posts):
    """Print all prompts without generating."""
    print("=" * 70)
    print("  INSTAGRAM BATCH — DRY RUN")
    print("=" * 70)
    for post in posts:
        num = post["post_number"]
        title = post["post_title"]
        prompt = post["prompt"]
        neg = post["negative_prompt"]
        dims = post["dimensions"]
        steps = post["steps"]
        cfg = post["cfg_scale"]
        out = post["output_filename"]

        print(f"\n[Post {num:02d}] {title}")
        print(f"  Output:   {out}")
        print(f"  Size:     {dims} | Steps: {steps} | CFG: {cfg}")
        print(f"  Prompt:   {prompt}")
        print(f"  Negative: {neg}")
        print("-" * 70)

    print(f"\nTotal: {len(posts)} images ready for generation.")
    print("Remove --dry-run to generate.\n")


def filter_posts(posts, post_arg):
    """Filter posts by number or range (e.g. '5' or '1-10')."""
    if "-" in post_arg:
        start, end = post_arg.split("-")
        start, end = int(start), int(end)
        return [p for p in posts if start <= p["post_number"] <= end]
    else:
        num = int(post_arg)
        return [p for p in posts if p["post_number"] == num]


def main():
    parser = argparse.ArgumentParser(
        description="Generate Instagram post images via Stable Diffusion WebUI API"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without generating images",
    )
    parser.add_argument(
        "--post",
        type=str,
        default=None,
        help="Generate specific post(s): single number (5) or range (1-10)",
    )
    args = parser.parse_args()

    # Load batch
    all_posts = load_batch()

    # Filter if needed
    if args.post:
        posts = filter_posts(all_posts, args.post)
        if not posts:
            print(f"[ERROR] No posts found matching: {args.post}")
            sys.exit(1)
    else:
        posts = all_posts

    # Dry run mode
    if args.dry_run:
        dry_run(posts)
        return

    # Check API before starting
    if not check_api():
        print(f"[ERROR] SD WebUI API not reachable at {SD_API_URL}")
        print("Start the Stable Diffusion WebUI first.")
        sys.exit(1)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate
    total = len(posts)
    success = 0
    failed = []

    print("=" * 70)
    print(f"  INSTAGRAM BATCH GENERATOR — {total} images")
    print("=" * 70)

    for i, post in enumerate(posts, 1):
        num = post["post_number"]
        title = post["post_title"]
        dims = post["dimensions"]
        steps = post["steps"]
        cfg = post["cfg_scale"]

        print(f"\n[{i}/{total}] Post {num:02d}: {title}")
        print(f"  Size: {dims} | Steps: {steps} | CFG: {cfg}")
        print(f"  Prompt: {post['prompt'][:80]}...")

        filepath = generate_image(post, OUTPUT_DIR)

        if filepath:
            print(f"  [SAVED] {filepath}")
            success += 1
        else:
            print(f"  [FAILED] Post {num:02d}")
            failed.append(num)

        # Pause between generations to let VRAM clear
        if i < total:
            time.sleep(3)

    # Summary
    print("\n" + "=" * 70)
    print(f"  COMPLETE: {success}/{total} images generated")
    if failed:
        print(f"  FAILED:   Posts {failed}")
    print(f"  Output:   {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
