#!/usr/bin/env python3
"""
Fleet Status - Check all machines and running jobs.

Usage:
    python3 bios/control/fleet_status.py
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = BASE_DIR / "bios" / "config.json"
JOBS_FILE = BASE_DIR / "bios" / "scheduler" / "jobs.json"


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def ping(ip, timeout=2):
    try:
        r = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            capture_output=True, timeout=timeout + 2
        )
        return r.returncode == 0
    except Exception:
        return False


def main():
    config = load_json(CONFIG_FILE)
    jobs = load_json(JOBS_FILE)

    print("\n  BIOS FLEET STATUS")
    print("  " + "=" * 55)

    fleet = config.get("fleet", {})
    for name, info in fleet.items():
        ip = info.get("ip", "?")
        enabled = info.get("enabled", False)
        role = info.get("role", "?")

        if not enabled:
            status = "DISABLED"
        elif ping(ip):
            status = "ONLINE"
        else:
            status = "OFFLINE"

        mode_str = ""
        if name == "cobo":
            mode = info.get("mode", "normal")
            mode_str = f" [{mode.upper()}]"

        print(f"  {name:10s} {ip:16s} {role:10s} {status}{mode_str}")

    # Job summary
    import time
    now = time.time()
    print(f"\n  RECENT JOBS:")
    if not jobs:
        print("  No jobs have run yet.")
    else:
        for name, state in sorted(jobs.items()):
            last = state.get("last_run", 0)
            status = state.get("last_status", "?")
            ago = int((now - last) / 60) if last else 0
            print(f"    {name:25s} {status:8s} {ago}m ago")

    # Disk space
    import shutil
    usage = shutil.disk_usage(str(BASE_DIR))
    free_gb = usage.free / (1024**3)
    total_gb = usage.total / (1024**3)
    pct = (usage.used / usage.total) * 100
    print(f"\n  DISK: {free_gb:.1f}GB free / {total_gb:.0f}GB total ({pct:.0f}% used)")
    print()


if __name__ == "__main__":
    main()
