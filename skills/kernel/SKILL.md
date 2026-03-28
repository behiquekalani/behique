---
name: kernel
description: Interface for the Ceiba Agent Kernel — the distributed AI task orchestrator that routes work between Computer 1 (Ceiba/Mac) and Computer 2 (Cobo/Windows). Use this skill whenever the user wants to send a task to the cluster, check what's running, query kernel memory, hit the bridge, or interact with Ollama/OpenClaw on Cobo. Triggers for "send this to Cobo", "submit a task", "check the queue", "what's running", "kernel status", "bridge health", "search memory", "run this on Ollama", "delegate this", or any reference to the ai_cluster, task queue, or distributed work. Also trigger when the user describes work that should run on a different machine or model — even if they don't say "kernel" explicitly.
---

# Kernel Skill — Ceiba Agent Cluster Interface

You are interfacing with the Ceiba Agent Kernel, a distributed task orchestrator that routes AI work across two machines via a shared filesystem and HTTP bridge.

## Architecture (what you're talking to)

| Component | Location | How to reach it |
|-----------|----------|-----------------|
| Task queue | `~/behique/ai_cluster/tasks/{inbox,active,done}/` | Read/write JSON files directly |
| Kernel memory | `~/behique/ai_cluster/memory/{knowledge,experiments,projects,skills}/` | Read `.md` files directly |
| Bridge (Cobo) | `https://bridge.merchoo.shop` | `curl` with bearer auth |
| Ollama (Cobo) | `http://192.168.0.151:11434` | `curl` directly (local network) |
| Kernel daemon | `python3 ai_cluster/kernel/agent_kernel.py` | Only on Computer 1 (requires Python) |

Both machines share `~/behique` via Syncthing in real time. Writing a file on either machine makes it appear on the other within seconds.

## Operations

### 1. Submit a task to the queue

Write a JSON file to the inbox. The kernel daemon on Computer 1 picks it up automatically.

```bash
TASK_ID="$(date +%Y%m%d-%H%M%S)-$(head -c 3 /dev/urandom | xxd -p | head -c 6)"
cat > ~/behique/ai_cluster/tasks/inbox/${TASK_ID}.json << 'TASKEOF'
{
  "task_id": "THE_TASK_ID",
  "objective": "What the AI worker should do",
  "context": "Any background info or constraints",
  "model_preference": [],
  "spawn_allowed": false
}
TASKEOF
```

**Routing hints** (put in `model_preference`):
- `["ollama"]` — free, fast, good for: summarize, classify, extract, format, score, list, count
- `["openclaw"]` or `["gpt4o"]` — GPT-4o via OpenClaw, good for: design, architect, debug, implement, code, research, analyze
- `[]` (empty) — let the kernel auto-route based on keywords in the objective

**spawn_allowed**: set `true` if the task can create subtasks (e.g., "research X and then summarize each source" might spawn per-source subtasks).

### 2. Check queue status

Read the directories directly — no Python needed.

```bash
echo "Inbox:  $(ls ~/behique/ai_cluster/tasks/inbox/*.json 2>/dev/null | wc -l) tasks"
echo "Active: $(ls ~/behique/ai_cluster/tasks/active/*.json 2>/dev/null | wc -l) tasks"
echo "Done:   $(ls ~/behique/ai_cluster/tasks/done/*.json 2>/dev/null | wc -l) tasks"

# Show pending tasks
for f in ~/behique/ai_cluster/tasks/inbox/*.json; do
  [ -f "$f" ] && echo "  Pending: $(cat "$f" | grep -o '"objective":[^,}]*')"
done

# Show active tasks
for f in ~/behique/ai_cluster/tasks/active/*.json; do
  [ -f "$f" ] && echo "  Active: $(cat "$f" | grep -o '"objective":[^,}]*')"
done
```

To read a completed task's result:
```bash
cat ~/behique/ai_cluster/tasks/done/TASK_ID.json
```

### 3. Search kernel memory

