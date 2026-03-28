#!/usr/bin/env python3
"""
BIOS Fleet Task Queue - The Nervous System
===========================================
Ceiba assigns tasks, Cobo/Naboria pick them up, results sync back.
Tasks are JSON files in bios/fleet/queue/ - synced via Syncthing automatically.

Usage:
    python3 task_queue.py create --machine cobo --type generate_image --params '{"prompt":"glowing cat"}'
    python3 task_queue.py create --machine naboria --type run_scraper --params '{"scraper_name":"news"}' --priority high
    python3 task_queue.py list
    python3 task_queue.py list --machine cobo --status pending
    python3 task_queue.py get <task_id>
    python3 task_queue.py complete <task_id> --result '{"output":"path/to/file.png"}'
    python3 task_queue.py cancel <task_id>
    python3 task_queue.py cleanup --days 7
"""

import json
import sys
import os
import uuid
import argparse
import tempfile
import fcntl
from datetime import datetime, timedelta, timezone
from pathlib import Path

QUEUE_DIR = Path(__file__).parent / "queue"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)

VALID_TASK_TYPES = [
    "generate_image",
    "generate_video",
    "run_scraper",
    "generate_blueprint",
    "run_conviction",
    "custom",
]

VALID_MACHINES = ["ceiba", "cobo", "naboria"]
VALID_STATUSES = ["pending", "running", "completed", "failed", "cancelled"]
VALID_PRIORITIES = ["low", "normal", "high", "critical"]


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(filepath, data):
    """Write JSON atomically: write to temp file, then rename."""
    filepath = Path(filepath)
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=filepath.parent, suffix=".tmp", prefix=".task_"
    )
    try:
        with os.fdopen(tmp_fd, "w") as f:
            f.write(content)
        os.replace(tmp_path, filepath)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _read_task(filepath):
    """Read a task file with shared lock."""
    filepath = Path(filepath)
    try:
        with open(filepath, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return data
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _update_task(filepath, updates):
    """Read-modify-write a task file with exclusive lock."""
    filepath = Path(filepath)
    with open(filepath, "r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            data = json.load(f)
            data.update(updates)
            data["updated_at"] = _now_iso()
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data


def create_task(machine, task_type, params=None, priority="normal"):
    """Create a new task in the queue.

    Returns the task dict with its generated ID.
    """
    machine = machine.lower()
    if machine not in VALID_MACHINES:
        raise ValueError(f"Unknown machine '{machine}'. Valid: {VALID_MACHINES}")
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(f"Unknown task_type '{task_type}'. Valid: {VALID_TASK_TYPES}")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Unknown priority '{priority}'. Valid: {VALID_PRIORITIES}")

    task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]

    task = {
        "id": task_id,
        "machine": machine,
        "task_type": task_type,
        "params": params or {},
        "priority": priority,
        "status": "pending",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "worker_hostname": None,
    }

    filepath = QUEUE_DIR / f"{task_id}.json"
    _atomic_write(filepath, task)
    return task


def list_tasks(machine=None, status=None):
    """List tasks, optionally filtered by machine and/or status.

    Returns list of tasks sorted by created_at descending.
    """
    tasks = []
    for f in QUEUE_DIR.glob("*.json"):
        if f.name.startswith("."):
            continue
        task = _read_task(f)
        if task is None:
            continue
        if machine and task.get("machine") != machine.lower():
            continue
        if status and task.get("status") != status.lower():
            continue
        tasks.append(task)

    # Sort: critical first, then high, normal, low. Within same priority, newest first.
    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    tasks.sort(
        key=lambda t: (
            priority_order.get(t.get("priority", "normal"), 2),
            t.get("created_at", ""),
        )
    )
    # Reverse created_at within same priority (newest first)
    tasks.sort(
        key=lambda t: priority_order.get(t.get("priority", "normal"), 2)
    )
    return tasks


def get_task(task_id):
    """Get a single task by ID. Returns None if not found."""
    filepath = QUEUE_DIR / f"{task_id}.json"
    if not filepath.exists():
        return None
    return _read_task(filepath)


def claim_task(task_id, hostname):
    """Atomically claim a pending task for a worker. Returns updated task or None."""
    filepath = QUEUE_DIR / f"{task_id}.json"
    if not filepath.exists():
        return None

    try:
        with open(filepath, "r+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                data = json.load(f)
                if data.get("status") != "pending":
                    return None  # Already claimed or not pending
                data["status"] = "running"
                data["started_at"] = _now_iso()
                data["updated_at"] = _now_iso()
                data["worker_hostname"] = hostname
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return data
    except Exception:
        return None


def complete_task(task_id, result=None):
    """Mark a task as completed with optional result data."""
    filepath = QUEUE_DIR / f"{task_id}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Task {task_id} not found")

    return _update_task(filepath, {
        "status": "completed",
        "result": result,
        "completed_at": _now_iso(),
    })


def fail_task(task_id, error=None):
    """Mark a task as failed with optional error message."""
    filepath = QUEUE_DIR / f"{task_id}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Task {task_id} not found")

    return _update_task(filepath, {
        "status": "failed",
        "error": str(error) if error else "Unknown error",
        "completed_at": _now_iso(),
    })


