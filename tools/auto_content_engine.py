#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Auto Content Engine. Master orchestrator that runs the entire content
pipeline end-to-end with minimal human intervention.

Steps: pick topic -> write script -> generate visuals -> add audio ->
       compose video -> write caption -> generate thumbnail -> queue for posting

Content types: news, story, education, meme, quote, all

Usage:
    python3 auto_content_engine.py --type news --count 3
    python3 auto_content_engine.py --type story --count 2
    python3 auto_content_engine.py --type education --count 1 --account behikeai
    python3 auto_content_engine.py --type meme --count 5
    python3 auto_content_engine.py --type quote --count 3
    python3 auto_content_engine.py --type all --count 2
    python3 auto_content_engine.py --daily              # full daily run (recommended)
    python3 auto_content_engine.py --status              # show pipeline status
    python3 auto_content_engine.py --dry-run --type all  # preview without generating
    python3 auto_content_engine.py --help

Accounts: behikeai, kalaniandrez, dulc3recuerdo, s0ftrewind

Requires:
    - Ollama at localhost:11434 with qwen2.5:7b
    - Pillow for thumbnails
    - Existing tools in ~/behique/tools/
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
DAILY_DIR = NEWS_DIR / "daily"
SCRIPTS_DIR = NEWS_DIR / "scripts"
THUMBS_DIR = NEWS_DIR / "thumbnails"
READY_DIR = NEWS_DIR / "ready-to-post"
ENGINE_LOG = NEWS_DIR / "engine-runs.json"
QUEUE_FILE = NEWS_DIR / "post-queue.json"

ACCOUNTS = ["behikeai", "kalaniandrez", "dulc3recuerdo", "s0ftrewind"]

# --- Import existing tools ---
sys.path.insert(0, str(TOOLS_DIR))

# --- Matrix Disk auto-routing ---

def _check_matrix_disk(topic: str) -> str:
    """Check if a relevant matrix disk exists for the topic.
    Returns disk name if found, empty string otherwise."""
    try:
        from matrix_writer import best_disk_for_topic
        disk = best_disk_for_topic(topic)
        if disk:
            print(f"    [MATRIX] Found matching disk: {disk}")
        return disk
    except ImportError:
        return ""


def _generate_with_matrix(disk_name: str, topic: str, fmt: str, language: str = "en") -> str:
    """Generate content using matrix_writer instead of script_writer.
    Returns path to output file, or empty string on failure."""
    try:
        from matrix_writer import matrix_generate
        output = matrix_generate(disk_name, topic, fmt, language)
        return output if output else ""
    except ImportError:
        print("    [!] matrix_writer.py not available, falling back to script_writer")
        return ""
    except Exception as e:
        print(f"    [!] Matrix generation failed: {e}")
        return ""


def _run_tool(cmd: list, description: str, dry_run: bool = False) -> bool:
    """Run a tool subprocess and return True on success."""
    print(f"  [{description}] {' '.join(cmd[:4])}...")

    if dry_run:
        print(f"    [DRY RUN] Would run: {' '.join(cmd)}")
        return True

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(PROJECT_DIR),
        )
        if result.returncode == 0:
            # Print first few lines of output
            lines = result.stdout.strip().split("\n")
            for line in lines[:5]:
                if line.strip():
                    print(f"    {line.strip()}")
            if len(lines) > 5:
                print(f"    ... ({len(lines) - 5} more lines)")
            return True
        else:
            print(f"    [!] Failed: {result.stderr[:200] if result.stderr else 'unknown error'}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    [!] Timed out after 300s")
        return False
    except Exception as e:
        print(f"    [!] Error: {e}")
        return False


def _queue_post(image_path: str, caption: str, account: str):
    """Add a post to the instagram_poster queue."""
    try:
        from instagram_poster import load_queue, save_queue, gen_id, validate_caption, package_post

        queue = load_queue()
        now = datetime.now().isoformat()
        post_id = gen_id(caption, now)

        entry = {
            "id": post_id,
            "image": image_path,
            "caption": caption,
            "account": account,
            "schedule": "",
            "status": "queued",
            "created": now,
            "issues": validate_caption(caption),
        }

        queue.append(entry)
        save_queue(queue)
        package_post(entry)
        return post_id
    except Exception as e:
        print(f"    [!] Queue error: {e}")
        return None


