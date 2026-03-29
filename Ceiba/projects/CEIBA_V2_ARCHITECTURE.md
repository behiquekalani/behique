# Ceiba v2 - Memory Architecture Redesign

## The Problem
Current system: 3 files (CLAUDE.md, primer.md, context.md) that drift out of sync, lose context across sessions, and don't connect ideas together.

## The Vision: 5 Organs

### 1. PRIMER (The Starter/Initializer)
- What it is now, but stricter
- Always read first. Always rewritten at session end.
- Contains: live state, what just happened, what's next, blockers

### 2. CONTEXT GRAPH (The Brain - Obsidian-style)
- Interconnects ideas, projects, people, tools
- When a new idea comes in, it auto-connects to related nodes
- "This new idea relates to: Project X, Tool Y, Customer Z"
- Prevents building the same thing twice
- Prevents losing connections between ideas

### 3. STATUS TRACKER (The Poop Shutter)
- Every project/product/idea has a status:
  - WORKING ON (active this session)
  - TO DO (queued, ready to build)
  - BACKLOG (captured, not prioritized)
  - TO BE REWORKED (built but needs fixes)
  - ARCHIVED (done or abandoned)
- Auto-sorts based on activity
- Prevents "wait, did we finish that?"

### 4. KNOWLEDGE LIBRARY (The Shell Collection)
- Templates, styles, patterns that work
- "When building a blueprint, use THIS CSS"
- "When writing copy, use THIS voice"
- "When making covers, use THIS format"
- Prevents starting from zero every time
- Prevents style inconsistencies

### 5. FLEET SYNC (The Network)
- Shared files between Ceiba, Cobo, Naboria
- Each machine knows what the others are doing
- Content generation instructions for each AI service
- Syncthing-based, works offline

## The Hermit Crab Pattern
- The CRAB = memory files, patterns, knowledge, context
- The SHELL = the AI model (Claude 3.5, 4, 5, Opus, etc)
- When a new model drops, swap the shell, keep the crab
- All memory is in files, not in the model's weights
- Test new models against old ones using the same memory stack

## What to Build NOW (makes money)
- Nothing here. Finish listing products.

## What to Build NEXT (after sprint)
- Context Graph prototype (markdown-based, not a database)
- Status Tracker (upgrade MASTER_TODO.md with auto-sorting)
- Knowledge Library (extract patterns from what works)

## What to Build LATER
- Fleet Sync improvements
- Hermit Crab model-swap testing
- Full Obsidian-style graph visualization

## Poop Shutter - Extended Responsibilities

### Session Weight Management
- Track how much context has been used in current session
- When context is getting heavy (70%+), auto-trigger:
  1. Save all state to files
  2. Commit and push to git
  3. Suggest starting a new chat/branch
  4. Write a handoff note so the next session picks up seamlessly
- Prevents the "context exhaustion crash" where you lose everything

### Git Handling
- Auto-commit at checkpoints (every 4-6 deliverables)
- Auto-push when session ends
- Branch management for parallel work
- Never lose work to a crashed session
- The poop shutter IS the git manager

### Session Branching
- When a conversation goes deep into one topic (e.g., meditation app), branch it
- Main branch stays on revenue tasks
- Side branches for exploration/ideas
- Merge back when the exploration produces something useful
