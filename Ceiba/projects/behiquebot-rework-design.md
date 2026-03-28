# BehiqueBot Rework: Complete Design Document

**Author:** Ceiba
**Date:** 2026-03-19
**Status:** DESIGN (awaiting Kalani review before build)
**Source:** Session 13 brain dump + source code analysis

---

## 1. Current Architecture Analysis

### What Exists (sharp-raman worktree)

**Stack:**
- Python, `python-telegram-bot`, OpenAI (Whisper + GPT-4o-mini), Ollama fallback (llama3.2 on Cobo)
- Notion as persistent storage (Railway wipes local JSON on redeploy)
- Railway hosting, single worker process (`Procfile: worker: python main.py`)

**Modules:**
| File | Purpose |
|------|---------|
| `main.py` | Telegram handlers (text + voice), core message processor |
| `modules/classifier.py` | LLM-based classification into 5 categories, niches, life pillars |
| `modules/memory.py` | JSON file storage, entry CRUD, archive logging, related-entry matching |
| `modules/notion_handler.py` | Notion API persistence (create page, append update blocks) |
| `modules/voice_handler.py` | Empty file (voice handling is inline in main.py) |

**Data Model (current):**
```json
{
  "id": "uuid",
  "user_id": "telegram_user_id",
  "seed": "original text (immutable)",
  "source": "text|voice",
  "timestamp": "ISO 8601",
  "category": "CREATIVE|BUSINESS|KNOWLEDGE|PERSONAL|TECHNICAL",
  "niche": "specific sub-category",
  "life_pillar": "health|wealth|relationships|general",
  "classification": { "category", "niche", "life_pillar", "summary", "tags", "is_update_signal" },
  "updates": [{ "timestamp", "text", "update_number" }],
  "tags": ["tag1", "tag2"],
  "notion_page_id": "optional"
}
```

**Storage:** `data/entries.json` (single flat JSON array) + `data/archive/YYYY-MM-DD.jsonl` (raw logs)

### What's Broken (from brain dump + code analysis)

1. **Single-idea assumption.** `process_message()` sends the entire message text to `classify_input()` once. A message like "I want to build a meal prep app AND I need to call mom about her birthday AND that ebook title should be different" becomes one entry.

2. **Thread continuation is weak.** `find_related_entry()` sends the last 20 entries' 8-char ID prefixes and summaries to an LLM and asks for a match. The LLM only sees truncated IDs and one-line summaries, making false negatives common. The `is_update_signal` field from classification is detected but never actually used in routing logic.

3. **Voice messages treated as single text block.** After Whisper transcription, the entire transcript goes through the same single-idea pipeline. A 2-minute voice note with 5 ideas becomes 1 entry.

4. **No proactive behavior.** The bot only responds when messaged. No reminders, no check-ins, no deadline tracking, no scheduled messages.

5. **No calendar integration.** Google Calendar is paid for but not connected.

6. **No Habitica integration.** No task tracking, no gamification.

7. **No Ceiba bridge.** BehiqueBot data lives on Railway. Ceiba (Claude Code) has no way to see what Kalani sent between sessions. Ideas get lost in the gap.

8. **`bot_data` is ephemeral.** The `context.bot_data` dictionary mapping message IDs to entry IDs lives in memory. Railway redeploys wipe it. Reply-based thread continuation breaks after every deploy.

9. **Notion is write-only.** Entries go to Notion but are never read back. On Railway restart, local JSON is empty and Notion data is orphaned.

---

## 2. Proposed Architecture

### High-Level Design

```
[Telegram] --> [Message Router] --> [Idea Splitter (LLM)] --> [Per-Idea Pipeline]
                                                                    |
                                                          +---------+---------+
                                                          |                   |
                                                   [New Entry]        [Thread Update]
                                                          |                   |
                                                          v                   v
                                                    [Classifier]      [Entry Updater]
                                                          |                   |
                                                          +--------+----------+
                                                                   |
                                                          [Storage Layer]
                                                          /    |       \
                                                      Notion  JSON    Ceiba Sync
                                                                        |
                                                               ~/behique/bridge/
                                                               behiquebot_sync.json

[Scheduler] --> [Reminders / Check-ins / Calendar Alerts / Habitica Sync]
```

### Core Principle Changes

1. **Idea Splitter before Classifier.** Every message (text or voice) goes through an LLM call that splits it into discrete ideas first. Each idea is then classified and routed independently.

2. **Notion as source of truth.** On startup, hydrate local state from Notion. This survives Railway redeploys.

3. **Ceiba sync file.** Write a structured JSON file to the syncthing-shared `~/behique/` directory so Ceiba can read BehiqueBot activity at session start.

