#!/usr/bin/env python3
"""
Hub Data Exporter — Generates hub.json for the Unified Dashboard

Aggregates live data from all Ceiba systems and writes hub.json
that the dashboard reads on load. Run this before opening the dashboard,
or add it to ceiba_run.py for automatic updates.

Data sources:
  - Git (commits, branch, uncommitted)
  - CMP database (entries, task events, errors)
  - Vault graph (nodes, edges, hubs, types)
  - Session tracker (today's plan, completion)
  - IDEAS_BACKLOG.md (done/ready/blocked counts)
  - Bridge tasks (Cobo delegation status)
  - primer.md (current focus)

Output: ~/behique/Ceiba/hub.json

Usage:
    python3 export_hub_data.py               # write hub.json
    python3 export_hub_data.py --stdout      # print to stdout
"""

import os
import json
import subprocess
import sqlite3
import time
from datetime import datetime, timezone


BEHIQUE = os.path.expanduser("~/behique")
OUTPUT = os.path.join(BEHIQUE, "Ceiba", "hub.json")
CMP_DB = os.path.join(BEHIQUE, "tools", "ai_agent_kernel", "cmp.db")
VAULT_GRAPH = os.path.join(BEHIQUE, "Ceiba", "vault_graph.json")
PRIMER = os.path.join(BEHIQUE, "primer.md")
BACKLOG = os.path.join(BEHIQUE, "Ceiba", "IDEAS_BACKLOG.md")
BRIDGE_TASKS = os.path.join(BEHIQUE, "bridge", "tasks.md")
SESSIONS_DIR = os.path.join(BEHIQUE, "Ceiba", "06-Sessions")


def collect_git():
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip()
        uncommitted = len([l for l in subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip().split("\n") if l])
        commits = subprocess.run(
            ["git", "log", "--oneline", "--since=midnight", "--format=%s|%ai"],
            capture_output=True, text=True, cwd=BEHIQUE, timeout=5
        ).stdout.strip().split("\n")
        commit_list = []
        for c in commits:
            if "|" in c:
                parts = c.split("|", 1)
                commit_list.append({"message": parts[0], "time": parts[1][:16]})
        return {
            "branch": branch,
            "uncommitted": uncommitted,
            "commits_today": len(commit_list),
            "recent_commits": commit_list[:10],
        }
    except Exception:
        return {"branch": "?", "uncommitted": 0, "commits_today": 0, "recent_commits": []}


def collect_cmp():
    if not os.path.exists(CMP_DB):
        return {"total": 0, "today": 0, "by_type": {}, "recent_tasks": []}
    try:
        conn = sqlite3.connect(CMP_DB)
        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        today = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE date(timestamp) = date('now')"
        ).fetchone()[0]
        by_type = {}
        for row in conn.execute("SELECT type, COUNT(*) FROM memories GROUP BY type").fetchall():
            by_type[row[0]] = row[1]

        # Recent task events
        tasks = conn.execute(
            "SELECT timestamp, payload FROM memories WHERE type='task' ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()
        recent = []
        for t in tasks:
            try:
                payload = json.loads(t[1])
                recent.append({
                    "time": t[0][:19],
                    "task_id": payload.get("task_id", "?")[:8],
                    "status": payload.get("status", "?"),
                })
            except Exception:
                pass
        conn.close()
        return {"total": total, "today": today, "by_type": by_type, "recent_tasks": recent}
    except Exception:
        return {"total": 0, "today": 0, "by_type": {}, "recent_tasks": []}


def collect_vault():
    if not os.path.exists(VAULT_GRAPH):
        return {"nodes": 0, "edges": 0, "types": {}, "hubs": []}
    try:
        with open(VAULT_GRAPH) as f:
            data = json.load(f)
        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        types = {}
        for _, nd in nodes.items():
            t = nd.get("type", "unknown")
            types[t] = types.get(t, 0) + 1

        # Top hubs (most connected)
        from collections import defaultdict
        degree = defaultdict(int)
        for e in edges:
            if isinstance(e, list) and len(e) == 2:
                degree[e[0]] += 1
                degree[e[1]] += 1
        hubs = sorted(degree.items(), key=lambda x: -x[1])[:5]

        return {
            "nodes": len(nodes),
            "edges": len(edges),
            "missing": data.get("stats", {}).get("missing_targets", 0),
            "types": types,
            "hubs": [{"name": h[0], "degree": h[1]} for h in hubs],
        }
    except Exception:
        return {"nodes": 0, "edges": 0, "types": {}, "hubs": []}


def collect_session():
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SESSIONS_DIR, f"{today}.json")
    if not os.path.exists(path):
        return {"active": False}
    try:
        with open(path) as f:
            data = json.load(f)
        planned = data.get("planned_tasks", [])
        completed = [t for t in planned if t.get("status") == "completed"]
        execution = data.get("execution_log", [])
        return {
            "active": True,
            "planned": len(planned),
            "completed": len(completed),
            "completion_pct": round(len(completed) / max(len(planned), 1) * 100),
            "execution_count": len(execution),
            "tasks": [{"task": t["task"], "status": t["status"]} for t in planned],
            "log": [{"task": e["task"], "type": e["type"]} for e in execution[-10:]],
        }
    except Exception:
        return {"active": False}


