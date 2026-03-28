#!/usr/bin/env python3
"""BIOS Master Cron Installer - installs all cron jobs in one command."""

import argparse
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

BIOS = "/Users/kalani/behique/bios"
PYTHON = sys.executable
LOG_DIR = f"{BIOS}/logs"

# (schedule, script_path, description)
JOBS = [
    ("0 */6 * * *",   f"{BIOS}/ingestion/news_scraper.py",         "News scraper (every 6h)"),
    ("*/30 * * * *",   f"{BIOS}/ingestion/social_scraper.py",       "Social scraper (every 30min)"),
    ("0 */2 * * *",    f"{BIOS}/ingestion/pr_scraper.py",           "PR scraper (every 2h)"),
    ("0 */12 * * *",   f"{BIOS}/ingestion/pr_opportunities.py",     "PR opportunities (every 12h)"),
    ("0 * * * *",      f"{BIOS}/intelligence/conviction_engine.py",  "Conviction engine (every hour)"),
    ("30 */6 * * *",   f"{BIOS}/intelligence/content_wiring.py",     "Content wiring (every 6h)"),
    ("0 6 * * *",      f"{BIOS}/scheduler/daily_briefing.py",        "Daily briefing (6 AM)"),
    ("15 * * * *",     f"{BIOS}/fleet/sync_results.py",              "Fleet sync (every hour)"),
    ("0 */4 * * *",    f"{BIOS}/health_check.py",                    "Health check (every 4h)"),
    ("30 * * * *",     f"{BIOS}/publisher/publish_daemon.py",        "Publisher daemon (every hour)"),
    ("0 21 * * *",     f"{BIOS}/sales/daily_digest.py",              "Sales digest (9 PM)"),
    ("0 3 * * *",      f"{BIOS}/fleet/backup.py",                    "Backup (3 AM)"),
    ("15 */6 * * *",   f"{BIOS}/trading/polymarket_research.py",     "Polymarket research (every 6h)"),
    ("45 */6 * * *",   f"{BIOS}/intelligence/trends_detector.py",    "Trends detector (every 6h)"),
    ("0 8 * * *",      f"{BIOS}/intelligence/price_monitor.py",      "Price monitor (8 AM daily)"),
    ("0 7 * * *",      f"{BIOS}/notifications/telegram_bot.py",      "Goal tracker morning message (7 AM)"),
    ("0 10 * * *",     f"{BIOS}/sales/review_request.py",            "Review request check (daily 10 AM)"),
]

MARKER = "# BIOS-MANAGED"


def log_name(script_path):
    """Derive log filename from script path."""
    return Path(script_path).stem + ".log"


def build_cron_line(schedule, script):
    """Build a full cron line with logging and marker."""
    log = f"{LOG_DIR}/{log_name(script)}"
    return f"{schedule} {PYTHON} {script} >> {log} 2>&1 {MARKER}"


def get_current_crontab():
    """Return current crontab as string."""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def set_crontab(content):
    """Write new crontab."""
    proc = subprocess.run(["crontab", "-"], input=content, capture_output=True, text=True)
    return proc.returncode == 0


def backup_crontab():
    """Save current crontab to bios/logs/."""
    current = get_current_crontab()
    if not current.strip():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{LOG_DIR}/crontab_backup_{ts}.txt"
    Path(backup_path).write_text(current)
    return backup_path


def is_job_installed(current_lines, script):
    """Check if a job for this script already exists."""
    return any(script in line for line in current_lines)


def cmd_list():
    """Show all jobs and their install status."""
    current = get_current_crontab()
    lines = current.splitlines()
    print(f"{'Status':<12} {'Schedule':<18} Description")
    print("-" * 70)
    for schedule, script, desc in JOBS:
        installed = is_job_installed(lines, script)
        status = "INSTALLED" if installed else "MISSING"
        color = "\033[32m" if installed else "\033[31m"
        print(f"{color}{status:<12}\033[0m {schedule:<18} {desc}")
    installed_count = sum(1 for _, s, _ in JOBS if is_job_installed(lines, s))
    print(f"\n{installed_count}/{len(JOBS)} jobs installed")


def cmd_install():
    """Install all missing cron jobs."""
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    backup = backup_crontab()
    if backup:
        print(f"Backed up crontab to {backup}")

    current = get_current_crontab()
    lines = current.splitlines()
    added = 0

    for schedule, script, desc in JOBS:
        if is_job_installed(lines, script):
            continue
        cron_line = build_cron_line(schedule, script)
        lines.append(cron_line)
        print(f"  + {desc}")
        added += 1

    if added == 0:
        print("All jobs already installed.")
        return

    new_crontab = "\n".join(lines) + "\n"
    if set_crontab(new_crontab):
        print(f"\nInstalled {added} new cron jobs ({len(JOBS)} total)")
    else:
        print("ERROR: Failed to write crontab", file=sys.stderr)
        sys.exit(1)


def cmd_remove():
    """Remove all BIOS-managed cron jobs."""
    backup = backup_crontab()
    if backup:
        print(f"Backed up crontab to {backup}")

    current = get_current_crontab()
    lines = current.splitlines()
    kept = [line for line in lines if MARKER not in line and not any(s in line for _, s, _ in JOBS)]
    removed = len(lines) - len(kept)

    new_crontab = "\n".join(kept) + "\n" if kept else ""
    if set_crontab(new_crontab):
        print(f"Removed {removed} BIOS cron jobs")
    else:
        print("ERROR: Failed to write crontab", file=sys.stderr)
        sys.exit(1)


def cmd_verify():
    """Check each job's script exists and is runnable."""
    ok = 0
    fail = 0
    for _, script, desc in JOBS:
        path = Path(script)
        exists = path.exists()
        executable = os.access(script, os.X_OK) or exists  # Python scripts don't need +x
        if exists:
            print(f"  \033[32mOK\033[0m  {desc} -> {script}")
            ok += 1
        else:
            print(f"  \033[31mMISS\033[0m {desc} -> {script}")
            fail += 1
    print(f"\n{ok} OK, {fail} missing")
    if fail:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="BIOS Master Cron Installer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true", help="Install all missing cron jobs")
    group.add_argument("--list", action="store_true", help="Show all jobs with status")
    group.add_argument("--remove", action="store_true", help="Remove all BIOS cron jobs")
    group.add_argument("--verify", action="store_true", help="Verify scripts exist")
    args = parser.parse_args()

    if args.install:
        cmd_install()
    elif args.list:
        cmd_list()
    elif args.remove:
        cmd_remove()
    elif args.verify:
        cmd_verify()


if __name__ == "__main__":
    main()
