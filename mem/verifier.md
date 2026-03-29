---
layer: kernel
purpose: Consistency checker - runs at session start and end
last_modified: 2026-03-28
last_run: 2026-03-28
last_result: clean
---

# Verifier - Consistency Checks

## When to Run
- Session start: before any work begins
- Session end: before git commit
- On demand: when something feels off

## Checks

### 1. Primer Staleness
- Read primer.md last_modified
- If older than 24 hours: FLAG as stale
- Action: rewrite primer.md with current state

### 2. Graph-Status Sync
- Every project node in context_graph.md must exist in status.md
- Every active item in status.md must have a graph node
- Mismatches: FLAG and list

### 3. Primer-Graph Contradictions
- If primer says "active: X" but graph says "status: backlog": FLAG
- If primer lists a blocker but graph shows no blocking edges: FLAG

### 4. Orphan Detection
- Nodes in graph with zero links: FLAG as orphan
- Patterns referenced in graph but file missing: FLAG as broken ref

### 5. Status Auto-Sort
- Items not touched in 7 days: demote to backlog
- Items with status=rework for 14+ days: FLAG for decision
- Items completed: move to archived after 48 hours

### 6. Session Weight
- Count files_modified + lines_changed + new_nodes
- Soft limit (weight > 50): auto git commit checkpoint
- Hard limit (weight > 100): branch + handoff to primer
- Critical (weight > 150): print "START NEW SESSION. State saved."

## How to Run

```bash
python3 mem/scripts/session_end.py --verify-only
```

Or manually check each section above against the current state of primer.md, context_graph.md, and status.md.

## Last Run Results
- Date: 2026-03-28
- Primer stale: NO
- Graph-Status sync: CLEAN
- Contradictions: NONE
- Orphans: NONE
- Status auto-sort: 0 items demoted
- Session weight: 0 (fresh session)
