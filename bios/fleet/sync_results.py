#!/usr/bin/env python3
"""
BIOS Fleet Result Sync
Runs on Ceiba. Pulls signals from Cobo and Naboria via HTTP bridge,
merges into local storage, deduplicates by signal ID.

Run hourly via cron:
    0 * * * * cd ~/behique/bios/fleet && python3 sync_results.py >> ~/behique/bios/logs/sync.log 2>&1
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

FLEET_CONFIG = Path(__file__).parent / "fleet.json"
LOCAL_STORAGE = Path(__file__).parent.parent / "storage"
TIMEOUT_SECONDS = 10

# Files to pull from remote machines
SYNC_FILES = ["signals.json", "social_signals.json"]


def load_fleet():
    with open(FLEET_CONFIG, "r") as f:
        return json.load(f)


def fetch_remote_file(ip, port, filename):
    """Pull a JSON file from a remote machine via bridge HTTP."""
    url = f"http://{ip}:{port}/file/{filename}"
    try:
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
        data = resp.read().decode("utf-8")
        return json.loads(data)
    except urllib.error.URLError as e:
        log(f"  Could not reach {ip}:{port} - {e.reason}")
        return None
    except json.JSONDecodeError:
        log(f"  Invalid JSON from {ip}:{port}/{filename}")
        return None
    except Exception as e:
        log(f"  Error fetching {filename} from {ip}: {e}")
        return None


def load_local_file(filepath):
    """Load a local JSON file, return empty list if missing."""
    if filepath.exists():
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_local_file(filepath, data):
    """Save data to a local JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def merge_signals(local_signals, remote_signals):
    """Merge remote signals into local, dedup by ID."""
    seen_ids = {s.get("id") for s in local_signals if s.get("id")}
    new_count = 0

    for signal in remote_signals:
        sid = signal.get("id")
        if sid and sid not in seen_ids:
            local_signals.append(signal)
            seen_ids.add(sid)
            new_count += 1

    return local_signals, new_count


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def main():
    log("BIOS Fleet Sync starting")

    fleet_data = load_fleet()
    fleet = fleet_data["fleet"]

    # Only pull from remote machines (not ceiba itself)
    remote_machines = {k: v for k, v in fleet.items() if k != "ceiba"}

    total_new = 0

    for filename in SYNC_FILES:
        local_path = LOCAL_STORAGE / filename
        local_data = load_local_file(local_path)
        initial_count = len(local_data)

        for machine_key, machine in remote_machines.items():
            name = machine["name"]
            ip = machine["ip"]
            port = machine["bridge_port"]

            log(f"  Pulling {filename} from {name} ({ip}:{port})")
            remote_data = fetch_remote_file(ip, port, filename)

            if remote_data is None:
                log(f"  Skipping {name} - no data")
                continue

            if not isinstance(remote_data, list):
                log(f"  Skipping {name} - expected list, got {type(remote_data).__name__}")
                continue

            local_data, new_count = merge_signals(local_data, remote_data)
            if new_count > 0:
                log(f"  Merged {new_count} new signals from {name}/{filename}")
            total_new += new_count

        # Sort by timestamp descending before saving
        local_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        save_local_file(local_path, local_data)
        final_count = len(local_data)
        log(f"  {filename}: {initial_count} -> {final_count} signals")

    log(f"Sync complete. {total_new} new signals merged total.")


if __name__ == "__main__":
    main()
