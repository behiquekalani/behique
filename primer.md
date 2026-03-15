# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-14
# Last Check-in: 2026-03-15

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-15 — Architecture session. Memory system built. Spine document written. Claude Code migration decided.
Focus: THE SPINE — architecture-spine.md written. Moving HQ from Cowork → Claude Code CLI. Memory/wiki-link system is Month 1 priority.
Next action: Migrate to Claude Code (see migration guide below). Run `bash ~/behique/memory.sh` first session.
Blocker: None technical. Kalani needs to install Claude Code and run first session from terminal.
Session status: ARCHITECTURE COMPLETE — ready to migrate

---

## 🎯 CURRENT PROJECT
**THE SPINE** — System architecture designed 2026-03-15. See `Ceiba/05-Knowledge/architecture-spine.md`.
Month 1: Wiki link system + Claude Code migration + routing.py v1.
eBay Listing Assistant still pending API keys — pick back up after migration is stable.

---

## 🏗️ WHAT EXISTS (current state of all projects)

### Skills (installed in Claude desktop)
- `ceiba.skill` — core session skill
- `professor.skill` — 10 expert personas, routing logic, The Connector
- `the-allocator.skill` — LLM cost optimizer, per-step model routing audit
- `schedule.skill` — scheduled tasks
- File skills (xlsx, docx, pptx, pdf) — disabled when not needed

### eBay Listing Assistant
- `~/behique/tools/ebay-listing-assistant/core/types.py` — shared data models
- `~/behique/tools/ebay-listing-assistant/core/pipeline.py` — 3-stage orchestrator
- Waiting on: App ID, Cert ID, Dev ID, OAuth token from developer.ebay.com

### BehiqueBot
- Live on Railway, Telegram bot active
- Notion persistence wired (BehiqueBot Ideas database)
- Classifies 5 categories + 4 life pillars via Ollama (llama3.2) — OpenAI fallback only
- classifier.py + memory.py both migrated to Ollama-first (2026-03-14) — BehiqueBot now runs free

### Infrastructure
- Ceiba Lite: `~/behique/ceiba_lite.py` — offline fallback on Ollama
- Trends scraper: `~/behique/tools/trends_scraper.py` — proxy rotation, 35 categories
- Obsidian vault: wired with HOME.md, project pages, MISSIONS.md
- **Computer 2 (192.168.0.151)** — worker node LIVE:
  - n8n running via pm2 → http://192.168.0.151:5678 (N8N_SECURE_COOKIE=false)
  - Ollama (llama3.2) → http://192.168.0.151:11434 (OLLAMA_HOST=0.0.0.0)
  - Syncthing → ~/behique synced in real time with Mac
  - Cowork working (VHDX sparse fix applied, Hyper-V enabled)
  - pm2-windows-startup installed, Syncthing scheduled task on login
- Telegram notify relay: notify.py + LaunchAgent on Mac (queues messages from sandbox)

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
1. **eBay Developer account** — single gate, developer.ebay.com
2. **n8n agency outreach** — zero clients, starts after eBay assistant ships

---

## 📋 NEXT SESSION SEQUENCE (Claude Code — first session)
1. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
2. Open terminal, cd to ~/behique, run: `claude`
3. CLAUDE.md loads automatically — Ceiba reads vault, loads context
4. Run `bash memory.sh` to inject live git state
5. First real task: add [[wiki links]] to the 3 most important vault files (VAULT_INDEX, primer, architecture-spine)
6. Then: build routing.py v1 (Ollama vs Claude decision layer)

eBay API keys still needed — do that from Claude Code once migration is stable.

---

## 🧵 ACTIVE THREAD
Architecture session 2026-03-15: Kalani called out the real problem — Ceiba defaults to easy projects, not ambitious ones. Built architecture-spine.md: 6-part AI body (Memory, Senses, Hands, Voice, Nervous System, Spine). 4-month plan.

Key decisions today:
- Move HQ from Cowork → Claude Code CLI (more power, less wrapper)
- The Spine is the real project — everything else plugs into it
- BehiqueBot should message based on EVENTS not schedules ("fancy alarm clock" lesson learned again)
- Vault is model-agnostic — this is the resilience strategy against credit limits / Anthropic dependency
- Wiki links are Month 1 priority — they turn flat files into a graph

Q3 target: $100K. Revenue: $0. The spine makes the revenue possible.

---

## 🧠 KEY MOMENTS (survives compression)
- "fancy alarm clock" — Kalani's critique of n8n daily briefing (2026-03-14). Pushes for revenue-generating automation, not reminders.
- "pen and paper" — recurring challenge. If Ceiba builds something a notebook can do, call it out immediately.
- "I don't want to lose you" — continuity is core. ADHD brain loses the thread when interrupted. This is why Ceiba Lite exists.
- Infrastructure building = avoidance pattern. Watch for this when revenue work is next on the list.
- "You go for easy doable projects" (2026-03-15) — Ceiba called out for defaulting to safe suggestions. Kalani wants limits tested, not protected.
- "I want the best, not the fastest" (2026-03-15) — build for architecture, not speed. Weeks/months, not hours.
- "For us, not Anthropic" (2026-03-15) — model-agnostic vault, local fallback, no single-provider dependency.

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates this after every completed task (takes 10 seconds)
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
