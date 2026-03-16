# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-16
# Last Check-in: 2026-03-16

---

## ⚡ LIVE STATE
<!-- Ceiba updates this block after every completed task. 5 lines max. -->
Last update: 2026-03-16 — Auto checkpoint via Claude Code stop hook.
Focus: eBay API keys obtained (Prod + Sandbox). V2 publisher + OAuth built. Quest dashboard v1 exists but needs pixel art rebuild.
Next action: POST THE FUNKO POPS. Revenue $0 → $27.99. Then Hello Kitty cups. Then OAuth flow to activate V2.
Blocker: Cobo running insecure bridge (needs switch to bridge_server_secure.js). Not blocking eBay listings.
Session status: ACTIVE — transcript persistence built, backlog synced, primer updated

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
- eBay API keys (Production): `~/.behique_ebay_keys` (chmod 600) — App ID, Dev ID, Cert ID
- eBay API keys (Sandbox): `~/.behique_ebay_keys_sandbox` (chmod 600)
- eBay OAuth tokens: `~/.behique_ebay_tokens.json` (NOT YET — needs OAuth consent flow)

---

## 🚧 OPEN BLOCKERS
1. **Cobo offline** — needs physical power-on, no wake-on-LAN configured yet
2. **eBay OAuth user token** — API keys obtained, but need to run OAuth consent flow (`python ebay_oauth_token.py`) to get user token for API calls
3. **n8n agency outreach** — zero clients, starts after eBay pipeline proven

---

## 📋 IMMEDIATE NEXT STEPS
1. ✅ eBay Listing Agent V1 built and tested
2. ✅ eBay API keys obtained (Production + Sandbox)
3. ✅ V2 publisher + OAuth token script built
4. ✅ Quest dashboard v1 built (needs aesthetic rebuild)
5. ✅ Transcript + image persistence system built
6. → **POST THE FUNKO POPS ON EBAY** — revenue action #1
7. → Hello Kitty cups listing next
8. → Run OAuth consent flow to activate V2 API publisher
9. → Switch Cobo to secure bridge (bridge_server_secure.js)
10. → Rebuild quest dashboard with pixel art/Stardew Valley aesthetic

---

## 🧵 ACTIVE THREAD
Session 2026-03-16 (extended): Massive session. Got eBay API keys (Prod + Sandbox), built V2 publisher with OAuth + rate limiting + draft preview, built quest dashboard v1, relayed Comp2 transcript with vision session (Book-to-Agent, Colmena66, tamagotchi, content funnel). Cobo came online.

Quest dashboard built but wrong aesthetic — Kalani wants pixel art/Habitica/Stardew Valley, not cyberpunk. ChatGPT prompt written for rebuild.

Kalani frustrated by memory loss: "its been demotivating me to work." Built transcript persistence system (`Ceiba/07-Transcripts/` + `Ceiba/08-Images/`). Synced all Comp2 ideas to IDEAS_BACKLOG.

Revenue is still $0. Funko Pop listing generated. Everything is ready except Kalani pasting it into eBay's form.

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
