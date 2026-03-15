# BehiqueBot
**Status:** ✅ Live on Railway
**Priority:** Ongoing — foundation tool
**Stack:** Python, python-telegram-bot, Ollama (llama3.2, primary) + OpenAI (fallback only), Railway

---

## What It Does
Telegram bot that captures Kalani's ideas on the go — text or voice.
Classifies every input into 5 categories + life pillar.
Now saves permanently to Notion (Railway resets no longer wipe data).

## Completed
- [x] Core bot live on Railway
- [x] Voice transcription via Whisper
- [x] Classification via Ollama-first (migrated 2026-03-14, OpenAI fallback only)
- [x] Memory matching via Ollama-first (migrated 2026-03-14)
- [x] Notion persistence (connected 2026-03-14)
- [x] Telegram bot token refreshed
- [x] Cloudflare tunnel exposes Computer 2 Ollama to Railway (URL rotates — needs named tunnel)

## Architecture
```
Telegram message → classify_input() → save_entry() → Notion + local JSON
```

## Files
- `~/behique/main.py` — core bot
- `~/behique/modules/classifier.py` — GPT-4o-mini classification
- `~/behique/modules/memory.py` — dual write: JSON + Notion
- `~/behique/modules/notion_handler.py` — Notion API integration

## Notion Database
- Database: BehiqueBot Ideas
- ID: 323501e0a68481fc822ad813448de602
- Properties: Name, Category, Pillar, Status, Raw Text, Source, Created

## Related
→ [[00-Identity/Psychologist-Framework]] — framework behind classification
→ [[01-Projects/MISSIONS]] — foundation for BehiqueBot SaaS (long-term)

## Next Phase
- Proactive scheduler — morning briefing + evening check-in via n8n on Computer 2
- Accountability nudges — detects quiet periods on projects, sends Telegram nudge
- `/status` command — pulls live state from primer.md on demand
- `/checkin` command — guided evening review
- Named Cloudflare tunnel — fixed URL so Ollama stays reachable after restarts
- Productize as SaaS for other ADHD entrepreneurs (long-term)

---

## 🧭 CEIBA BREADCRUMBS
*Ceiba leaves notes here for future sessions. Read before touching this project.*

- **2026-03-14:** Classifier + memory matcher migrated to Ollama-first. Both files updated. Pushed to Railway, redeployed.
- **2026-03-14:** Cloudflare tunnel active but URL rotates every restart — Railway env var `OLLAMA_HOST` needs manual update each time Computer 2 reboots.
- **2026-03-15:** Next big unlock is proactive messaging — bot should reach out to Kalani, not just wait. n8n on Computer 2 is the scheduler. Build morning briefing first.

*Last updated: 2026-03-15*
