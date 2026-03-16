# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16 (session 3)
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Auto checkpoint via Claude Code stop hook.
Focus: Dashboard visual overhaul + architecture docs + infrastructure tooling.
Done this session: DotGothic16 font swap, Command Hub built, Agent Kernel prototype saved, ChatGPT relay tested, 4 design docs captured, all ratings fixed.
Next action: **Tell Code GPT YES to produce the retry/failure manager with CMP logging.** Then **PASTE FUNKO POP LISTING ON EBAY.**
Revenue: **$0.** Funko Pop listing still at `listings/`. Post it.

---

## 🎯 CURRENT PROJECT
**Multi-track: eBay revenue + Dashboard system + Agent infrastructure**
- eBay Listing Agent V1 LIVE — Funko Pop listing waiting to be pasted
- Quest Dashboard: DotGothic16 font (PS1-era pixel gothic), vivid neon theme, Mario 64 stars
- Command Hub: `Ceiba/command-hub.html` — 5-panel dashboard (Quest Tracker, Agent Status, Terminal, Links, Ideas)
- Agent Kernel prototype: `tools/ai_agent_kernel/main.py` — TaskQueue, Scheduler, SkillRegistry, Workers
- ChatGPT Relay: `tools/chatgpt_relay.py` — Ceiba can call GPT-4o directly via CLI

---

## 🏗️ WHAT EXISTS (current state of all projects)

### eBay Listing Assistant (V1 — LIVE, V2 — BUILT)
- `tools/ebay-listing-assistant/` — full pipeline
- `quick_list.py` — direct listing without research loop
- `listings/` — saved generated listings (.txt + .json metadata)
- V1: CLI `run.py` → research → content → manual paste
- V2: `publisher_v2.py` + `ebay_oauth_token.py` → auto-publish via API
- Shipping, pricing, content generation all working

### Quest Dashboard (V3 — DotGothic16)
- `Ceiba/quest-dashboard.html` — 3 themes: Neon, Mono, Vivid (cyan/magenta/neon yellow)
- Font: DotGothic16 (PS1-era Japanese pixel gothic)
- Mario 64 stars for reward tiers (Common→Legendary with pulse glow)
- Real quest data from quests.json: 8 missions, 91 objectives
- Difficulty badges (very_easy→very_hard), all re-rated with real differentiation

### Command Hub (V1 — NEW)
- `Ceiba/command-hub.html` — central interface for agent cluster
- 5 panels: Quest Tracker, Agent Status Board, Command Terminal, Dashboard Links, Idea Inbox
- Terminal with command routing simulation (/cobo, /ebay, /vault, /bot, /openclaw)
- Loads from quests.json + hub.json with inline fallback
- Ideas stored in localStorage
- 3 themes: Neon, Mono, Vivid

### Agent Kernel (PROTOTYPE — NEW)
- `tools/ai_agent_kernel/main.py` — ~250 line prototype
- TaskQueue (heapq priority), Scheduler, SkillRegistry, MemoryInterface, WorkerManager
- Multiprocessing workers, dynamic skill loading via importlib
- Demo mode runs with sample tasks
- Code GPT asked about adding retry/failure manager with CMP logging — tell it YES

### Architecture Docs (DESIGN — NEW)
- `Ceiba/06-Designs/agent-kernel-architecture.md` — full Agent Kernel spec from ChatGPT
- `Ceiba/06-Designs/ceiba-memory-protocol-cmp.md` — CMP: typed payloads, SHA256 integrity, conflict resolution
- `Ceiba/06-Designs/ceiba-cobo-communication-protocol-ccp.md` — CCP: task lifecycle, message types, retry logic
- `Ceiba/06-Designs/ceiba-cobo-grpc-prototype.md` — gRPC streaming upgrade for CCP

### ChatGPT Relay (LIVE — NEW)
- `tools/chatgpt_relay.py` — CLI tool for Ceiba to call GPT-4o API
- Tested and working with gpt-4o-mini
- Auto-loads .env, retry logic, cost estimation, logging
- Usage: `python3 tools/chatgpt_relay.py --prompt "..." --output "file.md"`

### Product Research Engine (on Cobo — needs power-on)
- `~/product_research_engine/` on Cobo (synced via Syncthing)
- 61 products scored, needs eBay API data to improve

### BehiqueBot
- Live on Railway, Telegram bot active
- Notion persistence, Ollama-first classification

### Vault & Knowledge Graph
- Obsidian vault, vault_grapher.py, vis.js dashboard
- IDEAS_BACKLOG.md updated with Command Hub + design doc entries

### Infrastructure
- Claude Code = HQ
- Cobo (192.168.0.151): bridge, n8n, Ollama, OpenClaw, Syncthing
- Ceiba Lite: `ceiba_lite.py` — offline fallback

---

## 🔑 CREDENTIALS
- TELEGRAM_BOT_TOKEN: active
- NOTION_SECRET + NOTION_DATABASE_ID: active
- OPENAI_API_KEY: active (used by chatgpt_relay.py)
- OBSIDIAN_API_KEY: port 27123
- Webshare proxies: `~/Downloads/Webshare 10 proxies.txt`
- Bridge token: `~/.behique_bridge_token` (chmod 600)
- eBay API keys (Production): `~/.behique_ebay_keys` (chmod 600)
- eBay OAuth tokens: NOT YET — needs `python3 ebay_oauth_token.py`

---

## 🚧 OPEN BLOCKERS
1. **Revenue = $0** — Funko Pop listing READY, needs to be pasted into eBay
2. **eBay OAuth user token** — needs `python3 ebay_oauth_token.py`
3. **Cobo on insecure bridge** — needs switch to `bridge_server_secure.js`

---

## 📋 IMMEDIATE NEXT STEPS
1. → **Tell Code GPT YES on retry/failure manager + CMP logging**
2. → **PASTE FUNKO POP LISTING ON EBAY** — revenue action #1
3. → Run OAuth consent flow for V2 auto-publish
4. → Switch Cobo to secure bridge
5. → Test Agent Kernel prototype: `cd tools/ai_agent_kernel && python3 main.py`
6. → Open Command Hub in browser: `Ceiba/command-hub.html`

---

## 🧵 ACTIVE THREAD
Session 2026-03-16 (session 3, post-compaction):
- Committed all session 2 changes: quest ratings, dashboard typography, relay, design docs
- Saved Code GPT Command Hub HTML to `Ceiba/command-hub.html` (Ceiba's version is richer)
- Saved Agent Kernel prototype to `tools/ai_agent_kernel/main.py`
- Font pivot: Inter + Playfair Display → DotGothic16 (PS1 pixel gothic, Kalani's choice)
- Kalani explored Sadboys/Yung Lean aesthetic — DotGothic16 sits in the right zone
- Code GPT offered retry/failure manager with CMP logging — Kalani should say YES
- Two commits this session: typography overhaul + Command Hub/Kernel/font swap

Kalani's mood: Building momentum, exploring aesthetic identity for dashboards, actively using Code GPT as second builder. Multiple Code GPT outputs coming in that need to be saved to disk.

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
- DotGothic16 chosen for PS1 aesthetic — Kalani vibes with Japanese pixel gothic

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates after every completed task
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