4. **Scheduler for proactive behavior.** Use `python-telegram-bot`'s built-in `JobQueue` for reminders, calendar alerts, check-ins, and Habitica sync.

---

## 3. Feature Breakdown

### P0: Fix What's Broken (must ship)

| Feature | Description | Complexity |
|---------|-------------|------------|
| **Multi-idea splitter** | LLM call that splits a message into N discrete ideas before classification | Medium |
| **Voice multi-idea extraction** | Same splitter applied to Whisper transcripts | Low (reuses splitter) |
| **Better thread continuation** | Full entry summaries + embeddings-based similarity instead of 8-char ID matching | Medium |
| **Use is_update_signal** | If classifier flags `is_update_signal: true`, force thread matching even on lower confidence | Low |
| **Notion hydration on startup** | Read entries from Notion DB on boot so Railway redeploys don't lose state | Medium |
| **Persist bot_data mapping** | Store message_id-to-entry_id mappings in Notion or JSON so reply chains survive redeploys | Low |

### P1: New Capabilities (high value)

| Feature | Description | Complexity |
|---------|-------------|------------|
| **Ceiba sync file** | Write `~/behique/bridge/behiquebot_sync.json` with latest entries, updates, and daily summary | Low |
| **Google Calendar integration** | Read upcoming events, create events from messages, send reminders | Medium |
| **Accountability check-ins** | Scheduled daily/weekly messages asking about goals, progress, mood | Medium |
| **Deadline and birthday reminders** | Parse dates from messages, store in calendar, send reminders | Medium |
| **Clarifying questions** | When classification confidence is low or message is ambiguous, ask before saving | Low |

### P2: Gamification and Growth (nice to have)

| Feature | Description | Complexity |
|---------|-------------|------------|
| **Habitica API** | Auto-complete tasks, earn XP/gold from messages, sync habits | Medium |
| **Idea development prompts** | Periodically revisit old ideas and ask "want to develop this further?" | Low |
| **Weekly summary digest** | Sunday evening summary of all ideas captured, goals hit, tasks completed | Low |
| **Command system** | `/ideas`, `/goals`, `/calendar`, `/habits`, `/summary` Telegram commands | Medium |
| **Notion read-back** | Let Kalani query past ideas from Telegram ("what did I say about meal prep?") | Medium |

---

## 4. API Integrations

### Telegram Bot API (existing, extend)
- **Current:** Text handler, voice handler, reply detection
- **Add:** Command handlers (`/ideas`, `/goals`, `/calendar`, `/habits`), JobQueue for scheduled messages, inline keyboard for clarifying questions

### Google Calendar API
- **Auth:** OAuth 2.0 with refresh token (store in Railway env vars)
- **Endpoints needed:**
  - `events.list` (upcoming events for reminders)
  - `events.insert` (create events from messages)
  - `events.get` (event details)
- **MCP note:** Ceiba already has Google Calendar MCP connected (`gcal_*` tools). BehiqueBot needs its own direct API access since it runs on Railway, not on the Mac.
- **Setup required from Kalani:** Google Cloud project, enable Calendar API, create OAuth credentials, complete auth flow once to get refresh token

### Habitica API v3
- **Auth:** API key + User ID (header-based, simple)
- **Endpoints needed:**
  - `POST /api/v3/tasks/user` (create tasks)
  - `POST /api/v3/tasks/{id}/score/{direction}` (complete/uncomplete)
  - `GET /api/v3/tasks/user` (list tasks)
  - `GET /api/v3/user` (stats, HP, XP, gold)
- **Flow:** When Kalani marks something done via Telegram, BehiqueBot scores the corresponding Habitica task. Daily habits can auto-score based on check-in responses.

### Notion API (existing, extend)
- **Current:** Create page, append blocks
- **Add:** Query database (read entries back), search by title/category, sync on startup

### OpenAI / Ollama (existing, extend)
- **Current:** Whisper (voice transcription), GPT-4o-mini (classification, matching)
- **Add:** Idea splitting prompt, better thread matching prompt, clarifying question generation
- **Note:** primer.md says MiniMax M2.5 via OpenRouter is the current LLM. The code uses GPT-4o-mini as fallback after Ollama. Verify which is actually deployed on Railway.

---

## 5. Data Model Changes

### New: IdeaUnit (replaces raw text passing)

```python
@dataclass
class IdeaUnit:
    """A single discrete idea extracted from a message."""
    text: str                    # The idea text
    original_message_id: str     # Telegram message ID it came from
    position: int                # Which idea in the message (0-indexed)
    total_in_message: int        # How many ideas were in the original message
    source: str                  # "text" or "voice"
    classification: dict | None  # Filled after classification
    matched_entry_id: str | None # Filled if thread continuation matches
```

