# Prompt for Gemini: Ceiba v2 Memory Architecture

I'm building an AI memory system for Claude Code (Anthropic's CLI tool). The goal is to make AI sessions persistent, context-aware, and model-agnostic (so when a new model comes out, I swap the model but keep all the memory and patterns).

## Current System (what works but is fragile):
- 3 markdown files: CLAUDE.md (static rules), primer.md (live state), context.md (big picture)
- Claude reads these at session start
- primer.md gets rewritten at session end
- Problem: files drift out of sync, context gets lost, ideas disconnect, no automatic organization

## What I Want to Build (5 components):

### 1. Context Trio (3 files that verify each other)
- Primer: initializer, live state, what's happening right now
- Context Graph: connects ideas, projects, people, tools (like Obsidian but in markdown). When a new idea comes in, it auto-links to related nodes.
- Verifier: cross-checks the other two for contradictions or stale info

### 2. Status Tracker ("Poop Shutter")
- Every project/idea gets a status: ACTIVE, TODO, BACKLOG, REWORK, ARCHIVED
- Auto-sorts based on last activity
- Handles session weight (tracks context usage, triggers save+commit+branch when heavy)
- Manages git (auto-commit at checkpoints, auto-push at session end, branch management)
- Knows when to suggest starting a new chat session

### 3. Knowledge Library
- Patterns that work (CSS templates, copywriting voice, product structures)
- Prevents starting from zero every time
- "When building X, use pattern Y"

### 4. Fleet Sync
- 3 machines (Ceiba/Mac, Cobo/Linux, Naboria/Linux) share context via Syncthing
- Each machine can generate content using different AI services
- Instructions file tells each machine what to do

### 5. Hermit Crab Pattern (model-agnostic)
- Memory lives in files, not in the model
- When Claude 4/5/whatever drops, swap the model, keep the memory
- Test new models against old ones using the same memory stack

## Constraints:
- Must be markdown-based (no databases, no complex infrastructure)
- Must work with Claude Code's file reading capabilities
- Must be simple enough to maintain manually if the AI breaks
- Must handle git automatically (commit, push, branch)
- Must track session context weight and know when to branch/save

## What I Need From You:
1. Critique this architecture. What's missing? What's redundant?
2. Propose a file structure (exact filenames and what goes in each)
3. Design the Context Graph format (how do nodes connect in markdown?)
4. Design the Status Tracker auto-sort logic
5. How should session weight be measured and when should it trigger a save?
6. What's the simplest way to make this model-agnostic?

Be specific. Give me files I can create. Not theory.
