#!/usr/bin/env python3
"""
vault_grapher.py — Obsidian Vault Graph Builder for Ceiba
Parses wiki links, builds relationship map, generates VAULT_GRAPH.md

Usage:
    python3 vault_grapher.py              # Full scan + generate graph index
    python3 vault_grapher.py --orphans    # Show only orphan nodes
    python3 vault_grapher.py --missing    # Show links that point to non-existent files
    python3 vault_grapher.py --stats      # Quick stats only

Output:
    ~/behique/Ceiba/VAULT_GRAPH.md   (auto-generated graph index)
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────────

VAULT_ROOT = Path(os.path.expanduser("~/behique"))
CEIBA_DIR = VAULT_ROOT / "Ceiba"
OUTPUT_FILE = CEIBA_DIR / "VAULT_GRAPH.md"

# Directories to scan for .md files
SCAN_DIRS = [
    CEIBA_DIR,
    VAULT_ROOT / "ai_cluster",
    VAULT_ROOT / "bridge",
    VAULT_ROOT / "tools",
]

# Also scan these specific root files
SCAN_FILES = [
    VAULT_ROOT / "primer.md",
    VAULT_ROOT / "CLAUDE.md",
    VAULT_ROOT / "project_memory.md",
]

# Node type prefixes (from ChatGPT's design)
PREFIXES = {
    "PRJ_": "project",
    "TOOL_": "tool",
    "PAT_": "pattern",
    "DEC_": "decision",
    "SES_": "session",
    "SYS_": "system",
    "MEM_": "memory",
    "CAP_": "capability",
}

# Known entity mapping (current filenames → typed names)
# This helps during the transition from old names to new prefixed names
ENTITY_MAP = {
    # Projects
    "eBay-Listing-Assistant": "PRJ_Ebay_Listing_Assistant",
    "BehiqueBot": "PRJ_BehiqueBot",
    "n8n-Agency": "PRJ_n8n_Agency",
    "Google-Trends-Scraper": "PRJ_Google_Trends_Scraper",
    "Shopify-Store": "PRJ_Shopify_Store",
    "News-Intelligence-Bots": "PRJ_News_Intelligence_Bots",
    "MISSIONS": "PRJ_MISSIONS",
    # Tools
    "trends_scraper": "TOOL_Trends_Scraper",
    "ceiba_lite": "TOOL_Ceiba_Lite",
    "dispatch": "TOOL_Dispatch",
    "agent_kernel": "TOOL_Agent_Kernel",
    "notify": "TOOL_Notify_Relay",
    # System
    "architecture-spine": "SYS_Architecture_Spine",
    "VAULT_INDEX": "SYS_Vault_Index",
    # Identity
    "Kalani": "CAP_Kalani_Profile",
    "Psychologist-Framework": "CAP_Psychologist_Framework",
    # Goals
    "Q3-2026": "PRJ_Q3_2026_Target",
    "North-Star": "PRJ_North_Star",
    # Patterns
    "observations": "PAT_Observations",
}

# ── SCANNER ────────────────────────────────────────────────────────────────────

WIKI_LINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')


def scan_vault():
    """Scan all markdown files and extract wiki links."""
    files = {}  # filename (no ext) → {path, links_out, links_in, tags, type}

    # Collect all .md files
    all_paths = []
    for scan_dir in SCAN_DIRS:
        if scan_dir.exists():
            all_paths.extend(scan_dir.rglob("*.md"))
    for f in SCAN_FILES:
        if f.exists():
            all_paths.append(f)

    # Parse each file
    for path in all_paths:
        name = path.stem
        rel_path = str(path.relative_to(VAULT_ROOT))

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Extract wiki links
        links = WIKI_LINK_RE.findall(content)

        # Extract tags from YAML frontmatter or inline
        tags = []
        tag_matches = re.findall(r'tags:\s*\[([^\]]+)\]', content)
        if tag_matches:
            for match in tag_matches:
                tags.extend([t.strip() for t in match.split(",")])
        inline_tags = re.findall(r'#(\w+)', content)
        tags.extend(inline_tags)

        # Detect node type from prefix or folder
        node_type = "unknown"
        for prefix, ntype in PREFIXES.items():
            if name.startswith(prefix):
                node_type = ntype
                break
        if node_type == "unknown":
            # Infer from folder
            if "01-Projects" in rel_path or "Projects" in rel_path:
                node_type = "project"
            elif "02-Goals" in rel_path:
                node_type = "goal"
            elif "03-Check-ins" in rel_path:
                node_type = "session"
            elif "04-Patterns" in rel_path:
                node_type = "pattern"
            elif "05-Knowledge" in rel_path:
                node_type = "knowledge"
            elif "06-Sessions" in rel_path:
                node_type = "session"
            elif "00-Identity" in rel_path:
                node_type = "identity"
            elif "tools" in rel_path:
                node_type = "tool"
            elif "bridge" in rel_path:
                node_type = "system"
            elif "ai_cluster" in rel_path:
                node_type = "system"

        files[name] = {
            "path": rel_path,
            "links_out": links,
            "links_in": [],  # populated below
            "tags": list(set(tags)),
            "type": node_type,
            "word_count": len(content.split()),
        }

    # Build backlinks
    for name, data in files.items():
        for link in data["links_out"]:
            # Normalize link target
            target = link.split("/")[-1]  # handle path-based links
            target = target.split("#")[0]  # handle section links
            if target in files:
                files[target]["links_in"].append(name)

    return files


def find_orphans(files):
    """Files with no incoming or outgoing links."""
    return [
        name for name, data in files.items()
        if not data["links_out"] and not data["links_in"]
    ]


def find_missing_targets(files):
    """Links that point to files that don't exist."""
    missing = defaultdict(list)
    all_names = set(files.keys())
    for name, data in files.items():
        for link in data["links_out"]:
            target = link.split("/")[-1].split("#")[0]
            if target not in all_names:
                missing[target].append(name)
    return dict(missing)


