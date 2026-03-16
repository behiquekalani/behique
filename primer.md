# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Auto checkpoint via Claude Code stop hook.
Focus: Goodfellas Funko Pop set of 3 × qty 3 at $27.99/set. Photos taken, listing generated, Kalani posting.
Next action: Confirm listing live → Hello Kitty cups next → keep listing inventory.
Blocker: Cobo still offline (needs physical power-on). Not blocking eBay listings.
Session status: ACTIVE — first listing going live

---

## 🎯 CURRENT PROJECT
**eBay Listing Agent** — V1 built 2026-03-16. Full pipeline at `tools/ebay-listing-assistant/`.
- 9 files: shipping.py, pricing.py, types_v1.py, research.py, content_generator.py, publisher_v1.py, image_handler.py, run.py, + __init__.py × 6
- V1 = AI generates listing, Kalani pastes into eBay. No API keys needed.
- V2 = Telegram bot + eBay API auto-publish (needs API keys + build work)
- Next milestone: **First listing posted. First sale.**

---

## 🏗️ WHAT EXISTS (current state of all projects)

### eBay Listing Assistant (V1 — LIVE)
- `tools/ebay-listing-assistant/` — full pipeline: research → content → publish
- Shipping calculator (USPS from PR, zone 5, eBay label discount)
- Pricing engine (breakeven + margin + fees, fixed vs auction strategy)
- Content generator (80-char title SEO, HTML description, item specifics)
- V1 publisher (formatted copy-paste output)
- Image validator (format, size, recommendations)
- CLI: `python run.py "Product Name" --condition New --weight 12 --cost 3.00`

### Product Research Engine (on Cobo — needs power-on)
- `~/product_research_engine/` on Cobo (synced via Syncthing)
- Scoring engine (0-100, 5 weighted signals), normalizer, trends adapter
- 61 products scored from seeded trends data (scores flat at 38-40 — needs eBay API)
- Amazon scraper (Playwright, not returning products), Google Shopping (killed)
- Dashboard at `:8080` on Cobo

### BehiqueBot
- Live on Railway, Telegram bot active
- Notion persistence wired (BehiqueBot Ideas database)
- Ollama-first classification (5 categories + 4 life pillars)

### Vault & Knowledge Graph
- Obsidian vault with wiki links, HOME.md, MISSIONS.md
- vault_grapher.py → vault_graph.json → ceiba_dashboard.html (vis.js at :8081)
- IDEAS_BACKLOG.md — smart idea capture system (15 DONE, 9 READY, 5 BLOCKED, 23 FUTURE, 2 KILLED)

### Infrastructure
- Claude Code = HQ (migrated from Cowork 2026-03-15)
- Ceiba Lite: `ceiba_lite.py` — offline fallback on Ollama
- Trends scraper: `tools/trends_scraper.py` — proxy rotation, 35 categories
- **Computer 2 "Cobo" (192.168.0.151)** — worker node, currently OFFLINE:
  - Bridge: bridge.merchoo.shop:9876 (bearer auth, token in ~/.behique_bridge_token)
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
- eBay API keys: NOT YET — developer.ebay.com registration still pending

---

## 🚧 OPEN BLOCKERS
1. **Cobo offline** — needs physical power-on, no wake-on-LAN configured yet
2. **eBay API keys** — registration at developer.ebay.com (unlocks V2 auto-publish + product research scoring)
3. **n8n agency outreach** — zero clients, starts after eBay pipeline proven

---

## 📋 IMMEDIATE NEXT STEPS
1. ✅ eBay Listing Agent V1 built and tested
2. → Kalani sends Hello Kitty cup photos + details → Ceiba generates first listing
3. → Post first listing on eBay manually
4. → Power on Cobo → wire eBay API keys (instructions at `bridge/cobo_instructions_2026-03-16.md`)
5. → Build wake.sh/sleep.sh for Comp2 (READY in backlog, Kalani asked for it twice)

---

## 🧵 ACTIVE THREAD
Session 2026-03-16: Kalani wants to list Hello Kitty cups on eBay. Built V1 listing agent that generates everything (title, description, pricing, shipping) — Kalani pastes into eBay form. Pipeline tested with mock data, works end-to-end. Profit of $2.12 per cup at $14.99 list price (auction strategy recommended for low sell-through items).

Also captured: Telegram bot integration for V2, quest dashboard (Fallout/Skyrim style), multi-model A/B testing, dropship auto-lister, OpenClaw hub. All triaged to IDEAS_BACKLOG — none block today's work.

Kalani flagged: "we're moving in circles" — memory is stale, primer.md was 2 days behind. Fixed.

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

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates this after every completed task (takes 10 seconds)
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
