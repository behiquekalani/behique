#!/usr/bin/env python3
"""
Auto Content Pipeline - Runs on Cobo (Windows, GTX 1080 Ti).
Reads content-empire directories, generates images via Stable Diffusion,
organizes output by platform, and tracks what's been posted.

Usage:
    python auto_content_pipeline.py --run
    python auto_content_pipeline.py --status
    python auto_content_pipeline.py --platform instagram
    python auto_content_pipeline.py --dry-run
"""

import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, date
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths -- Windows (Cobo) paths. Syncthing mirrors content-empire here.
# ---------------------------------------------------------------------------
BEHIQUE_ROOT = Path(r"C:\behique")
CONTENT_EMPIRE = BEHIQUE_ROOT / "content-empire"
DATA_DIR = BEHIQUE_ROOT / "data"
OUTPUT_DIR = BEHIQUE_ROOT / "output"
MODE_FILE = BEHIQUE_ROOT / "mode.json"
POSTED_FILE = DATA_DIR / "posted.json"
SCHEDULE_FILE = DATA_DIR / "schedule.json"
LOG_FILE = DATA_DIR / "pipeline.log"

SD_URL = "http://127.0.0.1:7860"

# Daily quotas per platform
DAILY_QUOTAS = {
    "instagram": 2,
    "tiktok": 1,
    "twitter": 1,
    "linkedin": 1,
}

# Map platform to its content directory name and file prefix
PLATFORM_CONFIG = {
    "instagram": {"dir": "instagram-ready", "prefix": "post-", "ext": ".md"},
    "tiktok": {"dir": "tiktok-ready", "prefix": "tiktok-", "ext": ".md"},
    "twitter": {"dir": "twitter-ready", "prefix": "thread-", "ext": ".md"},
    "linkedin": {"dir": "linkedin-ready", "prefix": "linkedin-", "ext": ".md"},
}

# SD prompt field names to search for in content files
SD_PROMPT_KEYS = ["SD_PROMPT", "Image Prompt", "IMAGE_PROMPT"]


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def setup_logging():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("pipeline")


log = setup_logging()