def _load_engine_log() -> dict:
    """Load the engine run log."""
    if ENGINE_LOG.exists():
        try:
            with open(ENGINE_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return {"runs": []}


def _save_engine_log(log: dict):
    """Save engine run log."""
    ENGINE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ENGINE_LOG, "w") as f:
        json.dump(log, f, indent=2, default=str)


# =====================================================================
# SUB-PIPELINES
# =====================================================================

def pipeline_news(count: int, account: str, dry_run: bool, both_lang: bool) -> dict:
    """News carousel pipeline. Uses ai_news_pipeline.py."""
    results = {"type": "news", "generated": 0, "errors": 0, "files": []}

    print("\n  --- NEWS CAROUSEL PIPELINE ---")

    cmd = [
        sys.executable, str(TOOLS_DIR / "ai_news_pipeline.py"),
        "--stories", str(count),
        "--reels", str(min(count, 2)),
    ]
    if dry_run:
        cmd.append("--dry-run")
    if not both_lang:
        cmd.append("--no-spanish")

    success = _run_tool(cmd, "News Pipeline", dry_run=False)  # It handles its own dry-run

    if success:
        results["generated"] = count
        # Find today's output
        today = datetime.now().strftime("%Y-%m-%d")
        out_dir = DAILY_DIR / today
        if out_dir.exists():
            results["files"] = [str(f) for f in out_dir.iterdir() if f.is_file()]
    else:
        results["errors"] = 1

    # Generate thumbnails for carousels
    if not dry_run and results["files"]:
        today = datetime.now().strftime("%Y-%m-%d")
        out_dir = DAILY_DIR / today
        for caption_file in sorted(out_dir.glob("caption-*-en.txt")):
            try:
                caption_text = caption_file.read_text().strip()
                first_line = caption_text.split("\n")[0][:60]
                thumb_cmd = [
                    sys.executable, str(TOOLS_DIR / "thumbnail_generator.py"),
                    "--title", first_line,
                    "--size", "ig",
                    "--palette", "dark",
                ]
                _run_tool(thumb_cmd, "Thumbnail")
            except Exception:
                pass

    return results


def pipeline_story(count: int, account: str, dry_run: bool, both_lang: bool) -> dict:
    """Reddit story reel pipeline. Uses reddit_story_scraper.py + script_writer.py."""
    results = {"type": "story", "generated": 0, "errors": 0, "files": []}

    print("\n  --- REDDIT STORY PIPELINE ---")

    # Step 1: Scrape stories
    scrape_cmd = [
        sys.executable, str(TOOLS_DIR / "reddit_story_scraper.py"),
        "--count", str(count),
    ]
    scrape_ok = _run_tool(scrape_cmd, "Reddit Scraper", dry_run)

    if not scrape_ok and not dry_run:
        results["errors"] += 1
        return results

    # Step 2: Generate scripts from scraped stories
    stories_dir = TOOLS_DIR / "reel-pipeline" / "stories"
    if stories_dir.exists() and not dry_run:
        story_files = sorted(stories_dir.glob("reddit-*.json"))[:count]
        for sf in story_files:
            results["files"].append(str(sf))
            results["generated"] += 1

            # Generate thumbnail
            try:
                with open(sf) as f:
                    story = json.load(f)
                title = story.get("title", "").replace("-", " ").title()[:50]
                if title:
                    thumb_cmd = [
                        sys.executable, str(TOOLS_DIR / "thumbnail_generator.py"),
                        "--title", title,
                        "--template", "bold",
                        "--size", "both",
                    ]
                    _run_tool(thumb_cmd, "Thumbnail", dry_run)
            except Exception:
                pass
    elif dry_run:
        results["generated"] = count

    return results


