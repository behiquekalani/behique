#!/usr/bin/env python3
"""
BIOS Launcher - The ONE command to start everything on Ceiba.

Usage:
    python3 bios/launch.py start          Start all services
    python3 bios/launch.py stop           Stop all services
    python3 bios/launch.py status         Show service status
    python3 bios/launch.py restart        Stop then start
    python3 bios/launch.py run-pipeline   Run full data pipeline once
    python3 bios/launch.py cron-check     Verify cron jobs exist
    python3 bios/launch.py home           Bind to 0.0.0.0 (home network)
    python3 bios/launch.py away           Bind to 127.0.0.1 (out of house)

Zero dependencies. Stdlib only.
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
BIOS_DIR = BASE_DIR / "bios"
PID_FILE = BIOS_DIR / ".pids"
BIND_FILE = BIOS_DIR / ".bind_mode"
STORAGE_DIR = BIOS_DIR / "storage"
LOG_DIR = BIOS_DIR / "logs"

# ---------------------------------------------------------------------------
# Colors (ANSI)
# ---------------------------------------------------------------------------
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ---------------------------------------------------------------------------
# Service definitions
# ---------------------------------------------------------------------------
def get_bind_address():
    """Read bind mode from .bind_mode file. Default: 0.0.0.0 (home)."""
    try:
        return BIND_FILE.read_text().strip()
    except FileNotFoundError:
        return "0.0.0.0"


def get_services():
    """Return service definitions with current bind address."""
    bind = get_bind_address()
    # Webhook always binds to localhost for security
    return [
        {
            "name": "Faces",
            "port": 8091,
            "bind": bind,
            "directory": str(BASE_DIR / "Ceiba" / "faces"),
            "type": "http",
        },
        {
            "name": "BIOS Dashboard",
            "port": 8093,
            "bind": bind,
            "directory": str(BIOS_DIR / "dashboard"),
            "type": "http",
        },
        {
            "name": "VR War Room",
            "port": 8092,
            "bind": bind,
            "directory": str(BIOS_DIR / "dashboard"),
            "type": "http",
        },
        {
            "name": "Storefront",
            "port": 8080,
            "bind": bind,
            "directory": str(BASE_DIR / "storefront"),
            "type": "http",
        },
        {
            "name": "Webhook Server",
            "port": 8097,
            "bind": "127.0.0.1",
            "script": str(BIOS_DIR / "sales" / "webhook_server.py"),
            "type": "script",
        },
    ]


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------
PIPELINE_STEPS = [
    ("News scraper", "python3 bios/ingestion/news_scraper.py"),
    ("Social scraper", "python3 bios/ingestion/social_scraper.py"),
    ("PR scraper", "python3 bios/ingestion/pr_scraper.py"),
    ("Conviction engine", "python3 bios/intelligence/conviction_engine.py"),
    ("Content wiring", "python3 bios/intelligence/content_wiring.py"),
    ("Daily briefing", "python3 bios/run_all.py --pipeline"),
]

# ---------------------------------------------------------------------------
# Expected cron jobs
# ---------------------------------------------------------------------------
EXPECTED_CRONS = [
    "news_fetcher.py",
    "news_scraper.py",
    "social_scraper.py",
    "pr_scraper.py",
    "polymarket_fetcher.py",
    "reddit_signal.py",
    "conviction_engine.py",
    "content_wiring.py",
    "run_all.py",
]

# ---------------------------------------------------------------------------
# PID management
# ---------------------------------------------------------------------------
def save_pids(pid_map):
    """Save {name: {pid, port, bind, started}} to .pids file."""
    serializable = {}
    for name, info in pid_map.items():
        serializable[name] = {
            "pid": info["pid"],
            "port": info["port"],
            "bind": info["bind"],
            "started": info["started"],
        }
    PID_FILE.write_text(json.dumps(serializable, indent=2))


def load_pids():
    """Load pid map from .pids file."""
    try:
        return json.loads(PID_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def is_process_alive(pid):
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_process_uptime(started_str):
    """Return human-readable uptime from ISO timestamp."""
    try:
        started = datetime.fromisoformat(started_str)
        delta = datetime.now() - started
        total_seconds = int(delta.total_seconds())
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}m {total_seconds % 60}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    except Exception:
        return "?"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_start():
    """Start all services."""
    print(f"\n  {BOLD}BIOS{RESET} - Starting all services")
    print(f"  {'=' * 45}")

    bind = get_bind_address()
    mode = "HOME (0.0.0.0)" if bind == "0.0.0.0" else "AWAY (127.0.0.1)"
    print(f"  Network mode: {CYAN}{mode}{RESET}\n")

    # Kill any existing services first
    existing = load_pids()
    if existing:
        _stop_services(existing, quiet=True)

    services = get_services()
    pid_map = {}

    for svc in services:
        name = svc["name"]
        port = svc["port"]
        bind_addr = svc["bind"]

        # Check if port is already in use
        if _port_in_use(port):
            print(f"  {YELLOW}[SKIP]{RESET} {name} - port {port} already in use")
            continue

        if svc["type"] == "http":
            # Launch python3 -m http.server
            cmd = [
                sys.executable, "-m", "http.server",
                str(port),
                "--bind", bind_addr,
                "--directory", svc["directory"],
            ]
        elif svc["type"] == "script":
            cmd = [sys.executable, svc["script"]]
        else:
            continue

        try:
            # Ensure log directory exists
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_file = LOG_DIR / f"{name.lower().replace(' ', '_')}.log"

            with open(log_file, "a") as lf:
                proc = subprocess.Popen(
                    cmd,
                    stdout=lf,
                    stderr=lf,
                    cwd=str(BASE_DIR),
                    start_new_session=True,
                )

            pid_map[name] = {
                "pid": proc.pid,
                "port": port,
                "bind": bind_addr,
                "started": datetime.now().isoformat(),
            }

            url = f"http://{bind_addr}:{port}"
            print(f"  {GREEN}[  OK  ]{RESET} {name:<20} {DIM}PID {proc.pid:<8} {url}{RESET}")

        except Exception as e:
            print(f"  {RED}[ FAIL ]{RESET} {name:<20} {e}")

    if pid_map:
        save_pids(pid_map)
        print(f"\n  {GREEN}{len(pid_map)} services started.{RESET} PIDs saved to bios/.pids")
    else:
        print(f"\n  {RED}No services started.{RESET}")

    print()


def cmd_stop():
    """Stop all services."""
    print(f"\n  {BOLD}BIOS{RESET} - Stopping all services")
    print(f"  {'=' * 45}\n")

    pids = load_pids()
    if not pids:
        print(f"  {DIM}No services tracked in .pids{RESET}\n")
        return

    _stop_services(pids)

    # Clean up PID file
    if PID_FILE.exists():
        PID_FILE.unlink()

    print()


def _stop_services(pids, quiet=False):
    """Stop services from a pid map."""
    for name, info in pids.items():
        pid = info["pid"]
        if is_process_alive(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                # Give it a moment to die
                for _ in range(10):
                    if not is_process_alive(pid):
                        break
                    time.sleep(0.1)
                # Force kill if still alive
                if is_process_alive(pid):
                    os.kill(pid, signal.SIGKILL)

                if not quiet:
                    print(f"  {GREEN}[STOPPED]{RESET} {name:<20} PID {pid}")
            except Exception as e:
                if not quiet:
                    print(f"  {RED}[ ERROR]{RESET} {name:<20} {e}")
        else:
            if not quiet:
                print(f"  {DIM}[  DEAD ]{RESET} {name:<20} PID {pid} (already stopped)")


def cmd_status():
    """Show status of all services."""
    print(f"\n  {BOLD}BIOS{RESET} - Service Status")
    print(f"  {'=' * 60}")

    bind = get_bind_address()
    mode = "HOME (0.0.0.0)" if bind == "0.0.0.0" else "AWAY (127.0.0.1)"
    print(f"  Network mode: {CYAN}{mode}{RESET}\n")

    pids = load_pids()
    services = get_services()

    # Header
    print(f"  {'Service':<20} {'Status':<12} {'Port':<8} {'PID':<10} {'Uptime':<10}")
    print(f"  {'-' * 60}")

    running_count = 0
    total_count = len(services)

    for svc in services:
        name = svc["name"]
        port = svc["port"]
        info = pids.get(name, {})
        pid = info.get("pid", 0)

        if pid and is_process_alive(pid):
            uptime = get_process_uptime(info.get("started", ""))
            status = f"{GREEN}RUNNING{RESET}"
            running_count += 1
            print(f"  {name:<20} {status}     {port:<8} {pid:<10} {uptime}")
        elif _port_in_use(port):
            status = f"{YELLOW}EXTERNAL{RESET}"
            running_count += 1
            print(f"  {name:<20} {status}    {port:<8} {'?':<10} {'?'}")
        else:
            status = f"{RED}STOPPED{RESET}"
            print(f"  {name:<20} {status}     {port:<8} {'-':<10} {'-'}")

    print(f"\n  {running_count}/{total_count} services running")
    print()


def cmd_restart():
    """Stop then start all services."""
    cmd_stop()
    time.sleep(0.5)
    cmd_start()


def cmd_run_pipeline():
    """Run the full data pipeline manually."""
    print(f"\n  {BOLD}BIOS{RESET} - Running Full Pipeline")
    print(f"  {'=' * 45}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}
    total_start = time.time()

    for name, command in PIPELINE_STEPS:
        print(f"  [{name}]", end=" ", flush=True)
        step_start = time.time()
        try:
            result = subprocess.run(
                command.split(),
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=180,
            )
            duration = time.time() - step_start
            if result.returncode == 0:
                print(f"{GREEN}OK{RESET} ({duration:.1f}s)")
                results[name] = True
            else:
                print(f"{RED}FAIL{RESET} ({duration:.1f}s)")
                if result.stderr:
                    # Show first line of error
                    first_err = result.stderr.strip().split("\n")[0][:80]
                    print(f"    {DIM}{first_err}{RESET}")
                results[name] = False
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}TIMEOUT{RESET}")
            results[name] = False
        except FileNotFoundError:
            print(f"{RED}NOT FOUND{RESET}")
            results[name] = False
        except Exception as e:
            print(f"{RED}ERROR{RESET}: {e}")
            results[name] = False

    total_duration = time.time() - total_start
    ok = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  {'=' * 45}")
    color = GREEN if ok == total else (YELLOW if ok > 0 else RED)
    print(f"  Result: {color}{ok}/{total} steps passed{RESET} in {total_duration:.1f}s")

    # Signal count
    try:
        with open(STORAGE_DIR / "signals.json") as f:
            signals = json.load(f)
        print(f"  Signals: {len(signals)}")
    except Exception:
        pass

    # Insight count
    try:
        with open(STORAGE_DIR / "insights.json") as f:
            insights = json.load(f)
        actionable = sum(1 for i in insights if i.get("action_level") == "ACTIONABLE")
        print(f"  Insights: {len(insights)} ({actionable} actionable)")
    except Exception:
        pass

    print()


def cmd_cron_check():
    """Verify all expected cron jobs exist."""
    print(f"\n  {BOLD}BIOS{RESET} - Cron Job Audit")
    print(f"  {'=' * 45}\n")

    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  {RED}No crontab found for current user.{RESET}")
            print(f"  Expected {len(EXPECTED_CRONS)} jobs.\n")
            return

        crontab = result.stdout
    except FileNotFoundError:
        print(f"  {RED}crontab command not found.{RESET}\n")
        return

    found = 0
    missing = 0

    for job in EXPECTED_CRONS:
        if job in crontab:
            print(f"  {GREEN}[FOUND  ]{RESET} {job}")
            found += 1
        else:
            print(f"  {RED}[MISSING]{RESET} {job}")
            missing += 1

    print(f"\n  {found}/{len(EXPECTED_CRONS)} cron jobs present", end="")
    if missing:
        print(f" - {RED}{missing} missing{RESET}")
    else:
        print(f" - {GREEN}all good{RESET}")
    print()


def cmd_home():
    """Set bind address to 0.0.0.0 for home network access."""
    BIND_FILE.write_text("0.0.0.0")
    print(f"\n  {GREEN}Network mode: HOME{RESET}")
    print(f"  Servers will bind to 0.0.0.0 (accessible from LAN)")
    print(f"  Run {CYAN}python3 bios/launch.py restart{RESET} to apply.\n")


def cmd_away():
    """Set bind address to 127.0.0.1 for localhost only."""
    BIND_FILE.write_text("127.0.0.1")
    print(f"\n  {YELLOW}Network mode: AWAY{RESET}")
    print(f"  Servers will bind to 127.0.0.1 (localhost only)")
    print(f"  Run {CYAN}python3 bios/launch.py restart{RESET} to apply.\n")


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def _port_in_use(port):
    """Check if a port is in use (stdlib only)."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


def print_usage():
    """Print usage info."""
    print(f"""
  {BOLD}BIOS Launcher{RESET} - Behike Intelligence Operating System
  {'=' * 50}

  {CYAN}python3 bios/launch.py <command>{RESET}

  Commands:
    {GREEN}start{RESET}          Start all services
    {RED}stop{RESET}           Stop all services
    {CYAN}status{RESET}         Show which services are running
    {YELLOW}restart{RESET}        Stop then start all services
    {CYAN}run-pipeline{RESET}   Run full data pipeline manually
    {CYAN}cron-check{RESET}     Verify cron jobs are installed
    {GREEN}home{RESET}           Bind to 0.0.0.0 (home network)
    {YELLOW}away{RESET}           Bind to 127.0.0.1 (localhost only)
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
COMMANDS = {
    "start": cmd_start,
    "stop": cmd_stop,
    "status": cmd_status,
    "restart": cmd_restart,
    "run-pipeline": cmd_run_pipeline,
    "cron-check": cmd_cron_check,
    "home": cmd_home,
    "away": cmd_away,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print_usage()
        sys.exit(1 if len(sys.argv) >= 2 else 0)

    command = sys.argv[1]
    COMMANDS[command]()


if __name__ == "__main__":
    main()
