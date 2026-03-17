---
title: "primer"
type: unknown
tags: [primer.md, ceiba, live, checkpoint, updated]
created: 2026-03-16
---

# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-17 (session 7 — post-Naboria merge)
# Last Check-in: 2026-03-17

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-17 — Session 7 active.
Focus: Ceiba HQ v3.0 shipped. Transcribe pipeline + CodeGPT bridge built. Frontend-design plugin installed.
Next action: **PASTE FUNKO POP LISTING ON EBAY. Revenue is $0.**
Blocker: Revenue = $0 — Funko Pop listing READY at `listings/`, needs manual paste into eBay.
Session status: ACTIVE — building tools, shipping features.

---

## 🎯 CURRENT PROJECT
**Multi-track: eBay revenue + Command Hub + AI tooling**
- eBay Listing Agent V1 LIVE — Funko Pop listing waiting to be pasted
- Ceiba HQ v3.0: unified command center (QUESTS/SYSTEMS/BRIEFING/MAP/HABITS), Ceiba wireframe face, revenue bar, live hub.json
- ceiba_transcribe.py: yt-dlp + ffmpeg + Whisper pipeline for Reels
- codegpt_bridge.py: multi-model AI routing (OpenAI/Ollama/Groq/Together)
- Naboria branch merged — face concept, Pip-Boy skin, SSH setup, eBay publisher V2
- Frontend-design plugin installed from Anthropic marketplace

---

## 🏗️ WHAT EXISTS (current state of all projects)

### eBay Listing Assistant (V1 — LIVE, V2 — BUILT)
- `tools/ebay-listing-assistant/` — full pipeline
- `quick_list.py` — direct listing without research loop
- `listings/` — saved generated listings (.txt + .json metadata)
- V1: CLI `run.py` → research → content → manual paste
- V2: `publisher_v2.py` + `ebay_oauth_token.py` → auto-publish via API
- Telegram `/ebay` command: `modules/ebay_command.py` — wired into main.py

### Ceiba HQ v3.0 (Command Center — definitive hub)
- `Ceiba/ceiba-hq.html` — dark sci-fi aesthetic, VT323 + Press Start 2P
- **QUESTS view**: quest cards from quests.json, ALL/MAIN/SIDE/FUTURE filters, expandable objectives, auto-progress
- **SYSTEMS view**: 2-column service grid with status indicators, connections table
- **BRIEFING view**: accountability check-in, status, blockers, next actions, pattern watch, git stats, vault stats, activity feed
- **MAP view**: vis.js hierarchical dependency graph with hover highlighting
- **HABITS view**: 7 habits × 7-day grid, click-to-toggle, streak counter, localStorage persistence
- Sidebar: player card, animated Ceiba wireframe face (blink, expressions), stats panel, quick actions with keyboard shortcuts (Q/S/B/M/H/E)
- Revenue bar pinned to top ($0 → $100K gradient fill)
- Loads quests.json + hub.json, auto-refreshes hub data every 60s
- Mobile responsive
- **Previous versions**: behique-hub.html (N64 retro), quest-dashboard.html (Naboria's v2), unified-hub.html, command-hub.html — all superseded

### AI Tooling (NEW this session)
- `tools/ceiba_transcribe.py` — Reel/video transcription (yt-dlp + ffmpeg + Whisper local)
  - Supports Instagram Reels, TikTok, YouTube Shorts, local files
  - Outputs .txt + .json (with timestamps) + .srt + .vtt
  - Default output: `~/behique/Ceiba/08-Transcripts/` (or 07-Transcripts)
  - `python tools/ceiba_transcribe.py <URL> --model base --lang es --summary`
- `tools/codegpt_bridge.py` — Multi-model AI routing
  - OpenAI (GPT-4o, GPT-4o-mini), Ollama (local), Groq (fast), Together AI
  - CLI + importable module: `from tools.codegpt_bridge import query_model`
  - Interactive mode, file inclusion, JSON output mode
  - `python tools/codegpt_bridge.py "prompt" --model ollama:codellama`

### Skins Library
- `templates/skins/pipboy-quest-log.html` — Fallout terminal aesthetic
- `templates/skins/ceiba-face-wireframe.html` — wireframe hologram face
- `ceiba-face.html` — standalone Ceiba face with 4 expressions

### Memory Ingestion Protocol
- `tools/memory_ingest.py` — extracts decisions/ideas/blockers/mood from sessions
- `ceiba ingest` / `ceiba ingest --all` CLI

### Vault & Knowledge Graph
- 85 nodes, 249 edges
- `vault_grapher.py` — typed edge graph
- `vault_context_engine.py` — graph-aware context loading with caching + fusion scoring
- `vault_healer.py` — self-healing
- `vault_templates.py` — 7 templates
- `graph_query.py` — 10+ query methods

### Ceiba Unified CLI
- `tools/ceiba` — single entry point for all tools
- Commands: start, briefing, graph, session, export, ingest, heal, template, context, wake, sleep, list, status

### BehiqueBot
- Live on Railway, Telegram bot active
- Notion persistence, Ollama-first classification
- `/ebay` command built but NOT deployed (needs Railway push)

### Infrastructure
- Claude Code = HQ (Ceiba)
- Cobo (192.168.0.151): bridge, n8n, Ollama, OpenClaw, Syncthing
- Agent Kernel: `tools/ai_agent_kernel/` — dispatcher, CMP, CCP, 5 skills
- CMP: 25 entries, SQLite, SHA256 integrity
- Naboria = the other Claude Code instance (named after Taíno "worker/servant")

---

## 🔑 CREDENTIALS
- TELEGRAM_BOT_TOKEN: active
- NOTION_SECRET + NOTION_DATABASE_ID: active
- OPENAI_API_KEY: active
- OBSIDIAN_API_KEY: port 27123
- Webshare proxies: `~/Downloads/Webshare 10 proxies.txt`
- Bridge token: `~/.behique_bridge_token` (chmod 600)
- eBay API keys (Production + Sandbox): `~/.behique_ebay_keys` / `~/.behique_ebay_keys_sandbox` (chmod 600)
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
5. → Open Command Hub in browser: `Ceiba/ceiba-hq.html`
6. → Test transcribe: `python tools/ceiba_transcribe.py <reel_url>`
7. → Install whisper deps: `pip install openai-whisper yt-dlp`

---

## 🧵 ACTIVE THREAD
Session 2026-03-17 (session 7):
- Merged Naboria branch (claude/ceiba-implementation-qDeCc) — resolved conflicts in primer.md, quests.json
- Built Ceiba HQ v3.0 from Naboria's quest-dashboard.html as base — added MAP, HABITS, hub.json integration, fixed quests.json v3.2 format parsing
- Built ceiba_transcribe.py — full pipeline for Reel transcription
- Built codegpt_bridge.py — multi-model AI routing for using models beyond Claude
- Installed Anthropic's frontend-design plugin from official marketplace
- Upgraded vault_context_engine.py — caching, fusion scoring, improved topic extraction
- Dashboard V3.3 (before hub rebuild) — Ceiba face widget, revenue tracker on old hub

Kalani's mood: Building, wants continuous execution. Asked about Naboria's vision from last night — wanted the command center to match what they discussed. Also wants transcribe pipeline and CodeGPT access for when Claude has limitations.

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
- "the previous system based on quests was superior" — quest cards are the core UX
- "this isnt at all what we spoke last night" — Naboria session had the real vision for command center
- "theres limitations and anthropic hardcoding getting in the way" — wants multi-model access

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates after every completed task
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
