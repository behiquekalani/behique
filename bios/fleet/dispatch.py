#!/usr/bin/env python3
"""
BIOS Fleet Quick Dispatch
==========================
Fast command-line dispatch for common fleet tasks.

Usage:
    python3 dispatch.py image "glowing sacred geometry" --machine cobo
    python3 dispatch.py image "neon skull" --machine cobo --priority high
    python3 dispatch.py video 333 --machine cobo
    python3 dispatch.py video 528 --machine cobo --duration 60
    python3 dispatch.py scrape news --machine naboria
    python3 dispatch.py scrape reddit --machine cobo
    python3 dispatch.py blueprint "restaurant" --machine naboria
    python3 dispatch.py blueprint "gym" --machine naboria --language es
    python3 dispatch.py conviction --machine ceiba
    python3 dispatch.py run "python3 some_script.py" --machine cobo
    python3 dispatch.py status
    python3 dispatch.py status --machine cobo
    python3 dispatch.py pending
    python3 dispatch.py cancel <task_id>
"""

import sys
import json
import argparse
from pathlib import Path

# Import from task_queue
sys.path.insert(0, str(Path(__file__).parent))
from task_queue import (
    create_task,
    list_tasks,
    cancel_task,
    get_task,
    _format_task_line,
    _format_task_detail,
)

DEFAULT_MACHINE = "cobo"


def dispatch_image(args):
    prompt = args.prompt
    machine = args.machine or DEFAULT_MACHINE
    params = {"prompt": prompt}
    if args.preset:
        params["preset"] = args.preset
    if args.output_dir:
        params["output_dir"] = args.output_dir

    task = create_task(machine, "generate_image", params, args.priority)
    print(f"Dispatched image generation -> {machine}")
    print(f"  Task ID:  {task['id']}")
    print(f"  Prompt:   {prompt}")
    print(f"  Priority: {args.priority}")


def dispatch_video(args):
    theme = args.theme
    machine = args.machine or DEFAULT_MACHINE
    params = {"theme": str(theme), "duration": args.duration}

    task = create_task(machine, "generate_video", params, args.priority)
    print(f"Dispatched video generation -> {machine}")
    print(f"  Task ID:  {task['id']}")
    print(f"  Theme:    {theme}")
    print(f"  Duration: {args.duration}s")


def dispatch_scrape(args):
    scraper = args.scraper_name
    machine = args.machine or "naboria"
    params = {"scraper_name": scraper}
    if args.args:
        params["args"] = args.args

    task = create_task(machine, "run_scraper", params, args.priority)
    print(f"Dispatched scraper '{scraper}' -> {machine}")
    print(f"  Task ID: {task['id']}")


def dispatch_blueprint(args):
    niche = args.niche
    machine = args.machine or "naboria"
    language = args.language or "en"
    params = {"niche": niche, "language": language}

    task = create_task(machine, "generate_blueprint", params, args.priority)
    print(f"Dispatched blueprint '{niche}' ({language}) -> {machine}")
    print(f"  Task ID: {task['id']}")


def dispatch_conviction(args):
    machine = args.machine or "ceiba"
    task = create_task(machine, "run_conviction", {}, args.priority)
    print(f"Dispatched conviction engine -> {machine}")
    print(f"  Task ID: {task['id']}")


def dispatch_run(args):
    command = args.command
    machine = args.machine or DEFAULT_MACHINE
    params = {"command": command}
    if args.timeout:
        params["timeout"] = args.timeout

    task = create_task(machine, "custom", params, args.priority)
    print(f"Dispatched custom command -> {machine}")
    print(f"  Task ID: {task['id']}")
    print(f"  Command: {command}")


def show_status(args):
    machine = args.machine if hasattr(args, "machine") else None
    tasks = list_tasks(machine=machine)

    if not tasks:
        print("  No tasks in queue.")
        return

    # Group by status
    by_status = {}
    for t in tasks:
        s = t.get("status", "unknown")
        by_status.setdefault(s, []).append(t)

    total = len(tasks)
    print(f"\n  Fleet Queue Status ({total} total)")
    if machine:
        print(f"  Filtered: {machine}")
    print()

    for status in ["running", "pending", "failed", "completed", "cancelled"]:
        group = by_status.get(status, [])
        if not group:
            continue
        print(f"  --- {status.upper()} ({len(group)}) ---")
        for t in group[:20]:  # Show max 20 per group
            print(_format_task_line(t))
        if len(group) > 20:
            print(f"    ... and {len(group) - 20} more")
        print()


def show_pending(args):
    machine = args.machine if hasattr(args, "machine") else None
    tasks = list_tasks(machine=machine, status="pending")
    if not tasks:
        print("  No pending tasks.")
        return
    print(f"\n  Pending Tasks ({len(tasks)})\n")
    for t in tasks:
        print(_format_task_line(t))
    print()


def do_cancel(args):
    try:
        cancel_task(args.task_id)
        print(f"  Cancelled: {args.task_id}")
    except FileNotFoundError:
        print(f"  ERROR: Task {args.task_id} not found")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="BIOS Fleet Quick Dispatch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # Common args for dispatchers
    def add_common(p):
        p.add_argument("--machine", "-m", default=None, help="Target machine")
        p.add_argument("--priority", "-p", default="normal",
                       choices=["low", "normal", "high", "critical"])

    # image
    p_img = sub.add_parser("image", help="Generate an image")
    p_img.add_argument("prompt", help="Image prompt")
    p_img.add_argument("--preset", default=None)
    p_img.add_argument("--output-dir", default=None)
    add_common(p_img)

    # video
    p_vid = sub.add_parser("video", help="Generate a frequency video")
    p_vid.add_argument("theme", help="Frequency theme (e.g. 333, 528)")
    p_vid.add_argument("--duration", type=int, default=30)
    add_common(p_vid)

    # scrape
    p_scr = sub.add_parser("scrape", help="Run a scraper")
    p_scr.add_argument("scraper_name", help="Scraper name (news, social, reddit, trends)")
    p_scr.add_argument("--args", nargs="*", default=None, help="Extra args")
    add_common(p_scr)

    # blueprint
    p_bp = sub.add_parser("blueprint", help="Generate a business blueprint")
    p_bp.add_argument("niche", help="Business niche")
    p_bp.add_argument("--language", "-l", default="en")
    add_common(p_bp)

    # conviction
    p_conv = sub.add_parser("conviction", help="Run conviction engine")
    add_common(p_conv)

    # run (custom command)
    p_run = sub.add_parser("run", help="Run a custom command")
    p_run.add_argument("command", help="Command to execute")
    p_run.add_argument("--timeout", type=int, default=None)
    add_common(p_run)

    # status
    p_status = sub.add_parser("status", help="Show queue status")
    p_status.add_argument("--machine", "-m", default=None)

    # pending
    p_pend = sub.add_parser("pending", help="Show pending tasks only")
    p_pend.add_argument("--machine", "-m", default=None)

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel a task")
    p_cancel.add_argument("task_id", help="Task ID to cancel")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch_map = {
        "image": dispatch_image,
        "video": dispatch_video,
        "scrape": dispatch_scrape,
        "blueprint": dispatch_blueprint,
        "conviction": dispatch_conviction,
        "run": dispatch_run,
        "status": show_status,
        "pending": show_pending,
        "cancel": do_cancel,
    }

    handler = dispatch_map.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
