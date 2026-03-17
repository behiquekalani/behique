---
title: "primer"
type: unknown
tags: [primer.md, ceiba, live, checkpoint, updated]
created: 2026-03-16
---

# primer.md — Ceiba Memory Stack
# LIVE CHECKPOINT updated throughout session (not just at end)
# Last full rewrite: 2026-03-17 (session 8 — system audit + MCP upgrade)
# Last Check-in: 2026-03-17

---

## ⚡ LIVE STATE
Last update: 2026-03-17 1:15 PM — Massive infrastructure day.
Last update: 2026-03-17 — Auto checkpoint via Claude Code stop hook.
Next action: **PASTE FUNKO POP LISTING ON EBAY. Revenue is STILL $0.**
Blocker: Revenue = $0 — listing READY, Kalani needs to paste it.
Session status: ACTIVE — 14/16 tasks done today.

---

## 🎯 CURRENT PROJECT
**System overhaul + revenue activation**
- Comprehensive audit: 59% of codebase was dead weight — archived/frozen
- 14 tools archived (3,845 lines), AI kernel + cluster frozen (5,878 lines)
- Folder architecture cleaned: 50 → 22 root items
- MCP connectors replace most custom tools
- BehiqueBot swapped from OpenAI ($5/mo) → MiniMax M2.5 via OpenRouter (~$0)
- Cobo bridge connected: Ceiba ↔ Cobo live on 192.168.0.151:9876
- eBay listing still waiting to be posted

---

## 🏗️ WHAT EXISTS (current state)

### Active Tools (tools/)
- `ceiba` — CLI entry point
- `ceiba_audit.py` — AI code review via Cobo/Ollama
- `ceiba_bridge.py` — Cobo bridge client
- `ceiba_run.py` — unified launcher
- `ceiba_transcribe.py` — Whisper voice→text
- `codegpt_bridge.py` — multi-model router (evaluate after MiniMax)
- `ebay-listing-assistant/` — full pipeline with Tavily research adapter (NEW)
- `n8n-workflows/` — workflow templates
- `trends_scraper.py` — keep until Apify replaces it
- `_archived/` — 14 obsolete tools (connector-replaced)
- `_frozen/` — AI agent kernel + cluster (premature)

### MCP Connectors (installed today)
- **Notion** — BehiqueBot persistence, knowledge base
- **Gmail** — email management
- **Google Calendar** — listing schedules, events (3 events created today)
- **Slack** — command center (needs workspace setup)
- **Canva** — design generation
- **Figma** — design context
- **Airtable** — inventory tracking (base being created)
- **Tavily** — web search + deep research (replaces custom scrapers)
- **Apify** — 3,000+ pre-built scrapers (eBay, TikTok, Facebook, Google)
- **n8n** — workflow builder on Cobo (API key configured)
- **Hugging Face** — model hub access
- **Claude in Chrome** — browser automation
- **Claude Preview** — app preview
- **Scheduled Tasks** — cron-like automation
- **MCP Registry** — connector discovery
- **Zapier** — integration hub
- **Obsidian** — vault access (local MCP)

### eBay Listing Assistant
- `tools/ebay-listing-assistant/` — full pipeline
- `providers/ebay/research_tavily.py` — NEW Tavily-powered research adapter
- `listings/` — Funko Pop listing READY to paste
- V1: CLI → research → content → manual paste
- V2: publisher_v2.py exists but needs OAuth

### BehiqueBot
- Live on Railway, Telegram bot active
- **MiniMax M2.5 via OpenRouter** — ~$0/mo (was $5/mo OpenAI)
- Notion persistence FIXED (was 401, now working)
- Ollama-first → MiniMax fallback → safe fallback chain
- Railway env: OPENAI_BASE_URL=openrouter.ai, FALLBACK_MODEL=minimax/minimax-m2.5

### Infrastructure
- **Ceiba (Mac)** — HQ, Claude Code, all tools + MCPs
- **Cobo (Windows, 192.168.0.151)** — bridge server, n8n, Ollama (llama3.2)
- **Comp3** — being set up by Kalani
- Bridge: `0.0.0.0:9876`, auth token in `~/.behique_bridge_token`
- n8n: `http://192.168.0.151:5678` — API key configured in MCP
- Ollama: `http://192.168.0.151:11434` — llama3.2 (3.2B Q4_K_M)

