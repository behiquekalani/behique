#!/usr/bin/env python3
"""
BIOS Fleet Coordinator
Reads fleet.json, checks machine health, assigns tasks.
Run from Ceiba (command node).

Usage:
    python3 coordinator.py --status     Show fleet health
    python3 coordinator.py --assign     Show task assignments per machine
    python3 coordinator.py --ping       Quick ping all machines
"""

import json
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

FLEET_CONFIG = Path(__file__).parent / "fleet.json"
TIMEOUT_SECONDS = 5


def load_fleet():
    with open(FLEET_CONFIG, "r") as f:
        return json.load(f)


def ping_machine(ip, port, timeout=TIMEOUT_SECONDS):
    """Check if a machine's bridge port is reachable via HTTP."""
    url = f"http://{ip}:{port}/"
    try:
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=timeout)
        return {"online": True, "status_code": resp.status, "latency_ms": None}
    except urllib.error.URLError:
        return {"online": False, "status_code": None, "latency_ms": None}
    except Exception as e:
        return {"online": False, "error": str(e)}


def check_gaming_mode(machine_config):
    """Check if Cobo is in gaming mode. Only relevant for machines with gaming_mode_file."""
    gaming_file = machine_config.get("gaming_mode_file")
    if not gaming_file:
        return False

    # For remote machines, try to fetch mode.json via bridge
    ip = machine_config["ip"]
    port = machine_config["bridge_port"]
    url = f"http://{ip}:{port}/file/mode.json"
    try:
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("mode") == "gaming"
    except Exception:
        # If we can't read it, assume not gaming
        return False


def show_status(fleet_data):
    """Display fleet health status."""
    fleet = fleet_data["fleet"]
    print("=" * 60)
    print("  BIOS FLEET STATUS")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for key, machine in fleet.items():
        name = machine["name"]
        ip = machine["ip"]
        port = machine["bridge_port"]
        role = machine["role"]

        result = ping_machine(ip, port)
        status_icon = "[OK]" if result["online"] else "[DOWN]"
        gaming = ""

        if key == "cobo" and result["online"]:
            if check_gaming_mode(machine):
                gaming = " (GAMING MODE - tasks paused)"

        print(f"\n  {status_icon} {name} ({ip}:{port})")
        print(f"      Role: {role}")
        print(f"      OS: {machine['os']}")
        print(f"      Tasks: {', '.join(machine['tasks'])}")
        if gaming:
            print(f"      ** {gaming}")
        if machine.get("gpu"):
            print(f"      GPU: {machine['gpu']}")

    print("\n" + "=" * 60)


def show_assignments(fleet_data):
    """Display task assignments per machine."""
    fleet = fleet_data["fleet"]
    print("=" * 60)
    print("  BIOS TASK ASSIGNMENTS")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for key, machine in fleet.items():
        name = machine["name"]
        ip = machine["ip"]
        role = machine["role"]

        result = ping_machine(ip, machine["bridge_port"])
        available = result["online"]

        if key == "cobo" and available:
            if check_gaming_mode(machine):
                available = False
                print(f"\n  {name} ({ip}) - GAMING MODE, skipping tasks")
                continue

        status_label = "READY" if available else "OFFLINE"
        print(f"\n  {name} ({ip}) - {status_label}")
        print(f"  Role: {role}")

        if not available:
            print("    -> No tasks assigned (machine offline)")
            continue

        for task in machine["tasks"]:
            schedule = get_task_schedule(task)
            print(f"    -> {task} [{schedule}]")

    print("\n" + "=" * 60)


def get_task_schedule(task_name):
    """Return the schedule string for a given task."""
    schedules = {
        # Ceiba tasks
        "dashboard": "always-on",
        "daily_reports": "daily 06:00",
        "conviction_engine": "every 2h",
        "content_wiring": "every 2h",
        "sync_results": "every 1h",
        # Cobo tasks
        "social_scraper": "every 30min",
        "reddit_scraper": "every 30min via proxy",
        "google_trends": "every 30min",
        "blueprint_svg_generator": "every 2h via Ollama",
        # Naboria tasks
        "news_ingestion": "every 30min",
        "signal_processing": "every 1h",
        "always_on_monitor": "always-on",
    }
    return schedules.get(task_name, "unknown")


def quick_ping(fleet_data):
    """Just ping all machines, one-liner each."""
    fleet = fleet_data["fleet"]
    for key, machine in fleet.items():
        result = ping_machine(machine["ip"], machine["bridge_port"])
        tag = "UP" if result["online"] else "DOWN"
        print(f"  {machine['name']:10s} {machine['ip']:16s} [{tag}]")


def main():
    if not FLEET_CONFIG.exists():
        print(f"ERROR: Fleet config not found at {FLEET_CONFIG}")
        sys.exit(1)

    fleet_data = load_fleet()

    if len(sys.argv) < 2:
        print("Usage: coordinator.py [--status | --assign | --ping]")
        sys.exit(1)

    flag = sys.argv[1]

    if flag == "--status":
        show_status(fleet_data)
    elif flag == "--assign":
        show_assignments(fleet_data)
    elif flag == "--ping":
        quick_ping(fleet_data)
    else:
        print(f"Unknown flag: {flag}")
        print("Usage: coordinator.py [--status | --assign | --ping]")
        sys.exit(1)


if __name__ == "__main__":
    main()
