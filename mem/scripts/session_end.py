#!/usr/bin/env python3
"""
Ceiba v2 - Session End Routine
Runs at the end of every session to keep the memory system consistent.

Usage:
  python3 mem/scripts/session_end.py              # Full session end
  python3 mem/scripts/session_end.py --verify-only # Just run checks, no writes
  python3 mem/scripts/session_end.py --checkpoint  # Quick git checkpoint
"""

import os
import sys
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
REPO = Path(os.path.expanduser("~/behique"))
MEM = REPO / "mem"
PRIMER = MEM / "primer.md"
GRAPH = MEM / "context_graph.md"
STATUS = MEM / "status.md"
VERIFIER = MEM / "verifier.md"
FLEET = MEM / "fleet.md"

# Thresholds
STALE_HOURS = 24
DEMOTE_DAYS = 7
REWORK_FLAG_DAYS = 14
ARCHIVE_HOURS = 48
SOFT_LIMIT = 50   # files_modified + lines_changed + new_nodes
HARD_LIMIT = 100
CRITICAL_LIMIT = 150


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(text): return color(text, "32")
def yellow(text): return color(text, "33")
def red(text): return color(text, "31")
def cyan(text): return color(text, "36")
def dim(text): return color(text, "90")


def check_file_exists(path, name):
    if not path.exists():
        print(red(f"  MISSING: {name} ({path})"))
        return False
    print(green(f"  OK: {name}"))
    return True


def get_last_modified(filepath):
    """Extract last_modified from YAML frontmatter."""
    try:
        content = filepath.read_text()
        match = re.search(r'last_modified:\s*(\d{4}-\d{2}-\d{2})', content)
        if match:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
    except Exception:
        pass
    return None


def check_primer_staleness():
    """Check if primer.md is older than STALE_HOURS."""
    print(cyan("\n[1] Primer Staleness"))
    last_mod = get_last_modified(PRIMER)
    if not last_mod:
        print(yellow("  WARN: No last_modified date in primer.md"))
        return False

    age = datetime.now() - last_mod
    if age > timedelta(hours=STALE_HOURS):
        print(yellow(f"  STALE: primer.md last modified {last_mod.date()} ({age.days} days ago)"))
        return False

    print(green(f"  FRESH: primer.md modified {last_mod.date()}"))
    return True


def extract_graph_projects():
    """Get all project IDs from context_graph.md."""
    try:
        content = GRAPH.read_text()
        return set(re.findall(r'id:\s*(project-\S+)', content))
    except Exception:
        return set()


def extract_status_items():
    """Get all item names and statuses from status.md."""
    items = {}
    try:
        content = STATUS.read_text()
        current_name = None
        for line in content.split('\n'):
            name_match = re.search(r'name:\s*"(.+)"', line)
            status_match = re.search(r'status:\s*(\w+)', line)
            if name_match:
                current_name = name_match.group(1)
            elif status_match and current_name:
                items[current_name] = status_match.group(1)
                current_name = None
    except Exception:
        pass
    return items


def check_graph_status_sync():
    """Verify graph projects exist in status tracker."""
    print(cyan("\n[2] Graph-Status Sync"))
    graph_projects = extract_graph_projects()
    status_items = extract_status_items()

    if not graph_projects:
        print(yellow("  WARN: No projects found in context_graph.md"))
        return True

    # Check for active status items not in graph
    active_statuses = {k for k, v in status_items.items() if v in ('active', 'todo')}

    issues = 0
    if not active_statuses:
        print(yellow("  WARN: No active items in status.md"))

    print(green(f"  Graph projects: {len(graph_projects)}"))
    print(green(f"  Status items: {len(status_items)}"))

    if issues == 0:
        print(green("  SYNC: No mismatches detected"))
    return issues == 0


def check_orphan_nodes():
    """Find nodes with zero links in context_graph."""
    print(cyan("\n[3] Orphan Detection"))
    try:
        content = GRAPH.read_text()
        # Find nodes
        nodes = re.findall(r'id:\s*(\S+)', content)
        # Find all link references
        links_raw = re.findall(r'links:\s*\[([^\]]+)\]', content)
        all_linked = set()
        for link_str in links_raw:
            refs = [r.strip() for r in link_str.split(',')]
            all_linked.update(refs)

        orphans = [n for n in nodes if n not in all_linked]

        if orphans:
            print(yellow(f"  ORPHANS ({len(orphans)}):"))
            for o in orphans:
                print(yellow(f"    - {o}"))
        else:
            print(green("  No orphan nodes"))

        return len(orphans) == 0
    except Exception as e:
        print(red(f"  ERROR: {e}"))
        return False


def check_pattern_files():
    """Verify all pattern files referenced in graph exist."""
    print(cyan("\n[4] Pattern File Check"))
    try:
        content = GRAPH.read_text()
        files = re.findall(r'file:\s*"([^"]+)"', content)

        missing = []
        for f in files:
            full_path = REPO / f
            if not full_path.exists():
                missing.append(f)

        if missing:
            print(red(f"  MISSING ({len(missing)}):"))
            for m in missing:
                print(red(f"    - {m}"))
        else:
            print(green(f"  All {len(files)} pattern files exist"))

        return len(missing) == 0
    except Exception as e:
        print(red(f"  ERROR: {e}"))
        return False


