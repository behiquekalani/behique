- [2026-03-14 11:15] [main] 23aed4a: Add wake.sh — Ceiba activation script (files: wake.sh,)
- [2026-03-14 11:55] [main] 7567a90: Initialize Ceiba Obsidian vault + project ideas (files: Ceiba/00-Identity/Kalani.md,Ceiba/00-Identity/Psychologist-Framework.md,Ceiba/01-Projects/News-Intelligence-Bots.md,Ceiba/02-Goals/North-Star.md,Ceiba/02-Goals/Q3-2026.md,Ceiba/03-Check-ins/template.md,Ceiba/04-Patterns/observations.md,)
- [2026-03-14 18:02] [main] e8a96c0: feat: add Notion persistence — entries survive Railway redeployments (files: modules/memory.py,modules/notion_handler.py,requirements.txt,)
- [2026-03-14 23:27] [main] 0eb8f20: feat: classify via local Ollama, OpenAI fallback (files: modules/classifier.py,)
- [2026-03-14 23:35] [main] c695505: feat: BehiqueBot fully migrated to local Ollama, OpenAI fallback only (files: modules/memory.py,primer.md,)
- [2026-03-15 11:52] [claude/sharp-raman] 25e7715: auto: session checkpoint 2026-03-15 11:52:18 (files: primer.md,)
- [2026-03-15 12:03] [claude/sharp-raman] 701e12f: feat: routing.py v1 — Spine routing layer + ceiba_lite.py update

Keyword-based task router with 3 tiers (Ollama/Sonnet/Opus),
fallback chain, and CLI test mode. ceiba_lite.py now uses the
router and points to Computer 2 Ollama.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com> (files: ceiba_lite.py,routing.py,)
- [2026-03-15 09:31] [main] 60e1db6: feat: Ceiba spine architecture + full vault build

- architecture-spine.md: 6-part AI body framework, 4-month plan, routing layer design
- VAULT_INDEX.md: master session index, infrastructure state, key moments
- CLAUDE.md: session start protocol (grandma fix)
- primer.md: full rewrite with today's key decisions and active thread
- MIGRATE-TO-CODE.md: Claude Code migration guide
- All project files: BehiqueBot, eBay, n8n, Shopify, Trends, MISSIONS
- HOME.md, check-ins, observations: full vault operational
- tools/: eBay listing assistant skeleton, trends scraper, notify relay
- ceiba_lite.py: offline Ollama fallback

Key decisions: Cowork → Claude Code, vault is model-agnostic, build for architecture not speed.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> (files: CLAUDE.md,Ceiba/01-Projects/BehiqueBot.md,Ceiba/01-Projects/Google-Trends-Scraper.md,Ceiba/01-Projects/MISSIONS.md,Ceiba/01-Projects/Shopify-Store.md,Ceiba/01-Projects/eBay-Listing-Assistant.md,Ceiba/01-Projects/n8n-Agency.md,Ceiba/02-Goals/Q3-2026.md,Ceiba/03-Check-ins/2026-03-15.md,Ceiba/03-Check-ins/template.md,Ceiba/03-Check-ins/weekly-2026-03-15.md,Ceiba/04-Patterns/observations.md,Ceiba/05-Knowledge/architecture-spine.md,Ceiba/05-Knowledge/screen-assistant-idea.md,Ceiba/05-Knowledge/system-map-render.jsx,Ceiba/05-Knowledge/system-map.jsx,Ceiba/HOME.md,Ceiba/VAULT_INDEX.md,MIGRATE-TO-CODE.md,ceiba_lite.py,context.md,primer.md,project_memory.md,tools/ebay-listing-assistant/core/pipeline.py,tools/ebay-listing-assistant/core/types.py,tools/install-notify-agent.sh,tools/notify.py,tools/notion-triage.jsx,tools/setup_notion.py,tools/trends_scraper.py,)
- [2026-03-15 10:08] [main] 14d9d7e: feat: session capture + Cursor setup complete

- session-2026-03-15-capture.md: priority reorder, Allocator findings, stop hook design
- VAULT_INDEX: updated with capture file
- .cursorrules: already in place for Cursor auto-load

Priority order revised: stop hook → routing.py → wiki links (credit protection first)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> (files: Ceiba/05-Knowledge/session-2026-03-15-capture.md,Ceiba/VAULT_INDEX.md,)
- [2026-03-15 10:10] [main] f12084e: fix: remove hardcoded Notion token, use env var

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> (files: setup_notion.py,)
- [2026-03-15 10:26] [main] af365ae: security: fix hardcoded token in tools/setup_notion.py + harden .gitignore

- tools/setup_notion.py: remove hardcoded Notion token, use os.environ
- .gitignore: add .ceiba-config, venv, __pycache__, .DS_Store, output/,
  .obsidian, .claude, *.skill, .stfolder — was only blocking .env before

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> (files: .gitignore,tools/setup_notion.py,)
- [2026-03-15 10:43] [main] a0d1bdf: auto: session checkpoint 2026-03-15 10:43:03 (files: primer.md,)
- [2026-03-15 12:14] [main] 903008a: merge: resolve project_memory.md conflict (keep both histories) (files: modules/memory.py,project_memory.md,)
- [2026-03-15 12:51] [main] 848cbdb: feat: code-auditor skill — ChatGPT-drafted, bug-finding focused

