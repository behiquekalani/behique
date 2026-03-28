#!/usr/bin/env python3
"""
BIOS System Health Monitor
Checks all BIOS components and reports status.

Usage:
    python3 bios/health_check.py            # terminal output
    python3 bios/health_check.py --json     # JSON output
    python3 bios/health_check.py --alert    # Telegram alert on RED only

Cron (every 4 hours, alert on failures):
    0 */4 * * * cd /Users/kalani/behique && /usr/bin/python3 bios/health_check.py --alert >> bios/logs/health.log 2>&1
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BIOS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BIOS_ROOT.parent
STORAGE_DIR = BIOS_ROOT / "storage"
LOGS_DIR = BIOS_ROOT / "logs"

# Data freshness thresholds (file -> max age in hours)
DATA_FILES = {
    "signals.json": 6,
    "social_signals.json": 1,
    "convictions.json": 2,
    "pr_signals.json": 3,
}

# Expected cron job identifiers (substrings to match in crontab)
EXPECTED_CRONS = [
    ("Intelligence Pipeline", "bios/run_all.py"),
    ("Daily Report", "bios/scheduler/daily_report.py"),
    ("Social Scraper", "bios/ingestion/social_scraper.py"),
    ("Conviction Engine", "bios/intelligence/conviction_engine.py"),
    ("Fleet Sync", "bios/fleet/sync_results.py"),
    ("Content Publisher", "publish_daemon.py"),
    ("Sales Digest", "bios/sales/daily_digest.py"),
    ("News Scraper", "bios/ingestion/news_scraper.py"),
    ("PR Scraper", "bios/ingestion/pr_scraper.py"),
]

# Fleet nodes (name -> (ip, port))
FLEET_NODES = {
    "Cobo": ("192.168.0.151", 9876),
    "Naboria": ("192.168.0.152", 9876),
}

# Web servers (name -> port)
WEB_SERVERS = {
    "Faces": 8091,
    "Dashboard": 8093,
    "CallBuddy": 8094,
}

# Disk space threshold (GB)
DISK_WARN_GB = 20
DISK_CRIT_GB = 5

# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

GREEN = "GREEN"
YELLOW = "YELLOW"
RED = "RED"

COLORS = {
    GREEN: "\033[92m",
    YELLOW: "\033[93m",
    RED: "\033[91m",
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


def _color(status: str, text: str) -> str:
    return f"{COLORS.get(status, '')}{text}{RESET}"


def _icon(status: str) -> str:
    icons = {GREEN: "[OK]", YELLOW: "[!!]", RED: "[XX]"}
    return _color(status, icons.get(status, "[??]"))


# ---------------------------------------------------------------------------
# Check: Cron Jobs
# ---------------------------------------------------------------------------

def check_crons() -> dict:
    """Parse crontab and verify expected jobs exist."""
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, timeout=5
        )
        crontab = result.stdout if result.returncode == 0 else ""
    except Exception:
        crontab = ""

    found = []
    missing = []
    for name, pattern in EXPECTED_CRONS:
        if pattern in crontab:
            found.append(name)
        else:
            missing.append(name)

    if not missing:
        status = GREEN
        msg = f"All {len(found)} cron jobs registered"
    elif len(missing) <= 2:
        status = YELLOW
        msg = f"Missing {len(missing)}: {', '.join(missing)}"
    else:
        status = RED
        msg = f"Missing {len(missing)}/{len(EXPECTED_CRONS)}: {', '.join(missing)}"

    return {"name": "Cron Jobs", "status": status, "message": msg,
            "details": {"found": found, "missing": missing}}


# ---------------------------------------------------------------------------
# Check: Data Freshness
# ---------------------------------------------------------------------------

def check_data_freshness() -> dict:
    """Check last modified time of critical data files."""
    now = time.time()
    results = {}
    worst = GREEN

    for filename, max_hours in DATA_FILES.items():
        filepath = STORAGE_DIR / filename
        if not filepath.exists():
            results[filename] = {"status": RED, "age": None, "message": "File missing"}
            worst = RED
            continue

        mtime = filepath.stat().st_mtime
        age_hours = (now - mtime) / 3600

        if age_hours <= max_hours:
            s = GREEN
            msg = f"{age_hours:.1f}h old (limit: {max_hours}h)"
        elif age_hours <= max_hours * 2:
            s = YELLOW
            msg = f"{age_hours:.1f}h old (limit: {max_hours}h) — stale"
        else:
            s = RED
            msg = f"{age_hours:.1f}h old (limit: {max_hours}h) — critical"

        results[filename] = {"status": s, "age_hours": round(age_hours, 1), "message": msg}

        if s == RED:
            worst = RED
        elif s == YELLOW and worst != RED:
            worst = YELLOW

    stale = [f for f, r in results.items() if r["status"] != GREEN]
    if not stale:
        summary = f"All {len(DATA_FILES)} files fresh"
    else:
        summary = f"{len(stale)} stale: {', '.join(stale)}"

    return {"name": "Data Freshness", "status": worst, "message": summary,
            "details": results}


# ---------------------------------------------------------------------------
# Check: Fleet Status
# ---------------------------------------------------------------------------

def check_fleet() -> dict:
    """Ping fleet nodes via TCP connection."""
    results = {}
    worst = GREEN

    for name, (ip, port) in FLEET_NODES.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip, port))
            sock.close()
            results[name] = {"status": GREEN, "message": f"{ip}:{port} reachable"}
        except (socket.timeout, ConnectionRefusedError, OSError):
            results[name] = {"status": RED, "message": f"{ip}:{port} unreachable"}
            worst = RED

    online = sum(1 for r in results.values() if r["status"] == GREEN)
    summary = f"{online}/{len(FLEET_NODES)} nodes online"
    if online == 0:
        worst = RED
    elif online < len(FLEET_NODES) and worst != RED:
        worst = YELLOW

    return {"name": "Fleet Status", "status": worst, "message": summary,
            "details": results}


# ---------------------------------------------------------------------------
# Check: Disk Space
# ---------------------------------------------------------------------------

def check_disk() -> dict:
    """Check available disk space on /."""
    try:
        usage = shutil.disk_usage("/")
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        used_pct = (usage.used / usage.total) * 100

        if free_gb >= DISK_WARN_GB:
            status = GREEN
        elif free_gb >= DISK_CRIT_GB:
            status = YELLOW
        else:
            status = RED

        msg = f"{free_gb:.1f} GB free / {total_gb:.0f} GB total ({used_pct:.0f}% used)"
        return {"name": "Disk Space", "status": status, "message": msg,
                "details": {"free_gb": round(free_gb, 1), "total_gb": round(total_gb, 0),
                            "used_pct": round(used_pct, 1)}}
    except Exception as e:
        return {"name": "Disk Space", "status": RED, "message": f"Check failed: {e}",
                "details": {}}


# ---------------------------------------------------------------------------
# Check: Web Servers
# ---------------------------------------------------------------------------

def check_web_servers() -> dict:
    """Check if local web server ports are responding."""
    results = {}
    worst = GREEN

    for name, port in WEB_SERVERS.items():
        try:
            url = f"http://127.0.0.1:{port}/"
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=3)
            results[name] = {"status": GREEN, "message": f"Port {port} responding"}
        except urllib.error.HTTPError:
            # Server is up but returned an error code — still alive
            results[name] = {"status": GREEN, "message": f"Port {port} responding"}
        except (urllib.error.URLError, OSError, socket.timeout):
            results[name] = {"status": RED, "message": f"Port {port} not responding"}
            worst = RED

    online = sum(1 for r in results.values() if r["status"] == GREEN)
    summary = f"{online}/{len(WEB_SERVERS)} servers responding"

    return {"name": "Web Servers", "status": worst, "message": summary,
            "details": results}


# ---------------------------------------------------------------------------
# Check: Log Errors
# ---------------------------------------------------------------------------

def check_log_errors() -> dict:
    """Scan last 20 lines of each log file for errors."""
    results = {}
    worst = GREEN
    total_errors = 0

    if not LOGS_DIR.exists():
        return {"name": "Log Errors", "status": YELLOW, "message": "Logs directory missing",
                "details": {}}

    for logfile in sorted(LOGS_DIR.glob("*.log")):
        try:
            # Read last 20 lines efficiently
            with open(logfile, "rb") as f:
                # Seek to end, read last ~8KB
                f.seek(0, 2)
                size = f.tell()
                read_size = min(size, 8192)
                f.seek(max(0, size - read_size))
                tail = f.read().decode("utf-8", errors="replace")

            lines = tail.splitlines()[-20:]
            errors = []
            for i, line in enumerate(lines):
                lower = line.lower()
                if "error" in lower or "traceback" in lower:
                    errors.append(line.strip()[:120])

            if errors:
                results[logfile.name] = {
                    "status": YELLOW,
                    "error_count": len(errors),
                    "samples": errors[:3],
                }
                total_errors += len(errors)
                if worst == GREEN:
                    worst = YELLOW
            else:
                results[logfile.name] = {"status": GREEN, "error_count": 0}
        except Exception as e:
            results[logfile.name] = {"status": YELLOW, "error_count": 0,
                                     "message": f"Read failed: {e}"}

    if total_errors == 0:
        summary = f"No errors in {len(results)} log files"
    else:
        error_files = [f for f, r in results.items() if r.get("error_count", 0) > 0]
        summary = f"{total_errors} errors in {len(error_files)} file(s): {', '.join(error_files)}"
        if total_errors >= 10:
            worst = RED

    return {"name": "Log Errors", "status": worst, "message": summary,
            "details": results}


# ---------------------------------------------------------------------------
# Check: Git Status
# ---------------------------------------------------------------------------

def check_git() -> dict:
    """Count uncommitted files in the repo."""
    try:
        result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10
        )
        lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
        count = len(lines)

        if count == 0:
            status = GREEN
            msg = "Working tree clean"
        elif count <= 10:
            status = GREEN
            msg = f"{count} uncommitted files"
        elif count <= 30:
            status = YELLOW
            msg = f"{count} uncommitted files — consider committing"
        else:
            status = YELLOW
            msg = f"{count} uncommitted files — repo getting cluttered"

        return {"name": "Git Status", "status": status, "message": msg,
                "details": {"uncommitted_count": count}}
    except Exception as e:
        return {"name": "Git Status", "status": YELLOW, "message": f"Check failed: {e}",
                "details": {}}


# ---------------------------------------------------------------------------
# Run all checks
# ---------------------------------------------------------------------------

def run_all_checks() -> list:
    """Run every check and return list of results."""
    checks = [
        check_crons,
        check_data_freshness,
        check_fleet,
        check_disk,
        check_web_servers,
        check_log_errors,
        check_git,
    ]
    return [fn() for fn in checks]


# ---------------------------------------------------------------------------
# Output: Terminal
# ---------------------------------------------------------------------------

def print_terminal(results: list):
    """Print colored terminal report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{BOLD}BIOS Health Check — {now}{RESET}")
    print("=" * 55)

    for r in results:
        icon = _icon(r["status"])
        name = r["name"].ljust(18)
        print(f"  {icon} {name} {r['message']}")

        # Show sub-details for certain checks
        details = r.get("details", {})
        if r["name"] == "Data Freshness" and r["status"] != GREEN:
            for fname, info in details.items():
                if isinstance(info, dict) and info.get("status") != GREEN:
                    sub_icon = _icon(info["status"])
                    print(f"       {sub_icon} {fname}: {info['message']}")
        elif r["name"] == "Fleet Status":
            for node, info in details.items():
                sub_icon = _icon(info["status"])
                print(f"       {sub_icon} {node}: {info['message']}")
        elif r["name"] == "Web Servers":
            for srv, info in details.items():
                sub_icon = _icon(info["status"])
                print(f"       {sub_icon} {srv}: {info['message']}")
        elif r["name"] == "Log Errors" and r["status"] != GREEN:
            for fname, info in details.items():
                if isinstance(info, dict) and info.get("error_count", 0) > 0:
                    samples = info.get("samples", [])
                    print(f"       {DIM}{fname}: {info['error_count']} errors{RESET}")
                    for s in samples[:2]:
                        print(f"         {DIM}{s[:100]}{RESET}")

    # Summary
    operational = sum(1 for r in results if r["status"] != RED)
    total = len(results)
    has_red = any(r["status"] == RED for r in results)
    has_yellow = any(r["status"] == YELLOW for r in results)

    if has_red:
        color = RED
    elif has_yellow:
        color = YELLOW
    else:
        color = GREEN

    print("=" * 55)
    summary = f"BIOS Health: {operational}/{total} systems operational"
    print(f"  {_color(color, summary)}")
    print()