def pipeline_education(count: int, account: str, dry_run: bool, both_lang: bool) -> dict:
    """Educational content pipeline. Uses matrix_writer if a disk matches, otherwise script_writer."""
    results = {"type": "education", "generated": 0, "errors": 0, "files": [], "mode": []}

    print("\n  --- EDUCATION CONTENT PIPELINE ---")

    # Try to load ideas to check for matrix disk matches
    ideas_file = NEWS_DIR / "content-ideas.json"
    matrix_topics = []  # topics handled by matrix_writer
    general_count = count  # topics for script_writer

    if ideas_file.exists() and not dry_run:
        try:
            with open(ideas_file) as f:
                ideas_data = json.load(f)
            ideas = ideas_data.get("ideas", [])[:count]
            for idea in ideas:
                topic = idea.get("title", "")
                if topic:
                    disk = _check_matrix_disk(topic)
                    if disk:
                        matrix_topics.append((topic, disk))
                        general_count -= 1
        except Exception:
            pass

    # Generate via matrix_writer for matched topics (expert mode)
    for topic, disk in matrix_topics:
        if dry_run:
            print(f"    [DRY RUN] Would use matrix_writer({disk}) for: {topic}")
            results["generated"] += 1
            results["mode"].append(f"matrix:{disk}")
            continue

        print(f"    [MATRIX MODE] {disk} -> {topic}")
        output = _generate_with_matrix(disk, topic, "script")
        if output:
            results["generated"] += 1
            results["files"].append(output)
            results["mode"].append(f"matrix:{disk}")
        else:
            # Fall back to script_writer for this topic
            general_count += 1
            results["mode"].append("fallback:script_writer")

    # Generate remaining via script_writer (general mode)
    if general_count > 0:
        print(f"    [GENERAL MODE] {general_count} topics via script_writer")
        script_cmd = [
            sys.executable, str(TOOLS_DIR / "script_writer.py"),
            "--from-ideas",
            "--count", str(general_count),
            "--format", "list",
            "--reel",
        ]
        if both_lang:
            script_cmd.append("--both-languages")
        if dry_run:
            script_cmd.append("--dry-run")

        success = _run_tool(script_cmd, "Script Writer", dry_run=False)

        if success:
            results["generated"] += general_count
            results["mode"].extend(["general:script_writer"] * general_count)

            # Generate thumbnails for each script
            if not dry_run and SCRIPTS_DIR.exists():
                recent_scripts = sorted(SCRIPTS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)[:general_count]
                for sf in recent_scripts:
                    results["files"].append(str(sf))
                    thumb_cmd = [
                        sys.executable, str(TOOLS_DIR / "thumbnail_generator.py"),
                        "--auto-from-script", str(sf),
                    ]
                    _run_tool(thumb_cmd, "Thumbnail", dry_run)
        else:
            results["errors"] = 1

    # Log mode breakdown for performance comparison
    if results["mode"]:
        matrix_count = sum(1 for m in results["mode"] if m.startswith("matrix:"))
        general_count = sum(1 for m in results["mode"] if m.startswith("general:"))
        print(f"    [ROUTING] Matrix: {matrix_count}, General: {general_count}")

    return results


def pipeline_meme(count: int, account: str, dry_run: bool, both_lang: bool) -> dict:
    """Meme pipeline. Uses reddit_meme_scraper.py."""
    results = {"type": "meme", "generated": 0, "errors": 0, "files": []}

    print("\n  --- MEME PIPELINE ---")

    meme_cmd = [
        sys.executable, str(TOOLS_DIR / "reddit_meme_scraper.py"),
        "--count", str(count),
    ]

    success = _run_tool(meme_cmd, "Meme Scraper", dry_run)

    if success:
        results["generated"] = count
    else:
        results["errors"] = 1

    return results


def pipeline_quote(count: int, account: str, dry_run: bool, both_lang: bool) -> dict:
    """Quote card pipeline. Uses script_writer.py for quote generation + thumbnail_generator.py."""
    results = {"type": "quote", "generated": 0, "errors": 0, "files": []}

    print("\n  --- QUOTE CARD PIPELINE ---")

    # Use Ollama to generate quotes via script_writer
    topics = [
        "Building in public as a solo founder",
        "The real cost of not starting",
        "Why most people stay consumers instead of builders",
        "Discipline beats motivation every time",
        "The gap between knowing and doing",
        "Stop waiting for permission to build",
        "Your first version will be ugly. Ship it anyway.",
        "The algorithm rewards consistency, not perfection",
        "Build for one person. Scale later.",
        "The best time to start was yesterday. The second best time is now.",
    ]

    import random
    selected_topics = random.sample(topics, min(count, len(topics)))

    for topic in selected_topics:
        if dry_run:
            print(f"    [DRY RUN] Would generate quote: {topic}")
            results["generated"] += 1
            continue

        # Generate the quote as a thumbnail
        thumb_cmd = [
            sys.executable, str(TOOLS_DIR / "thumbnail_generator.py"),
            "--title", topic,
            "--template", "minimal",
            "--size", "ig",
            "--palette", "warm",
            "--subtitle", "@behikeai",
        ]
        success = _run_tool(thumb_cmd, "Quote Card", dry_run=False)

        if success:
            results["generated"] += 1

            # Queue it for posting
            caption = f"{topic}\n\nSave this. Share it with someone who needs to hear it.\n\n#builder #entrepreneur #mindset #hustle #grind #motivation #startup #solofounder"
            _queue_post("", caption, account or "behikeai")
        else:
            results["errors"] += 1

    return results