### Updated Entry Schema

```json
{
  "id": "uuid",
  "user_id": "telegram_user_id",
  "seed": "original idea text (immutable)",
  "source": "text|voice",
  "timestamp": "ISO 8601",
  "category": "CREATIVE|BUSINESS|KNOWLEDGE|PERSONAL|TECHNICAL",
  "niche": "specific sub-category",
  "life_pillar": "health|wealth|relationships|general",
  "classification": { ... },
  "updates": [{ "timestamp", "text", "update_number", "source_message_id" }],
  "tags": ["tag1", "tag2"],
  "notion_page_id": "optional",
  "status": "new|active|developing|completed|archived",
  "priority": "low|medium|high|urgent",
  "deadline": "ISO 8601 or null",
  "related_ids": ["other entry UUIDs"],
  "habitica_task_id": "optional",
  "calendar_event_id": "optional",
  "last_revisited": "ISO 8601 or null"
}
```

### New: GoalEntry (extends Entry for accountability)

```json
{
  "...all Entry fields...",
  "type": "goal",
  "target_date": "ISO 8601",
  "milestones": [
    { "description": "...", "completed": false, "completed_at": null }
  ],
  "check_in_frequency": "daily|weekly|none",
  "last_check_in": "ISO 8601 or null"
}
```

### New: ReminderEntry

```json
{
  "id": "uuid",
  "user_id": "telegram_user_id",
  "type": "deadline|birthday|appointment|custom",
  "description": "Mom's birthday",
  "trigger_at": "ISO 8601",
  "recurring": "yearly|monthly|weekly|none",
  "calendar_event_id": "optional",
  "notified": false
}
```

---

## 6. Ceiba Sync Protocol

### Purpose
Give Ceiba (Claude Code on Mac) visibility into what Kalani sends to BehiqueBot between sessions. Currently, Ceiba starts each session blind to anything Kalani thought about since the last conversation.

### File Location
`~/behique/bridge/behiquebot_sync.json`

This directory is in the syncthing share between Ceiba (Mac) and the behique repo. BehiqueBot on Railway writes this file. Ceiba reads it at session start.

### Sync Mechanism

**Option A: Direct file write (requires Railway -> Mac path)**
Not possible. Railway can't write to Kalani's Mac filesystem.

**Option B: Notion as intermediary**
BehiqueBot writes to Notion (already does this). Ceiba reads from Notion at session start using the Notion MCP.
- Pro: Already partially works. No new infrastructure.
- Con: Notion MCP reads are per-page, not bulk queries. Slow for many entries.

**Option C: Webhook to bridge (recommended)**
BehiqueBot POSTs a sync payload to Cobo's bridge (`192.168.0.151:9876`) or Ceiba's bridge. The bridge writes the file to disk.
- Pro: Real-time, uses existing bridge infrastructure.
- Con: Depends on Cobo being online.

**Option D: GitHub as intermediary (simplest, most reliable)**
BehiqueBot commits a sync file to the behique repo on GitHub. Syncthing pulls it to the Mac.
- Pro: Works even when home network is down. Git history provides audit trail.
- Con: Requires GitHub token on Railway. Slight delay.

### Recommended: Option B (Notion) + Option C (bridge) as enhancement

**Phase 1 (immediate):** Ceiba reads BehiqueBot's Notion database at session start using the Notion MCP that's already connected. Add a `memory.sh` step or CLAUDE.md instruction: "Read BehiqueBot Notion DB for recent entries."

**Phase 2 (later):** BehiqueBot POSTs daily sync summaries to the Cobo bridge, which writes `~/behique/bridge/behiquebot_sync.json` to the syncthing share.

### Sync File Schema

```json
{
  "last_sync": "2026-03-19T22:30:00",
  "sync_version": 1,
  "summary": {
    "total_entries": 47,
    "entries_today": 5,
    "updates_today": 3,
    "categories": { "BUSINESS": 2, "CREATIVE": 1, "TECHNICAL": 2 }
  },
  "recent_entries": [
    {
      "id": "abc123",
      "seed": "Build a meal prep subscription app",
      "category": "BUSINESS",
      "niche": "product",
      "life_pillar": "wealth",
      "timestamp": "2026-03-19T14:30:00",
      "update_count": 2,
      "status": "active"
    }
  ],
  "recent_updates": [
    {
      "entry_id": "abc123",
      "text": "Add a community feature for recipe sharing",
      "timestamp": "2026-03-19T16:45:00"
    }
  ],
  "active_goals": [
    {
      "description": "Launch first digital product on Gumroad",
      "target_date": "2026-03-25",
      "progress": "2/5 milestones"
    }
  ],
  "upcoming_reminders": [
    {
      "description": "Mom's birthday",
      "trigger_at": "2026-04-15",
      "type": "birthday"
    }
  ]
}
```

