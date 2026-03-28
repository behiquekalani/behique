"""
Daily Batch Image Generator for Cobo
Generates a daily set of images for different content needs:
  - 1 frequency thumbnail (YouTube)
  - 3 social media images (Instagram)
  - 1 product mockup (store)

Schedule via Windows Task Scheduler to run daily.

Setup Task Scheduler:
  1. Open Task Scheduler
  2. Create Basic Task > "SD Daily Batch"
  3. Trigger: Daily, at your preferred time (e.g., 3:00 AM)
  4. Action: Start a Program
     Program: python
     Arguments: C:\behique\stable-diffusion\batch_daily.py
     Start in: C:\behique\stable-diffusion\
  5. Make sure "Run whether user is logged on or not" is checked
  6. Condition: uncheck "Start only if AC power"

Or run manually:
  python batch_daily.py
  python batch_daily.py --dry-run     (preview what would generate)
  python batch_daily.py --category social  (only one category)
"""

import sys
import os
import random
import json
import logging
from datetime import datetime
from pathlib import Path

# Add script directory to path so we can import generate
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from generate import (
    check_api,
    generate_from_preset,
    load_presets,
    SD_API_URL,
    OUTPUT_DIR,
)

# --- Logging ---
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"batch_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("batch_daily")


# --- Daily batch configuration ---
DAILY_BATCH = {
    "frequency": {
        "count": 1,
        "description": "YouTube frequency thumbnail",
    },
    "social": {
        "count": 3,
        "description": "Instagram social media images",
    },
    "mockup": {
        "count": 1,
        "description": "Product mockup for store",
    },
}


def run_daily_batch(dry_run=False, category_filter=None):
    """Run the daily batch generation."""
    log.info("=" * 60)
    log.info("Starting daily batch generation")
    log.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info("=" * 60)

    # Check API
    if not dry_run:
        if not check_api():
            log.error(f"SD WebUI API not reachable at {SD_API_URL}")
            log.error("Start it with: C:\\behique\\stable-diffusion\\start_sd.bat")
            return False

    presets = load_presets()
    if not presets:
        log.error("Could not load presets.json")
        return False

    total_generated = 0
    all_files = []

    for category, config in DAILY_BATCH.items():
        if category_filter and category != category_filter:
            continue

        count = config["count"]
        desc = config["description"]

        log.info(f"\n--- {desc} ({count} image{'s' if count > 1 else ''}) ---")

        if category not in presets:
            log.warning(f"Category '{category}' not in presets, skipping")
            continue

        # Pick random presets (no repeats if possible)
        available = presets[category]
        picks = random.sample(available, min(count, len(available)))

        for i, preset in enumerate(picks):
            log.info(f"  [{i+1}/{count}] Preset: {preset['name']}")
            log.info(f"    Prompt: {preset['prompt'][:80]}...")

            if dry_run:
                log.info("    [DRY RUN] Would generate this image")
                continue

            try:
                files = generate_from_preset(category, preset["name"])
                if files:
                    all_files.extend(files)
                    total_generated += len(files)
                    log.info(f"    Generated {len(files)} file(s)")
                else:
                    log.warning(f"    No files generated for {preset['name']}")
            except Exception as e:
                log.error(f"    Error generating {preset['name']}: {e}")

    # Summary
    log.info("\n" + "=" * 60)
    if dry_run:
        planned = sum(
            c["count"]
            for cat, c in DAILY_BATCH.items()
            if not category_filter or cat == category_filter
        )
        log.info(f"DRY RUN complete. Would generate {planned} images.")
    else:
        log.info(f"Batch complete. Generated {total_generated} images.")
        if all_files:
            log.info("Files:")
            for f in all_files:
                log.info(f"  {f}")
    log.info("=" * 60)

    # Write summary to a daily manifest
    if not dry_run and all_files:
        manifest_file = OUTPUT_DIR / f"manifest_{datetime.now().strftime('%Y%m%d')}.json"
        manifest = {
            "date": datetime.now().isoformat(),
            "total_images": total_generated,
            "files": all_files,
        }
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        log.info(f"Manifest saved: {manifest_file}")

    return True


def setup_task_scheduler():
    """Print instructions for Windows Task Scheduler setup."""
    print()
    print("=" * 60)
    print("  Windows Task Scheduler Setup")
    print("=" * 60)
    print()
    print("Option 1: Command line (run as Administrator):")
    print()
    print('  schtasks /create /tn "SD Daily Batch" /tr "python %s" /sc daily /st 03:00' % __file__)
    print()
    print("Option 2: GUI:")
    print("  1. Open Task Scheduler (taskschd.msc)")
    print('  2. Create Basic Task > name: "SD Daily Batch"')
    print("  3. Trigger: Daily, 3:00 AM")
    print("  4. Action: Start a Program")
    print("     Program/script: python")
    print(f"     Arguments: {__file__}")
    print(f"     Start in: {SCRIPT_DIR}")
    print()
    print("Important:")
    print("  - Make sure SD WebUI is running before the scheduled time")
    print("  - Or add start_sd_api.bat as a separate scheduled task")
    print("    that runs 5 minutes before this one")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Daily SD image batch generator")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")
    parser.add_argument("--category", choices=["frequency", "social", "mockup"], help="Only run one category")
    parser.add_argument("--setup", action="store_true", help="Show Task Scheduler setup instructions")

    args = parser.parse_args()

    if args.setup:
        setup_task_scheduler()
    else:
        success = run_daily_batch(dry_run=args.dry_run, category_filter=args.category)
        sys.exit(0 if success else 1)
