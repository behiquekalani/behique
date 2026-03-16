# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16 (session 2)
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Auto checkpoint via Claude Code stop hook.
Focus: eBay listings. Funko Pop Goodfellas listing saved at `tools/ebay-listing-assistant/listings/`. Kalani needs to paste into eBay form.
Next action: **PASTE FUNKO POP LISTING ON EBAY.** File is at `listings/funko_pop_the_godfather_vito_corleone_mi_20260316_155205.txt`. Copy each section.
Blocker: None for listing. OAuth consent flow needed for V2 auto-publish (`python3 ebay_oauth_token.py`). Cobo still on insecure bridge.
Revenue: **$0.** Listing is generated and saved. Post it.

---

## 🎯 CURRENT PROJECT
**eBay Listing Agent** — V1 LIVE, V2 built pending OAuth. Quick lister built.
- `tools/ebay-listing-assistant/` — full pipeline, 15+ files
- `quick_list.py` — skip research, generate listing instantly, saves to `listings/`
- Funko Pop Goodfellas listing: 3 sets × $27.99/set, $11.22 profit each = **$33.66 total**
- Hello Kitty cups: SKIPPED (too many variants, needs Kalani to specify which one)
- V2 publisher + OAuth script built. Needs `python3 ebay_oauth_token.py` to activate.

---

## 🏗️ WHAT EXISTS (current state of all projects)

### eBay Listing Assistant (V1 — LIVE, V2 — BUILT)
- `tools/ebay-listing-assistant/` — full pipeline
- `quick_list.py` — direct listing without research loop
- `listings/` — saved generated listings (.txt + .json metadata)
- V1: CLI `run.py` → research → content → manual paste
- V2: `publisher_v2.py` + `ebay_oauth_token.py` → auto-publish via API
- Shipping calculator (USPS from PR, zone 5, eBay label discount)
- Pricing engine (breakeven + margin + fees, fixed vs auction)
- Content generator (80-char title SEO, HTML description, item specifics)