# ---------------------------------------------------------------------------
# Output: JSON
# ---------------------------------------------------------------------------

def output_json(results: list):
    """Print JSON report to stdout."""
    now = datetime.now().isoformat()
    operational = sum(1 for r in results if r["status"] != RED)
    total = len(results)
    has_red = any(r["status"] == RED for r in results)

    report = {
        "timestamp": now,
        "overall": RED if has_red else (YELLOW if any(r["status"] == YELLOW for r in results) else GREEN),
        "summary": f"{operational}/{total} systems operational",
        "checks": results,
    }
    print(json.dumps(report, indent=2))


# ---------------------------------------------------------------------------
# Output: Telegram Alert
# ---------------------------------------------------------------------------

def send_alert(results: list):
    """Send Telegram alert if any check is RED."""
    has_red = any(r["status"] == RED for r in results)
    if not has_red:
        return  # Only alert on failures

    # Import the notification system
    sys.path.insert(0, str(BIOS_ROOT / "notifications"))
    try:
        from telegram_bot import notify_system
    except ImportError:
        print("[health_check] Could not import telegram_bot", file=sys.stderr)
        return

    operational = sum(1 for r in results if r["status"] != RED)
    total = len(results)

    red_checks = [r for r in results if r["status"] == RED]
    lines = [f"BIOS Health: {operational}/{total} operational"]
    lines.append("")
    for r in red_checks:
        lines.append(f"  RED: {r['name']} — {r['message']}")

    yellow_checks = [r for r in results if r["status"] == YELLOW]
    if yellow_checks:
        lines.append("")
        for r in yellow_checks:
            lines.append(f"  WARN: {r['name']} — {r['message']}")

    notify_system("\n".join(lines), severity="ERROR")
    print(f"[health_check] Telegram alert sent ({len(red_checks)} RED)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = set(sys.argv[1:])
    results = run_all_checks()

    if "--json" in args:
        output_json(results)
    elif "--alert" in args:
        send_alert(results)
        # Also log a one-liner for cron.log
        operational = sum(1 for r in results if r["status"] != RED)
        total = len(results)
        has_red = any(r["status"] == RED for r in results)
        status_word = "FAIL" if has_red else "OK"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"[{now}] health_check: {status_word} — {operational}/{total} operational")
    else:
        print_terminal(results)


if __name__ == "__main__":
    main()
