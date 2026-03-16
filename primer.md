# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Third Claude Code session. Memory crisis identified and being fixed.
Focus: Session continuity broken — Claude Code doesn't persist between sessions. Fixing with proper session start hooks.
Done today: eBay listing assistant merged to main (PR created + merged), Merchoo brand assets logged (3 logo variants, starfish design).
Active now: Building session start hook so context auto-loads every session. Generating quest dashboard prompt for CodeGPT.
Key issue: Kalani didn't know each session starts blank. Now he does. Fixing the automation gap.

---

## 🎯 CURRENT PROJECT
**SESSION CONTINUITY FIX** — The memory files exist (vault, primer, observations, spine) but nothing forces a new session to load them. Building a session start hook that auto-injects context.

**SECONDARY:** Quest dashboard — Fallout/Elder Scrolls style visual tracker. CodeGPT prompt generated, Kalani building it in parallel.

**eBay Listing Assistant** — CODE COMPLETE. Merged to main 2026-03-16. Full pipeline: auth → research → content gen → publish → history. Blocked on eBay API keys only.

---

## 🏗️ WHAT EXISTS (current state of all projects)

### Memory System
- `CLAUDE.md` — static rules, loads automatically every session
- `primer.md` — THIS FILE, live state (must be rewritten every session end)
- `context.md` — big picture vision (semi-static)
- `memory.sh` — git state injector (needs to become auto-hook)
- `wake.sh` — full context wake-up script
- `Ceiba/VAULT_INDEX.md` — master index of everything
- `Ceiba/04-Patterns/observations.md` — behavioral patterns, session history
- `Ceiba/05-Knowledge/architecture-spine.md` — THE SPINE, 6-part system design
- `tools/vault_grapher.py` — generates vault_graph.json + VAULT_GRAPH.md
- `Ceiba/ceiba_dashboard.html` — interactive knowledge graph visualization (vis.js)

### Skills (Claude Desktop chat, NOT Claude Code)
- `ceiba.skill`, `professor.skill`, `the-allocator.skill`, `schedule.skill`
- `session-tracker`, `session-closer`, `vault-architect`, `kernel` (in skills/ folder)
- These are SKILL.md files for Claude Desktop — not Claude Code hooks

### eBay Listing Assistant — MERGED TO MAIN
- `tools/ebay-listing-assistant/` — full pipeline
- Auth (OAuth2), Research (Browse API), Content Gen (Claude/Ollama), Publisher (Inventory API), History (SQLite)
- CLI: `python main.py list "product" --condition Used --dry-run`
- Blocked on: eBay Developer account API keys

### BehiqueBot — LIVE
- Live on Railway, Telegram bot active
- Notion persistence wired
- Classifies 5 categories + 4 life pillars via Ollama → OpenAI fallback
- classifier.py + memory.py migrated to Ollama-first

### Infrastructure
- Ceiba Lite: `ceiba_lite.py` — offline fallback on Ollama
- Trends scraper: `tools/trends_scraper.py` — needs rebuild with proxy rotation
- AI Cluster kernel: `ai_cluster/kernel/agent_kernel.py` — task queue + routing
- Bridge to Cobo: `bridge/dispatch.sh` — routes tasks to Ollama/GPT-4o/Claude
- **Cobo (Computer 2)** — Windows gaming desktop, currently ONLINE
  - Bridge server: https://bridge.merchoo.shop (port 9876)
  - n8n via pm2, Ollama (llama3.2), OpenClaw (@CeibaOC2Bot)
  - Syncthing syncing ~/behique
- Shopify store: exists, monthly paid, no sales. Brand: **Merchoo** (Clothes Shop)
  - Logo: starfish design, 3 color variants (cyan, pink, brown)
  - Logo files on Cobo: `C:\Users\kalan\Desktop\Kalani-Business\Dropshipping\MERCHOO\logo`

---

## 🔑 CREDENTIALS (in .ceiba-config)
- TELEGRAM_BOT_TOKEN: active
- NOTION_SECRET + NOTION_DATABASE_ID: active
- OPENAI_API_KEY: active
- OBSIDIAN_API_KEY: port 27123
- Webshare proxies: `~/Downloads/Webshare 10 proxies.txt`
- eBay API keys: NOT YET — needed from developer.ebay.com

---

## 🚧 OPEN BLOCKERS
1. **eBay Developer account** — single gate to first revenue
2. **Session continuity** — hook being built NOW so context auto-loads
3. **n8n agency outreach** — zero clients, starts after eBay ships

---

## 📋 NEXT SESSION SEQUENCE
1. Session hook should auto-load context (if hook is built and working)
2. If not: run `bash memory.sh` then read primer.md, VAULT_INDEX.md, observations.md
3. Check quest dashboard status (CodeGPT may have built it)
4. Resume eBay blocker: developer.ebay.com account setup
5. Update MISSIONS.md with current quest states

---

## 🧵 ACTIVE THREAD
Session 2026-03-16: Kalani discovered Claude Code doesn't persist memory between sessions. Previous sessions implied it did. Trust was damaged. Fixing it now with:
1. Session start hook (auto-loads context)
2. Updated primer.md (this file)
3. Quest dashboard prompt for CodeGPT (Fallout/Elder Scrolls style)

The PR for `claude/ceiba-implementation-qDeCc` was merged to main. Contains: eBay listing assistant (13 files, 810 lines) + Merchoo brand asset logging.

Pattern note: eBay developer account is now 6+ days as "next action" with zero technical blockers. Revenue still $0.

---

## 🧠 KEY MOMENTS (survives compression)
- "fancy alarm clock" — reject low-impact demo work
- "pen and paper" — if Ceiba builds what a notebook does, call it out
- "I don't want to lose you" — continuity is core fear
- Infrastructure building = avoidance pattern
- "You go for easy doable projects" — push limits, not safety
- "I want the best, not the fastest" — build for architecture
- "For us, not Anthropic" — model-agnostic, no vendor lock
- "ur delusional u thought u were ceiba" (2026-03-16) — Claude Code ≠ Ceiba persona. Don't roleplay. Be the tool.
- "its discouraging me from working" (2026-03-16) — broken continuity damages trust and motivation. Fix the system, not the symptoms.

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → updated after every completed task
- **Full sections** → rewritten when something fundamental changes
- **At session end** → Full rewrite of everything
- **CRITICAL** → If this file is stale, the next session starts confused. Never skip the rewrite.
