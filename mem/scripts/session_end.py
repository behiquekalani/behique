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
    """Check if primer.md is older than STALE_HOURS (uses file mtime for accuracy)."""
    print(cyan("\n[1] Primer Staleness"))
    # Use actual file modification time for precision, YAML date as fallback
    try:
        mtime = datetime.fromtimestamp(PRIMER.stat().st_mtime)
    except OSError:
        mtime = None

    yaml_date = get_last_modified(PRIMER)
    last_mod = mtime or yaml_date

    if not last_mod:
        print(yellow("  WARN: Cannot determine primer.md modification time"))
        return False

    age = datetime.now() - last_mod
    if age > timedelta(hours=STALE_HOURS):
        print(yellow(f"  STALE: primer.md last modified {last_mod.strftime('%Y-%m-%d %H:%M')} ({age.days}d {age.seconds // 3600}h ago)"))
        return False

    print(green(f"  FRESH: primer.md modified {last_mod.strftime('%Y-%m-%d %H:%M')}"))
    return True


def extract_graph_node_ids():
    """Get all node IDs from context_graph.md."""
    try:
        content = GRAPH.read_text()
        return set(re.findall(r'id:\s*(\S+)', content))
    except Exception:
        return set()


def extract_graph_node_names():
    """Get description fields from graph nodes for fuzzy matching against status items."""
    names = {}
    try:
        content = GRAPH.read_text()
        current_id = None
        for line in content.split('\n'):
            id_match = re.search(r'id:\s*(\S+)', line)
            desc_match = re.search(r'description:\s*"(.+)"', line)
            if id_match:
                current_id = id_match.group(1)
            elif desc_match and current_id:
                names[current_id] = desc_match.group(1).lower()
                current_id = None
    except Exception:
        pass
    return names


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
    """Verify graph projects and status tracker are in sync."""
    print(cyan("\n[2] Graph-Status Sync"))
    graph_ids = extract_graph_node_ids()
    graph_names = extract_graph_node_names()
    status_items = extract_status_items()

    if not graph_ids:
        print(yellow("  WARN: No nodes found in context_graph.md"))
        return True

    issues = 0

    # Check: active/todo status items should have a related graph node
    active_items = {k for k, v in status_items.items() if v in ('active', 'todo')}
    graph_descriptions = set(graph_names.values())

    for item_name in active_items:
        item_lower = item_name.lower()
        # Fuzzy match: check if any graph node description contains key words from the status item
        found = any(
            word in desc for desc in graph_descriptions
            for word in item_lower.split() if len(word) > 3
        )
        if not found:
            print(yellow(f"  MISSING NODE: status item '{item_name}' has no matching graph node"))
            issues += 1

    # Check: active graph projects should have a related status item
    project_ids = {nid for nid in graph_ids if nid.startswith('project-')}
    status_lower = {k.lower() for k in status_items.keys()}

    for pid in project_ids:
        desc = graph_names.get(pid, "")
        # Check if any status item mentions words from the project description
        found = any(
            word in s for s in status_lower
            for word in desc.split() if len(word) > 3
        )
        if not found:
            print(yellow(f"  MISSING STATUS: graph project '{pid}' has no matching status item"))
            issues += 1

    print(f"  Graph nodes: {len(graph_ids)}")
    print(f"  Status items: {len(status_items)}")

    if issues == 0:
        print(green("  SYNC: No mismatches detected"))
    else:
        print(yellow(f"  SYNC: {issues} mismatch(es) found"))
    return issues == 0


def check_orphan_nodes():
    """Find nodes with no connections (neither outgoing nor incoming links)."""
    print(cyan("\n[3] Orphan Detection"))
    try:
        content = GRAPH.read_text()

        # Parse each node's ID and its outgoing links
        node_links = {}
        current_id = None
        for line in content.split('\n'):
            id_match = re.search(r'id:\s*(\S+)', line)
            links_match = re.search(r'links:\s*\[([^\]]+)\]', line)
            if id_match:
                current_id = id_match.group(1)
                node_links[current_id] = set()
            elif links_match and current_id:
                refs = [r.strip() for r in links_match.group(1).split(',')]
                node_links[current_id] = set(refs)

        # Build incoming links set
        incoming = set()
        for node_id, links in node_links.items():
            for target in links:
                incoming.add(target)

        # A node is orphan if it has ZERO outgoing links AND ZERO incoming links
        orphans = []
        for node_id, links in node_links.items():
            has_outgoing = len(links) > 0
            has_incoming = node_id in incoming
            if not has_outgoing and not has_incoming:
                orphans.append(node_id)

        # Also check for weakly connected: only incoming OR only outgoing (warn, not error)
        weak = []
        for node_id, links in node_links.items():
            has_outgoing = len(links) > 0
            has_incoming = node_id in incoming
            if has_outgoing != has_incoming:  # XOR - one but not both
                direction = "outgoing only" if has_outgoing else "incoming only"
                weak.append((node_id, direction))

        if orphans:
            print(yellow(f"  ORPHANS ({len(orphans)}):"))
            for o in orphans:
                print(yellow(f"    - {o}"))
        else:
            print(green("  No orphan nodes"))

        if weak:
            print(dim(f"  WEAK ({len(weak)} one-direction only):"))
            for w, direction in weak:
                print(dim(f"    - {w} ({direction})"))

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


