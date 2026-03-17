#!/usr/bin/env python3
"""
ceiba_run.py — One-Command Ceiba Session Startup

Runs the full initialization sequence:
  1. Rebuild vault graph (vault_grapher.py)
  2. Log session start (session_tracker.py)
  3. Run morning briefing (morning_briefing.py)
  4. Output Claude prompt context (primer + vault stats + git state)

Usage:
    python3 ceiba_run.py                        # full startup
    python3 ceiba_run.py --skip-graph           # skip vault rebuild
    python3 ceiba_run.py --skip-briefing        # skip morning briefing
    python3 ceiba_run.py --plan "Fix bugs, Ship listing"  # set today's plan
    python3 ceiba_run.py --context-only         # just output context for Claude
"""

import os
import sys
import json
import subprocess
import argparse
import time
from datetime import datetime
from pathlib import Path


BEHIQUE = os.path.expanduser("~/behique")
TOOLS = os.path.join(BEHIQUE, "tools")
PRIMER = os.path.join(BEHIQUE, "primer.md")
VAULT_GRAPH = os.path.join(BEHIQUE, "Ceiba", "vault_graph.json")


def run_step(name, cmd, cwd=None):
    """Run a subprocess step with timing."""
    print(f"\n{'─' * 50}")
    print(f"  ▶ {name}")
    print(f"{'─' * 50}")
    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=cwd or BEHIQUE, timeout=30
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            # Print output (trimmed)
            output = result.stdout.strip()
            if output:
                for line in output.split("\n")[:15]:
                    print(f"  {line}")
                if output.count("\n") > 15:
                    print(f"  ... ({output.count(chr(10)) - 15} more lines)")
            print(f"  ✅ Done ({elapsed:.1f}s)")
            return True
        else:
            print(f"  ❌ Failed (exit {result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().split("\n")[:5]:
                    print(f"  {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Timed out after 30s")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def output_context():
    """Output session context summary for Claude."""
    print(f"\n{'═' * 50}")
    print(f"  📋 SESSION CONTEXT")
    print(f"{'═' * 50}")

    # primer.md summary
    if os.path.exists(PRIMER):
        with open(PRIMER) as f:
            content = f.read()
        age_min = int((time.time() - os.path.getmtime(PRIMER)) / 60)
        print(f"\n  primer.md ({age_min}m old):")
        # Extract first meaningful section
        lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#")][:5]
        for line in lines:
            print(f"    {line[:100]}")

    # Vault stats
    if os.path.exists(VAULT_GRAPH):
        with open(VAULT_GRAPH) as f:
            data = json.load(f)
        nodes = len(data.get("nodes", {}))
        edges = len(data.get("edges", []))
        missing = data.get("stats", {}).get("missing_targets", 0)
        print(f"\n  Vault: {nodes} nodes, {edges} edges, {missing} missing targets")

    # Git state
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip()
        uncommitted = len([l for l in subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip().split("\n") if l])
        commits_today = len([l for l in subprocess.run(
            ["git", "log", "--oneline", "--since=midnight"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip().split("\n") if l])
        print(f"\n  Git: branch={branch}, {commits_today} commits today, {uncommitted} uncommitted")
    except Exception:
        pass

    # CMP stats
    cmp_db = os.path.join(BEHIQUE, "tools", "ai_agent_kernel", "cmp.db")
    if os.path.exists(cmp_db):
        try:
            import sqlite3
            conn = sqlite3.connect(cmp_db)
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            today = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE date(timestamp) = date('now')"
            ).fetchone()[0]
            conn.close()
            print(f"  CMP: {total} entries ({today} today)")
        except Exception:
            pass

    print(f"\n{'═' * 50}")


def main():
    parser = argparse.ArgumentParser(description="Ceiba Session Startup")
    parser.add_argument("--skip-graph", action="store_true", help="Skip vault graph rebuild")
    parser.add_argument("--skip-briefing", action="store_true", help="Skip morning briefing")
    parser.add_argument("--plan", default="", help="Comma-separated planned tasks for today")
    parser.add_argument("--context-only", action="store_true", help="Just output context")
    args = parser.parse_args()

    start_time = time.time()

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║  🌳 Ceiba Session Startup                    ║")
    print(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                         ║")
    print("╚══════════════════════════════════════════════╝")

    if args.context_only:
        output_context()
        return

    steps_run = 0
    steps_ok = 0

    # Step 1: Rebuild vault graph
    if not args.skip_graph:
        steps_run += 1
        if run_step("Rebuild Vault Graph",
                     ["python3", os.path.join(TOOLS, "vault_grapher.py"), "--json"]):
            steps_ok += 1

    # Step 2: Session tracker — start
    if args.plan:
        steps_run += 1
        if run_step("Start Session Tracking",
                     ["python3", os.path.join(TOOLS, "session_tracker.py"), "start"] + args.plan.split(",")):
            steps_ok += 1

    # Step 3: Export hub.json for dashboard
    steps_run += 1
    if run_step("Export Hub Data",
                 [sys.executable, os.path.join(TOOLS, "export_hub_data.py")]):
        steps_ok += 1

    # Step 4: Morning briefing
    if not args.skip_briefing:
        steps_run += 1
        if run_step("Morning Briefing",
                     [sys.executable, os.path.join(TOOLS, "morning_briefing.py"), "--short"]):
            steps_ok += 1

    # Step 5: Output context
    output_context()

    # Summary
    elapsed = time.time() - start_time
    print(f"\n  Startup complete: {steps_ok}/{steps_run} steps OK ({elapsed:.1f}s)")
    print(f"  Run 'bash bridge/wake.sh' for full cluster health check")
    print()


if __name__ == "__main__":
    main()
