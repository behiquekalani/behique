---
title: "primer"
type: unknown
tags: [primer.md, ceiba, live, checkpoint, updated]
created: 2026-03-16
---

# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16 (session 4 — continued from compaction)
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Auto checkpoint via Claude Code stop hook.
Focus: Graph-aware context engine + Dashboard V3.2 upgrades.
Done this session: vault_context_engine.py (graph-aware context loading via typed relationships), MAP hover-triggered path highlighting, 3-theme toggle (Neon/Mono/Pastel) on Command Hub, quests.json external loading (60/92 objectives, 65%), quest data sync (18 newly marked done).
Next action: **PASTE FUNKO POP LISTING ON EBAY. Revenue is $0.**
Revenue: **$0.** Funko Pop listing still at `listings/`. Post it.

---

## 🎯 CURRENT PROJECT
**Multi-track: eBay revenue + Dashboard system + Memory infrastructure**
- eBay Listing Agent V1 LIVE — Funko Pop listing waiting to be pasted
- BehiqueBot has /ebay command — needs Railway redeploy
- Behique Command Hub V3: 5 tabs, vis.js quest dependency graph, browse/search all objectives
- Memory Ingestion Protocol: auto-extracts decisions/ideas/blockers from sessions → CMP
- CMP: 25 entries (14 original + 11 ingested)

---

## 🏗️ WHAT EXISTS (current state of all projects)

### eBay Listing Assistant (V1 — LIVE, V2 — BUILT)
- `tools/ebay-listing-assistant/` — full pipeline
- `quick_list.py` — direct listing without research loop
- `listings/` — saved generated listings (.txt + .json metadata)
- V1: CLI `run.py` → research → content → manual paste
- V2: `publisher_v2.py` + `ebay_oauth_token.py` → auto-publish via API
- Telegram `/ebay` command: `modules/ebay_command.py` — wired into main.py

### Behique Command Hub (V3.2 — 6 tabs)
- `Ceiba/behique-hub.html` — N64 retro pixel aesthetic, Press Start 2P font
- **HUB tab**: live hub.json data (cluster, session, git, backlog, vault, focus)
- **QUESTS tab**: quest cards with Easy→Hard, Hard→Easy, By Progress sort + Type/Status filters
- **BROWSE tab**: flat search/sort all objectives (difficulty, reward, time, name), hide done toggle
- **MAP tab**: vis.js force-directed quest dependency graph — hover-triggered path highlighting, click to inspect
- **COMPLETED tab**: trophy room with stats (hours invested, reward stars, hard+ count)
- **HABITS tab**: 8 habits, click-to-toggle, 7-day mini heatmap, streak counter, localStorage persistence
- 3-theme toggle: NEON (default N64), MONO (low-dopamine), PASTEL (soft warm)
- Loads quests from `quests.json` (external, editable) + hub.json auto-refresh every 30s

### Memory Ingestion Protocol (NEW)
- `tools/memory_ingest.py` — extracts decisions/ideas/blockers/mood from sessions+transcripts+git
- Auto-tags projects, tools, patterns via keyword matching
- Writes structured memories to CMP with correlation IDs
- `ceiba ingest` / `ceiba ingest --all` CLI
- Ingestion log prevents duplicate processing

### Vault & Knowledge Graph
- 85 nodes, 334 edges (273 wiki + 61 typed), health score 90/100
- `vault_grapher.py` — parses YAML frontmatter relationships, builds typed edge graph (uses_tool, uses_system, follows_pattern, implements_decision, relates_to_project, logged_in_session)
- `vault_healer.py` — self-healing (missing targets, orphans, dead links, frontmatter)
- `vault_templates.py` — 7 templates (project/tool/decision/pattern/design/check-in/knowledge), auto-upgrades stubs, smart type detection
- `graph_query.py` — 10+ query methods (neighbors, search, shortest_path, hubs, context, rels, rel-types, reverse rels)
- `session_logger.py` — auto-generates SES_ vault files
- `ceiba heal` / `ceiba heal --fix` / `ceiba template` CLI

