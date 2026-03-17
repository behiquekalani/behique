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