# ---------------------------------------------------------------------------
# Gaming mode check
# ---------------------------------------------------------------------------
def is_gaming_mode() -> bool:
    """Check C:\\behique\\mode.json for gaming mode."""
    if not MODE_FILE.exists():
        return False
    try:
        with open(MODE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("mode", "").lower() == "gaming"
    except (json.JSONDecodeError, IOError):
        return False


# ---------------------------------------------------------------------------
# Stable Diffusion integration
# ---------------------------------------------------------------------------
def sd_is_running() -> bool:
    """Check if Stable Diffusion WebUI API is reachable."""
    try:
        req = urllib.request.Request(f"{SD_URL}/sdapi/v1/options", method="GET")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


def generate_image(prompt: str, output_path: Path, width: int = 1024, height: int = 1024) -> bool:
    """Generate an image using SD WebUI API (txt2img)."""
    payload = {
        "prompt": prompt,
        "negative_prompt": "blurry, low quality, watermark, text, logo, ugly, deformed",
        "steps": 30,
        "cfg_scale": 7.5,
        "width": width,
        "height": height,
        "sampler_name": "DPM++ 2M Karras",
        "batch_size": 1,
        "n_iter": 1,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{SD_URL}/sdapi/v1/txt2img",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if "images" in result and result["images"]:
            import base64
            img_data = base64.b64decode(result["images"][0])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_data)
            log.info(f"Image saved: {output_path}")
            return True
        else:
            log.warning("SD returned no images")
            return False
    except Exception as e:
        log.error(f"SD generation failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Content file parser
# ---------------------------------------------------------------------------
def parse_content_file(filepath: Path) -> dict:
    """Parse a markdown content file into structured data."""
    text = filepath.read_text(encoding="utf-8")
    result = {
        "file": str(filepath),
        "filename": filepath.name,
        "title": "",
        "caption": "",
        "hashtags": "",
        "sd_prompt": "",
        "carousel_slides": "",
        "hook": "",
        "script": "",
        "visual_direction": "",
        "cta": "",
        "best_time": "",
        "raw": text,
    }

    # Title from first heading
    title_match = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract sections by ## or ### headings
    sections = re.split(r"^#{2,3}\s+", text, flags=re.MULTILINE)
    headers = re.findall(r"^#{2,3}\s+(.+)", text, re.MULTILINE)

    for header, body in zip(headers, sections[1:]):
        header_lower = header.strip().lower()
        body = body.strip()

        if header_lower == "caption":
            result["caption"] = body
        elif header_lower in ("hashtags", "hashtags"):
            result["hashtags"] = body
        elif header_lower in ("image prompt",):
            result["sd_prompt"] = body
        elif header_lower == "sd_prompt":
            result["sd_prompt"] = body
        elif header_lower == "carousel slides":
            result["carousel_slides"] = body
        elif header_lower.startswith("hook"):
            result["hook"] = body
        elif header_lower == "script":
            result["script"] = body
        elif header_lower == "visual direction":
            result["visual_direction"] = body
        elif header_lower == "cta":
            result["cta"] = body
        elif header_lower == "best time to post":
            result["best_time"] = body

    # Fallback: look for SD_PROMPT in raw text
    if not result["sd_prompt"]:
        for key in SD_PROMPT_KEYS:
            match = re.search(rf"###?\s*{key}\s*\n(.+?)(?:\n###?\s|\Z)", text, re.DOTALL)
            if match:
                result["sd_prompt"] = match.group(1).strip()
                break

    return result


# ---------------------------------------------------------------------------
# Posted tracking
# ---------------------------------------------------------------------------
def load_posted() -> dict:
    """Load the posted items tracker."""
    if POSTED_FILE.exists():
        try:
            with open(POSTED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"posted": {}, "ready": {}, "last_updated": ""}


def save_posted(data: dict):
    """Save the posted items tracker."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_posted(tracker: dict, platform: str, filename: str) -> bool:
    """Check if a content piece has been posted."""
    return filename in tracker.get("posted", {}).get(platform, [])


def is_ready(tracker: dict, platform: str, filename: str) -> bool:
    """Check if a content piece is marked ready to post."""
    return filename in tracker.get("ready", {}).get(platform, [])


def mark_ready(tracker: dict, platform: str, filename: str):
    """Mark a content piece as ready to post."""
    if platform not in tracker.setdefault("ready", {}):
        tracker["ready"][platform] = []
    if filename not in tracker["ready"][platform]:
        tracker["ready"][platform].append(filename)


def mark_posted(tracker: dict, platform: str, filename: str):
    """Mark a content piece as posted."""
    if platform not in tracker.setdefault("posted", {}):
        tracker["posted"][platform] = []
    if filename not in tracker["posted"][platform]:
        tracker["posted"][platform].append(filename)
    # Remove from ready
    if platform in tracker.get("ready", {}):
        tracker["ready"][platform] = [
            f for f in tracker["ready"][platform] if f != filename
        ]


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
def load_schedule() -> dict:
    """Load the schedule tracker."""
    if SCHEDULE_FILE.exists():
        try:
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"days": {}}


def save_schedule(data: dict):
    """Save the schedule tracker."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_today_count(schedule: dict, platform: str) -> int:
    """How many items have been generated today for a given platform."""
    today = date.today().isoformat()
    return len(schedule.get("days", {}).get(today, {}).get(platform, []))


def record_generation(schedule: dict, platform: str, filename: str):
    """Record that a piece was generated today."""
    today = date.today().isoformat()
    days = schedule.setdefault("days", {})
    day_data = days.setdefault(today, {})
    platform_list = day_data.setdefault(platform, [])
    platform_list.append({
        "file": filename,
        "time": datetime.now().strftime("%H:%M:%S"),
    })


# ---------------------------------------------------------------------------
# Content discovery
# ---------------------------------------------------------------------------
def get_content_files(platform: str) -> list:
    """Get all content files for a platform, sorted by filename."""
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return []
    content_dir = CONTENT_EMPIRE / config["dir"]
    if not content_dir.exists():
        log.warning(f"Directory not found: {content_dir}")
        return []
    files = sorted(content_dir.glob(f"*{config['ext']}"))
    return files


def get_next_unposted(platform: str, tracker: dict, count: int = 1) -> list:
    """Get the next N unposted content files for a platform."""
    files = get_content_files(platform)
    unposted = []
    for f in files:
        if not is_posted(tracker, platform, f.name) and not is_ready(tracker, platform, f.name):
            unposted.append(f)
            if len(unposted) >= count:
                break
    return unposted


# ---------------------------------------------------------------------------
# Output organization
# ---------------------------------------------------------------------------
def get_output_dir(platform: str) -> Path:
    """Get the output directory for a platform, organized by date."""
    today = date.today().isoformat()
    out = OUTPUT_DIR / platform / today
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_content_output(platform: str, parsed: dict, image_path: Path = None) -> Path:
    """Save the processed content to the output folder."""
    out_dir = get_output_dir(platform)
    stem = Path(parsed["filename"]).stem

    # Save caption + hashtags as text file
    caption_file = out_dir / f"{stem}_caption.txt"
    caption_parts = []
    if parsed.get("caption"):
        caption_parts.append(parsed["caption"])
    elif parsed.get("script"):
        caption_parts.append(parsed["script"])
    if parsed.get("hashtags"):
        caption_parts.append(f"\n{parsed['hashtags']}")
    if parsed.get("cta"):
        caption_parts.append(f"\n{parsed['cta']}")

    caption_file.write_text("\n".join(caption_parts), encoding="utf-8")
    log.info(f"Caption saved: {caption_file}")

    # Save metadata
    meta_file = out_dir / f"{stem}_meta.json"
    meta = {
        "source_file": parsed["file"],
        "platform": platform,
        "title": parsed["title"],
        "best_time": parsed.get("best_time", ""),
        "generated_at": datetime.now().isoformat(),
        "image": str(image_path) if image_path else None,
        "status": "ready_to_post",
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # If there are carousel slides, save them separately
    if parsed.get("carousel_slides"):
        slides_file = out_dir / f"{stem}_slides.txt"
        slides_file.write_text(parsed["carousel_slides"], encoding="utf-8")

    return out_dir


# ---------------------------------------------------------------------------
# Pipeline core
# ---------------------------------------------------------------------------
def process_content(platform: str, filepath: Path, tracker: dict, schedule: dict,
                    dry_run: bool = False) -> bool:
    """Process a single content file: parse, generate image, save output."""
    log.info(f"Processing [{platform}] {filepath.name}")

    parsed = parse_content_file(filepath)

    if dry_run:
        log.info(f"  [DRY RUN] Would process: {filepath.name}")
        log.info(f"  Title: {parsed['title']}")
        log.info(f"  SD Prompt: {parsed['sd_prompt'][:100]}..." if parsed["sd_prompt"] else "  No SD prompt found")
        log.info(f"  Caption length: {len(parsed['caption'])} chars")
        return True

    # Generate image if SD is running and there's a prompt
    image_path = None
    if parsed["sd_prompt"] and sd_is_running():
        out_dir = get_output_dir(platform)
        stem = Path(parsed["filename"]).stem
        image_path = out_dir / f"{stem}.png"

        # Platform-specific dimensions
        dimensions = {
            "instagram": (1080, 1080),
            "tiktok": (1080, 1920),
            "twitter": (1200, 675),
            "linkedin": (1200, 627),
        }
        w, h = dimensions.get(platform, (1024, 1024))

        log.info(f"  Generating image ({w}x{h})...")
        if generate_image(parsed["sd_prompt"], image_path, w, h):
            log.info(f"  Image generated: {image_path}")
        else:
            log.warning(f"  Image generation failed, continuing without image")
            image_path = None
    elif parsed["sd_prompt"]:
        log.info("  SD not running, skipping image generation")
    else:
        log.info("  No SD prompt in content file")

    # Save organized output
    save_content_output(platform, parsed, image_path)

    # Update trackers
    mark_ready(tracker, platform, filepath.name)
    record_generation(schedule, platform, filepath.name)

    log.info(f"  Done: {filepath.name} -> ready to post")
    return True


def run_pipeline(platforms: list = None, dry_run: bool = False):
    """Run the full daily content pipeline."""
    if is_gaming_mode():
        log.info("Gaming mode active. Pipeline paused. Go frag.")
        return

    tracker = load_posted()
    schedule = load_schedule()

    if platforms is None:
        platforms = list(DAILY_QUOTAS.keys())

    total_processed = 0
    total_skipped = 0

    for platform in platforms:
        quota = DAILY_QUOTAS.get(platform, 0)
        already_done = get_today_count(schedule, platform)
        remaining = max(0, quota - already_done)

        if remaining == 0:
            log.info(f"[{platform}] Daily quota met ({quota}/{quota}). Skipping.")
            total_skipped += 1
            continue

        log.info(f"[{platform}] Generating {remaining} piece(s) (quota: {quota}, done today: {already_done})")

        next_files = get_next_unposted(platform, tracker, count=remaining)

        if not next_files:
            log.warning(f"[{platform}] No unposted content available")
            continue

        for filepath in next_files:
            success = process_content(platform, filepath, tracker, schedule, dry_run)
            if success:
                total_processed += 1

            # Small delay between SD generations to avoid overloading GPU
            if not dry_run and sd_is_running():
                time.sleep(2)

    # Save state
    if not dry_run:
        save_posted(tracker)
        save_schedule(schedule)

    log.info(f"\nPipeline complete. Processed: {total_processed}, Skipped (quota met): {total_skipped}")


# ---------------------------------------------------------------------------
# Status report
# ---------------------------------------------------------------------------
def show_status():
    """Show pipeline status: what's been posted, what's next, quotas."""
    tracker = load_posted()
    schedule = load_schedule()

    print("\n=== AUTO CONTENT PIPELINE STATUS ===\n")

    # Gaming mode check
    if is_gaming_mode():
        print("[!] GAMING MODE ACTIVE - pipeline paused\n")

    # SD status
    print(f"Stable Diffusion: {'ONLINE' if sd_is_running() else 'OFFLINE'}")
    print()

    for platform in DAILY_QUOTAS:
        config = PLATFORM_CONFIG[platform]
        content_dir = CONTENT_EMPIRE / config["dir"]

        total = len(list(content_dir.glob(f"*{config['ext']}"))) if content_dir.exists() else 0
        posted = len(tracker.get("posted", {}).get(platform, []))
        ready = len(tracker.get("ready", {}).get(platform, []))
        today_done = get_today_count(schedule, platform)
        quota = DAILY_QUOTAS[platform]

        print(f"--- {platform.upper()} ---")
        print(f"  Total content files: {total}")
        print(f"  Posted:              {posted}")
        print(f"  Ready to post:       {ready}")
        print(f"  Remaining:           {total - posted - ready}")
        print(f"  Today:               {today_done}/{quota}")

        # Show next up
        next_files = get_next_unposted(platform, tracker, count=3)
        if next_files:
            print(f"  Next up:")
            for f in next_files:
                parsed = parse_content_file(f)
                title = parsed["title"][:60] if parsed["title"] else f.name
                print(f"    -> {title}")
        else:
            print(f"  Next up: (none available)")

        print()

    # Today's output
    today = date.today().isoformat()
    today_output = OUTPUT_DIR / "instagram" / today
    if today_output.exists():
        files = list(today_output.iterdir())
        print(f"Today's output folder: {today_output}")
        print(f"  Files generated: {len(files)}")
    else:
        print(f"No output generated today yet.")

    # Schedule history (last 7 days)
    print(f"\n--- RECENT HISTORY ---")
    days = schedule.get("days", {})
    for day_key in sorted(days.keys(), reverse=True)[:7]:
        day_data = days[day_key]
        counts = {p: len(items) for p, items in day_data.items()}
        summary = ", ".join(f"{p}: {c}" for p, c in counts.items())
        print(f"  {day_key}: {summary}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Auto Content Pipeline - Generates and organizes daily content for all platforms."
    )
    parser.add_argument("--run", action="store_true", help="Run the full daily pipeline")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--platform", type=str, help="Generate for one platform only (instagram, tiktok, twitter, linkedin)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without doing it")
    parser.add_argument("--mark-posted", type=str, nargs=2, metavar=("PLATFORM", "FILENAME"),
                        help="Manually mark a file as posted")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.mark_posted:
        tracker = load_posted()
        platform, filename = args.mark_posted
        mark_posted(tracker, platform, filename)
        save_posted(tracker)
        log.info(f"Marked as posted: [{platform}] {filename}")
        return

    if args.run or args.platform or args.dry_run:
        platforms = [args.platform] if args.platform else None
        if args.platform and args.platform not in PLATFORM_CONFIG:
            log.error(f"Unknown platform: {args.platform}")
            log.info(f"Available: {', '.join(PLATFORM_CONFIG.keys())}")
            return

        run_pipeline(platforms=platforms, dry_run=args.dry_run or False)
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
