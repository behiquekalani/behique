#!/usr/bin/env python3
"""
BIOS Scheduler - Runs jobs on a configurable interval.
Phase 1: Simple cron-style scheduler with fleet awareness.

Usage:
    python3 bios/scheduler/scheduler.py                # Run all due jobs
    python3 bios/scheduler/scheduler.py --status       # Show job status
    python3 bios/scheduler/scheduler.py --run JOB_NAME # Run specific job
    python3 bios/scheduler/scheduler.py --daemon       # Run continuously
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BIOS_DIR = BASE_DIR / "bios"
CONFIG_FILE = BIOS_DIR / "config.json"
JOBS_FILE = BIOS_DIR / "scheduler" / "jobs.json"
LOG_DIR = BIOS_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_jobs():
    if not JOBS_FILE.exists():
        return {}
    with open(JOBS_FILE) as f:
        return json.load(f)


def save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def notify_telegram(message, config):
    """Send a Telegram notification."""
    token = os.environ.get(config["telegram"]["bot_token_env"], "")
    chat_id = os.environ.get(config["telegram"]["chat_id_env"], "")
    if not token or not chat_id:
        return False
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
        return True
    except Exception:
        return False


def check_machine(ip, timeout=3):
    """Check if a machine is reachable."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            capture_output=True, timeout=timeout + 2
        )
        return result.returncode == 0
    except Exception:
        return False


def check_gaming_mode(config):
    """Check if Cobo is in gaming mode."""
    cobo = config["fleet"].get("cobo", {})
    return cobo.get("mode", "normal") == "gaming"


def log_job(job_name, status, output="", duration=0):
    """Log job execution."""
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {job_name}: {status} ({duration:.1f}s)"
    if output:
        entry += f" | {output[:200]}"
    with open(log_file, "a") as f:
        f.write(entry + "\n")


# Job registry - maps job names to commands
JOB_REGISTRY = {
    "polymarket_monitor": {
        "command": "python3 tools/polymarket_telegram_bot.py",
        "interval_minutes": 15,
        "machine": "cobo",
        "description": "Monitor Polymarket for price movements"
    },
    "trends_scraper": {
        "command": "python3 tools/trends_scraper_v2.py --digest",
        "interval_minutes": 360,
        "machine": "cobo",
        "description": "Scrape Google Trends"
    },
    "reddit_scraper": {
        "command": "python3 tools/reddit_niche_crawler.py",
        "interval_minutes": 60,
        "machine": "cobo",
        "description": "Crawl Reddit for signals"
    },
    "news_ingestion": {
        "command": "python3 bios/ingestion/news_fetcher.py",
        "interval_minutes": 30,
        "machine": "naboria",
        "description": "Fetch and process news"
    },
    "daily_report": {
        "command": "python3 bios/scheduler/daily_report.py",
        "interval_minutes": 1440,
        "machine": "ceiba",
        "description": "Generate daily intelligence report"
    }
}


def get_due_jobs(jobs_state):
    """Return list of jobs that are due to run."""
    now = time.time()
    due = []
    for name, meta in JOB_REGISTRY.items():
        last_run = jobs_state.get(name, {}).get("last_run", 0)
        interval = meta["interval_minutes"] * 60
        if now - last_run >= interval:
            due.append(name)
    return due


def run_job(name, config, jobs_state, force=False):
    """Execute a single job."""
    if name not in JOB_REGISTRY:
        print(f"Unknown job: {name}")
        return False

    meta = JOB_REGISTRY[name]
    machine = meta["machine"]
    fleet = config["fleet"]

    # Check machine availability
    if machine == "cobo":
        if check_gaming_mode(config):
            log_job(name, "SKIPPED", "Cobo in gaming mode")
            print(f"  [{name}] Skipped: Cobo in gaming mode")
            return False
        if not fleet.get("cobo", {}).get("enabled", False):
            log_job(name, "SKIPPED", "Cobo disabled")
            return False

    if machine == "naboria" and not fleet.get("naboria", {}).get("enabled", False):
        log_job(name, "SKIPPED", "Naboria offline")
        return False

    # Run the job
    print(f"  [{name}] Running on {machine}...")
    start = time.time()
    try:
        result = subprocess.run(
            meta["command"].split(),
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        duration = time.time() - start
        status = "OK" if result.returncode == 0 else f"FAIL({result.returncode})"
        output = result.stdout[:200] if result.stdout else result.stderr[:200]
        log_job(name, status, output, duration)
        print(f"  [{name}] {status} in {duration:.1f}s")

        # Update state
        jobs_state[name] = {
            "last_run": time.time(),
            "last_status": status,
            "last_duration": round(duration, 1)
        }
        return result.returncode == 0

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        log_job(name, "TIMEOUT", "", duration)
        print(f"  [{name}] TIMEOUT after {duration:.1f}s")
        return False
    except Exception as e:
        log_job(name, "ERROR", str(e))
        print(f"  [{name}] ERROR: {e}")
        return False


def show_status(config, jobs_state):
    """Display current system status."""
    print("\n  BIOS SCHEDULER STATUS")
    print("  " + "=" * 50)

    # Fleet status
    print("\n  FLEET:")
    for name, machine in config["fleet"].items():
        online = check_machine(machine["ip"]) if machine.get("enabled") else False
        mode = f" [{machine.get('mode', 'normal')}]" if name == "cobo" else ""
        status = "ONLINE" if online else ("DISABLED" if not machine.get("enabled") else "OFFLINE")
        print(f"    {name:10s} {machine['ip']:16s} {status}{mode}")

    # Jobs
    print("\n  JOBS:")
    now = time.time()
    for name, meta in JOB_REGISTRY.items():
        state = jobs_state.get(name, {})
        last_run = state.get("last_run", 0)
        last_status = state.get("last_status", "NEVER")
        if last_run:
            ago = int((now - last_run) / 60)
            next_in = max(0, meta["interval_minutes"] - ago)
            timing = f"ran {ago}m ago, next in {next_in}m"
        else:
            timing = "never run"
        print(f"    {name:25s} {meta['machine']:10s} {last_status:8s} {timing}")

    print()


def daemon_loop(config):
    """Run continuously, checking for due jobs."""
    print("BIOS Scheduler daemon starting...")
    notify_telegram("BIOS Scheduler started.", config)

    while True:
        jobs_state = load_jobs()
        config = load_config()  # Reload config each cycle (for gaming mode changes)
        due = get_due_jobs(jobs_state)

        if due:
            print(f"\n[{datetime.now().strftime('%H:%M')}] {len(due)} jobs due:")
            for name in due:
                run_job(name, config, jobs_state)
            save_jobs(jobs_state)

        time.sleep(60)  # Check every minute


def main():
    config = load_config()
    jobs_state = load_jobs()

    if "--status" in sys.argv:
        show_status(config, jobs_state)
    elif "--daemon" in sys.argv:
        daemon_loop(config)
    elif "--run" in sys.argv:
        idx = sys.argv.index("--run")
        if idx + 1 < len(sys.argv):
            name = sys.argv[idx + 1]
            run_job(name, config, jobs_state, force=True)
            save_jobs(jobs_state)
        else:
            print("Usage: --run JOB_NAME")
    else:
        # Run all due jobs
        due = get_due_jobs(jobs_state)
        if not due:
            print("No jobs due. Use --status to see schedule.")
            return
        print(f"Running {len(due)} due jobs:")
        for name in due:
            run_job(name, config, jobs_state)
        save_jobs(jobs_state)


if __name__ == "__main__":
    main()