# =====================================================================
# MAIN ORCHESTRATOR
# =====================================================================

PIPELINES = {
    "news": pipeline_news,
    "story": pipeline_story,
    "education": pipeline_education,
    "meme": pipeline_meme,
    "quote": pipeline_quote,
}

ACCOUNT_DEFAULTS = {
    "news": "behikeai",
    "story": "s0ftrewind",
    "education": "behikeai",
    "meme": "dulc3recuerdo",
    "quote": "behikeai",
}

DAILY_COUNTS = {
    "news": 3,
    "story": 2,
    "education": 1,
    "meme": 3,
    "quote": 2,
}


def run_engine(content_type: str, count: int, account: str, dry_run: bool, both_lang: bool) -> list:
    """Run the content engine for specified type(s)."""
    if content_type == "all":
        types_to_run = list(PIPELINES.keys())
    else:
        types_to_run = [content_type]

    all_results = []

    for ct in types_to_run:
        pipeline_fn = PIPELINES.get(ct)
        if not pipeline_fn:
            print(f"[!] Unknown content type: {ct}")
            continue

        ct_count = count if content_type != "all" else DAILY_COUNTS.get(ct, 1)
        ct_account = account or ACCOUNT_DEFAULTS.get(ct, "behikeai")

        result = pipeline_fn(ct_count, ct_account, dry_run, both_lang)
        all_results.append(result)

    return all_results


