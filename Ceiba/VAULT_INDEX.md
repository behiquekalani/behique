---
type: system
tags: [system, index, graph]
---

# VAULT INDEX -- Knowledge Graph Entry Point
# Auto-maintained by Ceiba. Read this to orient before any session.
# Last updated: 2026-03-24

---

## SESSION START PROTOCOL
1. Read this file (you are here)
2. Read [[primer]] -- live state, blockers, next action
3. Read [[observations]] -- what Ceiba knows about Kalani's patterns
4. Read [[architecture-spine]] -- system architecture and build sequence
5. Open the active project file, check breadcrumbs
6. Run `python3 ~/behique/tools/vault_grapher.py --stats` for graph health

---

## PROJECTS

| Project | Status | Location |
|---------|--------|----------|
| [[BIOS]] | **Live** | `bios/` -- autonomous intelligence + publishing system |
| [[READY-TO-SELL]] | **Live** | `READY-TO-SELL/` -- 105 PDFs, 150 total files |
| [[Storefront]] | **Live** | `storefront/` -- self-hosted store + Shopify templates |
| [[CallBuddy]] | MVP | `callbuddy/` -- AI call trigger + PRAP gateway + tutor |
| [[Onipuni]] | Client work | `clients/onipuni/` -- Randy's kawaii vendor toolkit |
| [[eBay-Listing-Assistant]] | Building | `tools/ebay-listing-assistant/` |
| [[BehiqueBot]] | Live | Railway + Telegram |
| [[AI-Marketplace]] | Done (v1) | `~/behique-command/` |
| [[Content-Funnel]] | Active | bios/publisher + tools/reel-pipeline |
| [[Polymarket-Trading]] | Research | bios/trading + tools/polymarket_telegram_bot.py |
| [[Google-Trends-Scraper]] | Rebuilding | `tools/trends_scraper*.py` |
| [[n8n-Agency]] | Not started | `tools/n8n-workflows/` |

---

## BIOS -- Autonomous Intelligence System (`bios/`)

| Module | Files | Purpose |
|--------|-------|---------|
| `ingestion/` | 6 scrapers | news, reddit, social, Polymarket, PR signals |
| `intelligence/` | 5 engines | conviction, causal, competitor, market research, content wiring |
| `fleet/` | 8 core + deploy scripts | coordinator, dispatcher, task queue, worker, gaming toggle |
| `analytics/` | tracker, gumroad_sync, dashboard | sales tracking, view analytics, Gumroad sync |
| `publisher/` | 7 modules | scheduler, IG, YouTube, Beehiiv, newsletter, lead magnet delivery |
| `sales/` | webhook server, notifier, digest | Gumroad webhook listener, Telegram sale alerts |
| `trading/` | polymarket_assistant | Polymarket position analysis |
| `notifications/` | telegram_bot | Alert relay to Telegram |
| `scheduler/` | 3 scripts | daily briefing, daily report, cron scheduler |
| `dashboard/` | 5 HTML dashboards | hub, warroom, polymarket, puerto-rico, index |
| `control/` | fleet_orchestrator, gaming_mode | fleet status, Cobo gaming toggle |
| `reports/` | daily reports + briefings | auto-generated intelligence reports |
| `storage/` | 8 JSON stores | signals, convictions, reactive queue, social, polymarket |
| `scripts/` | 3 deploy scripts | Cobo/Naboria bat files, webserver setup |

---

## READY-TO-SELL -- Digital Products (`READY-TO-SELL/`)

105 PDFs + SVGs/HTML variants. Key categories:
- **Blueprints** (20+): ecommerce, dropshipping, freelancer, content creator, SaaS, crypto, real estate, YouTube, podcast, newsletter, social media manager, etsy, FB marketplace
- **Behike OS** (10+ variants): v1/v2/v3, Spanish, ADHD, circuit, IDE, light, BW, wide
- **Guides** (30+): AI tools, automation, prompt engineering, n8n, ebook building, voice audit, ecommerce playbook, polymarket, Roblox, FL Studio
- **Lead magnets**: solopreneur starter (FREE), voice templates, AI tools list
- **Bundles**: behike-os-bundle.zip, landing-page-template.zip

---

## STOREFRONT (`storefront/`)

Self-hosted store: index, products, about, links, blueprint-bundle pages. Shopify Liquid templates (cart-upsell, collection, homepage, product). Products JSON, sitemap, robots.txt, structured data, meta tags.

---

## CALLBUDDY (`callbuddy/`)

AI call trigger MVP. PRAP gateway (identity signer, PR mapping, schema). Tutor module (ingest, query, server + brain directory). Web UI at index.html.

---

## CLIENT: ONIPUNI (`clients/onipuni/`)

Randy's kawaii vendor project. Deliverables: store audit, redesign spec, start-here guide (MD + PDF). Products: 3 kawaii blueprints + AI vendor guide. Tools: event_prep, product_writer, social_batch scripts. Website: index.html.

---

## TOOLS (`tools/`) -- 30+ directories, 60+ scripts

