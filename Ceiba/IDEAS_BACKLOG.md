---
title: "IDEAS_BACKLOG"
type: unknown
tags: [ideas, backlog]
created: 2026-03-16
---

# IDEAS BACKLOG — Ceiba Idea Capture & Triage System
<!-- Updated: 2026-03-16 -->
<!-- Rule: Every ChatGPT/AI output gets logged here BEFORE implementation. Check DONE first to avoid rebuilds. -->

## How This Works
1. **Kalani pastes ChatGPT output** → Ceiba triages it here immediately
2. Each idea gets a status: `DONE`, `READY`, `BLOCKED`, `FUTURE`, `KILLED`
3. Before building anything, Ceiba checks this file to avoid duplicates
4. Ideas move between sections as blockers clear or priorities shift

---

## DONE — Already Built (do not rebuild)

| Idea | Source | Built By | Date | Where |
|------|--------|----------|------|-------|
| Vault knowledge graph scanner | ChatGPT Chat 4 | Ceiba | 2026-03-15 | `tools/vault_grapher.py` |
| --json flag for vault graph | ChatGPT Chat 4 | Ceiba | 2026-03-15 | `tools/vault_grapher.py` |
| Vault graph vis.js dashboard | ChatGPT Chat 3-4 | Ceiba | 2026-03-15 | `Ceiba/ceiba_dashboard.html` |
| Session stop hooks (summary + live state) | ChatGPT + Ceiba | Ceiba | 2026-03-15 | `.claude/hooks/stop_*.py` |
| Pre-push security scan hook | ChatGPT + Ceiba | Ceiba | 2026-03-15 | `.claude/hooks/pre_push_security.sh` |
| Vault context loader hook | ChatGPT + Ceiba | Ceiba | 2026-03-15 | `.claude/hooks/vault_context_loader.py` |
| vault-architect skill | ChatGPT Chat 4 | Ceiba | 2026-03-15 | `skills/vault-architect/` |
| Product research engine (core) | ChatGPT Chat 1-2 | Cobo | 2026-03-15 | `~/product_research_engine/` on Cobo |
| Scoring engine (0-100, 5 signals) | ChatGPT Chat 1 | Cobo | 2026-03-15 | `product_research_engine/core/scoring_engine.py` |
| Product normalizer (fuzzy dedup) | ChatGPT Chat 1 | Cobo | 2026-03-15 | `product_research_engine/core/normalizer.py` |
| Trends adapter (bridge to existing scraper) | ChatGPT Chat 1 | Cobo | 2026-03-15 | `product_research_engine/core/trends_adapter.py` |
| Amazon Playwright scraper (built, not working) | ChatGPT Chat 1 | Cobo | 2026-03-15 | `product_research_engine/scrapers/amazon.py` |
| Google Shopping scraper (built, selectors broken) | ChatGPT Chat 1 | Cobo | 2026-03-15 | `product_research_engine/scrapers/google_shopping.py` |
| Seed from trends workaround | Cobo initiative | Cobo | 2026-03-15 | `product_research_engine/seed_from_trends.py` |
| COBO Trends Intelligence dashboard | ChatGPT | Cobo | 2026-03-15 | `output/dashboard.html` |
| eBay Listing Agent V1 (full pipeline) | Kalani + Ceiba | Ceiba | 2026-03-16 | `tools/ebay-listing-assistant/` — 9 files: shipping, pricing, research, content gen, publisher, image handler, CLI |
| eBay V2 Publisher (API + OAuth) | Kalani + ChatGPT + Ceiba | ChatGPT→Ceiba | 2026-03-16 | `providers/ebay/publisher_v2.py` + `ebay_oauth_token.py` — auto-refresh, rate limit, policy mgmt, draft preview |
| eBay API Keys (Prod + Sandbox) | Kalani | Kalani | 2026-03-16 | `~/.behique_ebay_keys` + `~/.behique_ebay_keys_sandbox` (chmod 600) |
| Quest Dashboard V1 | ChatGPT | ChatGPT→Ceiba | 2026-03-16 | `Ceiba/quest-dashboard.html` — works but wrong aesthetic, needs pixel art rebuild |
| Quest Dashboard V2 — 3 theme modes | Ceiba | Ceiba | 2026-03-16 | `Ceiba/quest-dashboard.html` — Neon/Mono/Pastel toggle, localStorage persistence. Kalani said "beautiful" |
| Quick Lister (quick_list.py) | Ceiba | Ceiba | 2026-03-16 | `tools/ebay-listing-assistant/quick_list.py` — skip research, direct listing. Saves to `listings/` folder. |
| Session transcript persistence | Ceiba | Ceiba | 2026-03-16 | `Ceiba/07-Transcripts/` + `Ceiba/08-Images/` — survives context windows |
| Graph query layer (graph_query.py) | ChatGPT Chat 3 | Ceiba | 2026-03-16 | `tools/graph_query.py` — neighbors, search, shortest_path, hubs, context, 8 query methods. BFS + adjacency lists |
| wake.sh / sleep.sh for Comp2 | Kalani 2026-03-15 | Ceiba | 2026-03-16 | `bridge/wake.sh` + `bridge/sleep.sh` — health checks, CMP stats, session logging, Cobo ping |
| Jarvis morning briefing | Kalani 2026-03-15 | Ceiba | 2026-03-16 | `tools/morning_briefing.py` — 8 data sources (primer, git, CMP, vault, bridge, backlog, Cobo, sessions) |
| Session finish-tracker skill | Kalani 2026-03-16 | Ceiba | 2026-03-16 | `tools/session_tracker.py` — plan vs actual, fuzzy matching, drift detection, red flags, forensics reports |
| Prompt injection defense skill | Kalani 2026-03-16 | Ceiba | 2026-03-16 | `skills/prompt_guard.py` — 50+ regex patterns, base64 decode, unicode detection, 0-100 scoring |
| Agent Kernel architecture (full implementation) | ChatGPT 2026-03-16 | Ceiba | 2026-03-16 | `tools/ai_agent_kernel/` — main.py, kernel_dispatcher.py, ceiba_client.py, cobo_server.py, 5 skills |
| Ceiba Memory Protocol (CMP) implementation | ChatGPT 2026-03-16 | Ceiba | 2026-03-16 | `tools/ai_agent_kernel/cmp.py` — 480 lines, SQLite, SHA256 integrity, conflict resolution, CLI |
| Ceiba-Cobo Communication Protocol (CCP) implementation | ChatGPT 2026-03-16 | Ceiba | 2026-03-16 | gRPC pipeline: ccp.proto + ceiba_client.py + cobo_server.py — retry, heartbeats, CMP logging |
| Ghost node vault files (27 created) | ChatGPT Chat 4 | Ceiba | 2026-03-16 | 27 vault stubs: DEC_*, PAT_*, SYS_*, TOOL_*, projects. Graph: 41→83 nodes, 260→323 edges, 35→10 missing |
| Session auto-generator (session_logger.py) | ChatGPT Chat 3 | Ceiba | 2026-03-16 | `tools/session_logger.py` — auto-creates SES_ vault files with YAML frontmatter, project/tool links |
| ceiba_run.py orchestrator | ChatGPT Chat 3 | Ceiba | 2026-03-16 | `tools/ceiba_run.py` — rebuild graph → export hub.json → morning briefing → session context |
| Prompt quality comparator skill | Kalani 2026-03-16 | Ceiba | 2026-03-16 | `skills/prompt_comparator.py` — 3 backends (Ollama/OpenAI/Anthropic), 6 criteria, heuristic scoring |
| hub.json export for live dashboard | Ceiba | Ceiba | 2026-03-16 | `tools/export_hub_data.py` — aggregates git, CMP, vault, sessions, backlog → hub.json for dashboards |
| Behique Command Hub (N64 retro) | Kalani + Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` — 3 tabs (Hub/Quests/Completed), N64 pixel aesthetic, quest filters (sort by difficulty, filter by type/status), hub.json live data, auto-refresh |
| eBay Telegram /ebay command | Kalani + Ceiba | Ceiba | 2026-03-16 | `modules/ebay_command.py` — parses `/ebay "Product" price condition weight cost`, calls quick_list(), sends formatted listing via Telegram. Wired into main.py |
| Unified CLI orchestrator (ceiba command) | ChatGPT Chat 3 | Ceiba | 2026-03-16 | `tools/ceiba` — single entry point: start, briefing, graph, session, export, wake, sleep, list, status. Aliases for speed (g/s/l/st) |
| Self-healing vault (vault_healer.py) | ChatGPT Chat 4 | Ceiba | 2026-03-16 | `tools/vault_healer.py` — scans for missing targets, orphans, duplicates, dead links, missing frontmatter. --fix auto-creates stubs + adds YAML headers. Health: 60→90 |
| Memory Ingestion Protocol | Ceiba | Ceiba | 2026-03-16 | `tools/memory_ingest.py` — extracts decisions/ideas/blockers/mood from sessions+transcripts+git, auto-tags projects/tools/patterns, writes to CMP. 11 memories from day 1. `ceiba ingest` CLI |
| Quest Dependency Graph (vis.js MAP tab) | Kalani + Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` MAP tab — force-directed graph where quests are nodes, edges show dependencies. Click node → objectives. Node size = progress% |
| Browse tab (flat objectives search/sort) | Kalani + Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` BROWSE tab — search all objectives, sort by difficulty/reward/time/name, hide done toggle, stats bar |
| Dashboard V3 (5 tabs + updated quest data) | Kalani + Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` — HUB/QUESTS/BROWSE/MAP/COMPLETED tabs. Updated quest data: 42 done objectives tracked |
| Vault Template System (7 templates + CLI) | Ceiba | Ceiba | 2026-03-16 | `tools/vault_templates.py` — project/tool/decision/pattern/design/check-in/knowledge templates. Auto-upgrades stubs from vault_healer. Smart type detection by name. `ceiba template` CLI |
| YAML Typed Relationships in vault_grapher | ChatGPT Chat 3 | Ceiba | 2026-03-16 | `tools/vault_grapher.py` — parses YAML frontmatter (tools/systems/projects/patterns/decisions/sessions), creates typed edges (uses_tool/uses_system/etc). 39 typed relationships extracted. `graph_query.py rels` command + `rel-types` + `--reverse` flag |
| HABITS tab (daily habit tracker + streaks) | Kalani + Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` HABITS tab — 8 habits (revenue/build/health/growth/faith/relationships), click-to-toggle, 7-day mini heatmap, streak counter, localStorage persistence. Dashboard V3.1 |
| Graph-aware context engine | Ceiba | Ceiba | 2026-03-16 | `tools/vault_context_engine.py` — queries vault graph via typed relationships to find relevant context for any topic/prompt/CWD. Replaces dumb CWD→file mappings. `ceiba context` CLI. Wired into vault_context_loader.py hook |
| MAP hover-triggered path highlighting | Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` MAP tab — hover a quest node to highlight all connected paths (2-degree BFS), dim unrelated nodes. Blur restores. Dashboard V3.2 |
| Command Hub 3-theme toggle (Neon/Mono/Pastel) | Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` — NEON (full N64), MONO (greyscale low-dopamine), PASTEL (soft warm light). localStorage persistence. CSS custom properties swap |
| Load quests from external quests.json | Ceiba | Ceiba | 2026-03-16 | `Ceiba/behique-hub.html` + `Ceiba/quests.json` — dashboard fetches quest data from JSON file instead of inline. Auto-refresh. 60/92 objectives (65%) properly tracked |

---

## READY — Can Build Now (dependencies met)

| Idea | Source | Blocker Cleared | Priority | Notes |
|------|--------|-----------------|----------|-------|
| eBay Listing Agent V2 — API auto-publish | Kalani 2026-03-16 | eBay API keys obtained ✅ | HIGH | Swap EbayManualPublisher → EbayAPIPublisher using Sell/Inventory API. No more copy-paste. publisher_v2.py + ebay_oauth_token.py built. Need OAuth flow completion. |

---

## BLOCKED — Good Idea, Waiting On Something

| Idea | Source | Blocked By | Unblocks When | Priority |
|------|--------|------------|---------------|----------|
| eBay cross-reference engine | ChatGPT Chat 1 | eBay API keys ✅ — needs OAuth user token | OAuth flow completed | HIGH |
| Real scoring with margin/competition | ChatGPT Chat 1 | eBay API keys ✅ — needs OAuth user token | OAuth flow completed | HIGH |
| Amazon scraper with stealth+proxies | ChatGPT Chat 1 | Residential proxies on Cobo | proxies.txt copied to Cobo | MEDIUM |
| Walmart scraper | ChatGPT Chat 3 | Core scrapers need to work first | Amazon/eBay pipeline proven | LOW |
| Product clustering (group variants) | ChatGPT Chat 3 | Needs enough products in DB | eBay API populates real data | MEDIUM |

---

## FUTURE — Good Ideas, Not Yet Time

| Idea | Source | Why Not Now | Revisit When |
|------|--------|-------------|--------------|
| Real embeddings for vault search | ChatGPT Chat 4 | Vault now has 83 nodes ✅ — memory ingestion built ✅ | After ingestion proven with 30+ days of data |
| ~~Graph-aware prompting (auto-load context by graph distance)~~ | ~~ChatGPT Chat 4~~ | ~~DONE~~ | ~~DONE — `tools/vault_context_engine.py` with typed relationship traversal + `ceiba context` CLI~~ |
| AI price predictor (ML on historical scores) | ChatGPT Chat 3 | Need months of scoring data first | 90 days of scores in DB |
| AI title generator for eBay listings | ChatGPT Chat 3 | Need working listings first | First 10 eBay sales |
| Multi-model vault agent (route queries by type) | ChatGPT Chat 4 | Over-engineering right now | System is complex enough to need it |
| Dashboard semantic query (AI query → highlight related nodes) | ChatGPT Chat 3 | Needs embedding_index.json | After real embeddings built |
| Dashboard auto-orphan link suggestions | ChatGPT Chat 3 | Needs embedding_index.json | After real embeddings built |
| Dashboard animated pulsing edges on query | ChatGPT Chat 3 | Cosmetic, needs semantic query working | After semantic query works |
| ~~Dashboard hover-triggered live paths~~ | ~~ChatGPT Chat 3~~ | ~~DONE~~ | ~~DONE — MAP tab hover highlights connected paths, dims unrelated, 2-degree BFS~~ |
| Neo4j/ArangoDB graph upgrade | ChatGPT Chat 3 | Markdown graph works fine for now | 100+ nodes with complex queries |
| Graph service for AI cluster workers | ChatGPT Chat 3 | No workers need it yet | Multiple AI workers querying vault |
| ~~YAML metadata for typed relationships~~ | ~~ChatGPT Chat 3~~ | ~~DONE~~ | ~~DONE — vault_grapher.py parses 6 YAML relationship fields + graph_query.py rels command~~ |
| Vault wiki-link strategy (typed link conventions, structured sections) | ChatGPT Chat 3 | Already partially implemented | Next vault cleanup pass |
| ~~Vault template system~~ | ~~ChatGPT Chat 3~~ | ~~DONE~~ | ~~DONE — `tools/vault_templates.py` with 7 templates + ceiba CLI~~ |
| ~~Quest/Journal dashboard habit tracker~~ | ~~Kalani 2026-03-16~~ | ~~DONE~~ | ~~DONE — HABITS tab with 8 habits, streaks, 7-day heatmap, localStorage~~ |
| Book-to-Agent system | Comp2 2026-03-16 | Big concept, needs design | After core revenue flowing. Turn books into interactive AI tutors. |
| Colmena66 AI consulting play | Comp2 2026-03-16 | Need proven portfolio first | After 3+ automation projects done. PR startup accelerator = potential client. |
| Tamagotchi Pi companion device | Comp2 2026-03-16 | Quest dashboard needs to work first | After dashboard proven. Physical Raspberry Pi in 3D-printed cube on desk. |
| Digital twin system | Comp2 2026-03-16 | Over-engineering for now | When multiple agents handle distinct domains. |
| PR Government AI consulting | Comp2 2026-03-16 | Need credibility first | After n8n agency has 5+ clients. |
| Multi-model description A/B testing | Kalani 2026-03-16 | Need working listings + sales data | After 10+ eBay listings. Test Claude vs ChatGPT vs Ollama descriptions, measure which sells faster. |
| Dropship auto-lister (scraper → eBay pipeline 24/7) | Kalani 2026-03-16 | Need eBay API + working scrapers | After V2 API publisher + product research engine proven end-to-end. Workers auto-list from Amazon/Walmart to eBay. |
| OpenClaw as central agent management hub | Kalani 2026-03-16 | OpenClaw needs more skills deployed | After 5+ agents/skills proven. Central dispatch for all bots and automation. |
| Pixel art city simulator dashboard | Kalani 2026-03-16 | Fun but not priority | After quest dashboard proves the concept. Visual city where buildings represent projects. |
| Autonomous cross-computer communication | Kalani 2026-03-16 | Bridge is basic HTTP, need full agent protocol | After bridge proven + secure. Ceiba autonomously triggers Cobo sessions, controls browser to interact with ChatGPT, no human copy-paste relay needed. |
| Swarm Mode / Worker Spawning architecture | Kalani + ChatGPT 2026-03-16 | Over-engineering for now | After 3+ working agents. Workers can spawn new workers. AI-TASK protocol with structured task schemas. Ceiba only supervises. |
| Overnight autonomous scraping pipeline | Kalani 2026-03-16 | Need reliable scraper first | After trends scraper rebuild. Scheduled work sessions that run while Kalani sleeps. Scrape → score → queue listings. |
| Viral Vault scoring methodology | Kalani 2026-03-16 | Need product research engine working | After eBay API data flowing. 15-point scoring checklist from Viral Vault adapted for our product scoring engine. |
| Tamagotchi as mobile app (not just Pi) | Kalani 2026-03-16 | Quest dashboard needs to work first | After Pi version. React Native or PWA companion app that shows tamagotchi reacting to progress. |
| ~~Low-dopamine mode for all dashboards~~ | ~~Kalani 2026-03-16~~ | ~~DONE~~ | ~~DONE — Command Hub has Neon/Mono/Pastel toggle, localStorage persisted~~ |
| Social anxiety phone call bot | Kalani 2026-03-19 | Needs voice AI API (Vapi/Bland.ai/Retell) + use case validation | After revenue flowing. AI bot that makes phone calls on behalf of people with social anxiety. Books appointments, calls businesses, handles hold times. Massive TAM (~15M US adults). Could be SaaS or per-call pricing. |
| ~~Ecommerce Playbook ebook~~ | ~~Kalani 2026-03-19~~ | ~~DONE~~ | ~~DONE -- PDF at ~/behique/ebooks/ecommerce-playbook.pdf (1,041 pages, 3.8MB). Ready for Gumroad.~~ |
| Claude Code Mastery Guide | Kalani 2026-03-19 | Only 6 transcripts, thin content | After ebook pipeline proven. 6 Claude Code course transcripts, could be $5-9 mini-guide. |
| ~~AI Agent Installation Service~~ | ~~Kalani 2026-03-19~~ | ~~DONE~~ | ~~DONE -- Landing page at products/ai-agent-landing.html. Case study written. Service tiers defined.~~ |
| ~~Instagram Content Pipeline~~ | ~~Kalani 2026-03-19~~ | ~~DONE (infrastructure)~~ | ~~DONE -- 35 reel briefs, local pipeline built (Kokoro TTS + MLX SD + FFmpeg). Needs Instagram accounts from Kalani.~~ |
| Course content as ebook series | Kalani 2026-03-19 | 368 transcripts available, need formatting pipeline | After first ebook. Gaming KB (120 videos), Claude Code KB (6 videos). Could be a series. |
| DotCom Secrets + $100M Offers implementation | Kalani 2026-03-19 | Strategy documented, needs execution | NOW. Value ladder, funnel, Hormozi offer framework applied to all products. |
| ~~Meditation app as product/lead magnet~~ | ~~Kalani 2026-03-19~~ | ~~DONE~~ | ~~DONE -- Standalone HTML at products/meditation-app.html. Multiple breathing patterns, ambient audio, session history, streaks. Ready for Gumroad.~~ |
| Business Automation Audit (free lead magnet) | Kalani 2026-03-19 | Need template + landing page | After service offering finalized. 30-min audit, identify 3 AI automation opportunities. Door opener for agent installation service. |

---

## KILLED — Evaluated and Rejected

| Idea | Source | Why Killed | Date |
|------|--------|------------|------|
| Google Shopping CSS selector fix | ChatGPT Chat 1 | Fragile, Google changes DOM constantly. Trends + eBay API is the real pipeline. | 2026-03-15 |
| SerpAPI for product discovery | ChatGPT Chat 3 | Costs money. Free trends scraper works. | 2026-03-15 |

---

## Process Notes
- **Before building anything:** `grep` this file for the idea name first
- **When Kalani pastes ChatGPT output:** Triage every idea into the right section immediately
- **Weekly:** Review BLOCKED section — have any blockers cleared?
- **Ceiba responsibility:** Update this file at the end of every session that produces new ideas

## AI News Brand (like ohmo.ai)
- **Full vision:** AI/tech news reporting brand. Covers new AI apps, tech CEO drama, NVIDIA announcements, investor tweets, Claude updates, market-moving events
- **News tracking system:** ForexFactory-style impact ratings (low/medium/high), track key investors + their tweets, auto-capture major events. BUILT: `tools/ai_news_tracker.py` -- 18 RSS feeds (TechCrunch, Verge, Reddit, HN, etc), impact scoring, HTML digests
- **Sources tracked:** Reddit (8 subs), HackerNews, TechCrunch, The Verge, OpenAI/Anthropic/Google/NVIDIA blogs, VentureBeat, MIT Tech Review, Ars Technica
- **Content types:** Carousel posts (ohmo.ai style), daily news recap reels, tool reviews, market impact analysis
- **Differentiator:** Bilingual (EN/ES) + AI-native production pipeline + custom art per post
- **Revenue:** YouTube/TikTok/IG monetization, sponsorships, affiliate links to tools reviewed
- **Status:** News tracker BUILT and pulling 200+ articles. Brand plan at content-empire/ai-news-brand-plan.md.
- Priority: HIGH (aligns with Kalani's passion + AI expertise + content pipeline already built)
- Added: 2026-03-20

## VTuber Personal Brand (SEPARATE PROJECT -- FORK)
- Custom avatar rig (like @theburntpeanut), uses Kalani's face/expressions via face tracking
- Custom animations (dancing, sitting, reactions), persistent character across all content
- Tech: Face tracking (VSeeFace/Live2D/VMagicMirror), OBS integration, expression mapping
- This is Kalani's PERSONAL brand, separate from the AI news brand
- Priority: FUTURE (after AI news brand is running)
- Added: 2026-03-20

## Text Shape Generator (Robert Greene style)
- Tool that formats paragraphs into visual shapes (diamond, hourglass, triangle, etc)
- Robert Greene uses this extensively in Mastery, Art of Seduction, 48 Laws of Power
- Could be HTML tool or Python script
- Use case: content creation, product design, social media posts
- Priority: Low (nice-to-have tool)
- Added: 2026-03-20

## AI Pose/Expression Photo App
- Take a normal photo, AI modifies your pose, smile, expression, etc.
- Two modes: (1) Keep the AI-modified pic as-is, (2) Use it as a guide to match the pose yourself then retake
- Like a "photo coach" that shows you how to look better in photos
- Could use ControlNet/OpenPose for pose detection + img2img for modification
- Revenue model: freemium app, free basic filters, $4.99/mo for premium AI poses
- Competition: FaceApp (but that's filters, not pose coaching), Lensa (AI portraits)
- Unique angle: the "coach mode" where it guides you into the pose is novel
- Tech: React Native + on-device ML or API to Cobo/cloud
- Priority: IDEA STAGE (capture only, build later)
- Added: 2026-03-21

## YouTuber Outreach Bot (Influencer Marketing Automation)
- Bot that finds YouTubers in specific niches (Shopify, ecommerce, dropshipping, AI tools)
- Scrapes their email from channel About page, description, or linked socials
- Auto-generates personalized outreach email offering free product access in exchange for a mention/review
- Example: "Hey [name], I built 3 Shopify themes. Want free access? Use one in a video and keep it."
- The deal: free theme ($49.99 value) in exchange for 30 seconds in a video. ROI is insane.
- Could expand to any product: free AI Employee Guide to tech YouTubers, free templates to finance YouTubers
- Tech stack: YouTube Data API (channel search, about page), Apify for email scraping, n8n for automation pipeline, Ollama for personalized email drafting
- Pipeline: Search niche -> Filter by subscriber count (1K-100K sweet spot, micro-influencers) -> Scrape email -> Generate personalized pitch -> Send via Gmail API or SMTP -> Track responses
- Why micro-influencers: 1K-100K subs have higher engagement, actually read emails, more likely to feature small brands
- Machine: Cobo (n8n + Ollama for email drafting), Ceiba (YouTube API queries)
- Dependencies: Products listed on Gumroad first (need real URLs to share)
- Revenue model: Not a product to sell. This is a GROWTH tool for our own products.
- Could later be productized as a SaaS ("Influencer Outreach Bot" for other sellers)
- Priority: HIGH after products are listed. This is the growth engine.
- Added: 2026-03-21

## AI Chatbot Setup Guide ($4.99)
- Quick guide teaching people how to add an AI chatbot to ANY website
- What you teach: install Ollama, create a system prompt about their business, build a simple API endpoint, drop in the chat widget JS
- You already have all the code: chat-widget.js + Cobo's FastAPI server + Ollama setup
- Package as: short PDF (2,000-3,000 words) + the chat-widget.js file + server template code
- Selling point: "Add AI customer service to your website in 30 minutes. $0/month. Runs on your own computer."
- Target audience: small business owners, Shopify store owners, freelancers with portfolios
- Could pair with the AI Employee Guide as an upsell
- This is literally what we built tonight, just packaged as a tutorial
- Priority: HIGH (quick to build, you have all the code, $5 impulse buy price)
- Added: 2026-03-21

## "Claude Code for Non-Coders" Course (Remake)
- Original course exists but has poor execution: thick accent hard to understand, outdated examples, no AI-enhanced production, bad pacing
- The MARKET IS VALIDATED. People want this. The original sold despite being bad.
- Our version: clear voice (yours or TTS), modern examples, AI-assisted production, bilingual (EN + ES)
- You have the claude-code knowledge base (6 sessions transcribed) as topic reference
- Structure: 10 short video lessons (5-10 min each) + companion PDF
- Sell on Gumroad as video course ($19.99-$29.99)
- Also split into individual YouTube videos as free content -> funnel to paid course
- Your edge: you actually USE Claude Code daily. You built 170+ files in one session with it.
- The companion PDF can be another $4.99 quick guide
- Spanish version = zero competition in LATAM
- Priority: HIGH (validated market, you have the knowledge, just needs recording)
- Added: 2026-03-21

## Mac App Gap Filler (Shower Idea 1)
- Find niche software that only runs on Windows/Linux and has no Mac version
- Build Mac-native alternatives for these gaps
- Example: Yomas couldn't view biology graphics/charts on Mac because the program is Windows/Linux only
- Scientific/academic software is a HUGE gap on Mac (bioinformatics, lab tools, data visualization)
- Strategy: search for "no Mac version" complaints on Reddit, GitHub issues, forums
- Build lightweight Mac alternatives using Swift/SwiftUI or Python+tkinter
- Revenue: freemium app or one-time purchase on Mac App Store
- Could use AI to auto-port simple tools (translate Python Windows scripts to Mac-compatible)
- Also applies to dead/abandoned software whose devs stopped updating
- Priority: IDEA STAGE (research which gaps have the most demand first)
- Added: 2026-03-21 (voice note, Spanish)

## Video-to-Text Transcription SaaS (Shower Idea 2)
- Web app: paste any video URL (Instagram, YouTube, TikTok, Facebook), get text transcript
- YOU ALREADY HAVE THE PIPELINE: ceiba_transcribe.py uses yt-dlp + Whisper
- Monetization: free tier (3-5 transcripts/day), account required for more, credit system
- Kalani currently uses a competitor's free tier for this exact thing
- The competitor charges credits after the free tier. We can do the same.
- Tech: Flask/FastAPI web UI + yt-dlp + Whisper + user auth + Stripe/credits
- Host on Hutia or Cobo (Whisper runs locally, $0 per transcript)
- Add features competitors don't have: Spanish support, summary mode, chapter detection, export to PDF
- Security: audit for personal info, secure domain, no data leaks
- This is a REAL SaaS with recurring revenue potential
- Priority: HIGH (you have the code, just needs a web UI and auth)
- Machine: Cobo (GPU for faster Whisper) or Hutia (CPU, slower but always-on)
- Added: 2026-03-21 (voice note, Spanish)

## Reddit Niche Crawler (Product Research)
- Crawl Reddit for complaints about missing software, bad tools, unserved niches
- Subreddits: r/mac, r/macapps, r/bioinformatics, r/software, r/SaaS, r/startups, r/Entrepreneur
- Search patterns: "no Mac version", "wish there was", "looking for alternative", "this app is dead"
- Score by upvotes + comment count = demand validation
- Each complaint with 50+ upvotes = potential product
- Tech: Reddit RSS (already in ai_news_tracker.py) or Reddit API + scoring
- Machine: Cobo or Hutia (cron, overnight)
- Priority: MEDIUM (research infrastructure)
- Added: 2026-03-21

## Reddit Story Channel (Automated Content)
- Read Reddit stories aloud with TTS over background video
- Subreddits: r/tifu, r/AmItheAsshole, r/MaliciousCompliance, r/pettyrevenge, r/entitledparents
- YOU ALREADY HAVE THE PIPELINE: reel-pipeline (story JSON -> TTS -> video -> captions)
- Just swap nostalgia stories for Reddit stories
- Platforms: YouTube (long form 8-15 min), TikTok, Reels, X.com, Threads
- Also meme channel: r/memes, r/ProgrammerHumor, r/meirl -> post to all platforms
- Monetization: YouTube AdSense, TikTok creator fund, cross-promo to products
- Zero face. Zero original writing. 100% automatable with existing tools.
- Cross-post to: Instagram Reels, TikTok, YouTube Shorts, X.com, Threads
- Could run multiple channels: stories, memes, AI news, all automated
- Priority: HIGH (low effort, high volume, passive ad income)
- Added: 2026-03-21

## Behike Hub Website (Personal Portfolio + Playground)
- Personal website that documents EVERYTHING Kalani has built
- Merge styles: VHS lines from dashboard v3 + Apple minimalist + calligraphy aesthetic
- Sections: Journal/blog, project showcase, interactive creations, product store
- Embedded playable Minecraft (JS Minecraft clone like ClassiCube or voxel.js)
- Interactive demos: meditation app, agent faces, music player, text shaper
- Color scheme switcher (8 themes from settings widget)
- Font size control
- Journal/blog for documenting the build journey (great for @kalaniandrez content too)
- VHS aesthetic: scanlines, glitch effects, CRT glow, but clean and readable
- Apple aesthetic: system fonts, minimal layout, generous whitespace
- Calligraphy: Playfair Display or similar serif for headlines
- This becomes the main hub that bio-link page points to
- Priority: HIGH (this is the brand, the portfolio, the proof)
- Social media feeds: embed Instagram posts, YouTube videos, X posts via their embed APIs
- Auto-update: RSS or API pulls latest content so the site is always fresh
- Blog posts written here show as content on all platforms (write once, distribute everywhere)
- Added: 2026-03-21
- Tech: React Native + on-device ML or API to Cobo/cloud
- Priority: IDEA STAGE (capture only, build later)
- Added: 2026-03-21

## Web3 MySpace Revival (Platform Vision)
- The future: AI makes websites as easy as posting a photo
- Everyone will have a personal website (like MySpace profiles but modern)
- Need a NEW web to browse, discover, and visit people's sites
- Like MySpace + Web3 + AI website builder combined
- People customize their site (like Behike OS), visit others, interact
- Security-first (the current web isn't built for this scale of personal sites)
- Revenue: platform fees, premium features, hosting, themes marketplace
- This is a PLATFORM not a product. Needs funding/team eventually.
- But we can start by making Behike OS into a template others can fork
- Priority: VISION (long-term, capture now, build after revenue)
- Added: 2026-03-21

## AI Music Studio (Multi-Genre Web Synth)
- Expand the trance synth into a full multi-genre music maker in the browser
- Genres: Trance, Lo-fi, Ambient, Trap, Reggaeton, House, Chillwave
- Each genre has preset scales, tempos, drum patterns, synth sounds
- Users create music in the browser, export as WAV
- This is a TRAFFIC MAGNET. People come to play with it, discover products.
- Competition: very few browser-based AI music tools
- Could be standalone product or embedded in Behike OS
- Tech: Web Audio API, no external deps, pure JS
- Priority: HIGH (brings traffic to website, fun, shareable)
- Added: 2026-03-21

## Particle Cloud Face Rework (Viral Visual)
- Current agent faces look basic. Need particle/point cloud style like the LILYGO reels (86K+ likes)
- Reference: dense particle systems forming recognizable face shapes
- Thousands of tiny dots that flow, breathe, react
- Could use photo-to-particle conversion (sample pixels from a face image, convert each to a particle)
- Or use 3D face mesh data points rendered as particles
- Tech: Canvas 2D with thousands of particles, or WebGL for performance
- The face should feel alive: particles drift, react to mouse, pulse with audio
- This is content by itself. Film the face on screen, post as reel. Viral format.
- Reference images saved at: Ceiba/reference/behike-os-inspiration/
- Priority: HIGH (viral content potential, brand identity)
- Added: 2026-03-21

## Web Volca / Grid Sampler (2026-03-23)
Source: Kalani listening to Thomas Bangalter "Trax on da Rocks" (1995)
Insight: Raw, simple music > overproduced. Constraints create personality.
Concept: Browser-based sampler sequencer. 8-16 pads, load samples, grid sequence, play. 
No complexity. Analog-feel UI. Dark, minimal, monochrome.
Like a Volca Sample but in the browser.
Product angle: Free version drives traffic, $9.99 with sample packs.
Connects to: existing BeatSmith/ChordGenie/MelodyMind tools
Priority: FUTURE (capture now, build later)
Tags: music, product, web-app, simplicity

---

## Discord Community (Behike Builders)
- **Status:** FUTURE
- **What:** Discord server auto-linked to Gumroad. Every free download = community member.
- **Plan at:** `Ceiba/projects/DISCORD_SERVER_PLAN.md`
- **Effort:** Quick (10 min to create)
- **Priority:** After first 10+ downloads. No point having a server with 0 people.
