# EXECUTE: Build Ceiba v2 Memory Architecture

You are building a production-ready, file-based AI memory system. Not designing. Building. Every output must be a file I can save to disk immediately.

## Current System (replace this)
- CLAUDE.md (static rules), primer.md (live state), context.md (big picture)
- Problem: files drift, context lost, no auto-organization, no validation

## Build These 5 Components

### 1. Context Trio (3 files that verify each other)

Create these 3 files with YAML frontmatter and markdown body:

**`mem/primer.md`** - L1 Cache. Current task, active problems, immediate goals. Rewritten every session end.

**`mem/context_graph.md`** - L2 Cache. Bidirectional map of Projects <-> Tools <-> Patterns <-> People. Use this linking syntax:
```yaml
nodes:
  - id: project-behike-os
    type: project
    status: active
    links: [tool-claude-code, pattern-dark-theme, person-kalani]
```

**`mem/verifier.md`** - Kernel. Runs at session start/end. Checks:
- Is primer.md stale (last_modified > 24h)?
- Does context_graph reference projects not in status tracker?
- Are there contradictions between primer goals and graph status?

### 2. Status Tracker (`mem/status.md`)

Track every project/idea with YAML entries:
```yaml
items:
  - name: "List blueprints on Gumroad"
    status: active  # active|todo|backlog|rework|archived
    last_modified: 2026-03-28
    priority: 1
    context_weight: 3  # 1-5 how much context this needs
```

Auto-sort rules:
- Items not touched in 7 days: demote to backlog
- Items with status=rework for 14 days: flag for decision
- Items completed: move to archived after 48h

Session weight management:
- Soft limit (context 60%): `git add -A && git commit -m "mem: checkpoint"`
- Hard limit (context 80%): `git checkout -b session/YYYY-MM-DD-HH` + write handoff to primer.md
- Critical (context 90%): Print "START NEW SESSION. State saved."

### 3. Knowledge Library (`mem/patterns/`)

Create these starter pattern files:

**`mem/patterns/blueprint-css.md`** - The CSS variables, print rules, dark theme that works
**`mem/patterns/cover-html.md`** - The 1280x720 cover template structure
**`mem/patterns/thumbnail-html.md`** - The 600x600 thumbnail template
**`mem/patterns/product-folder.md`** - What goes in each product folder (PDF, cover.png, thumbnail.png, GUMROAD_INFO.txt)
**`mem/patterns/copywriting-voice.md`** - Hormozi/Gary Vee style, pain points, strikethrough, cyan hooks
**`mem/patterns/gumroad-listing.md`** - Standard listing template (name, price, slug, description, summary, receipt, tags)

Each pattern file has:
```yaml
---
name: Blueprint CSS Standard
type: pattern
use_when: "building any blueprint or guide product"
last_verified: 2026-03-28
---
[the actual template/code/structure]
```

### 4. Fleet Sync (`mem/fleet.md`)

```yaml
machines:
  ceiba:
    role: primary
    os: macOS
    capabilities: [claude-code, brave-pdf, git-push]
    ip: local
  cobo:
    role: content-generation
    os: linux
    capabilities: [ollama, free-tier-rotation]
    ip: 192.168.0.151
  naboria:
    role: always-on-worker
    os: linux
    capabilities: [hosting, background-tasks, discord-bot]
    ip: 192.168.0.152

sync:
  method: syncthing
  shared_folders: [mem/, READY-TO-SELL/gumroad-ready/]

tasks:
  cobo:
    - "Generate 10 social media captions using Gemini free tier"
    - "Generate 5 blog post drafts using ChatGPT free tier"
  naboria:
    - "Run Discord bot 24/7"
    - "Host behike.store"
    - "Run niche scanner on schedule"
```

### 5. Session End Routine (`mem/scripts/session_end.py`)

Pseudo-code:
```
1. Read primer.md, extract new facts/decisions
2. For each new fact, check if context_graph.md has a related node
   - If yes: update the node's last_modified
   - If no: create new node, auto-link to related nodes
3. Run verifier.md checks:
   - Primer vs Graph contradictions?
   - Stale items in status.md?
   - Orphaned nodes in graph?
4. Update status.md (demote inactive, promote active)
5. Calculate session weight:
   - Count: files modified + lines changed + new nodes
   - If > soft_limit: git commit
   - If > hard_limit: git branch + handoff
6. Rewrite primer.md with current state
7. Git add, commit, push
```

## Constraints
- Markdown only. No databases.
- YAML frontmatter for machine-parseable metadata.
- Human-readable for manual recovery.
- Model-agnostic (no Claude-specific formatting).
- Git-integrated at every level.

## Output
Create every file listed above with real content based on the current Behike project state. Use what you know about the project from CLAUDE.md and primer.md to populate the initial nodes, patterns, and status items.

Save everything under `~/behique/mem/`.