### Ceiba Session Start Protocol (updated)

Add to CLAUDE.md session start:
```
6. Query BehiqueBot Notion DB for entries since last session
7. Read ~/behique/bridge/behiquebot_sync.json if it exists
8. Mention any new ideas Kalani captured via BehiqueBot
```

---

## 7. Implementation Plan

### Phase 1: Core Fixes (can build NOW, no Kalani input needed)

**Estimated effort:** 1 session

1. **Idea Splitter module** (`modules/splitter.py`)
   - New LLM prompt that takes a message and returns an array of discrete ideas
   - Each idea gets its own classification and routing
   - Falls back to single-idea if splitter fails

2. **Better thread matching** (`modules/memory.py` rewrite)
   - Send full entry summaries (not 8-char IDs) to matcher
   - Use `is_update_signal` from classifier to lower match threshold
   - Weight recent entries higher

3. **Notion hydration on startup** (`modules/notion_handler.py` extension)
   - `hydrate_from_notion()` function that queries the Notion DB and rebuilds local entries.json
   - Called once in `main()` before polling starts

4. **Persist bot_data** (`modules/memory.py` extension)
   - Save message_id-to-entry_id mappings to a JSON file
   - Load on startup

5. **Voice multi-idea** (main.py update)
   - After Whisper transcription, pass through splitter before processing

### Phase 2: Ceiba Bridge + Accountability (needs minimal Kalani input)

**Estimated effort:** 1 session
**Kalani input needed:** Confirm bridge approach (Notion read vs webhook)

1. **Ceiba sync via Notion** (Phase 1 of sync protocol)
   - Update CLAUDE.md session start to query Notion
   - Add summary generation to BehiqueBot

2. **Accountability scheduler** (`modules/scheduler.py`)
   - Daily evening check-in: "How was today? What did you get done?"
   - Weekly Sunday summary
   - Uses `python-telegram-bot` JobQueue

