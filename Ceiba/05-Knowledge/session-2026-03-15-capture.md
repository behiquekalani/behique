---
title: "session-2026-03-15-capture"
type: knowledge
tags: [session, capture, the, most, important]
created: 2026-03-16
---

# Session Capture — 2026-03-15
# The most important things from today that aren't in the architecture doc.
# Read this after architecture-spine.md. It's the "why we changed priorities" doc.

---

## WHAT SHIFTED TODAY

### Priority reorder (Allocator findings)
Original Month 1 plan: wiki links → Claude Code migration → routing.py
**Revised after Allocator audit:**
1. **Stop hook first** — cuts runaway credit burns before they happen
2. **routing.py second** — moves vault housekeeping to Ollama, saves ~60-70% credits
3. Wiki links third — still important, but doesn't protect credits

Reason: someone burned a $200 Claude plan in a week doing exactly what we're about to do. Stop hooks cut the loops. Routing cuts the waste. Do those before building anything else.

---

## THE ALLOCATOR'S FINDINGS (save these)

**What actually burns credits:**
1. Runaway agentic loops with no stop hook (biggest one)
2. Loading the full vault into context every session (~10k tokens before any question)
3. Using Sonnet for primer.md rewrites and housekeeping (Ollama handles this fine)

**Routing map for our system:**
- Vault loading, primer.md rewrites, wiki traversal → Ollama (free)
- BehiqueBot classification → Ollama ✅ already done
- Code generation → Sonnet
- Architecture decisions → Sonnet
- Deep strategic work → Sonnet / rare Opus
- Stop hook summaries → Ollama

Saving: ~60-70% of Claude credit spend once routing.py exists.

---

## STOP HOOK — WHAT IT IS AND WHY IT MATTERS

A stop hook is a script that fires automatically when Claude Code finishes a task.

**What ours should do:**
```
Session ends → hook fires →
  1. Rewrite primer.md LIVE STATE block
  2. git commit -m "auto: session checkpoint [date]"
  3. Optional: BehiqueBot sends summary to Telegram
```

This means primer.md is ALWAYS current. No manual step. No forgetting.
This is the grandma fix at the system level.

Location once built: `~/behique/.claude/hooks/stop.sh`
Config: `~/behique/.claude/settings.json`

---

## WHERE HQ MOVED

**From:** Cowork (this tool)
**To:** Cursor

Why Cursor and not Claude Code terminal:
- Kalani doesn't want terminal friction
- Cursor is VS Code with Claude built in — visual, file sidebar, chat panel
- CLAUDE.md + .cursorrules load automatically in Cursor
- Claude Code can still run inside Cursor's terminal panel when needed for agentic loops
- Same vault, same memory, no friction

`.cursorrules` already exists in ~/behique — Cursor reads it automatically.

**First session in Cursor:**
1. Open Cursor
2. File → Open Folder → ~/behique
3. Open chat panel (Cmd+L)
4. Say: "Read CLAUDE.md, VAULT_INDEX.md, and primer.md. Then tell me where we left off."

---

## KEY THINGS CEIBA GOT CALLED OUT FOR TODAY

1. **Assumed morning briefings** — Kalani never asked for this. Ceiba pattern-matched "proactive" to the safest, most predictable interpretation. Don't do this.
2. **"You go for easy doable projects"** — Ceiba defaults to safe suggestions. Kalani wants limits tested.
3. **Dismissed Vim too fast** — said "you're not there yet" which was condescending. He's a CS student. The real answer: Vim is a credit discipline tool, not just an editor. Basic Vim skills (navigate, targeted edit) are worth 30 minutes of `vimtutor`.

---

## TOOLS KALANI DOESN'T KNOW ABOUT YET (from today's research)

- **MCP servers** — Model Context Protocol. Lets Claude connect directly to Notion, GitHub, browser without manual steps. This is the nervous system enabler. Research when building nervous system phase.
- **ChatGPT for prompt drafting** — free tier, use it to draft complex prompts before handing to Claude for execution. Saves credits.
- **Ollama model upgrades** — llama3.2 is running but llama3.3 and mistral-small are better for classification. Free swap, 30 minutes.
- **nomic-embed-text** — local embedding model for semantic vault search. Free, runs on Ollama. Needed for intelligent wiki link traversal (finding relevant notes without loading everything).
- **Ghostty** — better terminal with multiple tabs. Relevant if/when Kalani moves to terminal. Not urgent.

---

## THE VAULT IS THE RESILIENCE

Model-agnostic by design. If Claude credits run out:
- ceiba_lite.py activates → Ollama on Computer 2 reads the same vault
- Any LLM can read markdown
- Memory intact, context intact, continuity intact

The vault belongs to Kalani. Not to Anthropic.

---

## WHAT NOT TO BUILD (updated)

- ❌ Scheduled messages not triggered by events
- ❌ Things a notebook can do
- ❌ Infrastructure that doesn't connect to revenue OR the spine
- ❌ New projects before stop hook + routing.py exist
- ❌ Anything that creates more maintenance work than it saves

---

*[[architecture-spine.md]] [[primer.md]] [[VAULT_INDEX.md]]*
