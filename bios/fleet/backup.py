#!/usr/bin/env python3
"""
Behique Backup System
Automated backup of critical project directories with rotation and restore.

Usage:
    python3 bios/fleet/backup.py             # Run backup
    python3 bios/fleet/backup.py --list       # List existing backups
    python3 bios/fleet/backup.py --restore FILENAME  # Restore a backup

Cron (daily 3AM):
    0 3 * * * cd /Users/kalani/behique && /usr/bin/python3 bios/fleet/backup.py >> bios/logs/backup.log 2>&1
"""

import argparse
import os
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path

# --- Configuration ---

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ~/behique
BACKUP_DIR = BASE_DIR / "backups"
LOG_FILE = BASE_DIR / "bios" / "logs" / "backup.log"
MAX_BACKUPS = 7

TARGETS = [
    "READY-TO-SELL",
    "bios/storage",
    "bios/analytics",
    "storefront",
    "Ceiba",
    "clients",
]

EXCLUDE = {".git", "node_modules", "__pycache__"}


# --- Helpers ---

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def should_exclude(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(tarinfo.name).parts
    for part in parts:
        if part in EXCLUDE:
            return None
    return tarinfo


def human_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


# --- Commands ---

def run_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    filename = f"backup-{stamp}.tar.gz"
    dest = BACKUP_DIR / filename

    log(f"Starting backup -> {filename}")

    file_count = 0
    start = time.time()

    with tarfile.open(dest, "w:gz") as tar:
        for target in TARGETS:
            full = BASE_DIR / target
            if not full.exists():
                log(f"  SKIP (not found): {target}")
                continue
            count_before = file_count
            for root, dirs, files in os.walk(full):
                # prune excluded dirs in-place
                dirs[:] = [d for d in dirs if d not in EXCLUDE]
                for f in files:
                    fpath = Path(root) / f
                    arcname = str(fpath.relative_to(BASE_DIR))
                    tar.add(fpath, arcname=arcname, filter=should_exclude)
                    file_count += 1
            added = file_count - count_before
            log(f"  Added: {target} ({added} files)")

    elapsed = time.time() - start
    size = dest.stat().st_size

    log(f"Backup complete: {filename}")
    log(f"  Files: {file_count} | Size: {human_size(size)} | Time: {elapsed:.1f}s")

    # Rotation - keep only last MAX_BACKUPS
    backups = sorted(BACKUP_DIR.glob("backup-*.tar.gz"))
    if len(backups) > MAX_BACKUPS:
        to_delete = backups[: len(backups) - MAX_BACKUPS]
        for old in to_delete:
            old.unlink()
            log(f"  Rotated out: {old.name}")

    log("Done.")


def list_backups():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backups = sorted(BACKUP_DIR.glob("backup-*.tar.gz"))

    if not backups:
        print("No backups found.")
        return

    print(f"{'Backup':<40} {'Size':>10}")
    print("-" * 52)
    total = 0
    for b in backups:
        sz = b.stat().st_size
        total += sz
        print(f"{b.name:<40} {human_size(sz):>10}")
    print("-" * 52)
    print(f"{'Total: ' + str(len(backups)) + ' backups':<40} {human_size(total):>10}")


def restore_backup(filename: str):
    source = BACKUP_DIR / filename
    if not source.exists():
        print(f"Error: {filename} not found in {BACKUP_DIR}")
        sys.exit(1)

    print(f"Restoring {filename} to {BASE_DIR} ...")
    with tarfile.open(source, "r:gz") as tar:
        tar.extractall(path=BASE_DIR)

    print(f"Restored {filename} successfully.")
    log(f"Restored backup: {filename}")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Behique Backup System")
    parser.add_argument("--list", action="store_true", help="List existing backups")
    parser.add_argument("--restore", metavar="FILENAME", help="Restore a backup file")
    args = parser.parse_args()

    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(args.restore)
    else:
        run_backup()


if __name__ == "__main__":
    main()