3. **Command system** (main.py extension)
   - `/ideas` (list recent ideas by category)
   - `/goals` (show active goals and progress)
   - `/summary` (today's summary)

4. **Clarifying questions**
   - When classifier confidence is ambiguous, reply with inline keyboard: "Is this a new idea or an update to [existing idea]?"

### Phase 3: Calendar + Reminders (needs Kalani input)

**Estimated effort:** 1 session
**Kalani input needed:** Google Cloud OAuth setup, which calendars to watch

1. **Google Calendar integration** (`modules/calendar_handler.py`)
   - Read upcoming events, send morning briefing
   - Parse dates from messages ("meeting on Thursday at 3pm") and create events
   - Reminder system: 1 hour before, morning of

2. **Birthday and deadline tracking** (`modules/reminders.py`)
   - Parse and store dates mentioned in messages
   - Recurring birthday reminders
   - Deadline countdown alerts

### Phase 4: Habitica Gamification (needs Kalani input)

**Estimated effort:** 1 session
**Kalani input needed:** Habitica API key + User ID, which habits to track

1. **Habitica sync** (`modules/habitica_handler.py`)
   - Create Habitica tasks from BehiqueBot entries marked as goals
   - Score tasks complete when Kalani confirms via Telegram
   - Show XP/gold/level in check-in messages
   - Auto-create dailies from recurring goals

2. **Gamification layer in responses**
   - Show Habitica stats in summary messages
   - "You completed 3 tasks today. +45 XP. Level 12."

---

## 8. What Can Be Built NOW vs What Needs Kalani

### Can Build NOW (no input needed)

- [ ] Idea Splitter module
- [ ] Voice multi-idea extraction
- [ ] Better thread matching (full summaries, is_update_signal usage)
- [ ] Notion hydration on startup
- [ ] Persistent bot_data mappings
- [ ] Updated data model with status, priority, deadline fields
- [ ] Command handlers skeleton (/ideas, /goals, /summary)
- [ ] Daily check-in scheduler (basic)
- [ ] Ceiba session start Notion query (update CLAUDE.md)

### Needs Kalani Input

| Item | What's needed | Why |
|------|--------------|-----|
| Google Calendar | OAuth flow (browser login) | Google requires interactive consent |
| Habitica | API key + User ID | Only Kalani has these credentials |
| Bridge webhook | Confirm Cobo bridge approach | Affects architecture |
| Reminder preferences | How often, what time, which days | Personal preference |
| Check-in schedule | Daily? Evening? Morning? | Personal preference |
| LLM provider | Confirm: OpenRouter (MiniMax M2.5) or OpenAI (GPT-4o-mini) or Ollama? | Cost and reliability tradeoff |
| Railway env vars | Any new API keys need to be added | Only Kalani has Railway dashboard access |

---

## 9. New File Structure

```
BehiqueBot/
  main.py                      # Entry point, Telegram handlers, scheduler setup
  Procfile                     # worker: python main.py
  requirements.txt             # + google-api-python-client, google-auth
  .env.example                 # Document all required env vars
  modules/
    splitter.py                # NEW: Multi-idea extraction from messages
    classifier.py              # UPDATED: Confidence scoring
    memory.py                  # UPDATED: Better matching, Notion hydration
    notion_handler.py          # UPDATED: Query/read capabilities
    calendar_handler.py        # NEW: Google Calendar integration
    habitica_handler.py        # NEW: Habitica API integration
    reminders.py               # NEW: Deadline, birthday, appointment tracking
    scheduler.py               # NEW: Proactive check-ins, reminders, syncs
    ceiba_sync.py              # NEW: Sync file generation for Ceiba bridge
    commands.py                # NEW: /ideas, /goals, /calendar, /habits, /summary
  data/
    entries.json               # Local cache (hydrated from Notion on boot)
    bot_data.json              # Persistent message-to-entry mappings
    reminders.json             # Scheduled reminders
    archive/
      YYYY-MM-DD.jsonl         # Raw logs (unchanged)
```

---

## 10. Key Design Decisions

**1. Splitter-first architecture.** Every message goes through the splitter before anything else. This is the single biggest improvement. A voice message with 5 ideas becomes 5 entries. A text with 3 thoughts becomes 3 entries. The splitter is a single LLM call that returns a JSON array.

**2. Notion as source of truth, not local JSON.** Railway wipes local storage. Notion persists. On every boot, hydrate from Notion. Local JSON is a cache, not the database.

**3. LLM cost management.** The splitter adds one LLM call per message. Combined with the existing classifier call, that's 2 calls per message minimum (1 split + 1 classify per idea). Use Ollama on Cobo as primary to keep costs at zero. Fall back to OpenRouter/OpenAI only when Cobo is offline.

**4. No new infrastructure.** Everything runs on the existing Railway worker. No new servers, no new databases. Calendar and Habitica are API calls. Ceiba sync uses existing Notion + bridge.

**5. Incremental deployment.** Each phase can ship independently. Phase 1 fixes the core problems. Phases 2-4 add new capabilities. Nothing in Phase 2+ blocks Phase 1.

---

## 11. Splitter Prompt Design

This is the most critical new component. Here's the prompt:

```
You are an idea parser for a personal assistant. Your job is to take a message
(text or voice transcript) and split it into discrete, independent ideas.

Rules:
- Each idea should be self-contained and understandable on its own
- If the message contains only one idea, return an array with one element
- Preserve the original wording as much as possible
- For voice transcripts, clean up filler words but keep the meaning
- If part of the message is clearly a follow-up to a previous idea
  (uses words like "also", "and another thing", "oh and"), split it out
- Mark each idea with whether it sounds like a NEW idea or an UPDATE to something existing

Return ONLY valid JSON:
{
  "ideas": [
    {
      "text": "the idea text, cleaned up",
      "is_new": true,
      "context_hint": "optional: what existing idea this might relate to"
    }
  ]
}
```

---

## 12. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Splitter over-splits (1 idea becomes 3) | Medium: duplicate entries | Tune prompt, add "minimum confidence" threshold |
| Splitter under-splits (3 ideas stay as 1) | Medium: back to current problem | Better prompt engineering, test with real voice transcripts |
| Ollama on Cobo offline | Low: falls back to OpenAI | Already handled in current code |
| Railway free tier limits | Medium: bot goes offline | Monitor usage, consider $5/mo hobby plan |
| Google Calendar OAuth token expires | Low: reminders stop | Store refresh token, auto-renew |
| Notion API rate limits | Low: sync delays | Batch queries, cache aggressively |

---

## Next Step

Kalani reviews this document and confirms:
1. Which phase to start with (recommendation: Phase 1, the core fixes)
2. LLM provider preference for Railway
3. Whether to proceed with Notion-based Ceiba sync or webhook-to-bridge
4. Google Calendar OAuth setup (can do async while Phase 1 builds)
5. Habitica API credentials