def find_hubs(files, min_links=3):
    """Files with the most connections (in + out)."""
    scored = []
    for name, data in files.items():
        total = len(set(data["links_out"])) + len(set(data["links_in"]))
        if total >= min_links:
            scored.append((name, total, data["type"], data["path"]))
    scored.sort(key=lambda x: -x[1])
    return scored


def type_stats(files):
    """Count files by type."""
    counts = defaultdict(int)
    for data in files.values():
        counts[data["type"]] += 1
    return dict(counts)

# ── GRAPH INDEX GENERATOR ──────────────────────────────────────────────────────


def generate_graph_index(files):
    """Generate VAULT_GRAPH.md — the auto-generated graph index."""
    orphans = find_orphans(files)
    missing = find_missing_targets(files)
    hubs = find_hubs(files)
    stats = type_stats(files)
    total_links = sum(len(d["links_out"]) for d in files.values())

    lines = []
    lines.append("# VAULT_GRAPH — Auto-Generated Knowledge Graph Index")
    lines.append(f"<!-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} by vault_grapher.py -->")
    lines.append(f"<!-- DO NOT EDIT — this file is regenerated automatically -->")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"- **Total files:** {len(files)}")
    lines.append(f"- **Total links:** {total_links}")
    lines.append(f"- **Orphan nodes:** {len(orphans)}")
    lines.append(f"- **Missing targets:** {len(missing)}")
    lines.append("")

    # Type breakdown
    lines.append("## Nodes by Type")
    for ntype, count in sorted(stats.items(), key=lambda x: -x[1]):
        lines.append(f"- **{ntype}:** {count}")
    lines.append("")

    # Top connected nodes
    lines.append("## Top Connected Nodes")
    for name, count, ntype, path in hubs[:15]:
        lines.append(f"- [[{name}]] — {count} links ({ntype}) `{path}`")
    lines.append("")

    # Orphan nodes (need links)
    if orphans:
        lines.append("## Orphan Nodes (no links in or out)")
        for name in orphans:
            data = files[name]
            lines.append(f"- [[{name}]] ({data['type']}) `{data['path']}`")
        lines.append("")

    # Missing targets (broken links)
    if missing:
        lines.append("## Missing Targets (links to non-existent files)")
        for target, sources in sorted(missing.items()):
            src_str = ", ".join(f"[[{s}]]" for s in sources[:3])
            lines.append(f"- **{target}** ← linked from {src_str}")
        lines.append("")

    # Files by type with links
    lines.append("## Full Graph")
    by_type = defaultdict(list)
    for name, data in files.items():
        by_type[data["type"]].append((name, data))

    for ntype in sorted(by_type.keys()):
        items = by_type[ntype]
        lines.append(f"\n### {ntype.upper()} ({len(items)})")
        for name, data in sorted(items, key=lambda x: x[0]):
            out_count = len(data["links_out"])
            in_count = len(data["links_in"])
            lines.append(f"- [[{name}]] → {out_count} out, {in_count} in `{data['path']}`")

    return "\n".join(lines)