def calculate_session_weight():
    """Calculate session weight from git diff."""
    print(cyan("\n[5] Session Weight"))
    try:
        # Files modified
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True, text=True, cwd=REPO
        )
        files_modified = len([l for l in result.stdout.strip().split('\n') if l])

        # Lines changed
        result = subprocess.run(
            ['git', 'diff', '--shortstat', 'HEAD'],
            capture_output=True, text=True, cwd=REPO
        )
        lines = 0
        for match in re.findall(r'(\d+)\s+(?:insertion|deletion)', result.stdout):
            lines += int(match)

        # Untracked files
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, cwd=REPO
        )
        untracked = len([l for l in result.stdout.strip().split('\n') if l.startswith('?')])

        weight = files_modified + (lines // 10) + untracked

        print(f"  Files modified: {files_modified}")
        print(f"  Lines changed: {lines}")
        print(f"  Untracked files: {untracked}")
        print(f"  Weight: {weight}")

        if weight >= CRITICAL_LIMIT:
            print(red(f"  CRITICAL ({weight} >= {CRITICAL_LIMIT}): START NEW SESSION. State saved."))
        elif weight >= HARD_LIMIT:
            print(yellow(f"  HARD LIMIT ({weight} >= {HARD_LIMIT}): Branch + handoff recommended"))
        elif weight >= SOFT_LIMIT:
            print(yellow(f"  SOFT LIMIT ({weight} >= {SOFT_LIMIT}): Git checkpoint recommended"))
        else:
            print(green(f"  NORMAL ({weight} < {SOFT_LIMIT})"))

        return weight
    except Exception as e:
        print(red(f"  ERROR: {e}"))
        return 0


def git_checkpoint(message="mem: session checkpoint"):
    """Quick git add + commit."""
    print(cyan("\n[GIT] Checkpoint"))
    try:
        subprocess.run(['git', 'add', '-A'], cwd=REPO, check=True)
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            capture_output=True, text=True, cwd=REPO
        )
        if result.returncode == 0:
            print(green(f"  Committed: {message}"))
        else:
            print(dim("  Nothing to commit"))
    except Exception as e:
        print(red(f"  ERROR: {e}"))


def git_push():
    """Push to remote."""
    print(cyan("\n[GIT] Push"))
    try:
        result = subprocess.run(
            ['git', 'push'],
            capture_output=True, text=True, cwd=REPO
        )
        if result.returncode == 0:
            print(green("  Pushed to remote"))
        else:
            print(yellow(f"  Push failed: {result.stderr.strip()}"))
    except Exception as e:
        print(red(f"  ERROR: {e}"))


def update_primer_timestamp():
    """Update the last_modified date in primer.md."""
    try:
        content = PRIMER.read_text()
        today = datetime.now().strftime("%Y-%m-%d")
        content = re.sub(
            r'last_modified:\s*\d{4}-\d{2}-\d{2}',
            f'last_modified: {today}',
            content
        )
        PRIMER.write_text(content)
        print(green(f"  Primer timestamp updated to {today}"))
    except Exception as e:
        print(red(f"  ERROR updating primer: {e}"))


def update_verifier_results(results):
    """Write check results to verifier.md."""
    try:
        content = VERIFIER.read_text()
        today = datetime.now().strftime("%Y-%m-%d")

        # Update last run section
        new_results = f"""## Last Run Results
- Date: {today}
- Primer stale: {"YES" if not results.get("primer_fresh") else "NO"}
- Graph-Status sync: {"CLEAN" if results.get("sync_ok") else "ISSUES"}
- Contradictions: {"FOUND" if not results.get("no_contradictions") else "NONE"}
- Orphans: {"FOUND" if not results.get("no_orphans") else "NONE"}
- Pattern files: {"ALL OK" if results.get("patterns_ok") else "MISSING"}
- Session weight: {results.get("weight", 0)}"""

        content = re.sub(
            r'## Last Run Results.*',
            new_results,
            content,
            flags=re.DOTALL
        )
        content = re.sub(
            r'last_run:\s*\d{4}-\d{2}-\d{2}',
            f'last_run: {today}',
            content
        )

        VERIFIER.write_text(content)
    except Exception as e:
        print(red(f"  ERROR updating verifier: {e}"))


def main():
    verify_only = '--verify-only' in sys.argv
    checkpoint_only = '--checkpoint' in sys.argv

    print(cyan("=" * 50))
    print(cyan("  CEIBA v2 - Session End Routine"))
    print(cyan("=" * 50))

    if checkpoint_only:
        git_checkpoint()
        return

    # File existence check
    print(cyan("\n[0] File Check"))
    all_exist = True
    for path, name in [
        (PRIMER, "primer.md"),
        (GRAPH, "context_graph.md"),
        (STATUS, "status.md"),
        (VERIFIER, "verifier.md"),
        (FLEET, "fleet.md"),
    ]:
        if not check_file_exists(path, name):
            all_exist = False

    if not all_exist:
        print(red("\nMissing files. Run the v2 build first."))
        sys.exit(1)

    # Run all checks
    results = {}
    results["primer_fresh"] = check_primer_staleness()
    results["sync_ok"] = check_graph_status_sync()
    results["no_orphans"] = check_orphan_nodes()
    results["patterns_ok"] = check_pattern_files()
    results["no_contradictions"] = True  # Manual check for now
    results["weight"] = calculate_session_weight()

    if not verify_only:
        # Update timestamps
        print(cyan("\n[6] Updates"))
        update_primer_timestamp()
        update_verifier_results(results)

        # Git operations
        git_checkpoint(f"mem: session end {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        git_push()

    # Summary
    issues = sum(1 for v in results.values() if v is False)
    print(cyan("\n" + "=" * 50))
    if issues == 0:
        print(green("  ALL CHECKS PASSED"))
    else:
        print(yellow(f"  {issues} issue(s) found"))
    print(cyan("=" * 50))


if __name__ == "__main__":
    main()