def run_daily(dry_run: bool, both_lang: bool):
    """Full daily content run. The big one."""
    print()
    print("=" * 60)
    print("  BEHIKE AUTO CONTENT ENGINE. DAILY RUN")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    if dry_run:
        print("  MODE: DRY RUN (no content will be generated)")
        print()

    start_time = time.time()
    results = run_engine("all", 0, "", dry_run, both_lang)

    # Generate calendar after content creation
    print("\n  --- CONTENT CALENDAR ---")
    cal_cmd = [sys.executable, str(TOOLS_DIR / "content_calendar.py"), "--generate"]
    _run_tool(cal_cmd, "Calendar", dry_run)

    elapsed = time.time() - start_time

    # Summary
    total_generated = sum(r["generated"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    print()
    print("=" * 60)
    print("  DAILY RUN COMPLETE")
    print("=" * 60)
    print()
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Total generated: {total_generated}")
    print(f"  Errors: {total_errors}")
    print()

    for r in results:
        status = "OK" if r["errors"] == 0 else "ERRORS"
        print(f"  {r['type']:12s}: {r['generated']} generated [{status}]")

    print()
    print("  NEXT STEPS:")
    print("  1. Review generated content in Ceiba/news/")
    print("  2. Check calendar: python3 tools/content_calendar.py --today")
    print("  3. Post when ready: bash tools/auto_post.sh")
    print()
    print("=" * 60)
    print()

    # Log the run
    log = _load_engine_log()
    log["runs"].append({
        "date": datetime.now().isoformat(),
        "type": "daily",
        "duration": round(elapsed, 1),
        "total_generated": total_generated,
        "total_errors": total_errors,
        "results": results,
    })
    _save_engine_log(log)


def show_status():
    """Show pipeline status: what is available, what needs attention."""
    print()
    print("=" * 60)
    print("  CONTENT ENGINE STATUS")
    print("=" * 60)
    print()

    # Check Ollama
    try:
        import urllib.request
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        urllib.request.urlopen(f"{url}/api/tags", timeout=3)
        print("  Ollama:       ONLINE")
    except Exception:
        print("  Ollama:       OFFLINE (scripts won't generate)")

    # Check Pillow
    try:
        import PIL
        print(f"  Pillow:       v{PIL.__version__}")
    except ImportError:
        print("  Pillow:       NOT INSTALLED (thumbnails won't work)")

    # Check Kokoro TTS
    kokoro_model = TOOLS_DIR / "reel-pipeline" / "kokoro-v1.0.onnx"
    print(f"  Kokoro TTS:   {'AVAILABLE' if kokoro_model.exists() else 'NOT FOUND'}")

    # Content stats
    print()

    # Queue
    queue_count = 0
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE) as f:
                queue = json.load(f)
            queue_count = len([e for e in queue if e.get("status") == "queued"])
        except Exception:
            pass
    print(f"  Posts queued:  {queue_count}")

    # Scripts
    script_count = 0
    if SCRIPTS_DIR.exists():
        script_count = len(list(SCRIPTS_DIR.glob("*.json")))
    print(f"  Scripts:      {script_count}")

    # Thumbnails
    thumb_count = 0
    if THUMBS_DIR.exists():
        thumb_count = len(list(THUMBS_DIR.glob("*.png")))
    print(f"  Thumbnails:   {thumb_count}")

    # Calendar
    cal_files = sorted(NEWS_DIR.glob("calendar-*.json"), reverse=True)
    if cal_files:
        latest_cal = cal_files[0].stem.replace("calendar-", "")
        print(f"  Calendar:     {latest_cal}")
    else:
        print(f"  Calendar:     NONE (run --daily or content_calendar.py --generate)")

    # Engine runs
    log = _load_engine_log()
    runs = log.get("runs", [])
    if runs:
        last = runs[-1]
        print(f"  Last run:     {last.get('date', '?')[:19]}")
        print(f"  Last result:  {last.get('total_generated', 0)} generated, {last.get('total_errors', 0)} errors")
    else:
        print(f"  Last run:     NEVER")

    # Analytics
    analytics_file = NEWS_DIR / "analytics.json"
    if analytics_file.exists():
        try:
            with open(analytics_file) as f:
                analytics = json.load(f)
            post_count = len(analytics.get("posts", []))
            print(f"  Analytics:    {post_count} posts tracked")
        except Exception:
            print(f"  Analytics:    ERROR reading file")
    else:
        print(f"  Analytics:    NO DATA (use performance_tracker.py)")

    # Competitors
    comp_file = NEWS_DIR / "competitors.json"
    if comp_file.exists():
        try:
            with open(comp_file) as f:
                comp = json.load(f)
            comp_count = len(comp.get("competitors", {}))
            print(f"  Competitors:  {comp_count} tracked")
        except Exception:
            pass
    else:
        print(f"  Competitors:  NONE (use competitor_tracker.py)")

    print()
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Auto Content Engine. Master orchestrator for the Behike content pipeline. Copyright 2026 Behike."
    )

    parser.add_argument("--type", choices=list(PIPELINES.keys()) + ["all"],
                        help="Content type to generate")
    parser.add_argument("--count", type=int, default=3,
                        help="Number of items to generate per type (default: 3)")
    parser.add_argument("--account", choices=ACCOUNTS,
                        help="Target account (default: auto-assign)")
    parser.add_argument("--daily", action="store_true",
                        help="Full daily content run (all types, recommended)")
    parser.add_argument("--status", action="store_true",
                        help="Show pipeline status")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without generating")
    parser.add_argument("--both-languages", action="store_true",
                        help="Generate both EN and ES versions")

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.daily:
        run_daily(args.dry_run, args.both_languages)
    elif args.type:
        print()
        print("=" * 60)
        print(f"  BEHIKE AUTO CONTENT ENGINE. {args.type.upper()}")
        print("=" * 60)
        print()

        start_time = time.time()
        results = run_engine(args.type, args.count, args.account or "", args.dry_run, args.both_languages)
        elapsed = time.time() - start_time

        total_generated = sum(r["generated"] for r in results)
        total_errors = sum(r["errors"] for r in results)

        print()
        print("=" * 60)
        print(f"  Done in {elapsed:.1f}s. Generated: {total_generated}, Errors: {total_errors}")
        print("=" * 60)
        print()

        # Log
        log = _load_engine_log()
        log["runs"].append({
            "date": datetime.now().isoformat(),
            "type": args.type,
            "count": args.count,
            "duration": round(elapsed, 1),
            "total_generated": total_generated,
            "total_errors": total_errors,
            "results": results,
        })
        _save_engine_log(log)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
