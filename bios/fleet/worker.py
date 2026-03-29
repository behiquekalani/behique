#!/usr/bin/env python3
"""
BIOS Fleet Worker
==================
Runs on Cobo/Naboria. Polls the queue/ directory for tasks assigned to this machine.
Syncthing handles the file sync - this just watches the local directory.

Usage:
    python3 worker.py                  # Run forever, polling every 30s
    python3 worker.py --once           # Process one batch and exit
    python3 worker.py --machine cobo   # Override auto-detected hostname
    python3 worker.py --interval 10    # Poll every 10 seconds
"""

import json
import sys
import os
import socket
import signal
import subprocess
import logging
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

# Resolve paths relative to this script
FLEET_DIR = Path(__file__).parent
QUEUE_DIR = FLEET_DIR / "queue"
LOGS_DIR = FLEET_DIR / "logs"
BIOS_DIR = FLEET_DIR.parent

QUEUE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Machine name aliases (hostname -> fleet name)
HOSTNAME_MAP = {
    "ceiba": "ceiba",
    "cobo": "cobo",
    "naboria": "naboria",
    # Add actual hostnames as needed
}

# Import task_queue functions
sys.path.insert(0, str(FLEET_DIR))
from task_queue import (
    claim_task,
    complete_task,
    fail_task,
    _read_task,
    VALID_STATUSES,
)


def detect_machine():
    """Detect which fleet machine this is based on hostname."""
    hostname = socket.gethostname().lower().strip()

    # Direct match
    if hostname in HOSTNAME_MAP:
        return HOSTNAME_MAP[hostname]

    # Partial match
    for key, name in HOSTNAME_MAP.items():
        if key in hostname or hostname in key:
            return name

    return hostname


