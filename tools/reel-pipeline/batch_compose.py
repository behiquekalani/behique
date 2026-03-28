#!/usr/bin/env python3
"""Batch compose all stories that have complete image sets.
Skips stories that already have a final .mp4 or are missing images."""
import json, subprocess, os, sys, time
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"

def get_all_stories():
    """List all story JSON files."""
    return sorted(STORIES_DIR.glob("*.json"))

def check_story_ready(story_path):
    """Check if a story has all images, TTS, and timing ready."""
    name = story_path.stem
    out_dir = OUTPUT_DIR / name

    story = json.loads(story_path.read_text())
    num_scenes = len(story["scenes"])

    # Check images
    for i in range(num_scenes):
        if not (out_dir / f"scene_{i}.png").exists():
            return False, f"missing scene_{i}.png"

    # Check narration
    if not (out_dir / "narration.wav").exists():
        return False, "missing narration.wav"

    # Check timing
    if not (out_dir / "timing.json").exists():
        return False, "missing timing.json"

    # Check if already composed
    if (out_dir / f"{name}.mp4").exists():
        return False, "already composed"

    return True, "ready"

def compose_story(story_name):
    """Compose a single story reel."""
    result = subprocess.run(
        [sys.executable, str(PIPELINE_DIR / "compose_reel.py"), story_name],
        capture_output=True, text=True, cwd=str(PIPELINE_DIR)
    )
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"[ERROR] {story_name}: {result.stderr[-300:]}")
        return False

def main():
    watch_mode = "--watch" in sys.argv

    while True:
        stories = get_all_stories()
        composed = 0
        pending = 0

        for sp in stories:
            ready, reason = check_story_ready(sp)
            name = sp.stem
            if ready:
                print(f"\n{'='*50}")
                print(f"[COMPOSE] {name}")
                print(f"{'='*50}")
                if compose_story(name):
                    composed += 1
            elif reason == "already composed":
                pass  # Silent
            else:
                pending += 1
                if watch_mode:
                    print(f"[WAIT] {name}: {reason}")

        if not watch_mode:
            break

        if pending == 0:
            print("\n[DONE] All stories composed!")
            break

        print(f"\n[BATCH] Composed: {composed}, Pending: {pending}. Checking again in 60s...")
        time.sleep(60)

    # Summary
    print("\n" + "="*50)
    print("REEL INVENTORY")
    print("="*50)
    for sp in get_all_stories():
        name = sp.stem
        mp4 = OUTPUT_DIR / name / f"{name}.mp4"
        if mp4.exists():
            size = mp4.stat().st_size / (1024*1024)
            print(f"  [OK] {name}.mp4 ({size:.1f} MB)")
        else:
            ready, reason = check_story_ready(sp)
            print(f"  [--] {name}: {reason}")

if __name__ == "__main__":
    main()
