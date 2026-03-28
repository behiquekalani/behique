#!/usr/bin/env python3
"""
BIOS Fleet Orchestrator - Phase 6.
Dispatches jobs to Cobo/Naboria via bridge servers, monitors health,
handles failover.

Usage:
    python3 bios/control/fleet_orchestrator.py status     # Fleet health
    python3 bios/control/fleet_orchestrator.py dispatch    # Send pending jobs
    python3 bios/control/fleet_orchestrator.py run-local   # Run all locally (fallback)
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BIOS_DIR = BASE_DIR / "bios"
CONFIG_FILE = BIOS_DIR / "config.json"
HEALTH_FILE = BIOS_DIR / "storage" / "fleet_health.json"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def ping(ip, timeout=2):
    try:
        r = subprocess.run(["ping", "-c", "1", "-W", str(timeout), ip],
                          capture_output=True, timeout=timeout + 2)
        return r.returncode == 0
    except Exception:
        return False


def check_bridge(ip, port, timeout=3):
    """Check if bridge server is responding."""
    try:
        url = f"http://{ip}:{port}/status"
        req = Request(url, headers={"User-Agent": "BIOS/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def health_check(config):
    """Full fleet health check."""
    health = {"timestamp": datetime.now(timezone.utc).isoformat(), "machines": {}}

    for name, info in config["fleet"].items():
        ip = info.get("ip", "")
        enabled = info.get("enabled", False)

        machine_health = {
            "enabled": enabled,
            "reachable": False,
            "bridge_up": False,
            "mode": info.get("mode", "normal"),
            "role": info.get("role", "unknown"),
        }

        if enabled:
            machine_health["reachable"] = ping(ip)
            if machine_health["reachable"] and "bridge_port" in info:
                machine_health["bridge_up"] = check_bridge(ip, info["bridge_port"])

        health["machines"][name] = machine_health

    # Save health
    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_FILE, "w") as f:
        json.dump(health, f, indent=2)

    return health


def print_health(health):
    """Display health status."""
    print(f"\n  BIOS FLEET HEALTH CHECK")
    print(f"  {health['timestamp']}")
    print("  " + "=" * 50)

    for name, info in health["machines"].items():
        status_parts = []
        if not info["enabled"]:
            status_parts.append("DISABLED")
        elif not info["reachable"]:
            status_parts.append("OFFLINE")
        else:
            status_parts.append("ONLINE")
            if info.get("bridge_up"):
                status_parts.append("BRIDGE OK")
            elif info.get("role") != "command":
                status_parts.append("NO BRIDGE")

        mode = f" [{info.get('mode', 'normal').upper()}]" if name == "cobo" else ""
        print(f"  {name:10s} {' | '.join(status_parts)}{mode}")

    # Overall status
    online = sum(1 for m in health["machines"].values() if m.get("reachable"))
    total = len(health["machines"])
    print(f"\n  Fleet: {online}/{total} online")
    print()


def dispatch_to_bridge(ip, port, command, token=""):
    """Send a command to a bridge server."""
    try:
        import urllib.parse
        data = json.dumps({"command": command}).encode()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "BIOS/1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = Request(f"http://{ip}:{port}/run", data=data, headers=headers, method="POST")
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def run_local_fallback():
    """Run all ingestion locally when fleet is down."""
    print("  Running all ingestion locally (fleet fallback mode)...")
    scripts = [
        ("News", "python3 bios/ingestion/news_fetcher.py"),
        ("Polymarket", "python3 bios/ingestion/polymarket_fetcher.py"),
        ("Reddit", "python3 bios/ingestion/reddit_signal.py"),
        ("Intelligence", "python3 bios/intelligence/causal_engine.py"),
    ]
    for name, cmd in scripts:
        print(f"\n  [{name}]")
        try:
            subprocess.run(cmd.split(), cwd=str(BASE_DIR), timeout=120)
        except Exception as e:
            print(f"  ERROR: {e}")


def main():
    config = load_config()

    if len(sys.argv) < 2:
        print("Usage: fleet_orchestrator.py [status|dispatch|run-local]")
        return

    cmd = sys.argv[1]

    if cmd == "status":
        health = health_check(config)
        print_health(health)

    elif cmd == "dispatch":
        health = health_check(config)
        cobo = health["machines"].get("cobo", {})
        naboria = health["machines"].get("naboria", {})

        if cobo.get("reachable") and cobo.get("mode") != "gaming":
            print("  Cobo is online. Dispatching heavy scraping jobs...")
            # In production, this would send via bridge
            print("  (Bridge dispatch not yet configured. Run jobs locally.)")
        else:
            reason = "gaming mode" if cobo.get("mode") == "gaming" else "offline"
            print(f"  Cobo is {reason}. Running scraping locally.")

        if naboria.get("reachable"):
            print("  Naboria is online. Dispatching processing jobs...")
            print("  (Bridge dispatch not yet configured. Run jobs locally.)")
        else:
            print("  Naboria is offline. Processing locally.")

        run_local_fallback()

    elif cmd == "run-local":
        run_local_fallback()


if __name__ == "__main__":
    main()
