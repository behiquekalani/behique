#!/usr/bin/env python3
"""
Generate all missing scene images using mflux (FLUX.1-schnell 4-bit).
Runs sequentially. ~2.5 min per image on M4.

Usage:
    python3 generate_missing_images.py          # generate all missing
    python3 generate_missing_images.py old-sneakers  # specific story only
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"
MODEL_PATH = str((PIPELINE_DIR / "flux-schnell-4bit").expanduser())


def generate_image(prompt, output_path, steps=4):
    """Generate one image with mflux."""
    cmd = [
        "mflux-generate",
        "--model", MODEL_PATH,
        "--prompt", prompt,
        "--steps", str(steps),
        "--width", "768",
        "--height", "1024",
        "--output", str(output_path),
    ]
    env = {**os.environ, "HF_HUB_DISABLE_XET": "1"}

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr[-200:]}")
        return False
    return output_path.exists()


def get_missing_images():
    """Find all stories with missing scene images."""
    missing = []
    for sf in sorted(STORIES_DIR.glob("*.json")):
        name = sf.stem
        out_dir = OUTPUT_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(sf) as f:
            story = json.load(f)

        for i, scene in enumerate(story["scenes"]):
            img_path = out_dir / f"scene_{i}.png"
            if not img_path.exists():
                missing.append({
                    "story": name,
                    "scene": i,
                    "prompt": scene["image_prompt"],
                    "output": img_path,
                })

    return missing


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    missing = get_missing_images()

    if target:
        missing = [m for m in missing if m["story"] == target]

    if not missing:
        print("All images generated!")
        return

    print(f"\n{'='*60}")
    print(f"  GENERATING {len(missing)} MISSING IMAGES")
    print(f"  Estimated time: ~{len(missing) * 2.5:.0f} minutes")
    print(f"{'='*60}\n")

    for idx, item in enumerate(missing):
        print(f"[{idx+1}/{len(missing)}] {item['story']} scene {item['scene']}")
        print(f"  Prompt: {item['prompt'][:80]}...")

        start = time.time()
        ok = generate_image(item["prompt"], item["output"])
        elapsed = time.time() - start

        if ok:
            print(f"  Done in {elapsed:.1f}s")
        else:
            print(f"  FAILED after {elapsed:.1f}s")

    # Summary
    remaining = get_missing_images()
    if target:
        remaining = [m for m in remaining if m["story"] == target]

    print(f"\n{'='*60}")
    print(f"  COMPLETE: {len(missing) - len(remaining)}/{len(missing)} generated")
    if remaining:
        print(f"  Still missing: {len(remaining)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)
    main()
