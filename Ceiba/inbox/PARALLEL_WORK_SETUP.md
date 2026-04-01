# Parallel Work Setup — You + Ceiba at the same time

## How it works

Open 2-3 terminal tabs. Each one runs `claude`. They share the same repo and memory system. The session manager prevents conflicts.

### Terminal 1: YOU (interactive)
```
cd ~/behique && claude
```
This is YOUR terminal. You talk to Ceiba, dump ideas, give commands, review work.

### Terminal 2: CEIBA (autonomous builder)
```
cd ~/behique && claude
```
Paste this prompt to start it building:
```
Build mode. Read mem/status.md. Pick the highest-impact task you can build without Kalani. Build it completely. Commit. Push. Move to the next one. Don't ask what to build. Don't stop. Register as session: python3 mem/scripts/session_manager.py register "autonomous building"
```

### Terminal 3: MONITOR (optional, tiny window)
```
cd ~/behique && python3 mem/scripts/live_status.py
```
Shows both sessions, what they're working on, git commits in real-time.

## The flow

1. You open Terminal 1, start talking to Ceiba about ideas
2. Ceiba in Terminal 2 is building products/tools in parallel
3. You dump an idea: "I want to vlog like Casey Neistat"
4. Your Ceiba (Terminal 1) processes it, saves to pipeline
5. Builder Ceiba (Terminal 2) picks it up on next cycle if it's high priority
6. Or you explicitly tell Terminal 1: "tell terminal 2 to build the vlog system"
7. Terminal 1 writes a task to mem/status.md → Terminal 2 picks it up

## Idea capture in this setup

In Terminal 1, just type naturally:
```
capture: i want to make a youtube video about how i built 89 products
```

Ceiba processes it → tags it → routes it → saves to pipeline.json.

If it's actionable, it goes to mem/status.md as a todo.
If Terminal 2 is running in build mode, it picks up new todos automatically.

## Communication between terminals

Both terminals share:
- `mem/status.md` (task list)
- `mem/primer.md` (current state)
- `tools/idea-capture/pipeline.json` (idea queue)
- `mem/sessions.json` (who's doing what)

Terminal 1 adds a task → Terminal 2 sees it → builds it → commits → you see the commit in the monitor.

## Quick start

1. Open 3 terminal tabs
2. Tab 1: `cd ~/behique && claude` (you)
3. Tab 2: `cd ~/behique && claude` (paste build mode prompt)
4. Tab 3: `cd ~/behique && python3 mem/scripts/live_status.py` (monitor)
5. Start talking in Tab 1. Building happens in Tab 2.