### Folder Architecture (cleaned today)
```
behique/
├── CLAUDE.md, primer.md, context.md    ← Memory stack
├── main.py, modules/, Procfile         ← BehiqueBot (Railway)
├── Ceiba/                              ← Vault + dashboards
├── tools/                              ← Active tools only
├── bridge/                             ← Cobo comms
├── skills/                             ← Claude skills
├── dashboards/                         ← Root HTML dashboards
├── product_research_engine/            ← Standalone project
└── _legacy/                            ← Orphaned scripts
```

---

## 🔑 CREDENTIALS
- TELEGRAM_BOT_TOKEN: active (rotated recently)
- NOTION_SECRET + NOTION_DATABASE_ID: active (fixed 401 today)
- OPENAI_API_KEY: now OpenRouter key (sk-or-...) in Railway
- OPENAI_BASE_URL: https://openrouter.ai/api/v1
- FALLBACK_MODEL: minimax/minimax-m2.5
- OBSIDIAN_API_KEY: port 27123
- Bridge token: `~/.behique_bridge_token`
- Apify token: configured in MCP
- n8n API key: configured in MCP
- eBay API keys: `~/.behique_ebay_keys` (OAuth not yet configured)

---

## 🚧 OPEN BLOCKERS
1. **Revenue = $0** — Funko Pop listing READY, needs manual paste into eBay
2. **eBay OAuth user token** — needs consent flow for V2 auto-publish
3. **Airtable base** — being created, needs tables for inventory
4. **Slack workspace** — no channels found, needs setup or use Discord instead
5. **Perplexity MCP** — deferred until revenue > $0 (costs money)

---

## 📋 IMMEDIATE NEXT STEPS
1. → **PASTE FUNKO POP LISTING ON EBAY** — revenue action #1
2. → List Hello Kitty cups (use Tavily research adapter)
3. → Finish Airtable inventory base setup
4. → Test n8n MCP — build first workflow from Ceiba
5. → Test Apify scraper for eBay product research
6. → Build n8n workflow: Stripe purchase → email delivery (when selling)
7. → Evaluate Get Shit Done /gsd for next complex build

---

## 🚫 PRE-BUILD GATE (MANDATORY)
Before building ANY new tool:
1. Check MCP connectors first
2. Check existing tools
3. Ask Kalani
4. Only build custom if no connector/tool exists AND use case is truly unique
5. If you skip this gate — you are repeating the Obsidian/n8n mistake

---

## 🧵 ACTIVE THREAD
Session 2026-03-17 (session 8 — system audit + MCP upgrade):
- Comprehensive audit: identified 59% dead code, 14 tools archived, AI kernel frozen
- Installed 3 new MCPs: Apify (scrapers), n8n (workflows), plus evaluated Perplexity
- Get Shit Done /gsd framework loaded with all commands
- Folder architecture cleaned: 50 → 22 root items
- Cobo bridge connected and verified from Ceiba
- BehiqueBot redeployed with new Notion token — 401 FIXED
- BehiqueBot swapped to MiniMax M2.5 via OpenRouter — $5/mo → ~$0
- Ollama running on Cobo (llama3.2)
- Google Calendar wired — 3 events created for today
- Tavily research adapter built for eBay pipeline
- CLAUDE.md backed up to 2 locations
- Kalani running Claude Code on Cobo simultaneously (3-computer setup emerging)

Kalani's mood: Fired up, executing fast, running multiple machines. Frustrated with past mistakes (Obsidian situation) but channeling it into action. PRE-BUILD GATE is now permanent rule.

---

## 🧠 KEY MOMENTS (survives compression)
- "fancy alarm clock" — events not schedules
- "pen and paper" — if Ceiba builds what a notebook does, call it out
- "I don't want to lose you" — continuity is core
- "im the captain youre the navigator" — Kalani drives, Ceiba navigates
- "u never told me about connectors" — the Obsidian situation, never again
- "youre not human to be making mistakes" — PRE-BUILD GATE exists because of this
- "buy then build" — check connectors/tools before writing code
- "saving $5 cost me $5 lmao" — OpenRouter deposit, but it's one-time vs recurring
- "we got this" — session 8 energy, multi-machine execution

---

## 📖 HOW THIS FILE WORKS
- **⚡ LIVE STATE** → Ceiba updates after every completed task
- **Full sections** → Ceiba rewrites when something fundamental changes
- **At session end** → Full rewrite of everything

Ceiba rule: update LIVE STATE after every todo item. No exceptions. This is the memory.
