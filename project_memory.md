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
