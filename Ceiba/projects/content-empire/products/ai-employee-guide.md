# How I Built an AI Employee: The Complete System Guide

**By Kalani Andre Gomez Padin**

*A computer engineering student's blueprint for building a multi-machine AI agent system that works while you sleep. Three computers, zero monthly cost, infinite use.*

---

## Table of Contents

1. [Introduction: The Story](#1-introduction-the-story)
2. [The Architecture](#2-the-architecture)
3. [Hardware Requirements](#3-hardware-requirements)
4. [Software Stack](#4-software-stack)
5. [Setting Up Your First Machine (HQ)](#5-setting-up-your-first-machine-hq)
6. [Adding Worker Nodes](#6-adding-worker-nodes)
7. [Cross-Machine Communication](#7-cross-machine-communication)
8. [Agent Configuration](#8-agent-configuration)
9. [Task Delegation Framework](#9-task-delegation-framework)
10. [Building Your First Automation](#10-building-your-first-automation)
11. [Monitoring and Maintenance](#11-monitoring-and-maintenance)
12. [Cost Breakdown](#12-cost-breakdown)
13. [Troubleshooting](#13-troubleshooting)
14. [What's Next: Scaling Beyond 3 Machines](#14-whats-next-scaling-beyond-3-machines)

---

## 1. Introduction: The Story

I am a computer engineering student in Puerto Rico. I do not work for a tech company. I do not have a server rack in my closet. I do not pay for cloud computing. What I do have is three computers, a local network, and a system that executes tasks for me while I am in class, while I am eating dinner, and while I am sleeping.

The system is called Behique. Named after the spiritual healers and knowledge-keepers of the Taino people, the indigenous civilization of the Caribbean. A behique was the person in the community who understood systems that others could not see. That felt like the right name for what I was building.

Here is what Behique does on any given day:

- Processes a queue of AI tasks across three physical machines
- Routes work to the cheapest available model (free local inference first, paid APIs only when necessary)
- Generates short-form video content using text-to-speech, image generation, and FFmpeg
- Manages an eBay listing pipeline that researches products, writes descriptions, and formats listings
- Runs an accountability bot on Telegram that classifies my ideas, tracks my progress, and stores everything to Notion
- Syncs files across all machines automatically
- Accumulates knowledge in a persistent memory system that makes every future task smarter

The total monthly cost of running this system is zero dollars.

I built this over the course of several weeks, starting from scratch. Not because I am some genius, but because the tools exist and nobody is talking about how to connect them. Every tutorial I found online was about one tool in isolation. "How to use Ollama." "How to set up n8n." "How to use Claude." Nobody was writing about how to make all of them work together as a single organism distributed across multiple machines.

That is what this guide is for.

By the end of this document, you will have a complete blueprint for building your own AI employee. Not a chatbot. Not a single script. A distributed, autonomous system that runs on hardware you probably already own, costs nothing per month, and gets smarter over time.

I will show you exactly how I built mine. Every tool, every configuration file, every decision I made and why. Where I failed. What I would do differently. And how you can build yours in a weekend.

Let's get into it.

---

## 2. The Architecture

Before we install anything, you need to understand the shape of the system. Every decision I made flows from this architecture. If you understand the shape, you can adapt everything else to your own hardware and use case.

### The Three-Machine Layout

```
 ┌──────────────────────────────────┐
 │ YOU (Human) │
 │ Telegram / Terminal / Web │
 └───────────────┬──────────────────┘
 │
 (primary interface)
 │
 ┌───────────────▼──────────────────┐
 │ CEIBA (HQ Machine) │
 │ Mac M4, 16GB, 192.168.0.145 │
 │ │
 │ - Claude Code CLI (brain) │
 │ - Agent Kernel (orchestrator) │
 │ - Task queue (inbox/active/done) │
 │ - Memory system (knowledge DB) │
 │ - Ollama (qwen2.5:7b local) │
 │ - Reel pipeline (TTS + SD) │
 │ - Git repo (source of truth) │
 └──────┬──────────────┬────────────┘
 │ │
 ┌────────────┘ └────────────┐
 │ Syncthing (file sync) │
 │ HTTP Bridge (task dispatch) │
 │ │
 ┌─────────▼──────────────┐ ┌───────────────▼──────────┐
 │ COBO (Worker #1) │ │ HUTIA (Worker #2) │
 │ Windows, GTX 1080 Ti │ │ Always-on Node │
 │ 192.168.0.151 │ │ 192.168.0.152 │
 │ │ │ │
 │ - Ollama (inference) │ │ - Background tasks │
 │ - n8n (automations) │ │ - Cron jobs │
 │ - Bridge server │ │ - Monitoring │
 │ - 11GB VRAM for GPU │ │ - Always available │
 │ inference │ │ │
 └────────────────────────┘ └───────────────────────────┘
```

### The Core Concept: Think, Route, Execute

The entire system follows one pattern:

1. A task enters the system (from you, from a cron job, from another task)
2. The HQ machine decides which model and which machine should handle it
3. The task gets routed to the appropriate node
4. The result comes back, gets stored, and may spawn new tasks

That is it. Everything else is implementation detail.

### Three Routing Lanes

Every task in the system goes through one of three lanes:

| Lane | Model | Machine | Cost | Use Case |
|------|-------|---------|------|----------|
| FAST | Ollama (qwen2.5:7b) | Cobo or Ceiba | Free | Summarize, classify, format, extract |
| WORKER | GPT-4o / Heavy LLM | Cobo | Paid (optional) | Code gen, deep research, debugging |
| BRAIN | Claude Code | Ceiba | Included with CLI | Architecture, planning, final synthesis |

The FAST lane handles 70-80% of all tasks. That is why the system costs nothing. Most AI work does not require GPT-4 or Claude. It requires a 7B parameter model that can follow instructions. Those run for free on consumer hardware.

### File-Based Task Queue

I do not use Redis. I do not use RabbitMQ. I do not use Kafka. The task queue is JSON files in folders.

```
ai_cluster/
 tasks/
 inbox/ <-- New tasks land here
 active/ <-- Currently being processed
 done/ <-- Completed with results
 memory/
 knowledge/ <-- Facts the system has learned
 experiments/<-- What worked and what failed
 projects/ <-- Project-specific context
 skills/ <-- Skill behavior documentation
 kernel/
 agent_kernel.py <-- The orchestrator
 skills/
 registry.json <-- All registered capabilities
```

Why files instead of a database? Because files sync with Syncthing. Because files are human-readable. Because when something breaks at 2 AM, I can open a folder and see exactly what happened. Because JSON files in a folder is the simplest possible queue, and simplicity is what lets a single person manage a distributed system.

---

## 3. Hardware Requirements

### What I Actually Use

| Machine | Role | Specs | Cost |
|---------|------|-------|------|
| Ceiba (Mac M4) | HQ, brain, orchestrator | M4 chip, 16GB unified RAM, 256GB SSD | ~$1,200 |
| Cobo (Windows PC) | GPU worker, bridge | GTX 1080 Ti (11GB VRAM), 16GB RAM | ~$600 used |
| Hutia (Comp 3) | Always-on background | Basic specs, always powered on | Already owned |

Total hardware investment: Whatever computers you already have.

### Minimum Viable System (1 Machine)

You can start with a single machine. Honestly, one computer with 16GB RAM can run the entire system minus the GPU inference. Here is the minimum:

- **CPU:** Any modern processor (M1+ Mac, Ryzen 5+, Intel i5+)
- **RAM:** 16GB minimum (8GB works but you will feel it)
- **Storage:** 50GB free space (models take up room)
- **GPU:** Optional but helpful. Any NVIDIA card with 6GB+ VRAM, or an Apple Silicon Mac
- **Network:** Just needs to reach the internet for initial downloads

### Budget Build (2 Machines, Under $400)

If you are starting from nothing:

- **Machine 1 (HQ):** Used ThinkPad T480 or similar, $150-200. Runs the kernel, CLI tools, and orchestration.
- **Machine 2 (Worker):** Used desktop with a GTX 1060 6GB or GTX 1070, $150-200. Runs Ollama for local inference.

Total: Under $400. Both machines on the same local network.

### The GPU Question

You do not need a GPU to start. Ollama runs on CPU. It is slower but it works. A 7B model on a modern CPU generates about 5-10 tokens per second. On a GPU, that jumps to 30-80 tokens per second.

For reference, here is what different GPUs can handle:

| GPU | VRAM | Largest Model | Tokens/sec (7B) |
|-----|------|---------------|------------------|
| GTX 1060 6GB | 6GB | 7B (tight) | ~25 |
| GTX 1080 Ti | 11GB | 13B comfortable | ~35 |
| RTX 3060 12GB | 12GB | 13B comfortable | ~40 |
| RTX 3090 | 24GB | 30B+ | ~50 |
| Mac M1/M2/M4 | Unified | Depends on RAM | 20-40 |

My GTX 1080 Ti handles qwen2.5:7b at around 35 tokens per second. That is more than fast enough for background task processing.

### Apple Silicon Note

If you have a Mac with Apple Silicon (M1, M2, M3, M4), you are in a great position. The unified memory architecture means your GPU and CPU share the same RAM pool. A 16GB M4 Mac can run 7B models natively using Metal acceleration. I run Ollama with qwen2.5:7b directly on my Mac as a backup when Cobo is offline.

For image generation, Apple Silicon supports MLX Stable Diffusion, which generates images locally using the Metal 3 GPU. No NVIDIA required.

---

## 4. Software Stack

Here is every piece of software in the system, why I chose it, and what it connects to.

### AI Models and Inference

| Tool | What It Does | Why I Chose It |
|------|-------------|----------------|
| **Ollama** | Local LLM inference server | Free, simple, runs anywhere, REST API built in |
| **qwen2.5:7b** | Primary local model | Best quality-to-size ratio I have tested at 7B |
| **Claude Code CLI** | Primary reasoning engine | Best at complex planning, architecture, code generation |
| **GPT-4o-mini** | BehiqueBot backend | Cheap API, good for classification and short responses |

**Ollama** is the backbone. It turns any machine into an inference server with one command. Install it, pull a model, and you have a REST API at `localhost:11434` that any script can call. No Python wrappers needed, no SDK, just HTTP POST requests with JSON.

**Why qwen2.5:7b?** I tested llama3.2, mistral, phi-3, and qwen2.5 at the 7B size. Qwen2.5 consistently produced the most structured, instruction-following output. When your tasks are automated, you need a model that follows formatting instructions reliably. Qwen2.5 does that.

### Automation and Orchestration

| Tool | What It Does | Why I Chose It |
|------|-------------|----------------|
| **n8n** | Visual workflow automation | Self-hosted, free, connects to everything |
| **Agent Kernel** | Custom Python task orchestrator | Built for exactly my use case |
| **Shell scripts** | Task dispatch, cron jobs | Simple, portable, no dependencies |
| **pm2** | Process manager | Keeps services alive after crashes |

**n8n** runs on Cobo and handles the workflows that connect external services. Webhook triggers, API calls, data transformations. It is like Zapier but self-hosted and free.

**The Agent Kernel** is a Python script I wrote. It polls an inbox folder, routes tasks to the right AI model, processes results, and stores learnings in memory. About 600 lines of code. I will show you the entire thing later.

### Communication Layer

| Tool | What It Does | Why I Chose It |
|------|-------------|----------------|
| **Syncthing** | File synchronization | Free, peer-to-peer, no cloud, encrypted |
| **HTTP Bridge** | Remote command execution | Custom Node.js server with bearer auth |
| **Telegram Bot API** | Human interface | Free, works on phone, supports voice |
| **Cloudflare Tunnel** | External access | Free, secure, no port forwarding needed |

**Syncthing** is the glue. It keeps the `~/behique` folder synchronized between Ceiba and Cobo in real time. When Ceiba drops a task file into the inbox folder, Syncthing copies it to Cobo within seconds. When Cobo writes results, they sync back. No central server required. Peer-to-peer, encrypted, and it has never failed me.

**The HTTP Bridge** is a small Node.js server running on Cobo. It accepts POST requests with a bearer token and executes shell commands. This is how Ceiba sends direct commands to Cobo without waiting for file sync.

### Content Production

| Tool | What It Does | Why I Chose It |
|------|-------------|----------------|
| **Kokoro TTS** | Text-to-speech narration | Open source, runs locally, ONNX format |
| **MLX Stable Diffusion** | Image generation on Mac | Native Apple Silicon, no NVIDIA needed |
| **FFmpeg** | Video assembly | Industry standard, scriptable, free |

My reel production pipeline takes a JSON story file and produces a finished video. Kokoro generates the narration audio. Stable Diffusion generates the images. FFmpeg stitches everything together with transitions and timing. The whole pipeline runs in 3-4 minutes per reel at zero cost.

### Persistence and Memory

| Tool | What It Does | Why I Chose It |
|------|-------------|----------------|
| **Notion** | Structured data for BehiqueBot | Great API, flexible schema, Kalani already uses it |
| **File-based memory** | AI knowledge persistence | Simple, syncable, human-readable |
| **Git** | Version control and history | Every change is tracked and reversible |

---

## 5. Setting Up Your First Machine (HQ)

This is the step-by-step for getting your primary machine running. I am going to assume you are on macOS or Linux. Windows instructions are similar but I will call out differences where they matter.

### Step 1: Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

On Windows, download the installer from ollama.com.

### Step 2: Pull Your First Model

```bash
# Pull qwen2.5:7b (4.4 GB download)
ollama pull qwen2.5:7b

# Test it
ollama run qwen2.5:7b "What is 2+2? Reply in one word."
```

If that responds with "Four" or "4", your local inference is working. You now have a free AI model running on your machine.

### Step 3: Make Ollama Accessible on Your Network

By default, Ollama only listens on localhost. To let other machines reach it:

```bash
# macOS / Linux: Set environment variable
export OLLAMA_HOST=0.0.0.0

# Then restart Ollama
# On macOS, quit the Ollama app and reopen it
# On Linux:
systemctl restart ollama

# Verify it is accessible from another machine
# From another computer on your network:
curl http://YOUR_IP:11434/api/tags
```

Replace `YOUR_IP` with your machine's local IP address (like 192.168.0.145).

### Step 4: Set Up the Project Directory

```bash
mkdir -p ~/behique
cd ~/behique

# Create the AI cluster directory structure
mkdir -p ai_cluster/tasks/{inbox,active,done}
mkdir -p ai_cluster/memory/{knowledge,experiments,projects,skills}
mkdir -p ai_cluster/kernel
mkdir -p ai_cluster/skills
mkdir -p bridge
mkdir -p tools

# Initialize git
git init
```

### Step 5: Install Python Dependencies

```bash
# Create a virtual environment (optional but recommended)
python3 -m venv ~/.venvs/behique
source ~/.venvs/behique/bin/activate

# Install what the kernel needs
pip install requests
```

That is it. The agent kernel only needs `requests` for HTTP calls. I keep dependencies minimal on purpose.

### Step 6: Create the Agent Kernel

Create the file `ai_cluster/kernel/agent_kernel.py`. Here is the core structure:

```python
#!/usr/bin/env python3
"""
Agent Kernel - Distributed AI Task Orchestrator
Polls an inbox folder for JSON task files, routes them to
the appropriate AI model, and stores results.
"""

import os
import json
import time
import uuid
import re
import requests
from pathlib import Path
from datetime import datetime

# === CONFIG ===
ROOT = Path(__file__).resolve().parent.parent
TASK_INBOX = ROOT / "tasks" / "inbox"
TASK_ACTIVE = ROOT / "tasks" / "active"
TASK_DONE = ROOT / "tasks" / "done"
MEMORY_DIR = ROOT / "memory"

# AI endpoints - adjust these IPs to match your network
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

BRIDGE_URL = "http://192.168.0.151:9876" # Worker machine
BRIDGE_TOKEN = os.getenv("BRIDGE_TOKEN", "")

POLL_INTERVAL = 3 # seconds


def generate_task_id():
 ts = datetime.now().strftime("%Y%m%d-%H%M%S")
 short = uuid.uuid4().hex[:6]
 return f"{ts}-{short}"


def run_ollama(prompt):
 """Send prompt to Ollama. Free and fast."""
 payload = {
 "model": OLLAMA_MODEL,
 "prompt": prompt,
 "stream": False,
 }
 try:
 r = requests.post(OLLAMA_URL, json=payload, timeout=120)
 return r.json().get("response", "")
 except Exception as e:
 return f"[OLLAMA ERROR] {e}"


def memory_search(query, limit=5):
 """Search memory files for relevant context."""
 results = []
 query_words = set(query.lower().split())

 for mem_dir in MEMORY_DIR.iterdir():
 if not mem_dir.is_dir():
 continue
 for f in mem_dir.glob("*.md"):
 try:
 text = f.read_text()
 score = sum(1 for w in query_words if w in text.lower())
 if score > 0:
 results.append((score, text[:500], f.name))
 except Exception:
 pass

 results.sort(key=lambda x: x[0], reverse=True)
 return results[:limit]


def route_task(objective):
 """Decide which AI model handles this task."""
 obj = objective.lower()

 cheap_keywords = [
 "summarize", "format", "extract", "classify",
 "clean", "list", "count", "score", "simple", "quick"
 ]

 for kw in cheap_keywords:
 if kw in obj:
 return "ollama"

 return "ollama" # Default to free. Change to "bridge" for paid.


def execute_task(task_data):
 """Build prompt, inject memory, route to AI, return output."""
 objective = task_data.get("objective", "")
 context = task_data.get("context", "")

 # Search memory for relevant context
 memories = memory_search(objective)
 memory_text = ""
 if memories:
 memory_text = "\nRelevant knowledge:\n"
 for score, text, name in memories:
 memory_text += f"- [{name}] {text}\n"

 prompt = f"""You are an AI worker in a distributed system.

Objective: {objective}
Context: {context}
{memory_text}

Respond in JSON:
{{
 "result": "your answer here",
 "memory_write": [],
 "spawn_tasks": []
}}

If you learn something useful, add to memory_write:
{{"type": "knowledge", "content": "what you learned"}}
"""

 route = route_task(objective)

 if route == "ollama":
 raw = run_ollama(prompt)
 else:
 raw = run_ollama(prompt) # Fallback to Ollama

 # Parse response
 try:
 match = re.search(r'\{[\s\S]*\}', raw)
 if match:
 parsed = json.loads(match.group())
 else:
 parsed = {"result": raw}
 except Exception:
 parsed = {"result": raw}

 # Store memory writes
 for entry in parsed.get("memory_write", []):
 store_memory(entry)

 return parsed


def store_memory(entry):
 """Persist a knowledge entry to disk."""
 mem_type = entry.get("type", "knowledge")
 content = entry.get("content", "")
 if not content:
 return

 target = MEMORY_DIR / mem_type
 target.mkdir(parents=True, exist_ok=True)

 slug = re.sub(r'[^a-z0-9]+', '-', content[:50].lower()).strip('-')
 path = target / f"{slug}.md"
 path.write_text(content)


def main():
 """Main loop: poll inbox, process tasks, store results."""
 print(f"Agent Kernel started. Watching: {TASK_INBOX}")

 while True:
 tasks = sorted(TASK_INBOX.glob("*.json"))

 if not tasks:
 time.sleep(POLL_INTERVAL)
 continue

 task_file = tasks[0]
 print(f"Processing: {task_file.name}")

 # Move to active
 active_path = TASK_ACTIVE / task_file.name
 task_file.rename(active_path)

 # Load and execute
 task_data = json.loads(active_path.read_text())
 result = execute_task(task_data)

 # Save to done
 result["task_id"] = task_data.get("task_id", task_file.stem)
 result["completed"] = datetime.now().isoformat()

 done_path = TASK_DONE / task_file.name
 done_path.write_text(json.dumps(result, indent=2))

 # Clean up active
 if active_path.exists():
 active_path.unlink()

 print(f"Done: {result.get('result', '')[:100]}")
 print("---")


if __name__ == "__main__":
 main()
```

### Step 7: Test the Kernel

```bash
# Submit a test task
cat > ~/behique/ai_cluster/tasks/inbox/test-001.json << 'EOF'
{
 "task_id": "test-001",
 "objective": "Summarize the benefits of local AI inference in 3 bullet points",
 "context": "This is a test task for the agent kernel",
 "model_preference": ["ollama"]
}
EOF

# Run the kernel
python3 ~/behique/ai_cluster/kernel/agent_kernel.py
```

You should see the kernel pick up the task, route it to Ollama, and write the result to the `done` folder. Check `ai_cluster/tasks/done/test-001.json` to see the output.

### Step 8: Create the Dispatch Script

This is a quick shortcut for sending tasks to different AI models from the command line:

```bash
cat > ~/behique/bridge/dispatch.sh << 'SCRIPT'
#!/bin/bash
# Quick dispatch to different AI lanes
# Usage: bash dispatch.sh <fast|worker|brain> <prompt>

OLLAMA_URL="http://localhost:11434/api/generate"

LANE="$1"
shift
PROMPT="$*"

if [ -z "$LANE" ] || [ -z "$PROMPT" ]; then
 echo "Usage: dispatch.sh <fast|worker|brain> <prompt>"
 exit 1
fi

case "$LANE" in
 fast)
 JSON=$(python3 -c "import json,sys; print(json.dumps({
 'model':'qwen2.5:7b',
 'prompt':sys.argv[1],
 'stream':False
 }))" "$PROMPT")
 curl -s -X POST "$OLLAMA_URL" \
 -H "Content-Type: application/json" \
 -d "$JSON" \
 | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"
 ;;
 worker)
 echo "[WORKER] Route to remote GPU node"
 echo "Prompt: $PROMPT"
 ;;
 brain)
 echo "[BRAIN] This stays on HQ for deep reasoning"
 echo "Prompt: $PROMPT"
 ;;
esac
SCRIPT

chmod +x ~/behique/bridge/dispatch.sh
```

Test it:

```bash
bash ~/behique/bridge/dispatch.sh fast "What is the capital of France? One word."
```

Congratulations. You have a working AI employee on one machine. It can accept tasks, route them to a local model, execute them, and store the results. Everything from here builds on this foundation.

---

## 6. Adding Worker Nodes

One machine is fine. Two machines is a force multiplier. Here is how to turn a second computer into a worker node.

### Why Add a Second Machine?

Three reasons:

1. **Parallel execution.** While your HQ machine is doing complex planning, the worker can be crunching through a queue of simple tasks.
2. **GPU offloading.** If your worker has a dedicated GPU, it handles inference faster than your CPU.
3. **Always-on capability.** Your HQ might be your laptop that you close and carry around. A desktop worker stays running 24/7.

### Worker Setup (Linux or Windows)

#### Install Ollama on the Worker

Same process as HQ:

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull qwen2.5:7b

# Make it accessible on the network
export OLLAMA_HOST=0.0.0.0
```

On Windows, install Ollama from the website. It binds to all interfaces by default.

Verify from your HQ machine:

```bash
curl http://WORKER_IP:11434/api/tags
```

#### Install n8n (Optional but Powerful)

n8n gives you visual workflow automation. Install it with npm:

```bash
npm install -g n8n

# Run it
n8n start

# Or use pm2 to keep it alive
npm install -g pm2
pm2 start n8n
pm2 save
```

n8n will be available at `http://WORKER_IP:5678`. You can build workflows that trigger on webhooks, process data, call APIs, and feed results back into your task queue.

#### Set Up the Bridge Server

The bridge server is a lightweight HTTP server that lets your HQ machine execute commands on the worker remotely. Here is a minimal Node.js implementation:

```javascript
// bridge-server.js
const http = require('http');
const { exec } = require('child_process');

const PORT = 9876;
const AUTH_TOKEN = process.env.BRIDGE_TOKEN || 'your-secret-token-here';

const server = http.createServer((req, res) => {
 // Only accept POST
 if (req.method !== 'POST') {
 res.writeHead(405);
 res.end('Method not allowed');
 return;
 }

 // Check auth
 const auth = req.headers['authorization'];
 if (auth !== `Bearer ${AUTH_TOKEN}`) {
 res.writeHead(401);
 res.end('Unauthorized');
 return;
 }

 let body = '';
 req.on('data', chunk => body += chunk);
 req.on('end', () => {
 try {
 const { command } = JSON.parse(body);

 exec(command, { timeout: 300000 }, (error, stdout, stderr) => {
 res.writeHead(200, { 'Content-Type': 'application/json' });
 res.end(JSON.stringify({
 stdout: stdout || '',
 stderr: stderr || '',
 exitCode: error ? error.code : 0
 }));
 });
 } catch (e) {
 res.writeHead(400);
 res.end(JSON.stringify({ error: e.message }));
 }
 });
});

server.listen(PORT, '0.0.0.0', () => {
 console.log(`Bridge server running on port ${PORT}`);
});
```

Run it:

```bash
# Set a secure token
export BRIDGE_TOKEN="generate-a-random-string-here"

# Start with pm2
pm2 start bridge-server.js --name bridge
pm2 save
```

**Security note:** This bridge server executes arbitrary commands. Only run it on a trusted local network. The bearer token provides basic authentication. For production use, add HTTPS and IP whitelisting.

#### Test the Bridge

From your HQ machine:

```bash
curl -s -X POST http://WORKER_IP:9876 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer your-secret-token-here" \
 -d '{"command": "ollama list"}'
```

You should see a JSON response with the command output. If that works, your HQ can now execute commands on the worker.

### Adding Hutia (The Always-On Node)

My third machine, Hutia, serves a different purpose than Cobo. It is not a GPU powerhouse. It is simply always on. Here is what always-on gets you:

- **Cron jobs that actually run.** Scheduled tasks need a machine that does not sleep.
- **Monitoring.** Health checks on other machines, alerting when something goes down.
- **Background processing.** Long-running tasks that take hours.
- **Telegram bot hosting.** Your bot is always reachable.

The setup is identical to a worker node. Install Ollama (even a small model is useful), set up Syncthing, and configure it as a background task runner.

---

## 7. Cross-Machine Communication

This is the part most people get wrong. They try to build a complex microservices architecture with message queues and service discovery. You do not need any of that. You need two things: file sync and an HTTP bridge.

### Syncthing: The Backbone

Syncthing keeps folders synchronized between machines in real time. No cloud server, no account, peer-to-peer, encrypted. Install it on every machine in your fleet.

#### Installation

```bash
# macOS
brew install syncthing

# Linux (Debian/Ubuntu)
sudo apt install syncthing

# Windows
# Download from syncthing.net
```

#### Configuration

1. Start Syncthing on each machine. It opens a web UI at `http://localhost:8384`.
2. On each machine, note the Device ID (a long string in Settings > Show ID).
3. On Machine A, add Machine B as a remote device using its Device ID.
4. On Machine B, accept the connection from Machine A.
5. Share the `~/behique` folder between both machines.

That is the entire setup. Now when you drop a file in `~/behique/ai_cluster/tasks/inbox/` on your Mac, it appears on your Windows PC within seconds.

#### What I Sync

```
~/behique/ <-- The entire project folder
 ai_cluster/ <-- Task queue, memory, kernel
 bridge/ <-- Dispatch scripts, task specs
 tools/ <-- Shared tools and pipelines
 Ceiba/ <-- Knowledge vault
```

#### What I Do Not Sync

Large model files, temporary outputs, virtual environments. Add a `.stignore` file:

```
# .stignore
.venv
__pycache__
*.pyc
node_modules
*.onnx
*.bin
output/
.git
```

### The HTTP Bridge: Direct Commands

File sync is great for asynchronous work. But sometimes you need a response right now. That is what the bridge is for.

The bridge server (shown in the previous chapter) runs on your worker node and accepts HTTP requests. Your HQ machine sends commands and gets results back immediately.

Here is how the dispatch script uses both channels:

```bash
# FAST lane: Direct Ollama call to worker's GPU
bash dispatch.sh fast "Classify this product: Nike Air Max 90"

# Response comes back in ~2 seconds via HTTP
```

Versus the file-based queue:

```bash
# Submit task to inbox (async, processed whenever)
cat > ai_cluster/tasks/inbox/classify-001.json << 'EOF'
{
 "task_id": "classify-001",
 "objective": "Classify these 50 products into categories",
 "context": "See products.csv in the project folder"
}
EOF

# Syncthing delivers it to the worker
# Kernel picks it up and processes it
# Result appears in tasks/done/ via Syncthing
```

### Telegram Bot Relay

BehiqueBot runs on Railway (free tier) and acts as my human interface to the system. I send it a voice message while walking to class, and it:

1. Transcribes the audio using OpenAI Whisper
2. Classifies the idea (CREATIVE, BUSINESS, KNOWLEDGE, PERSONAL, TECHNICAL)
3. Tags it with a life pillar (health, wealth, relationships, general)
4. Saves a seed record to Notion
5. Sends me a confirmation

I can also send it text commands that get routed to the agent kernel. The bot is the bridge between my phone and the distributed system.

### Cloudflare Tunnel (Optional)

If you want to access your system from outside your home network (for webhooks, remote monitoring, or mobile access), Cloudflare Tunnel gives you a secure public URL for free:

```bash
# Install cloudflared
brew install cloudflared # or apt install cloudflared

# Create a named tunnel
cloudflared tunnel create behique-bridge

# Route traffic
cloudflared tunnel route dns behique-bridge bridge.yourdomain.com

# Run it
cloudflared tunnel run --url http://localhost:9876 behique-bridge
```

Now `https://bridge.yourdomain.com` routes to your local bridge server with full HTTPS. No port forwarding, no exposed IPs.

---

## 8. Agent Configuration

An "agent" in this system is not a magic autonomous being. It is a prompt template plus a routing rule plus a set of tools it can access. Here is how to configure them.

### The Task Protocol (AI-TASK v1)

Every task in the system follows this JSON schema:

```json
{
 "task_id": "20260315-143022-a8f3c1",
 "parent_task": null,
 "objective": "What needs to be done, in one clear sentence",
 "context": "Background information the model needs",
 "model_preference": ["ollama", "gpt4o", "claude"],
 "spawn_allowed": true,
 "deliverables": ["analysis", "code", "summary"]
}
```

**task_id** is generated automatically (timestamp + random hex). **parent_task** links subtasks to their parent for tracking. **model_preference** tells the kernel which AI to try first. **spawn_allowed** controls whether the task can create child tasks autonomously.

### Configuring Model Routing

The kernel routes tasks based on two things: explicit preference and keyword matching.

```python
# Keywords that trigger free (Ollama) routing
CHEAP_KEYWORDS = [
 "summarize", "format", "extract", "classify", "clean",
 "list", "count", "evaluate", "score", "review output",
 "simple", "quick", "translate", "rewrite"
]

# Keywords that trigger heavy (paid API) routing
HEAVY_KEYWORDS = [
 "design", "architect", "debug", "implement", "code",
 "build", "analyze deeply", "research", "create module",
 "write function", "fix bug", "refactor", "plan"
]
```

You can customize these lists to match your use patterns. If you find that Ollama handles coding tasks well enough for your needs, move "code" to the cheap list. The goal is to use the cheapest model that produces acceptable output.

### Agent Personas

For different types of work, I configure different system prompts. These are not separate agents. They are prompt templates that the kernel selects based on the task type.

```python
PERSONAS = {
 "researcher": """You are a thorough researcher. Find specific,
 actionable information. Cite sources when possible. Focus on
 practical applications, not theory.""",

 "coder": """You are a senior developer. Write clean, working code.
 Include error handling. Keep functions small. Add comments only
 where the logic is not obvious.""",

 "analyst": """You are a data analyst. Extract patterns from data.
 Present findings in structured formats. Flag anomalies. Be specific
 about numbers.""",

 "writer": """You are a content writer. Match the specified tone.
 Keep sentences short. Use active voice. Every paragraph should
 advance the argument.""",
}
```

The kernel selects a persona based on keywords in the objective:

```python
def select_persona(objective):
 obj = objective.lower()
 if any(w in obj for w in ["research", "find", "discover", "investigate"]):
 return PERSONAS["researcher"]
 if any(w in obj for w in ["code", "implement", "build", "fix", "debug"]):
 return PERSONAS["coder"]
 if any(w in obj for w in ["analyze", "data", "metrics", "pattern"]):
 return PERSONAS["analyst"]
 if any(w in obj for w in ["write", "draft", "content", "copy"]):
 return PERSONAS["writer"]
 return "" # No persona, generic prompt
```

### The Skill Registry

Skills are reusable capabilities that the system tracks and improves over time. The registry is a simple JSON file:

```json
{
 "skills": [
 {
 "name": "product_research",
 "description": "Research eBay/Amazon products and generate listings",
 "version": 2,
 "score": 0.78
 },
 {
 "name": "content_writing",
 "description": "Generate social media posts and long-form content",
 "version": 1,
 "score": 0.85
 },
 {
 "name": "code_generation",
 "description": "Write Python scripts and shell automation",
 "version": 3,
 "score": 0.72
 }
 ]
}
```

The score field (0 to 1) tracks how well each skill performs. Low-scoring skills get prioritized for improvement. This is a manual process right now. I review outputs, adjust the score, and iterate on the prompt templates. The important thing is that the tracking exists. Without measurement, you cannot improve.

---

## 9. Task Delegation Framework

Knowing how to configure agents is one thing. Knowing what to delegate and how to structure the delegation is where most people fail. Here is my framework.

### The Delegation Decision Tree

Before creating a task, I ask three questions:

1. **Can Ollama handle this?** If yes, route it to the free lane. Most tasks are simpler than you think.
2. **Does it need external data?** If yes, it might need an API call or web access, which changes the routing.
3. **Does the output need to be perfect, or just good enough?** Perfect goes to Claude. Good enough goes to Ollama.

### Task Decomposition

The single most important skill for delegating to AI is breaking big tasks into small ones. An AI agent cannot "build me a website." But it can:

1. Generate a list of pages needed for the site
2. Write the HTML for the header component
3. Write the CSS for the color palette
4. Generate copy for the landing page
5. Create the contact form markup

Each of those is a single, clear task that a 7B model can handle.

### The Task Template

Every task I create follows this pattern:

```
OBJECTIVE: [One sentence. What needs to be done.]
CONTEXT: [What the model needs to know to do it well.]
FORMAT: [Exactly how the output should be structured.]
CONSTRAINTS: [What to avoid, length limits, style rules.]
```

Example:

```json
{
 "task_id": "listing-042",
 "objective": "Write an eBay product description for Nike Air Max 90",
 "context": "Product is used, size 10, white/black colorway, 8/10 condition. Selling for $85. Target audience is sneaker collectors.",
 "model_preference": ["ollama"],
 "deliverables": ["title", "description", "bullet_points"]
}
```

### Batch Processing

The real power of this system is batching. Instead of asking one question at a time, I create 10, 20, or 50 tasks and drop them all into the inbox. The kernel processes them sequentially (or in parallel if you run multiple kernel instances).

```bash
# Generate 20 product research tasks
for product in "Nike Air Max" "Vintage Levi's" "Pokemon Cards" "AirPods Pro"; do
 cat > ai_cluster/tasks/inbox/research-$(date +%s%N | md5 | head -c6).json << EOF
 {
 "objective": "Research $product on eBay. Find avg selling price, demand level, best listing keywords.",
 "model_preference": ["ollama"],
 "context": "Product research for dropshipping evaluation."
 }
EOF
done
```

Twenty tasks, submitted in seconds, processed without me touching anything.

### Subtask Spawning

The kernel supports autonomous subtask creation. When a task's response includes a `spawn_tasks` array, the kernel creates new tasks automatically:

```json
{
 "result": "Identified 5 high-demand product categories",
 "spawn_tasks": [
 {
 "objective": "Deep-dive research on vintage denim market",
 "model_preference": ["ollama"]
 },
 {
 "objective": "Analyze Pokemon card grading requirements",
 "model_preference": ["ollama"]
 }
 ]
}
```

The parent task finishes, and two child tasks appear in the inbox. This is how one task turns into a research tree without human intervention.

Set `spawn_allowed: true` on the parent task to enable this. I recommend being conservative with spawning at first. An AI that can create its own tasks can create a lot of them very quickly if you are not careful.

---

## 10. Building Your First Automation

Let's build something real. I will walk you through creating an automated content pipeline that takes a topic, researches it, writes a social media post, and saves the result. All running locally, all free.

### The Content Generation Pipeline

Here is what we are building:

```
Topic (input)
 -> Research task (Ollama)
 -> Writing task (Ollama)
 -> Formatting task (Ollama)
 -> Final output (saved to disk)
```

### Step 1: Create the Pipeline Script

```python
#!/usr/bin/env python3
"""
content_pipeline.py - Automated content generation
Takes a topic, researches it, writes a post, formats it.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
OUTPUT_DIR = Path.home() / "behique" / "output" / "content"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ask_ollama(prompt):
 """Send a prompt to Ollama and return the response."""
 payload = {
 "model": MODEL,
 "prompt": prompt,
 "stream": False,
 }
 r = requests.post(OLLAMA_URL, json=payload, timeout=120)
 return r.json().get("response", "")


def research(topic):
 """Step 1: Generate research notes on the topic."""
 prompt = f"""Research the following topic and provide 5 key facts
that would be interesting for a social media audience.

Topic: {topic}

Format your response as a numbered list. Focus on surprising,
counterintuitive, or practical information. No fluff."""

 print(f"[1/3] Researching: {topic}")
 return ask_ollama(prompt)


def write_post(topic, research_notes):
 """Step 2: Write a social media post using the research."""
 prompt = f"""Write an Instagram caption about this topic.

Topic: {topic}
Research notes:
{research_notes}

Rules:
- Start with a hook (question or bold statement)
- Keep it under 200 words
- Include 3-5 relevant hashtags at the end
- Conversational tone, not corporate
- End with a call to action"""

 print("[2/3] Writing post.")
 return ask_ollama(prompt)


def format_output(topic, research_notes, post):
 """Step 3: Package everything into a clean output."""
 timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
 slug = topic.lower().replace(" ", "-")[:30]

 output = {
 "topic": topic,
 "research": research_notes,
 "post": post,
 "generated_at": timestamp,
 "model": MODEL,
 "cost": "$0.00"
 }

 filename = f"{timestamp}-{slug}.json"
 output_path = OUTPUT_DIR / filename

 output_path.write_text(json.dumps(output, indent=2))
 print(f"[3/3] Saved to: {output_path}")

 return output_path


def run_pipeline(topic):
 """Run the full content pipeline."""
 start = time.time()

 notes = research(topic)
 post = write_post(topic, notes)
 path = format_output(topic, notes, post)

 elapsed = time.time() - start
 print(f"\nDone in {elapsed:.1f} seconds. Cost: $0.00")
 print(f"Output: {path}")

 return path


if __name__ == "__main__":
 import sys
 topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "local AI inference"
 run_pipeline(topic)
```

### Step 2: Run It

```bash
python3 content_pipeline.py "how to build an AI employee for free"
```

Output:

```
[1/3] Researching: how to build an AI employee for free
[2/3] Writing post.
[3/3] Saved to: /Users/you/behique/output/content/20260315-143022-how-to-build-an-ai-employee.json

Done in 24.3 seconds. Cost: $0.00
```

### Step 3: Batch It

```bash
# Run 5 topics in sequence
topics=(
 "why local AI beats cloud AI"
 "the $0 startup toolkit"
 "how I automated my side hustle"
 "building an AI agent with Python"
 "the future of personal AI assistants"
)

for topic in "${topics[@]}"; do
 python3 content_pipeline.py "$topic"
 echo ""
done
```

Five pieces of content, generated in about two minutes, completely free. Now imagine running this every morning as a cron job. By the time you wake up, five new posts are waiting for you to review and publish.

### Step 4: Add It to the Kernel

To make this a proper skill in the system, wrap it as a task handler:

```bash
# Submit as a kernel task
cat > ~/behique/ai_cluster/tasks/inbox/content-batch-001.json << 'EOF'
{
 "task_id": "content-batch-001",
 "objective": "Generate social media content about local AI inference benefits",
 "context": "Target audience: developers and tech entrepreneurs. Platform: Instagram. Tone: conversational, educational.",
 "model_preference": ["ollama"],
 "spawn_allowed": true
}
EOF
```

---

## 11. Monitoring and Maintenance

A distributed system needs monitoring. Not enterprise-grade Datadog monitoring. Simple, practical checks that tell you if something is broken.

### Health Check Script

```bash
#!/bin/bash
# health_check.sh - Check all nodes in the fleet

echo "=== Behique Fleet Health Check ==="
echo "Time: $(date)"
echo ""

# Check Ceiba (local)
echo "[Ceiba - HQ]"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
 echo " Ollama: UP"
else
 echo " Ollama: DOWN"
fi

# Check Cobo (worker)
echo "[Cobo - Worker]"
if curl -s --connect-timeout 3 http://192.168.0.151:11434/api/tags > /dev/null 2>&1; then
 echo " Ollama: UP"
else
 echo " Ollama: DOWN"
fi

if curl -s --connect-timeout 3 http://192.168.0.151:9876 > /dev/null 2>&1; then
 echo " Bridge: UP"
else
 echo " Bridge: DOWN"
fi

if curl -s --connect-timeout 3 http://192.168.0.151:5678 > /dev/null 2>&1; then
 echo " n8n: UP"
else
 echo " n8n: DOWN"
fi

# Check Hutia (always-on)
echo "[Hutia - Background]"
if ping -c 1 -W 2 192.168.0.152 > /dev/null 2>&1; then
 echo " Network: UP"
else
 echo " Network: DOWN"
fi

# Task queue status
echo ""
echo "[Task Queue]"
INBOX=$(ls ~/behique/ai_cluster/tasks/inbox/*.json 2>/dev/null | wc -l)
ACTIVE=$(ls ~/behique/ai_cluster/tasks/active/*.json 2>/dev/null | wc -l)
DONE=$(ls ~/behique/ai_cluster/tasks/done/*.json 2>/dev/null | wc -l)
echo " Inbox: $INBOX"
echo " Active: $ACTIVE"
echo " Done: $DONE"

# Disk space
echo ""
echo "[Disk Space]"
df -h / | tail -1 | awk '{print " Used: " $5 " of " $2}'
```

Run it manually or add it to a cron job:

```bash
# Check health every 30 minutes
crontab -e
# Add: */30 * * * * bash ~/behique/tools/health_check.sh >> ~/behique/logs/health.log 2>&1
```

### Log Rotation

The kernel and task queue generate files. Left unchecked, the `done` folder fills up. Clean old tasks periodically:

```bash
# Archive tasks older than 7 days
find ~/behique/ai_cluster/tasks/done -name "*.json" -mtime +7 \
 -exec mv {} ~/behique/ai_cluster/tasks/archive/ \;
```

### Syncthing Monitoring

Syncthing has a built-in web UI at `http://localhost:8384`. Check it periodically to make sure all machines are connected and in sync. The most common issue is a machine going offline and accumulating a sync backlog. When it comes back online, Syncthing handles the sync automatically, but large backlogs can take a few minutes.

### Process Management with pm2

On machines running services (bridge server, n8n, Ollama on Linux), use pm2 to keep them alive:

```bash
# Check all managed processes
pm2 status

# Restart a crashed service
pm2 restart bridge

# View logs
pm2 logs bridge --lines 50

# Auto-start on system boot
pm2 startup
pm2 save
```

### The Dashboard (Optional)

I built a simple HTML dashboard that shows the status of all machines. It is served by Python's built-in HTTP server:

```bash
cd ~/behique/Ceiba/faces && python3 -m http.server 8091 --bind 0.0.0.0
```

Accessible at `http://192.168.0.145:8091` from any device on the network. It shows agent status, task queue counts, and recent completions. This is optional but useful when you want to check the system from your phone.

---

## 12. Cost Breakdown

This is the section I am most proud of. Here are the real numbers.

### Monthly Operating Costs

| Service | Cost | Notes |
|---------|------|-------|
| Ollama inference | $0 | Runs on your hardware |
| Syncthing sync | $0 | Peer-to-peer, no cloud |
| n8n automation | $0 | Self-hosted |
| Agent Kernel | $0 | Python script |
| Bridge server | $0 | Node.js on your machine |
| Telegram Bot API | $0 | Free tier |
| Cloudflare Tunnel | $0 | Free tier |
| Electricity | ~$5-15 | Depends on your machines |
| **Total** | **~$5-15** | **Just electricity** |

### What I Pay For (Optional)

| Service | Cost | Why |
|---------|------|-----|
| Claude Code CLI | $20/month | Primary reasoning, worth every penny |
| Railway (BehiqueBot) | $0 (free tier) | Bot hosting, minimal usage |
| Notion | $0 (free tier) | Database for BehiqueBot |
| Domain name | ~$10/year | For Cloudflare tunnel |

The Claude Code subscription is the only real expense, and it is optional. You can build the entire system using only Ollama for inference. Claude Code is my force multiplier for complex tasks, but the system works without it.

### Comparison to Cloud Alternatives

If I ran this same workload on cloud services:

| Service | Estimated Monthly Cost |
|---------|----------------------|
| AWS EC2 (GPU instance) | $200-800 |
| OpenAI API (equivalent usage) | $50-200 |
| Zapier (workflow automation) | $20-50 |
| Cloud file storage | $5-10 |
| Managed bot hosting | $10-25 |
| **Total** | **$285-1,085/month** |

My system does the same work for $5-15/month in electricity. Over a year, that is a savings of $3,000 to $12,000. The hardware pays for itself in the first month.

### The Real Cost: Your Time

I will be honest. The actual cost of this system is the time it takes to build and maintain it. I spent weeks getting everything working. That is time I could have spent on other things.

But here is the difference. I spent that time once. The system runs every day. Cloud services cost money every month forever. My system costs time upfront and then runs for free.

If you follow this guide, you can cut that setup time down to a weekend for the basics. A week if you want the full fleet.

---

## 13. Troubleshooting

Here are the problems I ran into and how I fixed them.

### Ollama Won't Start

**Symptom:** `ollama serve` hangs or crashes.

**Fix:** Check if another instance is already running.

```bash
# Kill existing instances
pkill ollama

# Check if the port is in use
lsof -i :11434

# Start fresh
ollama serve
```

On macOS, the Ollama app runs a background service. If you are also trying to run `ollama serve` manually, they will conflict. Use one or the other.

### Model Too Large for RAM

**Symptom:** Ollama says "out of memory" or the system becomes unresponsive.

**Fix:** Use a smaller model or quantization.

```bash
# Instead of the full model, try a quantized version
ollama pull qwen2.5:7b-q4_0

# Or use a smaller model entirely
ollama pull phi-3:mini
```

7B models need roughly 4-8GB of RAM depending on quantization. If you only have 8GB total, close other applications while running inference.

### Syncthing Not Syncing

**Symptom:** Files on one machine do not appear on the other.

**Fixes:**

1. Check both machines are online in the Syncthing UI (`http://localhost:8384`)
2. Verify the shared folder path is correct on both machines
3. Check `.stignore` is not excluding the files you expect to sync
4. Restart Syncthing on both machines

```bash
# Restart on macOS
brew services restart syncthing

# Restart on Linux
systemctl restart syncthing@$USER
```

### Bridge Server Connection Refused

**Symptom:** `curl: (7) Failed to connect to 192.168.0.151 port 9876`

**Fixes:**

1. Verify the bridge server is running: `pm2 status`
2. Check the firewall on the worker machine:

```bash
# Windows (PowerShell, run as admin)
New-NetFirewallRule -DisplayName "Bridge" -Direction Inbound -Port 9876 -Protocol TCP -Action Allow

# Linux
sudo ufw allow 9876/tcp
```

3. Verify the IP address has not changed (DHCP can reassign IPs)

### Task Stuck in Active

**Symptom:** A task file sits in `tasks/active/` forever.

**Fix:** The kernel crashed while processing. Move it back to inbox:

```bash
mv ~/behique/ai_cluster/tasks/active/stuck-task.json \
 ~/behique/ai_cluster/tasks/inbox/stuck-task.json
```

Then restart the kernel. Consider adding a timeout to your kernel's task processing.

### Ollama Slow on CPU

**Symptom:** Inference takes 30+ seconds for short prompts.

**Fixes:**

1. Use a smaller model: `qwen2.5:3b` instead of `7b`
2. Reduce the prompt length (less context = faster)
3. Set a token limit in your Ollama call:

```python
payload = {
 "model": "qwen2.5:7b",
 "prompt": prompt,
 "stream": False,
 "options": {
 "num_predict": 256 # Limit output tokens
 }
}
```

4. Consider getting a GPU. Even a used GTX 1060 6GB on eBay for $100 makes a massive difference.

### Memory Running Low on macOS

**Symptom:** System becomes sluggish, apps start crashing.

**Fixes:**

1. Check what Ollama is using: `ps aux | grep ollama`
2. Unload the model when not in use:

```bash
# Ollama unloads models after 5 minutes of inactivity by default
# To force unload:
curl -X POST http://localhost:11434/api/generate \
 -d '{"model": "qwen2.5:7b", "keep_alive": 0}'
```

3. Close unnecessary applications
4. Set `OLLAMA_MAX_LOADED_MODELS=1` to prevent multiple models from staying in memory

### n8n Workflow Failures

**Symptom:** Workflows stop executing or throw errors.

**Fixes:**

1. Check n8n logs: `pm2 logs n8n`
2. Verify webhook URLs are correct and accessible
3. Check that external services (APIs, databases) are reachable from the worker machine
4. Restart n8n: `pm2 restart n8n`

### Git Conflicts from Syncthing

**Symptom:** Syncthing creates `.sync-conflict` files.

This happens when two machines edit the same file at the same time. Syncthing cannot merge, so it keeps both versions.

**Fix:**

```bash
# Find conflict files
find ~/behique -name "*.sync-conflict*"

# Manually resolve (keep the version you want)
# Then delete the conflict file
```

**Prevention:** Designate one machine as the "writer" for each file. Ceiba writes `primer.md`. Cobo writes its own logs. They do not write to the same files.

---

## 14. What's Next: Scaling Beyond 3 Machines

The architecture I have shown you scales. Here is where it goes from here.

### Adding Machine 4, 5, 6.

Every new machine follows the same pattern:

1. Install Ollama
2. Install Syncthing, join the cluster
3. Optionally install the bridge server
4. Update the health check script

The kernel does not care how many machines exist. It routes to Ollama endpoints. Add a new endpoint, add a new machine.

```python
# Multi-node Ollama routing
OLLAMA_NODES = [
 "http://192.168.0.145:11434", # Ceiba
 "http://192.168.0.151:11434", # Cobo
 "http://192.168.0.152:11434", # Hutia
 "http://192.168.0.153:11434", # Future node
]

def get_available_node():
 """Find the first responsive Ollama node."""
 for url in OLLAMA_NODES:
 try:
 r = requests.get(f"{url}/api/tags", timeout=2)
 if r.status_code == 200:
 return url
 except Exception:
 continue
 return None
```

### Specialized Nodes

As you add machines, specialize them:

- **Inference node:** Beefy GPU, runs large models
- **Workflow node:** Runs n8n, handles integrations
- **Storage node:** Large hard drive, serves files
- **Always-on node:** Low power, runs cron jobs and monitoring

### Better Task Routing

The current keyword-based routing is simple. Next-level routing uses embeddings:

```python
# Future: Semantic task routing
# Embed the task objective, compare to skill embeddings,
# route to the best-matching skill automatically.
```

This is on my roadmap. The kernel already has the memory search infrastructure. Adding embedding-based routing is a natural next step.

### Voice-First Interface

My long-term vision is fully voice-controlled. Walk into the room, say "Behique, research trending products in the vintage clothing category and generate five listing drafts." The system captures the voice, transcribes it, decomposes it into tasks, routes them across the fleet, and sends me the results on Telegram when they are done.

BehiqueBot already handles voice messages. The missing piece is the automatic task decomposition from natural language. That is a solvable problem with the right prompt engineering.

### Selling the System

If you build this for yourself and it works, you can sell it. Not the code. The installation. There are businesses that would pay $2,000-5,000 for someone to set up an autonomous AI system that runs on their existing hardware with zero monthly cost. I know because I am building that service right now.

The value proposition is simple: "You have computers sitting idle. I will turn them into an AI workforce that operates 24/7 for the cost of electricity."

### The Bigger Picture

What we are building is not just a set of scripts. It is a personal AI infrastructure. The kind of system that major tech companies have internal versions of, built on consumer hardware by one person.

Every task the system processes makes the memory smarter. Every automation you build compounds on the ones before it. Every machine you add multiplies your capacity.

Most people will read about AI agents and think "that sounds cool, maybe someday." You are now one of the people who can actually build one. The tools exist. The hardware is cheap. The architecture is proven.

The only question is: what are you going to have your AI employee do first?

---

## Appendix A: Complete File Structure

```
~/behique/
 ai_cluster/
 kernel/
 agent_kernel.py # The orchestrator
 tasks/
 inbox/ # New tasks
 active/ # Currently processing
 done/ # Completed results
 archive/ # Old results
 memory/
 knowledge/ # Accumulated facts
 experiments/ # What worked/failed
 projects/ # Project context
 skills/ # Skill documentation
 skills/
 registry.json # All registered skills
 bridge/
 dispatch.sh # Quick task dispatch
 bridge-server.js # HTTP command server
 wake.sh # Wake worker node
 sleep.sh # Sleep worker node
 tools/
 health_check.sh # Fleet health monitoring
 content_pipeline.py # Content generation
 reel-pipeline/
 make_reel.py # Video production
 stories/ # Story JSON files
 output/ # Generated videos
 ebay-listing-assistant/
 core/
 pipeline.py # Listing generation
 Ceiba/
 VAULT_INDEX.md # Knowledge graph index
 projects/ # Project documentation
 faces/ # Web dashboards
 primer.md # Live system state
 .stignore # Syncthing exclusions
```

## Appendix B: Quick Reference Card

### Start the System

```bash
# Start Ollama (macOS - just open the app)
# Start Ollama (Linux)
ollama serve &

# Start the agent kernel
python3 ~/behique/ai_cluster/kernel/agent_kernel.py &

# Start the bridge server (on worker)
pm2 start bridge-server.js --name bridge

# Start n8n (on worker)
pm2 start n8n

# Start the dashboard
cd ~/behique/Ceiba/faces && python3 -m http.server 8091 --bind 0.0.0.0 &
```

### Submit Tasks

```bash
# Quick dispatch
bash ~/behique/bridge/dispatch.sh fast "Your prompt here"

# Kernel task
cat > ~/behique/ai_cluster/tasks/inbox/task-$(date +%s).json << 'EOF'
{
 "objective": "Your task description",
 "model_preference": ["ollama"]
}
EOF
```

### Check Status

```bash
# Fleet health
bash ~/behique/tools/health_check.sh

# Task queue
python3 ~/behique/ai_cluster/kernel/agent_kernel.py status

# Syncthing
open http://localhost:8384

# n8n
open http://192.168.0.151:5678
```

### Common Ollama Commands

```bash
ollama list # Show installed models
ollama pull qwen2.5:7b # Download a model
ollama rm model-name # Remove a model
ollama ps # Show running models
ollama show qwen2.5:7b # Show model details
```

---

## Appendix C: Security Checklist

Before you expose anything to the internet, go through this list:

- [ ] Bridge server uses a strong, random bearer token (32+ characters)
- [ ] Syncthing is configured with device authentication (not open to all)
- [ ] Cloudflare tunnel is the only external access point (no port forwarding)
- [ ] n8n has authentication enabled (Settings > Security)
- [ ] No API keys or tokens are hardcoded in scripts (use environment variables)
- [ ] Worker machines are on a trusted local network
- [ ] Firewall rules only open necessary ports (11434, 9876, 5678, 8384)
- [ ] Regular OS updates on all machines
- [ ] SSH key authentication instead of passwords (if using SSH)

---

## Final Words

I wrote this guide because I could not find it when I needed it. Everything I learned came from stitching together documentation from 15 different tools, failing, debugging at 2 AM, and slowly building something that works.

The system is not perfect. The keyword-based routing is primitive. The memory search is basic. The monitoring is minimal. But it works. It processes tasks while I sleep. It generates content while I am in class. It costs me nothing to run.

You do not need permission from a company to build AI infrastructure. You do not need a server budget. You do not need a computer science degree (though I am working on one). You need a computer, an internet connection, and the willingness to build something that does not exist yet.

If you build your own version of this system, I would love to hear about it. Reach out on Telegram or Instagram. Show me what you built. Tell me what you improved. The whole point of putting this out into the world is that someone will take it further than I did.

Now go build your AI employee.

-- Kalani Andre Gomez Padin
Puerto Rico, 2026
