#!/usr/bin/env python3
"""
AUTOPILOT - Continuous Reel Production Daemon
Watches for completed assets and automatically runs the full pipeline.
Designed to run overnight unattended.

What it does every 60 seconds:
1. Checks for stories with all images + TTS but no IG reel
2. Runs instagram_pipeline.py on them
3. Updates the posting queue
4. Logs everything

Usage:
    python3 autopilot.py              # run daemon
    python3 autopilot.py --once       # single pass then exit
    python3 autopilot.py --status     # show what would run
"""

import json
import subprocess
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"
INSTAGRAM_DIR = PIPELINE_DIR / "instagram_ready"
LOG_FILE = PIPELINE_DIR / "autopilot.log"

POLL_INTERVAL = 60  # seconds between checks


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [AUTOPILOT] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE),
        ]
    )
    return logging.getLogger('autopilot')


def find_ready_stories():
    """Find stories that have all assets but no IG reel yet."""
    ready = []
    for sf in sorted(STORIES_DIR.glob("*.json")):
        name = sf.stem
        out = OUTPUT_DIR / name
        ig = INSTAGRAM_DIR / f"{name}.mp4"

        if ig.exists():
            continue  # already done

        if not out.exists():
            continue

        # Check timing + narration
        if not (out / "timing.json").exists():
            continue
        if not (out / "narration.wav").exists():
            continue

        # Check all scene images
        with open(sf) as f:
            story = json.load(f)
        expected = len(story.get("scenes", []))
        actual = len(list(out.glob("scene_*.png")))

        if actual >= expected:
            ready.append(name)

    return ready


def find_needs_tts():
    """Find stories that need TTS generated."""
    needs = []
    for sf in sorted(STORIES_DIR.glob("*.json")):
        name = sf.stem
        out = OUTPUT_DIR / name

        if not out.exists() or not (out / "narration.wav").exists():
            needs.append(name)

    return needs


def find_needs_images():
    """Find stories that need images."""
    needs = []
    for sf in sorted(STORIES_DIR.glob("*.json")):
        name = sf.stem
        out = OUTPUT_DIR / name

        with open(sf) as f:
            story = json.load(f)
        expected = len(story.get("scenes", []))
        actual = len(list(out.glob("scene_*.png"))) if out.exists() else 0

        if actual < expected:
            needs.append((name, actual, expected))

    return needs


def run_tts_for_story(name, log):
    """Generate TTS for a story."""
    log.info(f"Generating TTS for {name}...")
    r = subprocess.run(
        ['python3', 'full_pipeline.py', name, '--skip-images'],
        cwd=str(PIPELINE_DIR),
        capture_output=True, text=True,
        timeout=120
    )
    if r.returncode == 0:
        log.info(f"TTS done: {name}")
        return True
    else:
        log.warning(f"TTS failed for {name}: {r.stderr[-200:]}")
        return False


def run_ig_pipeline(name, log):
    """Run Instagram pipeline on a story."""
    log.info(f"Running IG pipeline: {name}")
    start = time.time()

    r = subprocess.run(
        ['python3', 'instagram_pipeline.py', name],
        cwd=str(PIPELINE_DIR),
        capture_output=True, text=True,
        timeout=600  # 10 min max per reel
    )

    elapsed = time.time() - start

    if r.returncode == 0:
        ig = INSTAGRAM_DIR / f"{name}.mp4"
        if ig.exists():
            size = ig.stat().st_size / (1024 * 1024)
            log.info(f"DONE: {name} ({size:.1f}MB, {elapsed:.0f}s)")
            return True

    log.warning(f"FAILED: {name} after {elapsed:.0f}s")
    if r.stderr:
        log.warning(f"  stderr: {r.stderr[-200:]}")
    return False


def update_queue(log):
    """Regenerate posting queue and preview."""
    r = subprocess.run(
        ['python3', 'posting_queue.py', '--preview'],
        cwd=str(PIPELINE_DIR),
        capture_output=True, text=True
    )
    if r.returncode == 0:
        log.info("Posting queue updated")


def run_once(log):
    """Single pass: process everything that's ready."""
    # Phase 1: Generate TTS for stories that need it
    needs_tts = find_needs_tts()
    if needs_tts:
        log.info(f"Stories needing TTS: {len(needs_tts)}")
        for name in needs_tts:
            run_tts_for_story(name, log)

    # Phase 2: Run IG pipeline on stories with complete assets
    ready = find_ready_stories()
    if ready:
        log.info(f"Stories ready for IG pipeline: {ready}")
        processed = 0
        for name in ready:
            if run_ig_pipeline(name, log):
                processed += 1
        log.info(f"Processed: {processed}/{len(ready)}")
        if processed > 0:
            update_queue(log)
    else:
        log.info("No new stories ready for IG pipeline")

    # Status report
    needs_images = find_needs_images()
    total_stories = len(list(STORIES_DIR.glob("*.json")))
    ig_done = len(list(INSTAGRAM_DIR.glob("*.mp4"))) if INSTAGRAM_DIR.exists() else 0

    log.info(f"STATUS: {ig_done}/{total_stories} IG-ready, "
             f"{len(needs_images)} need images, "
             f"{len(needs_tts)} need TTS")

    return len(ready)


def show_status():
    """Show what autopilot would do."""
    ready = find_ready_stories()
    needs_tts = find_needs_tts()
    needs_images = find_needs_images()
    total = len(list(STORIES_DIR.glob("*.json")))
    ig_done = len(list(INSTAGRAM_DIR.glob("*.mp4"))) if INSTAGRAM_DIR.exists() else 0

    print(f"\n{'='*60}")
    print(f"  AUTOPILOT STATUS")
    print(f"{'='*60}")
    print(f"  Total stories:    {total}")
    print(f"  IG-ready:         {ig_done}")
    print(f"  Ready to compose: {len(ready)}")
    if ready:
        for r in ready:
            print(f"    - {r}")
    print(f"  Need TTS:         {len(needs_tts)}")
    print(f"  Need images:      {len(needs_images)}")
    if needs_images:
        for name, have, need in needs_images:
            print(f"    - {name} ({have}/{need})")
    print()


def daemon(log):
    """Run continuously, checking every POLL_INTERVAL seconds."""
    log.info(f"AUTOPILOT STARTED - checking every {POLL_INTERVAL}s")
    log.info(f"PID: {os.getpid()}")

    cycle = 0
    while True:
        cycle += 1
        log.info(f"--- Cycle {cycle} ---")

        try:
            run_once(log)
        except Exception as e:
            log.error(f"Cycle error: {e}")

        log.info(f"Sleeping {POLL_INTERVAL}s...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)

    if "--status" in sys.argv:
        show_status()
    elif "--once" in sys.argv:
        log = setup_logging()
        run_once(log)
    else:
        log = setup_logging()
        try:
            daemon(log)
        except KeyboardInterrupt:
            log.info("AUTOPILOT STOPPED")