### Quest Dashboard (V2 — LIVE)
- `Ceiba/quest-dashboard.html` — 3 theme modes: Neon, Mono (low dopamine), Pastel Neon
- Theme toggle in top bar, saves to localStorage
- Real quest data: 4 active quests, 2 future, 4 completed
- Donut rings, bar chart, habit tracker, tab navigation
- Kalani said "beautiful" — SHIPPED
- Future: FocusLab Weekly-style clean layout (see `08-Images/` for reference screenshots)
- SEPARATE from tamagotchi (that's Raspberry Pi / mobile app — future)

### Product Research Engine (on Cobo — needs power-on)
- `~/product_research_engine/` on Cobo (synced via Syncthing)
- Scoring engine (0-100, 5 weighted signals), normalizer, trends adapter
- 61 products scored from seeded trends data (scores flat at 38-40 — needs eBay API)

### BehiqueBot
- Live on Railway, Telegram bot active
- Notion persistence wired (BehiqueBot Ideas database)
- Ollama-first classification (5 categories + 4 life pillars)

### Vault & Knowledge Graph
- Obsidian vault with wiki links, HOME.md, MISSIONS.md
- vault_grapher.py → vault_graph.json → ceiba_dashboard.html (vis.js)
- IDEAS_BACKLOG.md — 17 DONE, 12 READY, 5 BLOCKED, 32 FUTURE, 2 KILLED
- Session transcripts: `Ceiba/07-Transcripts/`
- Image references: `Ceiba/08-Images/`

### Infrastructure
- Claude Code = HQ (migrated from Cowork 2026-03-15)
- Ceiba Lite: `ceiba_lite.py` — offline fallback on Ollama
- Trends scraper: `tools/trends_scraper.py` — proxy rotation, 35 categories
- **Computer 2 "Cobo" (192.168.0.151)** — worker node:
  - Bridge: bridge.merchoo.shop:9876 (bearer auth) — RUNNING BUT INSECURE VERSION
  - n8n: pm2, webhooks at n8n.merchoo.shop
  - Ollama: llama3.2 at :11434
  - OpenClaw: @CeibaOC2Bot, GPT-4o, 3+ skills
  - Syncthing: ~/behique synced both machines
- Telegram notify relay: notify.py + LaunchAgent

---

## 🔑 CREDENTIALS
- TELEGRAM_BOT_TOKEN: active
- NOTION_SECRET + NOTION_DATABASE_ID: active
- OPENAI_API_KEY: active
- OBSIDIAN_API_KEY: port 27123
- Webshare proxies: `~/Downloads/Webshare 10 proxies.txt`
- Bridge token: `~/.behique_bridge_token` (chmod 600)
- eBay API keys (Production): `~/.behique_ebay_keys` (chmod 600) — App ID, Dev ID, Cert ID
- eBay API keys (Sandbox): `~/.behique_ebay_keys_sandbox` (chmod 600)
- eBay OAuth tokens: `~/.behique_ebay_tokens.json` (NOT YET — needs `python3 ebay_oauth_token.py`)

---

## 🚧 OPEN BLOCKERS
1. **eBay OAuth user token** — API keys obtained, need to run `python3 ebay_oauth_token.py` to get user token
2. **Cobo on insecure bridge** — needs switch to `bridge_server_secure.js`
3. **Revenue = $0** — Funko Pop listing is READY, just needs to be pasted into eBay

---

## 📋 IMMEDIATE NEXT STEPS
1. ✅ eBay Listing Agent V1 built and tested
2. ✅ eBay API keys obtained (Production + Sandbox)
3. ✅ V2 publisher + OAuth token script built
4. ✅ Quest dashboard v2 with 3 themes (Neon/Mono/Pastel)
5. ✅ Quick lister built (`quick_list.py`)
6. ✅ Funko Pop Goodfellas listing generated + saved to `listings/`
7. ✅ 12 missing ideas synced to IDEAS_BACKLOG.md from 12am-3am session
8. ✅ All files committed to git (33 files, 3939 insertions)
9. → **PASTE FUNKO POP LISTING ON EBAY** — revenue action #1
10. → Run OAuth consent flow to activate V2 API publisher
11. → Switch Cobo to secure bridge (`bridge_server_secure.js`)

---

## 🧵 ACTIVE THREAD
Session 2026-03-16 (session 2, continuing from context compaction):
- Built `quick_list.py` — skip-research direct lister. Generates listing in 2 seconds, saves to `listings/`.
- Generated Funko Pop Goodfellas listing: 3 sets × $27.99, $11.22 profit each = $33.66 total
- Hello Kitty cups SKIPPED — too many variants, Kalani needs to specify
- Quest dashboard v2: Added 3 theme modes (Neon/Mono/Pastel Neon) with toggle + localStorage
- Kalani shared FocusLab Weekly screenshots as inspo — saved references to `08-Images/`
- Clarified: dashboard = FocusLab style (web), tamagotchi = separate project (Raspberry Pi or app)
- Found and synced 12 missing ideas from 12am-3am session to IDEAS_BACKLOG.md
- Committed 33 files (3939 insertions) to git

Kalani's mood: Excited about dashboard ("beautiful", "I LOVE IT!!!!!!!"), wants to keep building, told me "keep building dont stop im busy do everything u can without me to advance todays goals"

---

## 🧠 KEY MOMENTS (survives compression)
- "fancy alarm clock" — events not schedules. Revenue-generating automation, not reminders.
- "pen and paper" — if Ceiba builds what a notebook does, call it out.
- "I don't want to lose you" — continuity is core. ADHD brain loses the thread.
- Infrastructure building = avoidance. Watch for it when revenue work is next.
- "You go for easy doable projects" — test limits, not protect them.
- "I want the best, not the fastest" — architecture over speed.
- "For us, not Anthropic" — model-agnostic, no single-provider dependency.
- "we're moving in circles" (2026-03-16) — memory must stay current or we repeat ourselves.
- "im the captain youre the navigator" (2026-03-16) — Kalani drives direction, Ceiba manages course.
- "keep building dont stop" (2026-03-16) — Kalani trusts autonomous work. Don't ask, build.

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates this after every completed task (takes 10 seconds)
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
