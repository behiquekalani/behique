#!/usr/bin/env python3
"""
Vault Self-Healer — Auto-detect and fix stale/broken vault links

Scans the vault graph for:
  1. Missing targets (nodes referenced but no file exists)
  2. Orphan nodes (files with zero connections)
  3. Stale links (files that link to moved/renamed targets)
  4. Duplicate names (case-insensitive collisions)
  5. Missing frontmatter (files without YAML header)

Actions:
  --report     Show all issues (default)
  --fix        Auto-create stub files for missing targets
  --fix-orphans  Add orphans to HOME.md or nearest hub

Usage:
    python3 vault_healer.py                # full report
    python3 vault_healer.py --fix          # auto-fix missing targets
    python3 vault_healer.py --json         # machine-readable
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

BEHIQUE = os.path.expanduser("~/behique")
CEIBA = os.path.join(BEHIQUE, "Ceiba")
VAULT_GRAPH = os.path.join(CEIBA, "vault_graph.json")


def load_graph():
    """Load vault graph data."""
    if not os.path.exists(VAULT_GRAPH):
        print("❌ vault_graph.json not found. Run: python3 tools/vault_grapher.py")
        sys.exit(1)
    with open(VAULT_GRAPH) as f:
        return json.load(f)


def scan_missing_targets(data):
    """Find nodes referenced in edges but with no vault file."""
    nodes = set(data.get("nodes", {}).keys())
    all_refs = set()
    for edge in data.get("edges", []):
        if isinstance(edge, list) and len(edge) == 2:
            all_refs.add(edge[0])
            all_refs.add(edge[1])
    missing = all_refs - nodes

    # Filter out junk references (common parsing artifacts)
    junk = {"wiki link", "wiki links", "links", "link"}
    real_missing = sorted(m for m in missing if m.lower() not in junk)
    junk_found = sorted(m for m in missing if m.lower() in junk)

    return real_missing, junk_found


def scan_orphans(data):
    """Find nodes with zero connections."""
    nodes = data.get("nodes", {})
    adjacency = defaultdict(set)
    reverse = defaultdict(set)
    for edge in data.get("edges", []):
        if isinstance(edge, list) and len(edge) == 2:
            adjacency[edge[0]].add(edge[1])
            reverse[edge[1]].add(edge[0])

    orphans = []
    for name in nodes:
        if not adjacency.get(name) and not reverse.get(name):
            orphans.append(name)
    return sorted(orphans)


def scan_duplicates(data):
    """Find case-insensitive name collisions."""
    nodes = data.get("nodes", {})
    lower_map = defaultdict(list)
    for name in nodes:
        lower_map[name.lower()].append(name)

    dupes = {k: v for k, v in lower_map.items() if len(v) > 1}
    return dupes


def scan_missing_frontmatter(data):
    """Find vault files without YAML frontmatter."""
    nodes = data.get("nodes", {})
    missing_fm = []
    for name, info in nodes.items():
        path = info.get("path", "")
        if not path:
            continue
        full_path = os.path.join(BEHIQUE, path) if not os.path.isabs(path) else path
        if not os.path.exists(full_path):
            continue
        try:
            with open(full_path) as f:
                first_line = f.readline().strip()
            if first_line != "---":
                missing_fm.append((name, path))
        except Exception:
            pass
    return missing_fm


def scan_dead_links(data):
    """Find nodes whose file no longer exists on disk."""
    nodes = data.get("nodes", {})
    dead = []
    for name, info in nodes.items():
        path = info.get("path", "")
        if not path:
            continue
        full_path = os.path.join(BEHIQUE, path) if not os.path.isabs(path) else path
        if not os.path.exists(full_path):
            dead.append((name, path))
    return dead


def fix_missing_targets(missing, data):
    """Create stub files for missing targets."""
    created = 0
    nodes = data.get("nodes", {})

    # Determine type from name prefix
    type_map = {
        "DEC_": ("decision", "04-Patterns/decisions"),
        "PAT_": ("pattern", "04-Patterns"),
        "SYS_": ("system", "06-Designs"),
        "TOOL_": ("tool", "05-Knowledge/tools"),
        "SES_": ("session", "06-Sessions"),
    }

    for name in missing:
        # Skip names that look like file extensions or code
        if "." in name and not name.endswith(".md"):
            continue

        # Determine type and location
        node_type = "note"
        subdir = "05-Knowledge"
        for prefix, (ntype, ndir) in type_map.items():
            if name.startswith(prefix):
                node_type = ntype
                subdir = ndir
                break

        dir_path = os.path.join(CEIBA, subdir)
        os.makedirs(dir_path, exist_ok=True)

        filename = name if name.endswith(".md") else f"{name}.md"
        filepath = os.path.join(dir_path, filename)

        if os.path.exists(filepath):
            continue

        content = f"""---
title: "{name}"
type: {node_type}
tags: [auto-generated, needs-review]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {name}

> Auto-generated stub by vault_healer.py. Needs content.
"""
        with open(filepath, "w") as f:
            f.write(content)
        created += 1
        print(f"  ✅ Created: {subdir}/{filename}")

    return created


def fix_missing_frontmatter(no_fm, data):
    """Add YAML frontmatter to files that lack it."""
    fixed = 0
    nodes = data.get("nodes", {})

    # Type detection from path
    type_from_path = {
        "01-Projects": "project",
        "02-Goals": "goal",
        "03-Check-ins": "check-in",
        "04-Patterns": "pattern",
        "05-Knowledge": "knowledge",
        "06-Designs": "design",
        "06-Sessions": "session",
        "07-Transcripts": "transcript",
        "08-Images": "image-ref",
    }

    for name, rel_path in no_fm:
        full_path = os.path.join(BEHIQUE, rel_path) if not os.path.isabs(rel_path) else rel_path
        if not os.path.exists(full_path):
            continue

        # Detect type from path
        node_type = "note"
        for folder, ntype in type_from_path.items():
            if folder in rel_path:
                node_type = ntype
                break

        # Also check node data
        node_data = nodes.get(name, {})
        if node_data.get("type"):
            node_type = node_data["type"]

        try:
            with open(full_path) as f:
                content = f.read()

            # Extract tags from content (words after # headers)
            tags = []
            for line in content.split("\n")[:10]:
                if line.startswith("# "):
                    words = line[2:].lower().split()
                    tags.extend(w for w in words[:3] if len(w) > 2)

            frontmatter = f"""---