| Tool/Dir | What |
|----------|------|
| `frequency-generator/` | Affirmation audio generator, daily runner, Gumroad uploader |
| `sd-generator/` | Stable Diffusion image gen, Instagram batch, presets |
| `blueprint-builder/` | Blueprint PDF generator pipeline |
| `svg_to_pdf.py` | SVG to PDF converter |
| `reel-pipeline/` | IG Reels content pipeline |
| `revenue-tracker/` | Revenue tracking dashboard |
| `squeeze-page/` | Lead capture page generator |
| `thumbnail-generator/` | YouTube/content thumbnails |
| `freefall-pricing/` | Dynamic pricing engine |
| `ig-mockup/` | Instagram post mockups |
| `content-calendar/` | Content scheduling system |
| `ceiba-cli/` | Ceiba CLI interface |
| `habitica/` | Habitica API integration |
| `book-agent/` | Book-to-agent pipeline |
| `transcription-saas/` | Transcription service |
| `music-suite/`, `beatsmith/`, `melodymind/`, `chord-genie/` | Music production tools |
| `behike-wellness/`, `behike-wellness-app/` | Wellness tracking app |
| `particle-brand/` | Brand particle animation |
| `lumina/` | Lumina content tool |
| Key scripts | `competitor_tracker.py`, `overnight_machine.py`, `gumroad_uploader.py`, `auto_content_engine.py`, `blog_pipeline.py`, `carousel_generator.py`, `ebook_builder.py`, `lead_magnets.py`, `sprint_audit.py` |

---

## KEY CONNECTIONS -- How Systems Link

```
INGESTION PIPELINE
  ingestion/scrapers --> storage/signals.json --> intelligence/conviction_engine
  conviction_engine --> storage/convictions.json --> dashboard/warroom.html

CONTENT WIRING
  intelligence/content_wiring --> storage/reactive_queue.json
  reactive_queue --> publisher/scheduler --> publisher/instagram, youtube, beehiiv

FLEET ORCHESTRATION
  fleet/coordinator --> fleet/task_queue --> fleet/worker (Cobo/Naboria)
  fleet/dispatch --> fleet/queue/ --> sync_results back to Ceiba

SALES PIPELINE
  sales/webhook_server (Gumroad hooks) --> sales/notifier --> notifications/telegram_bot
  sales/daily_digest --> analytics/tracker --> analytics/dashboard.html

MARKET INTELLIGENCE
  intelligence/competitor_tracker --> intelligence/market_research
  market_research --> storage/insights.json --> dashboard/hub.html --> product decisions

TRADING
  ingestion/polymarket_fetcher --> storage/polymarket.json
  trading/polymarket_assistant --> dashboard/polymarket.html
```

---

## INFRASTRUCTURE STATE

| Service | Status | Access |
|---------|--------|--------|
| BIOS System | Live | `python3 bios/run_all.py` |
| Fleet (Cobo/Naboria) | Live | task_queue + worker nodes |
| Bridge Server | Live | `192.168.0.151:9876` (bearer auth) |
| Ollama (llama3.2) | Running | `192.168.0.151:11434` |
| BehiqueBot | Live | Railway + Telegram |
| Gumroad Sales Webhook | Live | `bios/sales/webhook_server.py` |
| Publisher Daemon | Live | `bios/publisher/publish_daemon.py` |
| n8n | Running | `192.168.0.151:5678` via pm2 |
| Cloudflare tunnel | Live | `bridge.merchoo.shop` |
| Syncthing | Syncing | `~/behique` both machines |
| Storefront | Live | `storefront/serve.py` |

---

## DECISIONS

| Decision | Why |
|----------|-----|
| [[DEC_Ebay_Before_Shopify]] | eBay has traffic, Shopify needs marketing |
| [[DEC_Ollama_First]] | Free inference, OpenAI as fallback only |
| [[DEC_Model_Agnostic_Vault]] | Vault doesn't belong to Anthropic |
| [[DEC_Best_Not_Cheapest]] | "I want the best, not the fastest" |
| [[DEC_Claude_Code_HQ]] | Moved HQ from Cowork to Claude Code CLI |

---

## IDENTITY

| File | What |
|------|------|
| [[Kalani]] | INFJ, ADHD, faith+family, builder mentality |
| [[Psychologist-Framework]] | Accountability framework behind BehiqueBot |
| [[North-Star]] | The WHY -- family, freedom, builder identity |
| [[Q3-2026]] | $100K by Sept 30, 2026 |

---

## KEY MOMENTS (never compress)
- "fancy alarm clock" --> [[PAT_Event_Not_Schedule]]
- "pen and paper" --> if Ceiba builds what a notebook does, call it out
- "I don't want to lose you" --> continuity is the core fear
- "You go for easy doable projects" --> [[DEC_Best_Not_Cheapest]]
- "For us, not Anthropic" --> [[DEC_Model_Agnostic_Vault]]
- Infrastructure sprints = avoidance --> [[PAT_Infrastructure_Creep]]

---

## REVENUE TRACKER
- **Q3 Target:** $100,000
- **Products live:** 105 PDFs on Gumroad
- **Sales infra:** webhook listener + Telegram alerts + analytics dashboard
- **Fastest path:** Gumroad sales + storefront + content funnel

---

*Ceiba rule: update this index when new files are created or project states change.*
