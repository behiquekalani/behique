#!/usr/bin/env python3
"""
Hutia Remote Image Generation -- Delegates SDXL Turbo to Comp3.

Sends image prompts to Hutia's SDXL Turbo server (192.168.0.152:9879)
and downloads results. Used by the reel pipeline for scene images.

Usage:
    python3 hutia_image_gen.py "a sunset over the ocean, cinematic" output.png
    python3 hutia_image_gen.py --story the-tailgater    # generate all scenes
    python3 hutia_image_gen.py --all-new                # generate for all stories missing images
"""
import json
import sys
import os
import argparse
import urllib.request
import urllib.parse
from pathlib import Path

HUTIA_HOST = "192.168.0.152"
HUTIA_PORT = 9879
HUTIA_URL = f"http://{HUTIA_HOST}:{HUTIA_PORT}"

PIPELINE_DIR = Path(__file__).parent / "reel-pipeline"
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"


def check_hutia():
    """Check if Hutia's image gen server is reachable."""
    try:
        req = urllib.request.Request(f"{HUTIA_URL}/health", method="GET")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        # Try a simpler check
        try:
            import socket
            s = socket.create_connection((HUTIA_HOST, HUTIA_PORT), timeout=5)
            s.close()
            return True
        except Exception:
            return False


def generate_image(prompt, output_path, width=1024, height=1024, steps=4):
    """Send prompt to Hutia and download result."""
    # Build request payload
    payload = json.dumps({
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "guidance_scale": 0.0,  # SDXL Turbo uses 0 guidance
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{HUTIA_URL}/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response = urllib.request.urlopen(req, timeout=120)

        # Check content type
        content_type = response.headers.get("Content-Type", "")

        if "image" in content_type:
            # Direct image response
            with open(output_path, "wb") as f:
                f.write(response.read())
            return True
        else:
            # JSON response with image URL or base64
            data = json.loads(response.read().decode("utf-8"))

            if "image" in data:
                # Base64 encoded image
                import base64
                img_data = base64.b64decode(data["image"])
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True
            elif "url" in data:
                urllib.request.urlretrieve(data["url"], output_path)
                return True
            else:
                print(f"  [HUTIA] Unexpected response: {list(data.keys())}")
                return False

    except Exception as e:
        print(f"  [HUTIA] Error: {e}")
        return False


def generate_for_story(story_name):
    """Generate all scene images for a story."""
    story_path = STORIES_DIR / f"{story_name}.json"
    if not story_path.exists():
        print(f"  Story not found: {story_name}")
        return False

    with open(story_path) as f:
        story = json.load(f)

    out_dir = OUTPUT_DIR / story_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n  Generating images for: {story['title']}")
    print(f"  Scenes: {len(story['scenes'])}")
    print()

    success_count = 0
    for i, scene in enumerate(story["scenes"]):
        img_path = out_dir / f"scene_{i}.png"
        if img_path.exists():
            print(f"  [SKIP] Scene {i} already exists")
            success_count += 1
            continue

        prompt = scene.get("image_prompt", scene.get("text", ""))
        print(f"  [GEN] Scene {i}: {prompt[:60]}...")

        # SDXL Turbo works best at 512x512 with 4 steps
        # We'll upscale later if needed
        if generate_image(prompt, str(img_path), width=512, height=512, steps=4):
            size_kb = os.path.getsize(img_path) / 1024
            print(f"  [OK]  Scene {i}: {size_kb:.0f}KB")
            success_count += 1
        else:
            print(f"  [FAIL] Scene {i}")

    print(f"\n  Done: {success_count}/{len(story['scenes'])} images")
    return success_count == len(story["scenes"])


def find_stories_missing_images():
    """Find stories that have TTS but no images."""
    missing = []
    for story_file in sorted(STORIES_DIR.glob("*.json")):
        name = story_file.stem
        if name.endswith("_es"):
            continue  # Skip Spanish versions (share images with EN)
        out_dir = OUTPUT_DIR / name
        with open(story_file) as f:
            story = json.load(f)
        num_scenes = len(story["scenes"])
        existing = len(list(out_dir.glob("scene_*.png"))) if out_dir.exists() else 0
        if existing < num_scenes:
            missing.append((name, existing, num_scenes))
    return missing


def main():
    parser = argparse.ArgumentParser(description="Hutia Remote Image Generation")
    parser.add_argument("prompt", nargs="?", help="Image prompt")
    parser.add_argument("output", nargs="?", default="output.png", help="Output path")
    parser.add_argument("--story", help="Generate images for a story")
    parser.add_argument("--all-new", action="store_true", help="Generate for all stories missing images")
    parser.add_argument("--check", action="store_true", help="Check Hutia connection")
    parser.add_argument("--list-missing", action="store_true", help="List stories missing images")

    args = parser.parse_args()

    if args.check:
        if check_hutia():
            print(f"  Hutia is online at {HUTIA_URL}")
        else:
            print(f"  Hutia is not reachable at {HUTIA_URL}")
        return

    if args.list_missing:
        missing = find_stories_missing_images()
        if missing:
            print(f"\n  Stories missing images:\n")
            for name, have, need in missing:
                print(f"  {name}: {have}/{need} images")
        else:
            print("  All stories have images.")
        return

    if not check_hutia():
        print(f"  Hutia not reachable at {HUTIA_URL}")
        print(f"  Make sure the SDXL server is running on port {HUTIA_PORT}")
        return

    if args.all_new:
        missing = find_stories_missing_images()
        print(f"\n  {len(missing)} stories need images\n")
        for name, have, need in missing:
            generate_for_story(name)
        return

    if args.story:
        generate_for_story(args.story)
        return

    if args.prompt:
        print(f"  Generating: {args.prompt[:60]}...")
        if generate_image(args.prompt, args.output):
            print(f"  Saved: {args.output}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
