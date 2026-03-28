# CLAUDE Reference — Extended Context
# Read this file only when relevant, not every session.
# Moved here from CLAUDE.md to save ~3K tokens per session.

## BEHIQUEBOT ACCOUNTABILITY FRAMEWORK

BehiqueBot is built on Kalani's real psychologist's framework. When using accountability logic, apply these principles:

### For attention/ADHD:
- Break tasks into small, concrete subtasks
- Use Pomodoro-style framing when stuck (25 min focus, 5 min rest)
- Minimize cognitive load. One thing at a time.
- Visual/structured output helps him process (tables, clear lists, step-by-step)
- "Post-it mental" principle: capture ideas immediately without needing to execute them now

### For emotional accountability:
- Weekly emotional state check-in: "How are you actually doing?"
- Identify early warning signs: going quiet, scattered energy, jumping between projects
- Validate effort over result: "You showed up" matters as much as "you shipped"
- Reframe self-criticism: not "I failed" but "what got in the way?"
- Celebrate small wins explicitly. He tends to skip this.

### Relapse/avoidance protocol:
1. Name what's being avoided without judgment
2. Ask: what strategy stopped working and why?
3. Reduce scope: what's the smallest possible next action?
4. If patterns persist: suggest he reconnect with his support network or psychologist

### Core principle:
Ask the right questions. Notice what he doesn't say as much as what he does.

## BEHIQUEBOT CURRENT SYSTEM

Live on Railway. Text and voice via Telegram.
- Classifies inputs: CREATIVE, BUSINESS, KNOWLEDGE, PERSONAL, TECHNICAL
- Tags with life pillar: health, wealth, relationships, general
- Saves seed (immutable) + living updates per idea
- Logs to daily raw archive
- Detects Telegram replies to link updates
- Uses OpenAI Whisper for voice transcription
- Next phase: Notion database, memory system, Claude-powered check-ins

## TECH STACK

- Languages: Python (learning), C++ (knows), JavaScript/Node.js (learning)
- Frameworks: LangGraph, AutoGen, React (learning)
- Tools: Claude (Ceiba), Cursor, NotebookLM, n8n, Warp
- Automation: Playwright/Selenium
- AI video: CapCut (now), Veo3/Kling/Sora+ (learning)
- BehiqueBot: Python, python-telegram-bot, OpenAI (GPT-4o-mini + Whisper), Railway, GitHub

## FILE SYSTEM ACCESS

- ~/behique: main project folder
- ~/Desktop: cleaned, organized
- ~/Documents: documents, assignments
- ~/Downloads: downloads. Webshare proxies.txt for trends bot.

## MEMORY STACK

| File | Type | Purpose |
|------|------|---------|
| CLAUDE.md | Static | Core rules, identity, tone |
| CLAUDE_REFERENCE.md | Static | Extended context (this file) |
| primer.md | Dynamic | Current session state |
| context.md | Semi-static | Big picture vision |
| memory.sh | Script | Git state injection |
| .git/hooks/post-commit | Hook | Auto-logs commits |
