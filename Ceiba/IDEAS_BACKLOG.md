# IDEAS BACKLOG — Ceiba Idea Capture & Triage System
<!-- Updated: 2026-03-15 23:00 -->
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

---

## BLOCKED — Good Idea, Waiting On Something

| Idea | Source | Blocked By | Unblocks When | Priority |
|------|--------|------------|---------------|----------|
| eBay cross-reference engine | ChatGPT Chat 1 | eBay API keys | Monday 2026-03-16 | HIGH |
| Real scoring with margin/competition | ChatGPT Chat 1 | eBay API keys | Monday 2026-03-16 | HIGH |
| Amazon scraper with stealth+proxies | ChatGPT Chat 1 | Residential proxies on Cobo | proxies.txt copied to Cobo | MEDIUM |
| Walmart scraper | ChatGPT Chat 3 | Core scrapers need to work first | Amazon/eBay pipeline proven | LOW |
| Product clustering (group variants) | ChatGPT Chat 3 | Needs enough products in DB | eBay API populates real data | MEDIUM |

---

## FUTURE — Good Ideas, Not Yet Time

| Idea | Source | Why Not Now | Revisit When |
|------|--------|-------------|--------------|
| Discord voice cowork — Jarvis mode | Kalani voice memo 2026-03-16 | Needs Voice body part built, real-time API access (OpenAI Realtime or future Claude voice), screen capture pipeline | Month 4+ on spine, after Senses + Hands + Nervous System proven |
| Personal visual dashboard (pixel art / lo-fi) | Kalani 2026-03-16 | Habitica-inspired visual layer — shows project state, progress, mood. NO RPG/quests/gamification. Tamagotchi-of-a-builder vibe. Pixel art aesthetic. Journal component possible. Text-based game layer later as enhancement, not core. Simple first → improve. | After one revenue project is live |

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