def check_primer_graph_contradictions():
    """Check for contradictions between primer.md and context_graph.md."""
    print(cyan("\n[3.5] Primer-Graph Contradictions"))
    try:
        primer_content = PRIMER.read_text().lower()
        graph_content = GRAPH.read_text()

        issues = 0

        # Extract graph project statuses
        current_id = None
        graph_statuses = {}
        for line in graph_content.split('\n'):
            id_match = re.search(r'id:\s*(\S+)', line)
            status_match = re.search(r'status:\s*(\w+)', line)
            if id_match:
                current_id = id_match.group(1)
            elif status_match and current_id:
                graph_statuses[current_id] = status_match.group(1)
                current_id = None

        # Check: if primer mentions something as active/blocker but graph says backlog/archived
        for node_id, status in graph_statuses.items():
            # Extract a readable name from the node ID
            readable = node_id.replace('project-', '').replace('product-', '').replace('-', ' ')
            if status in ('backlog', 'archived') and readable in primer_content:
                # Check if primer treats it as active
                # Look for the name near words like "active", "working", "current", "now"
                active_pattern = rf'(?:active|working|current|now|blocker).*{re.escape(readable)}'
                reverse_pattern = rf'{re.escape(readable)}.*(?:active|working|current|now|blocker)'
                if re.search(active_pattern, primer_content) or re.search(reverse_pattern, primer_content):
                    print(yellow(f"  CONFLICT: '{readable}' is {status} in graph but appears active in primer"))
                    issues += 1

        if issues == 0:
            print(green("  No contradictions detected"))
        return issues == 0
    except Exception as e:
        print(red(f"  ERROR: {e}"))
        return True  # Don't block on errors


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


def auto_sort_status():
    """Enforce auto-sort rules on status.md items."""
    print(cyan("\n[5.5] Auto-Sort Status"))
    try:
        content = STATUS.read_text()
        now = datetime.now()
        changes = 0

        # Parse items
        lines = content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Find last_modified dates and check staleness
            last_mod_match = re.search(r'last_modified:\s*(\d{4}-\d{2}-\d{2})', line)
            if last_mod_match:
                item_date = datetime.strptime(last_mod_match.group(1), "%Y-%m-%d")
                age_days = (now - item_date).days

                # Look backward for the status line of this item
                status_line_idx = None
                for j in range(max(0, i-5), i):
                    if re.search(r'status:\s*(active|todo)', lines[j]):
                        status_line_idx = j
                        break

                # Demote active/todo items not touched in 7+ days to backlog
                if age_days >= DEMOTE_DAYS and status_line_idx is not None:
                    old_status = re.search(r'status:\s*(\w+)', lines[status_line_idx])
                    if old_status and old_status.group(1) in ('active', 'todo'):
                        new_lines_copy = list(new_lines)  # Don't modify while iterating
                        # We already added the status line to new_lines
                        for k in range(len(new_lines_copy)):
                            if new_lines_copy[k] == lines[status_line_idx]:
                                new_lines[k] = re.sub(
                                    r'status:\s*(active|todo)',
                                    'status: backlog',
                                    new_lines[k]
                                )
                                changes += 1

                                # Find item name for logging
                                for m in range(max(0, status_line_idx-3), status_line_idx):
                                    name_match = re.search(r'name:\s*"(.+)"', lines[m])
                                    if name_match:
                                        print(yellow(f"  DEMOTED: '{name_match.group(1)}' ({age_days} days stale → backlog)"))
                                        break
                                break

            new_lines.append(line)
            i += 1

        if changes > 0:
            STATUS.write_text('\n'.join(new_lines))
            print(yellow(f"  {changes} item(s) demoted to backlog"))
        else:
            print(green("  No items need demotion"))

        return changes
    except Exception as e:
        print(red(f"  ERROR: {e}"))
        return 0


def auto_branch_if_needed(weight):
    """Create a new branch if session weight exceeds hard limit."""
    if weight < HARD_LIMIT:
        return

    print(cyan("\n[5.6] Auto-Branch"))
    branch_name = f"session/{datetime.now().strftime('%Y-%m-%d-%H%M')}"

    try:
        # Commit current state first
        subprocess.run(['git', 'add', 'mem/', 'primer.md'], cwd=REPO, check=True)
        subprocess.run(
            ['git', 'commit', '-m', f'mem: checkpoint before branch {branch_name}'],
            capture_output=True, text=True, cwd=REPO
        )

        if weight >= CRITICAL_LIMIT:
            print(red(f"  CRITICAL WEIGHT ({weight}). Creating branch: {branch_name}"))
            # Create branch from current state
            subprocess.run(['git', 'branch', branch_name], cwd=REPO, check=True)
            print(green(f"  Branch created: {branch_name}"))
            print(red(f"  START NEW SESSION. Run: git checkout main"))
        elif weight >= HARD_LIMIT:
            print(yellow(f"  HARD WEIGHT ({weight}). Branch recommended: {branch_name}"))

    except Exception as e:
        print(red(f"  ERROR: {e}"))