Prompt engineered by ChatGPT (cross-model prompting). Assumes bugs exist,
follows execution paths, includes subtle real-world examples for each of
7 bug classes. First skill built using the routing system's offloading principle.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com> (files: skills/code-auditor/SKILL.md,)
- [2026-03-15 13:19] [main] 36da3c8: auto: session checkpoint 2026-03-15 13:19:22 (files: primer.md,)
- [2026-03-15 15:02] [main] 7e84380: auto: session checkpoint 2026-03-15 15:02:38 (files: primer.md,)
- [2026-03-15 15:10] [main] 68b49b6: auto: session checkpoint 2026-03-15 15:10:42 (files: primer.md,)
- [2026-03-15 15:43] [main] e75556d: auto: session checkpoint 2026-03-15 15:43:48 (files: primer.md,)
- [2026-03-15 20:01] [main] a95d366: feat: full infrastructure day — dashboard, backlog, product engine, skills, security fixes

- Ceiba vault graph dashboard (vis.js, Jarvis theme, live at :8081)
- IDEAS_BACKLOG.md — smart idea capture system to prevent ChatGPT idea loss
- Product research engine (18 files: scrapers, scoring, normalization, pipeline)
- vault_grapher.py with --json output for dashboard consumption
- 8 skills: ceiba, security-auditor, vault-architect, session-closer, etc.
- Bridge infrastructure: dispatch.sh, COMPUTER2_MIND, Cobo instructions
- AI cluster: agent_kernel, architecture, task queue, memory system
- Security: removed hardcoded bridge token, added cache/ to .gitignore
- Updated all project files with wiki links and typed node structure

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com> (files: .gitignore,Ceiba/01-Projects/BehiqueBot.md,Ceiba/01-Projects/Google-Trends-Scraper.md,Ceiba/01-Projects/Shopify-Store.md,Ceiba/01-Projects/eBay-Listing-Assistant.md,Ceiba/01-Projects/n8n-Agency.md,Ceiba/04-Patterns/observations.md,Ceiba/05-Knowledge/architecture-spine.md,Ceiba/05-Knowledge/computer2-full-context.md,Ceiba/05-Knowledge/computer2-openclaw-instructions.md,Ceiba/05-Knowledge/openclaw-setup.md,Ceiba/IDEAS_BACKLOG.md,Ceiba/VAULT_GRAPH.md,Ceiba/VAULT_INDEX.md,Ceiba/ceiba_dashboard.html,Ceiba/vault_graph.json,ai_cluster/ARCHITECTURE.md,ai_cluster/kernel/agent_kernel.py,ai_cluster/memory/knowledge/a-modular-skill-system-can-benefit-from-async-pyth.md,ai_cluster/memory/knowledge/async-python-allows-for-non-blocking-i-o-operation.md,ai_cluster/memory/knowledge/async-python-enables-the-use-of-coroutines-and-asy.md,ai_cluster/memory/knowledge/async-python-promotes-loose-coupling-and-modularit.md,ai_cluster/memory/knowledge/async-python-s-async-await-syntax-allows-for-writi.md,ai_cluster/memory/knowledge/async-python-s-async-await-syntax-simplifies-concu.md,ai_cluster/memory/knowledge/async-python-s-coroutines-and-asynchronous-generat.md,ai_cluster/memory/knowledge/async-python-s-non-blocking-i-o-operations-can-imp.md,ai_cluster/memory/knowledge/coroutines-and-asynchronous-generators-in-async-py.md,ai_cluster/skills/registry.json,ai_cluster/tasks/done/20260315-154234-1f594f.json,ai_cluster/tasks/done/20260315-154239-052b73.json,ai_cluster/tasks/done/20260315-154446-5ebb2f.json,ai_cluster/tasks/done/20260315-154502-64a446.json,ai_cluster/tasks/done/20260315-154502-c8b410.json,ai_cluster/tasks/done/20260315-154502-d5c150.json,ai_cluster/tasks/done/20260315-155452-a2182a.json,ai_cluster/tasks/done/20260315-155532-b9f3ce.json,ai_cluster/tasks/inbox/20260315-155547-test01.json,bridge/COMPUTER2_MIND.md,bridge/README.md,bridge/cobo_instructions_2026-03-16.md,bridge/dispatch.sh,bridge/tasks.md,modules/routing.py,product_research_engine/cli/__init__.py,product_research_engine/config.yaml,product_research_engine/core/__init__.py,product_research_engine/core/database.py,product_research_engine/core/feature_engineering.py,product_research_engine/core/models.py,product_research_engine/core/product_normalizer.py,product_research_engine/core/scoring_engine.py,product_research_engine/core/trends_adapter.py,product_research_engine/core/utils.py,product_research_engine/ebay/__init__.py,product_research_engine/ebay/ebay_client.py,product_research_engine/ebay/ebay_cross_reference.py,product_research_engine/main.py,product_research_engine/pipeline/__init__.py,product_research_engine/pipeline/cross_reference.py,product_research_engine/pipeline/discovery.py,product_research_engine/pipeline/reporting.py,product_research_engine/pipeline/scoring.py,product_research_engine/requirements.txt,product_research_engine/scrapers/__init__.py,product_research_engine/scrapers/amazon_best_sellers.py,product_research_engine/scrapers/base_scraper.py,product_research_engine/scrapers/costco_popular.py,product_research_engine/scrapers/home_depot_best_sellers.py,product_research_engine/scrapers/target_trending.py,product_research_engine/scrapers/walmart_trending.py,product_research_engine/seed_from_trends.py,project_memory.md,skills/ceiba-accountability/SKILL.md,skills/idea-classifier/SKILL.md,skills/kernel/SKILL.md,skills/security-auditor/SKILL.md,skills/session-closer/SKILL.md,skills/session-tracker/SKILL.md,skills/trends-scraper/SKILL.md,skills/vault-architect/SKILL.md,tools/trends_scraper.py,tools/vault_grapher.py,)
