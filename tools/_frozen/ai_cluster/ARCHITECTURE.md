---
title: "ARCHITECTURE"
type: system
tags: [ceiba, cobo, built:, 2026-03-15, status:]
created: 2026-03-16
---

# Ceiba + Cobo — Distributed AI Cluster Architecture
# Built: 2026-03-15
# Status: OPERATIONAL — kernel tested, all routes working

---

## What This Is

A 2-node distributed AI cluster running on consumer hardware:
- **Computer 1 (Mac)** — Ceiba (Claude Opus) — planner, orchestrator, brain
- **Computer 2 (Windows)** — Cobo (GPT-4o + Ollama) — worker node, parallel reasoning

Ceiba thinks. Cobo executes. Ollama handles the cheap stuff for free.

---

## Architecture Overview

```
                 ┌─────────────────────────┐
                 │        HUMAN            │
                 └────────────┬────────────┘
                              │
                       (primary interface)
                              │
                    ┌─────────▼─────────┐
                    │   CEIBA (Mac)     │
                    │ Claude Opus Brain │
                    │ Task Orchestrator │
                    └───────┬───────────┘
                            │
      ┌─────────────────────┼───────────────────┐
      │                     │                   │
      │                     │                   │
┌─────▼───────┐   ┌────────▼────────┐  ┌───────▼─────────┐
│   OLLAMA    │   │  HTTP BRIDGE    │  │  LOCAL TOOLS    │
│ Llama3.2   │   │  port 9876      │  │  git, fs, etc   │
│ (free)     │   │  bearer auth    │  │                 │
└─────┬──────┘   └────────┬────────┘  └─────────────────┘
      │                   │
      │                   │
      │           ┌───────▼────────────┐
      │           │   COBO (Windows)   │
      │           │ OpenClaw + GPT-4o  │
      │           │ Worker Agent Node  │
      │           └─────────┬──────────┘
      │                     │
      │                     ▼
      │               Parallel Tasks
      │
      ▼
 Cheap preprocessing
```

---

## Three Routing Lanes

| Lane   | Model              | Use Case                        | Cost  |
|--------|--------------------|---------------------------------|-------|
| FAST   | Ollama (Llama3.2)  | Summarize, classify, format     | Free  |
| WORKER | GPT-4o via OpenClaw| Code, debug, design, research   | Paid  |
| BRAIN  | Claude Opus        | Planning, architecture, eval    | Included |

---

## How It Works

### Task Protocol (AI-TASK v1)

Every job follows this schema:

```json
{
  "task_id": "string",
  "parent_task": "string|null",
  "objective": "what needs to be done",
  "context": "background info",
  "model_preference": ["ollama", "gpt4o", "claude"],
  "spawn_allowed": true,
  "deliverables": ["architecture", "code", "analysis"]
}
```

### Task Lifecycle

```
tasks/inbox/task.json     ← Ceiba drops task here
        ↓
kernel picks it up
        ↓
tasks/active/             ← being processed
        ↓
memory search             ← inject relevant knowledge
        ↓
route to AI model         ← Ollama / GPT-4o / Claude
        ↓
execute + parse result
        ↓
store memory writes       ← knowledge persists
        ↓
spawn subtasks            ← workers create child tasks
        ↓
tasks/done/task.json      ← result stored
```

### Worker Spawning

Workers can create new tasks autonomously:

```json
{
  "result": "High-level architecture designed",
  "spawn_tasks": [
    {"objective": "Design database schema", "model_preference": ["gpt4o"]},
    {"objective": "Generate API endpoints", "model_preference": ["gpt4o"]}
  ],
  "memory_write": [
    {"type": "knowledge", "content": "Async queues outperform polling for task distribution"}
  ]
}
```

Ceiba launches those subtasks automatically.

---

## Persistent Memory System

Workers accumulate knowledge over time.

```
ai_cluster/memory/
    knowledge/     ← facts about the world
    experiments/   ← what worked and failed
    projects/      ← project-specific context
    skills/        ← how skills behave
```

**Before every task**, the kernel searches memory and injects relevant context into the prompt. Workers store discoveries automatically. Future agents reuse them.

---

## Self-Improving Skill Factory

Skills are first-class objects with a development pipeline:

```
PLAN → DESIGN → IMPLEMENT → TEST → SCORE → IMPROVE
```

```
ai_cluster/skills/
    registry.json          ← tracks all skills with versions + scores
    web_research/
        skill.yaml
        code/
        tests/
        metrics.json
```

Ceiba prioritizes low-scoring skills for improvement.

---

## Infrastructure (Live)

| Component | Location | Status |
|-----------|----------|--------|
| Agent Kernel | `~/behique/ai_cluster/kernel/agent_kernel.py` | Operational |
| Bridge Server | `192.168.0.151:9876` (pm2) | Online |
| Cloudflare Tunnel | `bridge.merchoo.shop` | Online |
| Ollama | `192.168.0.151:11434` (llama3.2) | Online |
| OpenClaw | Cobo, @CeibaOC2Bot, GPT-4o | Online |
| Syncthing | `~/behique` synced both machines | Synced |
| Task Queue | `ai_cluster/tasks/{inbox,active,done}` | Working |
| Memory Store | `ai_cluster/memory/{knowledge,experiments,projects,skills}` | Working |

---

## CLI Reference

```bash
# Run kernel daemon (polls inbox continuously)
python3 ai_cluster/kernel/agent_kernel.py

# Execute single task immediately
python3 ai_cluster/kernel/agent_kernel.py run '{"objective": "...", "model_preference": ["ollama"]}'

# Submit task to queue
python3 ai_cluster/kernel/agent_kernel.py submit '{"objective": "..."}'

# Check queue status
python3 ai_cluster/kernel/agent_kernel.py status

# Search memory
python3 ai_cluster/kernel/agent_kernel.py memory "search query"

# List registered skills
python3 ai_cluster/kernel/agent_kernel.py skills

# Quick dispatch (bash)
bash bridge/dispatch.sh fast "cheap task for Ollama"
bash bridge/dispatch.sh worker "heavy task for GPT-4o"
bash bridge/dispatch.sh brain "stays on Ceiba"
```

---

## Smart Cost Routing

The kernel auto-routes based on task content:

| Task Type | Route | Reason |
|-----------|-------|--------|
| Summarization | Ollama | Free |
| Classification | Ollama | Free |
| Formatting | Ollama | Free |
| Log analysis | Ollama | Free |
| Code generation | GPT-4o | Fast + capable |
| Debugging | GPT-4o | Excellent |
| Architecture design | GPT-4o | Strong reasoning |
| Research | GPT-4o | Scale horizontally |
| Strategic planning | Claude Opus | Best coherence |
| System evaluation | Claude Opus | Deepest reasoning |
| Final synthesis | Claude Opus | Best quality |

---

## Future Scaling

```
Mac    → Ceiba (planner)
Windows → Cobo (worker)
Linux  → Cobo2 (worker)
Server → GPU inference
```

Architecture already supports adding nodes.

---

## The Vision

This is a personal autonomous AI research platform.
Two consumer machines running:
- Distributed reasoning
- Autonomous skill creation
- Memory accumulation
- Self-improving codebase
- Cost-optimized inference
- Parallel execution

Very close to what internal AI research platforms at major companies look like.

Built by Kalani with Ceiba + ChatGPT architecture design.
Running on a Mac and a Windows PC in Puerto Rico.
