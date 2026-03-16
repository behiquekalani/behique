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

---

## READY — Can Build Now (dependencies met)

| Idea | Source | Blocker Cleared | Priority | Notes |
|------|--------|-----------------|----------|-------|
| Create 35 ghost node vault files | ChatGPT Chat 4 | vault_graph.json exists | LOW | YAML frontmatter stubs for missing targets in vault graph |
| Graph query layer (graph_query.py) | ChatGPT Chat 3 | vault_graph.json exists | MEDIUM | neighbors(), find_by_type(), tools_for_project(), graph_context() — lets Ceiba query graph programmatically |
| Session auto-generator (session_logger.py) | ChatGPT Chat 3 | vault exists | MEDIUM | Auto-creates structured SES_ files with links to projects, tools, decisions, patterns |
| ceiba_run.py orchestrator | ChatGPT Chat 3 | graph + session logger built | LOW | One-command: rebuild graph → generate embeddings → log session → output Claude prompt context |
| wake.sh / sleep.sh for Comp2 | Kalani 2026-03-15 | Can build now | HIGH | One script to start all services (Ollama, bridge, Obsidian API), one to stop them. "Power button" for the AI cluster. |
| Discord server as content hub | Kalani voice memo 2026-03-16 | Can build now | HIGH | Discord server to store/preview AI-generated content (reels, animations). Visual review before publishing. Webhook integration with n8n. |
| Content approval pipeline | Kalani voice memo 2026-03-16 | Discord server exists | HIGH | Flow: content generated → preview (localhost or Discord embed) → Kalani approves via Discord/Telegram → auto-upload. n8n orchestrates. |
| Localhost visual preview for reels/animations | Kalani voice memo 2026-03-16 | Can build now | MEDIUM | Local web server to render and preview AI-generated animations/reels visually before they go out. Could be a simple HTML dashboard. |
| n8n → Discord webhook pipeline | Kalani voice memo 2026-03-16 | Discord server + n8n running | MEDIUM | Pattern from video: trigger → process → summarize → Discord webhook. Adapt for content approval, not just news. |
| Jarvis morning briefing | Kalani 2026-03-15 | Need wake.sh + primer.md | HIGH | "Good morning Ceiba" → overnight summary, project status, today's priorities, blockers cleared, what Cobo did. Like the Jarvis reel transcript. |
| Use Ralph Loop for autonomous task completion | Kalani 2026-03-15 | Plugin already installed | HIGH | `/ralph-loop` — set task + completion promise, walk away. Use for dashboard polish, eBay API wiring, any well-defined build task. |
| eBay Listing Agent V2 — Telegram bot `/ebay newlisting` | Kalani 2026-03-16 | V1 pipeline built | HIGH | Telegram command → LLM pipeline → auto-list. Format: `/ebay newlisting "Name" (qty) #tags`. Route through BehiqueBot or separate bot. |
| eBay Listing Agent V2 — API auto-publish | Kalani 2026-03-16 | eBay API keys obtained ✅ | HIGH | Swap EbayManualPublisher → EbayAPIPublisher using Sell/Inventory API. No more copy-paste. publisher_v2.py + ebay_oauth_token.py built. Need OAuth flow completion. |
| Prompt quality comparator skill | Kalani 2026-03-16 | Can build now | MEDIUM | Skill that takes a prompt, runs through multiple LLMs, evaluates/combines best output. Multi-model prompt A/B testing at skill level. |
| Session finish-tracker skill | Kalani 2026-03-16 | Can build now | HIGH | Tracks planned-vs-completed work across sessions. "Did we finish what we planned?" accountability system. ADHD-critical. |
| Prompt injection defense skill | Kalani 2026-03-16 | Can build now | MEDIUM | Skill to prevent prompt injection when agents browse the web. Security layer for autonomous browsing tasks. |

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
| Discord voice cowork — Jarvis mode | Kalani voice memo 2026-03-16 | Needs Voice body part built, real-time API access (OpenAI Realtime or future Claude voice), screen capture pipeline | Month 4+ on spine, after Senses + Hands + Nervous System proven |
| Personal passive dashboard | Kalani 2026-03-16 | Simple visual dashboard — project states, revenue tracker, vault health. Web-based (HTML/CSS/JS). Can run on Raspberry Pi as dedicated physical display. BUILD TOMORROW ASAP. | Ready now — build 2026-03-17 |
| AI tamagotchi quest companion | Kalani 2026-03-16 | AI-powered pixel art companion. Reads vault, generates quests from real project state. Psicólogo framework as brain. Evolves visually with progress. Raspberry Pi inside 3D-printed cube enclosure. Visual options: smiley face companion OR pixel art city that grows with progress. Builds on top of passive dashboard. | After passive dashboard works |