def cancel_task(task_id):
    """Cancel a pending or running task."""
    filepath = QUEUE_DIR / f"{task_id}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Task {task_id} not found")

    task = _read_task(filepath)
    if task and task.get("status") in ("completed", "cancelled"):
        return task  # Already done

    return _update_task(filepath, {
        "status": "cancelled",
        "completed_at": _now_iso(),
    })


def cleanup(days=7):
    """Remove completed/cancelled/failed tasks older than N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    removed = 0

    for f in QUEUE_DIR.glob("*.json"):
        if f.name.startswith("."):
            continue
        task = _read_task(f)
        if task is None:
            continue
        if task.get("status") not in ("completed", "cancelled", "failed"):
            continue

        completed_at = task.get("completed_at")
        if not completed_at:
            continue

        try:
            task_time = datetime.fromisoformat(completed_at)
            if task_time < cutoff:
                f.unlink()
                removed += 1
        except (ValueError, TypeError):
            continue

    return removed


def _format_task_line(task):
    """Format a single task for display."""
    priority_icons = {"critical": "!!", "high": "! ", "normal": "  ", "low": "- "}
    status_icons = {
        "pending": "PEND",
        "running": "RUN ",
        "completed": "DONE",
        "failed": "FAIL",
        "cancelled": "CANC",
    }

    p = priority_icons.get(task.get("priority", "normal"), "  ")
    s = status_icons.get(task.get("status", "pending"), "????")
    machine = task.get("machine", "???")[:6].ljust(6)
    task_type = task.get("task_type", "???")[:18].ljust(18)
    task_id = task.get("id", "???")
    created = task.get("created_at", "")[:19].replace("T", " ")

    return f"  {p} [{s}] {machine} {task_type} {task_id}  ({created})"


def _format_task_detail(task):
    """Format full task details."""
    lines = [
        "=" * 60,
        f"  Task: {task.get('id')}",
        "=" * 60,
        f"  Machine:    {task.get('machine')}",
        f"  Type:       {task.get('task_type')}",
        f"  Priority:   {task.get('priority')}",
        f"  Status:     {task.get('status')}",
        f"  Created:    {task.get('created_at')}",
        f"  Started:    {task.get('started_at') or '-'}",
        f"  Completed:  {task.get('completed_at') or '-'}",
        f"  Worker:     {task.get('worker_hostname') or '-'}",
        f"  Params:     {json.dumps(task.get('params', {}), indent=4)}",
    ]
    if task.get("result") is not None:
        lines.append(f"  Result:     {json.dumps(task.get('result'), indent=4)}")
    if task.get("error"):
        lines.append(f"  Error:      {task.get('error')}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="BIOS Fleet Task Queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # create
    p_create = sub.add_parser("create", help="Create a new task")
    p_create.add_argument("--machine", "-m", required=True, choices=VALID_MACHINES)
    p_create.add_argument("--type", "-t", dest="task_type", required=True, choices=VALID_TASK_TYPES)
    p_create.add_argument("--params", "-p", default="{}", help="JSON params string")
    p_create.add_argument("--priority", default="normal", choices=VALID_PRIORITIES)

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--machine", "-m", choices=VALID_MACHINES)
    p_list.add_argument("--status", "-s", choices=VALID_STATUSES)

    # get
    p_get = sub.add_parser("get", help="Get task details")
    p_get.add_argument("task_id", help="Task ID")

    # complete
    p_complete = sub.add_parser("complete", help="Mark task completed")
    p_complete.add_argument("task_id", help="Task ID")
    p_complete.add_argument("--result", "-r", default="{}", help="JSON result string")

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel a task")
    p_cancel.add_argument("task_id", help="Task ID")

    # cleanup
    p_cleanup = sub.add_parser("cleanup", help="Remove old completed tasks")
    p_cleanup.add_argument("--days", "-d", type=int, default=7)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "create":
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON params: {e}")
            sys.exit(1)

        task = create_task(args.machine, args.task_type, params, args.priority)
        print(f"Task created: {task['id']}")
        print(f"  Machine:  {task['machine']}")
        print(f"  Type:     {task['task_type']}")
        print(f"  Priority: {task['priority']}")

    elif args.command == "list":
        tasks = list_tasks(args.machine, args.status)
        if not tasks:
            print("  No tasks found.")
            return

        machine_label = args.machine or "all"
        status_label = args.status or "all"
        print(f"\n  Fleet Queue ({len(tasks)} tasks) - machine={machine_label} status={status_label}\n")
        for t in tasks:
            print(_format_task_line(t))
        print()

    elif args.command == "get":
        task = get_task(args.task_id)
        if not task:
            print(f"ERROR: Task {args.task_id} not found")
            sys.exit(1)
        print(_format_task_detail(task))

    elif args.command == "complete":
        try:
            result = json.loads(args.result)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON result: {e}")
            sys.exit(1)

        try:
            task = complete_task(args.task_id, result)
            print(f"Task {args.task_id} marked completed.")
        except FileNotFoundError:
            print(f"ERROR: Task {args.task_id} not found")
            sys.exit(1)

    elif args.command == "cancel":
        try:
            task = cancel_task(args.task_id)
            print(f"Task {args.task_id} cancelled.")
        except FileNotFoundError:
            print(f"ERROR: Task {args.task_id} not found")
            sys.exit(1)

    elif args.command == "cleanup":
        removed = cleanup(args.days)
        print(f"Cleaned up {removed} tasks older than {args.days} days.")


if __name__ == "__main__":
    main()
