# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Fourth Claude Code session. Quest dashboard built + eBay publisher upgraded.
Focus: Quest dashboard v1.1 shipped (tabs, auto-progress, JSON import/export). eBay publisher upgraded with user tokens + error handling.
Done today: quest-dashboard.html (2 versions), publisher.py + auth.py upgraded, session transcript saved.
Active now: Nothing — session ending. Next: open dashboard in browser, get eBay sandbox keys.
Key win: eBay API keys obtained! First real revenue blocker cleared.

---

## 🎯 CURRENT PROJECT
**eBay Empire** — Publisher code is complete. Next blocker: sandbox API keys from developer.ebay.com + policy IDs from Seller Hub. Then test_sandbox() and first real listing.

**Quest Dashboard** — BUILT. `quest-dashboard.html` in repo root. v1.1 has category tabs, auto-progress from objectives, JSON import/export. Open in browser to verify.

**Session Continuity** — FIXED. SessionStart hook auto-loads vault context. Working as of this session.

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
- `Ceiba/06-Sessions/SES_2026_03_16_claude_code.md` — this session's full transcript
- `tools/vault_grapher.py` — generates vault_graph.json + VAULT_GRAPH.md
- `Ceiba/ceiba_dashboard.html` — interactive knowledge graph visualization (vis.js)

### Quest Dashboard — BUILT
- `quest-dashboard.html` — Fallout/Elder Scrolls RPG-style quest tracker
- Auto-progress from objectives (no manual percentages)
- Category tabs: ALL / MAIN / SIDE / FUTURE
- JSON import (loads quests.json) + export button
- Hardcoded fallback data if quests.json missing

### Skills (Claude Desktop chat, NOT Claude Code)
- `ceiba.skill`, `professor.skill`, `the-allocator.skill`, `schedule.skill`
- `session-tracker`, `session-closer`, `vault-architect`, `kernel` (in skills/ folder)
- These are SKILL.md files for Claude Desktop — not Claude Code hooks

### eBay Listing Assistant — CODE COMPLETE
- `tools/ebay-listing-assistant/` — full pipeline
- Auth: OAuth2 Client Credentials + User Token (EBAY_USER_TOKEN)
- Research (Browse API), Content Gen (Claude/Ollama), Publisher (Inventory API), History (SQLite)
- Publisher upgraded: EbayApiError, _api_call() wrapper, shipping defaults (PR 00901), test_sandbox()
- Policy IDs from env vars: EBAY_FULFILLMENT_POLICY_ID, EBAY_PAYMENT_POLICY_ID, EBAY_RETURN_POLICY_ID
- CLI: `python main.py list "product" --condition Used --dry-run`
- Blocked on: eBay Developer sandbox keys + Seller Hub policy IDs

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
  - Bridge server: `bridge_server_secure.js` (port 9876, Bearer auth) — switched from insecure this session
  - n8n via pm2, Ollama (llama3.2), OpenClaw (@CeibaOC2Bot)
  - Syncthing syncing ~/behique (port 8384)
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
- eBay API keys: GOT THEM (2026-03-16) — need sandbox keys + policy IDs next

---

## 🚧 OPEN BLOCKERS
1. **eBay sandbox keys + policy IDs** — create policies in Seller Hub, get IDs for env vars
2. **Quest dashboard verification** — open in browser, confirm it renders
3. **n8n agency outreach** — zero clients, starts after eBay ships

---

## 📋 NEXT SESSION SEQUENCE
1. Session hook should auto-load context
2. Open quest-dashboard.html in browser — verify rendering
3. eBay: create sandbox account → get test keys → run test_sandbox()
4. eBay: create fulfillment/payment/return policies in Seller Hub → get policy IDs
5. First real eBay listing attempt

---

## 🧵 ACTIVE THREAD
Session 2026-03-16 (4th Claude Code session):
- Quest dashboard built from scratch (not ChatGPT's version)
- v1.1 added: tabs, auto-progress, JSON import/export
- eBay publisher upgraded: user tokens, error handling, shipping defaults, test_sandbox()
- Did NOT duplicate ChatGPT's proposed ebay_api_publisher.py — upgraded existing files
- Cursor handled Cobo security (bridge switch to secure version)
- Kalani got eBay API keys — first real revenue blocker cleared

Pattern note: eBay developer account blocker is now partially cleared (keys obtained). Still need sandbox keys and Seller Hub policy IDs before first listing. Revenue still $0.

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