def collect_backlog():
    if not os.path.exists(BACKLOG):
        return {"done": 0, "ready": 0, "blocked": 0, "future": 0}
    try:
        with open(BACKLOG) as f:
            content = f.read()
        sections = {"done": 0, "ready": 0, "blocked": 0, "future": 0, "killed": 0}
        current = None
        for line in content.split("\n"):
            l = line.lower()
            if "## done" in l:
                current = "done"
            elif "## ready" in l:
                current = "ready"
            elif "## blocked" in l:
                current = "blocked"
            elif "## future" in l:
                current = "future"
            elif "## killed" in l:
                current = "killed"
            elif line.strip().startswith("|") and current and "---" not in line and "idea" not in l:
                sections[current] = sections.get(current, 0) + 1
        return sections
    except Exception:
        return {"done": 0, "ready": 0, "blocked": 0, "future": 0}


def collect_bridge():
    if not os.path.exists(BRIDGE_TASKS):
        return {"pending": 0, "in_progress": 0, "done": 0}
    try:
        with open(BRIDGE_TASKS) as f:
            content = f.read().lower()
        return {
            "pending": content.count("[pending]"),
            "in_progress": content.count("[in progress]"),
            "done": content.count("[done]"),
        }
    except Exception:
        return {"pending": 0, "in_progress": 0, "done": 0}


def collect_primer():
    if not os.path.exists(PRIMER):
        return {"focus": "(not found)", "age_minutes": 999}
    try:
        with open(PRIMER) as f:
            content = f.read()
        age = int((time.time() - os.path.getmtime(PRIMER)) / 60)
        # Extract focus line
        focus = ""
        for line in content.split("\n"):
            if "focus" in line.lower() and ":" in line:
                focus = line.split(":", 1)[1].strip()[:150]
                break
        return {"focus": focus or content[:100], "age_minutes": age}
    except Exception:
        return {"focus": "?", "age_minutes": 999}


def collect_cobo():
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "192.168.0.151"],
            capture_output=True, timeout=5
        )
        return {"online": result.returncode == 0}
    except Exception:
        return {"online": False}


def collect_revenue():
    """Revenue tracking — counts listings, sales, and profit."""
    listings_dir = os.path.join(BEHIQUE, "tools", "ebay-listing-assistant", "listings")
    revenue_file = os.path.join(BEHIQUE, "Ceiba", "revenue.json")

    # Count generated listings
    listings_ready = 0
    try:
        for f in os.listdir(listings_dir):
            if f.endswith('.txt'):
                listings_ready += 1
    except Exception:
        pass

    # Load revenue tracking file if it exists
    revenue_data = {
        "current": "$0",
        "listings_ready": listings_ready,
        "listings_live": 0,
        "total_sales": 0,
        "total_profit": "$0",
        "note": f"{listings_ready} listing(s) generated, waiting to be posted on eBay",
    }

    try:
        if os.path.exists(revenue_file):
            with open(revenue_file) as f:
                saved = json.load(f)
                revenue_data.update(saved)
                # Always refresh listings_ready count
                revenue_data["listings_ready"] = listings_ready
    except Exception:
        pass

    return revenue_data


def export():
    """Collect all data and write hub.json."""
    hub = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_local": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "git": collect_git(),
        "cmp": collect_cmp(),
        "vault": collect_vault(),
        "session": collect_session(),
        "backlog": collect_backlog(),
        "bridge": collect_bridge(),
        "primer": collect_primer(),
        "cobo": collect_cobo(),
        "revenue": collect_revenue(),
    }
    return hub


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hub Data Exporter")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    hub = export()

    if args.stdout:
        print(json.dumps(hub, indent=2))
    else:
        with open(OUTPUT, "w") as f:
            json.dump(hub, f, indent=2)
        print(f"  ✅ hub.json exported: {OUTPUT}")
        print(f"     Vault: {hub['vault']['nodes']} nodes | CMP: {hub['cmp']['total']} entries")
        print(f"     Git: {hub['git']['commits_today']} commits | Session: {hub['session'].get('completion_pct', 0)}% done")
        print(f"     Backlog: {hub['backlog']['done']} done, {hub['backlog']['ready']} ready")


if __name__ == "__main__":
    main()