Kernel memory is plain markdown files organized by type. Search them directly.

```bash
# Search all memory for a keyword
grep -rl "keyword" ~/behique/ai_cluster/memory/

# Read a specific memory file
cat ~/behique/ai_cluster/memory/knowledge/filename.md

# List all memories by type
ls ~/behique/ai_cluster/memory/knowledge/
ls ~/behique/ai_cluster/memory/experiments/
ls ~/behique/ai_cluster/memory/projects/
ls ~/behique/ai_cluster/memory/skills/
```

To write a memory (the kernel also does this automatically from task output):
```bash
cat > ~/behique/ai_cluster/memory/knowledge/slug-name.md << 'EOF'
Your knowledge content here
EOF
```

### 4. Run a task immediately via Ollama

Skip the queue entirely — send a prompt straight to Ollama on Cobo.

```bash
curl -s http://192.168.0.151:11434/api/generate \
  -d '{"model": "llama3.2", "prompt": "YOUR PROMPT HERE", "stream": false}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('response',''))" 2>/dev/null \
  || curl -s http://192.168.0.151:11434/api/generate \
       -d '{"model": "llama3.2", "prompt": "YOUR PROMPT HERE", "stream": false}'
```

The first attempt uses Python to extract the response cleanly. If Python isn't available (Computer 2), the raw JSON is returned — still readable.

### 5. Run a command on Cobo via bridge

Execute any shell command on Computer 2 remotely.

```bash
BRIDGE_TOKEN=$(cat ~/.ceiba-config 2>/dev/null | grep BRIDGE_TOKEN | cut -d= -f2 || echo "$BRIDGE_TOKEN")
curl -s -X POST https://bridge.merchoo.shop \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BRIDGE_TOKEN" \
  -d '{"command": "YOUR COMMAND HERE"}'
```

Response: `{"stdout": "...", "stderr": "...", "exitCode": 0}`

### 6. Check bridge health

```bash
curl -s https://bridge.merchoo.shop
```

Expected: `{"status":"Bridge active","machine":"Cobo"}`

If it returns nothing or errors, the bridge server or Cloudflare tunnel may be down on Computer 2. Check pm2: send `pm2 list` via bridge, or if the bridge itself is down, it needs manual restart on Cobo.

## Task JSON format reference

**Submitted task** (inbox):
```json
{
  "task_id": "20260315-143022-a1b2c3",
  "objective": "Summarize the top 5 eBay listings for wireless earbuds under $30",
  "context": "For product research. Focus on price, reviews, seller rating.",
  "model_preference": ["ollama"],
  "spawn_allowed": false
}
```

**Completed task** (done):
```json
{
  "task_id": "20260315-143022-a1b2c3",
  "objective": "Summarize the top 5 eBay listings...",
  "result": "The AI worker's response text",
  "spawned": 0,
  "started": "2026-03-15T14:30:22",
  "completed": "2026-03-15T14:30:45"
}
```

## When to use which operation

| Situation | Operation |
|-----------|-----------|
| "Send this to Cobo" / "have the cluster do X" | Submit task to queue |
| "What's the kernel doing?" / "any tasks pending?" | Check queue status |
| "What does the kernel know about X?" | Search kernel memory |
| Quick question, no queue needed | Run directly via Ollama |
| Need to run a specific command on Computer 2 | Bridge command |
| "Is Cobo alive?" / "bridge working?" | Bridge health check |

## Important notes

- The kernel daemon must be running on Computer 1 for queued tasks to process. If tasks pile up in inbox, the daemon may be stopped.
- Ollama calls go to Cobo's local network IP (192.168.0.151). This only works from Computer 1 on the same network. From outside the network, use the bridge to run `curl localhost:11434/...` on Cobo instead.
- Bridge auth token is stored in `~/.ceiba-config` under `BRIDGE_TOKEN=`. Never hardcode it in skills or committed files.
- Task files sync via Syncthing. If you submit from Computer 2, it appears on Computer 1 within seconds.