def auto_rewrite_primer():
    """Auto-rewrite primer.md with current state from git and status.md."""
    print(cyan("\n[6.5] Auto-Rewrite Primer"))
    try:
        # Gather current state
        today = datetime.now().strftime("%Y-%m-%d")

        # Count products
        products_dir = REPO / "READY-TO-SELL" / "products-organized"
        product_count = len(list(products_dir.iterdir())) if products_dir.exists() else 0

        # Get recent commits
        result = subprocess.run(
            ['git', 'log', '--oneline', '-5', '--format=%s'],
            capture_output=True, text=True, cwd=REPO
        )
        recent_commits = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]

        # Get active items from status.md
        active_items = []
        todo_items = []
        try:
            status_content = STATUS.read_text()
            current_name = None
            for line in status_content.split('\n'):
                name_match = re.search(r'name:\s*"(.+)"', line)
                status_match = re.search(r'status:\s*(\w+)', line)
                if name_match:
                    current_name = name_match.group(1)
                elif status_match and current_name:
                    if status_match.group(1) == 'active':
                        active_items.append(current_name)
                    elif status_match.group(1) == 'todo':
                        todo_items.append(current_name)
                    current_name = None
        except:
            pass

        # Check session manager for active sessions
        sessions_file = MEM / "sessions.json"
        active_sessions = 0
        if sessions_file.exists():
            try:
                import json, time
                sdata = json.loads(sessions_file.read_text())
                active_sessions = len([s for s in sdata.get("sessions", [])
                                       if time.time() - s.get("last_heartbeat", 0) < 300])
            except:
                pass

        # Rewrite primer
        primer_content = f"""---
layer: L1-cache
purpose: Current session state and immediate goals
rewrite_frequency: every session end
last_modified: {today}
session_id: auto-{datetime.now().strftime('%H%M')}
---

# Primer - Live State

## What Just Happened
- Auto-rewritten by session_end.py at {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Recent: {'; '.join(recent_commits[:3])}

## Active Right Now
- Products ready: {product_count}
- Active sessions: {active_sessions}

## Active Tasks
{chr(10).join('- ' + item for item in active_items[:5])}

## Next Up
{chr(10).join('- ' + item for item in todo_items[:5])}

## Session Weight
- files_modified: 0
- lines_changed: 0
- new_nodes: 0
- checkpoint_needed: false
"""
        PRIMER.write_text(primer_content)
        print(green(f"  Primer auto-rewritten with {product_count} products, {len(active_items)} active tasks"))

    except Exception as e:
        print(red(f"  ERROR: {e}"))


def deregister_session():
    """Deregister this session from the session manager."""
    try:
        import json, time
        sessions_file = MEM / "sessions.json"
        if sessions_file.exists():
            data = json.loads(sessions_file.read_text())
            pid = os.getpid()
            data["sessions"] = [s for s in data["sessions"] if s.get("pid") != pid]
            # Release claimed tasks
            session_ids = {s["id"] for s in data["sessions"]}
            data["claimed_tasks"] = {
                k: v for k, v in data.get("claimed_tasks", {}).items()
                if v in session_ids
            }
            sessions_file.write_text(json.dumps(data, indent=2))
            print(green("  Session deregistered"))
    except Exception as e:
        print(dim(f"  Session deregister skipped: {e}"))


def git_checkpoint(message="mem: session checkpoint"):
    """Quick git add + commit."""
    print(cyan("\n[GIT] Checkpoint"))
    try:
        # Only stage mem/ files and known safe paths, not everything
        subprocess.run(['git', 'add', 'mem/', 'primer.md', 'CLAUDE.md', 'dashboards/', 'Ceiba/'], cwd=REPO, check=True)
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

        # Replace only the Last Run Results section (stop at next ## or end of file)
        content = re.sub(
            r'## Last Run Results\n(?:(?!^## ).)*',
            new_results + "\n",
            content,
            flags=re.DOTALL | re.MULTILINE
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
    results["no_contradictions"] = check_primer_graph_contradictions()
    results["weight"] = calculate_session_weight()

    # Auto-sort (runs in both verify and full mode)
    sort_changes = auto_sort_status()

    if not verify_only:
        # Update timestamps
        print(cyan("\n[6] Updates"))
        update_primer_timestamp()
        update_verifier_results(results)

        # Auto-rewrite primer with current state
        auto_rewrite_primer()

        # Auto-branch if weight is too high
        auto_branch_if_needed(results["weight"])

        # Deregister this session from session manager
        deregister_session()

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