# ── CLI ────────────────────────────────────────────────────────────────────────


def main():
    files = scan_vault()

    if "--orphans" in sys.argv:
        orphans = find_orphans(files)
        print(f"Orphan nodes ({len(orphans)}):")
        for name in orphans:
            print(f"  {name} — {files[name]['path']}")
        return

    if "--missing" in sys.argv:
        missing = find_missing_targets(files)
        print(f"Missing targets ({len(missing)}):")
        for target, sources in missing.items():
            print(f"  {target} ← {', '.join(sources)}")
        return

    if "--stats" in sys.argv:
        stats = type_stats(files)
        total_links = sum(len(d["links_out"]) for d in files.values())
        orphans = find_orphans(files)
        print(f"Files: {len(files)} | Links: {total_links} | Orphans: {len(orphans)}")
        for ntype, count in sorted(stats.items(), key=lambda x: -x[1]):
            print(f"  {ntype}: {count}")
        return

    if "--json" in sys.argv:
        # Output graph as JSON for dashboards and other consumers
        nodes = {}
        edges = []
        for name, data in files.items():
            nodes[name] = {
                "type": data["type"],
                "path": data["path"],
                "links": data["links_out"],
                "tags": data["tags"],
                "word_count": data["word_count"],
            }
            for link in data["links_out"]:
                target = link.split("/")[-1].split("#")[0]
                edges.append([name, target])
        graph_json = {
            "generated": datetime.now().isoformat(),
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_files": len(files),
                "total_links": sum(len(d["links_out"]) for d in files.values()),
                "orphans": len(find_orphans(files)),
                "missing_targets": len(find_missing_targets(files)),
            }
        }
        json_path = CEIBA_DIR / "vault_graph.json"
        json_path.write_text(json.dumps(graph_json, indent=2))
        print(f"JSON graph written to {json_path}")
        return

    # Full run — generate graph index + JSON
    print(f"Scanning vault at {VAULT_ROOT}...")
    print(f"Found {len(files)} files")

    graph_md = generate_graph_index(files)
    OUTPUT_FILE.write_text(graph_md)
    print(f"Graph index written to {OUTPUT_FILE}")

    # Always output JSON alongside markdown on full runs
    nodes = {}
    edges = []
    for name, data in files.items():
        nodes[name] = {
            "type": data["type"],
            "path": data["path"],
            "links": data["links_out"],
            "tags": data["tags"],
            "word_count": data["word_count"],
        }
        for link in data["links_out"]:
            target = link.split("/")[-1].split("#")[0]
            edges.append([name, target])
    graph_json = {
        "generated": datetime.now().isoformat(),
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_files": len(files),
            "total_links": sum(len(d["links_out"]) for d in files.values()),
            "orphans": len(find_orphans(files)),
            "missing_targets": len(find_missing_targets(files)),
        }
    }
    json_path = CEIBA_DIR / "vault_graph.json"
    json_path.write_text(json.dumps(graph_json, indent=2))
    print(f"JSON graph written to {json_path}")

    # Print summary
    orphans = find_orphans(files)
    missing = find_missing_targets(files)
    hubs = find_hubs(files)
    print(f"\nTop 5 hubs:")
    for name, count, ntype, _ in hubs[:5]:
        print(f"  {name}: {count} links ({ntype})")
    print(f"\nOrphans: {len(orphans)} | Missing targets: {len(missing)}")


if __name__ == "__main__":
    main()
