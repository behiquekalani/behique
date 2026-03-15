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