def setup_logging(machine_name):
    """Set up logging to both console and file."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"worker-{machine_name}-{today}.log"

    logger = logging.getLogger("fleet_worker")
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def find_pending_tasks(machine_name):
    """Find all pending tasks for this machine, sorted by priority."""
    tasks = []
    for f in QUEUE_DIR.glob("*.json"):
        if f.name.startswith("."):
            continue
        task = _read_task(f)
        if task is None:
            continue
        if task.get("machine") != machine_name:
            continue
        if task.get("status") != "pending":
            continue
        tasks.append(task)

    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    tasks.sort(key=lambda t: (
        priority_order.get(t.get("priority", "normal"), 2),
        t.get("created_at", ""),
    ))
    return tasks


def execute_generate_image(params, logger):
    """Execute image generation task."""
    prompt = params.get("prompt", "")
    preset = params.get("preset", "default")
    output_dir = params.get("output_dir", str(BIOS_DIR / "storage" / "images"))

    # Look for sd-generator in common locations
    generator_paths = [
        BIOS_DIR / "sd-generator" / "generate.py",
        BIOS_DIR.parent / "sd-generator" / "generate.py",
        Path.home() / "sd-generator" / "generate.py",
    ]

    generator = None
    for p in generator_paths:
        if p.exists():
            generator = p
            break

    if not generator:
        return {"error": "sd-generator/generate.py not found", "searched": [str(p) for p in generator_paths]}

    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable, str(generator),
        "--prompt", prompt,
        "--preset", preset,
        "--output-dir", output_dir,
    ]

    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    return {
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
        "output_dir": output_dir,
    }


def execute_generate_video(params, logger):
    """Execute video generation task."""
    theme = params.get("theme", "333")
    duration = params.get("duration", 30)

    generator_paths = [
        BIOS_DIR / "frequency-generator" / "generate.py",
        BIOS_DIR.parent / "frequency-generator" / "generate.py",
        Path.home() / "frequency-generator" / "generate.py",
    ]

    generator = None
    for p in generator_paths:
        if p.exists():
            generator = p
            break

    if not generator:
        return {"error": "frequency-generator/generate.py not found", "searched": [str(p) for p in generator_paths]}

    cmd = [
        sys.executable, str(generator),
        "--theme", str(theme),
        "--duration", str(duration),
    ]

    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    return {
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
    }


def execute_run_scraper(params, logger):
    """Execute a scraper task."""
    scraper_name = params.get("scraper_name", "")
    if not scraper_name:
        return {"error": "No scraper_name provided"}

    scraper_map = {
        "news": BIOS_DIR / "scrapers" / "news_scraper.py",
        "social": BIOS_DIR / "scrapers" / "social_scraper.py",
        "reddit": BIOS_DIR / "scrapers" / "reddit_scraper.py",
        "trends": BIOS_DIR / "scrapers" / "trends_scraper.py",
    }

    scraper_path = scraper_map.get(scraper_name)
    if not scraper_path:
        # Try direct path
        scraper_path = Path(scraper_name)

    if not scraper_path or not scraper_path.exists():
        return {"error": f"Scraper '{scraper_name}' not found", "available": list(scraper_map.keys())}

    cmd = [sys.executable, str(scraper_path)]

    # Pass any extra params as args
    extra_args = params.get("args", [])
    if extra_args:
        cmd.extend(extra_args)

    logger.info(f"Running scraper: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    return {
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
    }


def execute_generate_blueprint(params, logger):
    """Execute blueprint generation task."""
    niche = params.get("niche", "")
    language = params.get("language", "en")

    if not niche:
        return {"error": "No niche provided"}

    generator_paths = [
        BIOS_DIR / "blueprint-generator" / "generate.py",
        BIOS_DIR.parent / "blueprint-generator" / "generate.py",
    ]

    generator = None
    for p in generator_paths:
        if p.exists():
            generator = p
            break

    if not generator:
        return {"error": "blueprint-generator/generate.py not found"}

    cmd = [
        sys.executable, str(generator),
        "--niche", niche,
        "--language", language,
    ]

    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    return {
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
    }


def execute_run_conviction(params, logger):
    """Execute conviction engine."""
    engine_paths = [
        BIOS_DIR / "conviction" / "run.py",
        BIOS_DIR / "conviction-engine" / "run.py",
    ]

    engine = None
    for p in engine_paths:
        if p.exists():
            engine = p
            break

    if not engine:
        return {"error": "conviction engine not found"}

    cmd = [sys.executable, str(engine)]
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    return {
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
    }


def execute_custom(params, logger):
    """Execute a custom command."""
    command = params.get("command", "")
    if not command:
        return {"error": "No command provided"}

    # Safety: allowlist of permitted command prefixes
    import shlex
    allowed_prefixes = [
        "python3", "python", "git", "ls", "cat", "echo",
        "pip", "npm", "node", "curl", "wget",
    ]
    try:
        cmd_parts = shlex.split(command)
    except ValueError as e:
        return {"error": f"Invalid command syntax: {e}"}

    if not cmd_parts or cmd_parts[0] not in allowed_prefixes:
        return {"error": f"Command '{cmd_parts[0] if cmd_parts else ''}' not in allowlist: {allowed_prefixes}"}

    # Block dangerous patterns as second layer
    dangerous = ["rm -rf", "format ", "del /s", "mkfs", "> /dev/", "sudo ",
                  "chmod 777", "eval ", "exec(", "| sh", "| bash"]
    for d in dangerous:
        if d in command.lower():
            return {"error": f"Blocked dangerous command pattern: {d}"}

    timeout = params.get("timeout", 300)
    cwd = params.get("cwd", str(BIOS_DIR))

    logger.info(f"Running custom command: {command}")
    result = subprocess.run(
        cmd_parts,
        shell=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )

    return {
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "returncode": result.returncode,
    }


# Task type -> executor mapping
EXECUTORS = {
    "generate_image": execute_generate_image,
    "generate_video": execute_generate_video,
    "run_scraper": execute_run_scraper,
    "generate_blueprint": execute_generate_blueprint,
    "run_conviction": execute_run_conviction,
    "custom": execute_custom,
}


def process_task(task, hostname, logger):
    """Claim and execute a single task."""
    task_id = task["id"]
    task_type = task["task_type"]

    # Attempt to claim
    claimed = claim_task(task_id, hostname)
    if not claimed:
        logger.info(f"Could not claim task {task_id} (already taken or not pending)")
        return False

    logger.info(f"Claimed task {task_id}: {task_type} (priority={task.get('priority', 'normal')})")
    logger.info(f"  Params: {json.dumps(task.get('params', {}))}")

    executor = EXECUTORS.get(task_type)
    if not executor:
        fail_task(task_id, f"Unknown task_type: {task_type}")
        logger.error(f"Unknown task_type: {task_type}")
        return False

    try:
        result = executor(task.get("params", {}), logger)

        # Check if the result indicates an error
        if isinstance(result, dict) and result.get("returncode", 0) != 0:
            fail_task(task_id, result.get("stderr", "Non-zero exit code"))
            logger.warning(f"Task {task_id} failed with returncode {result.get('returncode')}")
        elif isinstance(result, dict) and "error" in result:
            fail_task(task_id, result["error"])
            logger.warning(f"Task {task_id} failed: {result['error']}")
        else:
            complete_task(task_id, result)
            logger.info(f"Task {task_id} completed successfully")

    except subprocess.TimeoutExpired:
        fail_task(task_id, "Task timed out")
        logger.error(f"Task {task_id} timed out")
    except Exception as e:
        fail_task(task_id, str(e))
        logger.error(f"Task {task_id} exception: {e}")

    return True


def poll_loop(machine_name, interval=30, once=False):
    """Main polling loop."""
    hostname = socket.gethostname()
    logger = setup_logging(machine_name)

    # Graceful shutdown
    running = True

    def handle_signal(sig, frame):
        nonlocal running
        logger.info(f"Received signal {sig}, shutting down gracefully...")
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info(f"Fleet worker started for machine '{machine_name}' (hostname={hostname})")
    logger.info(f"Queue directory: {QUEUE_DIR}")
    logger.info(f"Poll interval: {interval}s")

    while running:
        try:
            tasks = find_pending_tasks(machine_name)
            if tasks:
                logger.info(f"Found {len(tasks)} pending tasks")
                for task in tasks:
                    if not running:
                        break
                    process_task(task, hostname, logger)
        except Exception as e:
            logger.error(f"Poll error: {e}")

        if once:
            break

        # Sleep in small increments so we can respond to signals
        for _ in range(interval):
            if not running:
                break
            time.sleep(1)

    logger.info("Worker stopped.")


def main():
    parser = argparse.ArgumentParser(description="BIOS Fleet Worker")
    parser.add_argument(
        "--machine", "-m",
        default=None,
        help="Override auto-detected machine name",
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Poll interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process one batch and exit",
    )

    args = parser.parse_args()

    machine_name = args.machine or detect_machine()
    print(f"Machine: {machine_name}")

    poll_loop(machine_name, args.interval, args.once)


if __name__ == "__main__":
    main()