| Idea | Source | Why Not Now | Revisit When |
|------|--------|-------------|--------------|
| Memory ingestion protocol (auto-tag sessions) | ChatGPT Chat 4 | Vault needs more content first | Vault has 60+ real nodes |
| Real embeddings for vault search | ChatGPT Chat 4 | Need enough content to make it useful | Vault has 60+ real nodes |
| Self-healing vault (auto-detect stale links) | ChatGPT Chat 4 | vault_grapher already handles this partially | After ghost nodes created |
| Graph-aware prompting (auto-load context by graph distance) | ChatGPT Chat 4 | vault_context_loader does basic version | After vault grows |
| AI price predictor (ML on historical scores) | ChatGPT Chat 3 | Need months of scoring data first | 90 days of scores in DB |
| AI title generator for eBay listings | ChatGPT Chat 3 | Need working listings first | First 10 eBay sales |
| Orchestrator (unified CLI for all tools) | ChatGPT Chat 3 | Individual tools need to work first | 3+ tools proven |
| Multi-model vault agent (route queries by type) | ChatGPT Chat 4 | Over-engineering right now | System is complex enough to need it |
| Dashboard semantic query (AI query → highlight related nodes) | ChatGPT Chat 3 | Needs embedding_index.json | After real embeddings built |
| Dashboard auto-orphan link suggestions | ChatGPT Chat 3 | Needs embedding_index.json | After real embeddings built |
| Dashboard animated pulsing edges on query | ChatGPT Chat 3 | Cosmetic, needs semantic query working | After semantic query works |
| Dashboard hover-triggered live paths | ChatGPT Chat 3 | Cosmetic polish | After core dashboard proven |
| Neo4j/ArangoDB graph upgrade | ChatGPT Chat 3 | Markdown graph works fine for now | 100+ nodes with complex queries |
| Graph service for AI cluster workers | ChatGPT Chat 3 | No workers need it yet | Multiple AI workers querying vault |
| YAML metadata for typed relationships in frontmatter | ChatGPT Chat 3 | Current link sections work | Vault is large enough to need machine parsing |
| Vault wiki-link strategy (typed link conventions, structured sections) | ChatGPT Chat 3 | Already partially implemented | Next vault cleanup pass |
| Vault template system (standardized PROJECT/TOOL/SESSION/DECISION/PATTERN templates) | ChatGPT Chat 3 | Already partially exists | Next vault content sprint |
| Quest/Journal dashboard (Pixel art/Stardew Valley style) | Kalani 2026-03-16 | V1 built, needs aesthetic rebuild | After aesthetic rebuild. V1 at `Ceiba/quest-dashboard.html`. Kalani wants pixel art/Habitica/cozy, NOT cyberpunk. |
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
| Agent Kernel (~300 line orchestrator) | ChatGPT 2026-03-16 | Need working agents first | After task queue + routing proven. Python script: task queue, worker spawning, memory search, routing, skill registry. "OS for the AI cluster." |
| Overnight autonomous scraping pipeline | Kalani 2026-03-16 | Need reliable scraper first | After trends scraper rebuild. Scheduled work sessions that run while Kalani sleeps. Scrape → score → queue listings. |
| Ceiba Memory Protocol (CMP) | Kalani + ChatGPT 2026-03-16 | Vault needs structure first | After vault has 60+ nodes. Structured protocol for any agent to write to the vault safely with typed payloads. Machine-readable knowledge graph. |
| Viral Vault scoring methodology | Kalani 2026-03-16 | Need product research engine working | After eBay API data flowing. 15-point scoring checklist from Viral Vault adapted for our product scoring engine. |
| Tamagotchi as mobile app (not just Pi) | Kalani 2026-03-16 | Quest dashboard needs to work first | After Pi version. React Native or PWA companion app that shows tamagotchi reacting to progress. |
| Low-dopamine mode for all dashboards | Kalani 2026-03-16 | Done for quest dashboard ✅ | Apply mono/pastel toggle to ALL future UIs. Design system-level concern. |

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