### Ceiba Unified CLI
- `tools/ceiba` — single entry point for all tools
- Commands: start, briefing, graph, session, export, ingest, heal, template, context, wake, sleep, list, status
- Aliases: g, s, l, st, i, h, t, ctx, c
- `ceiba context "eBay"` — graph-aware vault context loading via typed relationships

### BehiqueBot
- Live on Railway, Telegram bot active
- Notion persistence, Ollama-first classification
- `/ebay` command built but NOT deployed (needs Railway push)

### Product Research Engine (on Cobo — needs power-on)
- `~/product_research_engine/` on Cobo (synced via Syncthing)
- 61 products scored, needs eBay API data to improve

### Infrastructure
- Claude Code = HQ
- Cobo (192.168.0.151): bridge, n8n, Ollama, OpenClaw, Syncthing
- Agent Kernel: `tools/ai_agent_kernel/` — dispatcher, CMP, CCP, 5 skills
- CMP: 25 entries, SQLite, SHA256 integrity

---

## 🔑 CREDENTIALS
- TELEGRAM_BOT_TOKEN: active
- NOTION_SECRET + NOTION_DATABASE_ID: active
- OPENAI_API_KEY: active
- OBSIDIAN_API_KEY: port 27123
- Webshare proxies: `~/Downloads/Webshare 10 proxies.txt`
- Bridge token: `~/.behique_bridge_token` (chmod 600)
- eBay API keys (Production): `~/.behique_ebay_keys` (chmod 600)
- eBay OAuth tokens: NOT YET — needs `python3 ebay_oauth_token.py`

---

## 🚧 OPEN BLOCKERS
1. **Revenue = $0** — Funko Pop listing READY, needs to be pasted into eBay
2. **eBay OAuth user token** — needs `python3 ebay_oauth_token.py` in browser
3. **BehiqueBot redeploy** — /ebay command built but not pushed to Railway
4. **Cobo on insecure bridge** — needs switch to `bridge_server_secure.js`

---

## 📋 IMMEDIATE NEXT STEPS
1. → **PASTE FUNKO POP LISTING ON EBAY** — revenue action #1
2. → **Redeploy BehiqueBot to Railway** with /ebay command
3. → Run OAuth consent flow for V2 auto-publish
4. → Switch Cobo to secure bridge
5. → Open Command Hub in browser: `Ceiba/behique-hub.html`

---

## 🧵 ACTIVE THREAD
Session 2026-03-16 (session 4, post-compaction continuation):
- Came in from compacted context — previous session built eBay Telegram bot, ceiba CLI, vault_healer, behique-hub, ghost nodes
- This session: Dashboard V3 upgrades (Browse tab, MAP tab with vis.js graph), memory ingestion protocol, backlog cleanup
- Kalani asked for quest filters + ability to see all quests sorted — delivered Browse tab
- Kalani suggested visual path with nodes — built MAP tab with vis.js force-directed graph
- Kalani said "the previous system based on quests was superior" — kept quest cards as primary, added Browse/MAP as alternate views
- Memory ingestion extracted 2 decisions, 15 ideas, 3 blockers, detected 8 projects + 5 tools + 3 patterns from today's data

Kalani's mood: Building, engaged, wants continuous execution. "keep doing tasks", "go". Prefers the quest card system. Aesthetic preferences: N64 retro, Press Start 2P, pixel art.

---

## 🧠 KEY MOMENTS (survives compression)
- "fancy alarm clock" — events not schedules
- "pen and paper" — if Ceiba builds what a notebook does, call it out
- "I don't want to lose you" — continuity is core
- Infrastructure building = avoidance. Watch for it when revenue work is next.
- "I want the best, not the fastest" — architecture over speed
- "For us, not Anthropic" — model-agnostic
- "we're moving in circles" — memory must stay current
- "im the captain youre the navigator" — Kalani drives, Ceiba navigates
- "keep building dont stop" — trusts autonomous work
- "the previous system based on quests was superior" — quest cards are the core UX, don't over-engineer
- DotGothic16 chosen for PS1 aesthetic — Kalani vibes with Japanese pixel gothic

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates after every completed task
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