title: "{name}"
type: {node_type}
tags: [{', '.join(tags[:5])}]
created: {datetime.now().strftime('%Y-%m-%d')}
---

"""
            with open(full_path, "w") as f:
                f.write(frontmatter + content)

            fixed += 1
        except Exception as e:
            print(f"    ⚠️ Could not fix {name}: {e}")

    return fixed


def generate_report(data):
    """Generate comprehensive vault health report."""
    missing, junk = scan_missing_targets(data)
    orphans = scan_orphans(data)
    dupes = scan_duplicates(data)
    dead = scan_dead_links(data)
    no_fm = scan_missing_frontmatter(data)

    nodes = data.get("nodes", {})
    edges = data.get("edges", [])

    total_issues = len(missing) + len(orphans) + len(dupes) + len(dead) + len(no_fm)

    # Health score
    node_count = len(nodes)
    if node_count == 0:
        health = 0
    else:
        issue_ratio = total_issues / node_count
        health = max(0, min(100, int(100 - issue_ratio * 50)))

    report = {
        "timestamp": datetime.now().isoformat(),
        "health_score": health,
        "nodes": node_count,
        "edges": len(edges),
        "total_issues": total_issues,
        "missing_targets": missing,
        "junk_references": junk,
        "orphan_nodes": orphans,
        "duplicate_names": dupes,
        "dead_links": dead,
        "missing_frontmatter": no_fm,
    }

    return report


def print_report(report):
    """Pretty-print the health report."""
    health = report["health_score"]
    emoji = "💚" if health >= 80 else "💛" if health >= 60 else "🔴"

    print()
    print("╔══════════════════════════════════════════════╗")
    print(f"║  🏥 Vault Health Report                      ║")
    print(f"║  {emoji} Health Score: {health}/100                    ║")
    print("╚══════════════════════════════════════════════╝")

    print(f"\n  📊 {report['nodes']} nodes, {report['edges']} edges, {report['total_issues']} issues")

    # Missing targets
    missing = report["missing_targets"]
    if missing:
        print(f"\n  ❌ Missing Targets ({len(missing)}):")
        for m in missing[:15]:
            print(f"     • {m}")
        if len(missing) > 15:
            print(f"     ... and {len(missing) - 15} more")
    else:
        print(f"\n  ✅ No missing targets")

    # Junk references
    junk = report["junk_references"]
    if junk:
        print(f"\n  🗑️  Junk References ({len(junk)}): {', '.join(junk)}")

    # Orphans
    orphans = report["orphan_nodes"]
    if orphans:
        print(f"\n  🏝️  Orphan Nodes ({len(orphans)}):")
        for o in orphans[:10]:
            print(f"     • {o}")
        if len(orphans) > 10:
            print(f"     ... and {len(orphans) - 10} more")
    else:
        print(f"\n  ✅ No orphan nodes")

    # Duplicates
    dupes = report["duplicate_names"]
    if dupes:
        print(f"\n  ⚠️  Name Collisions ({len(dupes)}):")
        for lower_name, names in dupes.items():
            print(f"     • {' vs '.join(names)}")
    else:
        print(f"\n  ✅ No name collisions")

    # Dead links
    dead = report["dead_links"]
    if dead:
        print(f"\n  💀 Dead Links ({len(dead)}):")
        for name, path in dead[:10]:
            print(f"     • {name} → {path}")
    else:
        print(f"\n  ✅ No dead links")

    # Missing frontmatter
    no_fm = report["missing_frontmatter"]
    if no_fm:
        print(f"\n  📝 Missing Frontmatter ({len(no_fm)}):")
        for name, path in no_fm[:10]:
            print(f"     • {name}")
        if len(no_fm) > 10:
            print(f"     ... and {len(no_fm) - 10} more")

    print(f"\n  {'─' * 40}")
    if report["total_issues"] > 0:
        print(f"  Run with --fix to auto-create missing target stubs")
    else:
        print(f"  ✅ Vault is healthy!")
    print()


def main():
    parser = argparse.ArgumentParser(description="Vault Self-Healer")
    parser.add_argument("--fix", action="store_true", help="Auto-fix missing targets")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    data = load_graph()
    report = generate_report(data)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return

    print_report(report)

    if args.fix:
        missing = report["missing_targets"]
        fixed_total = 0
        if missing:
            print(f"\n  🔧 Auto-fixing {len(missing)} missing targets...")
            created = fix_missing_targets(missing, data)
            fixed_total += created
            print(f"  Created {created} stub files")

        no_fm = report["missing_frontmatter"]
        if no_fm:
            print(f"\n  🔧 Adding frontmatter to {len(no_fm)} files...")
            added = fix_missing_frontmatter(no_fm, data)
            fixed_total += added
            print(f"  Added frontmatter to {added} files")

        if fixed_total > 0:
            print(f"\n  ✅ Fixed {fixed_total} issues. Run vault_grapher.py to rebuild graph")
        else:
            print(f"\n  ✅ Nothing to fix!")


if __name__ == "__main__":
    main()
