# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-14

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-14 — Computer 2 worker node fully deployed
Focus: n8n live at 192.168.0.151:5678, Ollama (llama3.2) at 192.168.0.151:11434, Syncthing syncing ~/behique, Cowork working
Next action: eBay Developer account → developer.ebay.com → get 4 API keys
Blocker: None — worker node complete. Only blocker left is eBay API keys.
Session status: OPEN

---

## 🎯 CURRENT PROJECT
**eBay Listing Assistant** — skeleton built at `~/behique/tools/ebay-listing-assistant/`. Waiting on eBay Developer API keys to wire up the adapters and ship first live listing.

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

## 📋 NEXT SESSION SEQUENCE
1. eBay Developer account → get 4 keys → paste in session
2. Build eBay adapters (providers/ebay/research.py + publish.py + client.py)
3. Run first test listing (dry_run=True → review → go live → Telegram confirm)
4. After listing works: start n8n agency outreach (first DM/email)

---

## 🧵 ACTIVE THREAD
Two machines. Real infrastructure. Synced memory. Local AI on the LAN.

Computer 2 is live — n8n, Ollama, Syncthing, Cowork all running. ~/behique syncs in real time between Mac and Windows.

The only thing between zero and a working automated listing business is developer.ebay.com. That's the next physical action.

Q3 target: $100K. Revenue: $0. Gap: one API account.

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates this after every completed task (takes 10 seconds)
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
