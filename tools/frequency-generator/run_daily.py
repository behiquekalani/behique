#!/usr/bin/env python3
"""
Daily Orchestrator for Frequency Video Generator.
Calls generate.py then upload.py. Logs everything.

Designed for Windows Task Scheduler on Cobo:
  Action: Start a program
  Program: python
  Arguments: C:\\path\\to\\frequency-generator\\run_daily.py
  Start in: C:\\path\\to\\frequency-generator
"""

import logging
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Set up logging
today = datetime.now().strftime("%Y%m%d")
log_file = LOGS_DIR / f"run-{today}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("frequency-generator")


def run_script(script_name, args=None):
    """Run a Python script and capture output."""
    script_path = BASE_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    log.info(f"Running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
        timeout=18000,  # 5 hour timeout
    )

    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            log.info(f"  {line}")

    if result.stderr:
        for line in result.stderr.strip().split("\n"):
            log.warning(f"  {line}")

    if result.returncode != 0:
        log.error(f"{script_name} failed with exit code {result.returncode}")
        return None

    # Return the last line (metadata path from generate.py)
    lines = result.stdout.strip().split("\n")
    return lines[-1] if lines else None


def main():
    log.info("=" * 60)
    log.info("FREQUENCY GENERATOR - Daily Run")
    log.info(f"Date: {datetime.now().isoformat()}")
    log.info("=" * 60)

    try:
        # Step 1: Generate video
        log.info("Step 1: Generating video...")
        metadata_path = run_script("generate.py")

        if not metadata_path or not Path(metadata_path).exists():
            log.error("Video generation failed or metadata not found.")
            sys.exit(1)

        log.info(f"Video generated. Metadata: {metadata_path}")

        # Step 2: Upload
        log.info("Step 2: Uploading to YouTube...")
        run_script("upload.py", [metadata_path])

        log.info("=" * 60)
        log.info("Daily run complete.")
        log.info("=" * 60)

    except subprocess.TimeoutExpired:
        log.error("Script timed out after 5 hours.")
        sys.exit(1)
    except Exception:
        log.error(f"Unexpected error:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
