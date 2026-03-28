---
title: "Case Study: The Behique AI System"
type: case-study
tags: [case-study, service, ai-agents, portfolio]
created: 2026-03-22
---

# Case Study: How a College Student Built an AI Workforce on Three Computers

## Client Profile
- **Who:** Solo entrepreneur and computer engineering student in Puerto Rico
- **Problem:** Too many projects, not enough hands. Needed automation that runs 24/7 without cloud bills.
- **Budget:** $0/month operational cost. Used existing hardware only.

## The Challenge

Running multiple businesses as a solo operator means constant context switching. Product research, content creation, customer communication, bookkeeping, data processing. Every task competes for the same limited hours.

Hiring wasn't an option. Cloud AI services charge per API call, and at scale those bills add up fast. The challenge was clear: build an autonomous AI system using hardware already on hand, with zero recurring costs.

## The Solution

We designed and deployed a **three-machine AI agent network** that handles tasks autonomously.

### Architecture

```
+------------------+     HTTP Bridge      +------------------+
|   CEIBA (HQ)     |<------------------->|   COBO (GPU)     |
|   Mac M4, 16GB   |   Bearer Auth        |   GTX 1080 Ti    |
|   Orchestration   |   Task Routing       |   Local LLMs     |
|   Claude Code CLI |                      |   n8n Workflows   |
+------------------+                      +------------------+
         |                                         |
         |          Syncthing File Sync             |
         |<--------------------------------------->|
         |
         v
+------------------+
|   HUTIA (Node 3) |
|   Always-On      |
|   Background Ops |
+------------------+
```

### Machine Roles

**Ceiba (Mac M4, 16GB RAM, Metal 3 GPU)**
- Central orchestration and task management
- Runs the CLI spawner that creates and assigns tasks
- Handles text generation, code writing, document creation
- Apple Silicon optimized for local ML inference (MLX framework)

**Cobo (Windows, GTX 1080 Ti 11GB VRAM, EVGA FTW Edition)**
- GPU-heavy workloads: image generation, local LLM inference
- Runs Ollama with multiple models (llama3.2, qwen2.5:7b)
- Hosts n8n for workflow automation (self-hosted, unlimited)
- Bridge server for cross-machine task delegation

**Hutia (Dedicated Node)**
- Always-on background operations
- Handles scheduled tasks, monitoring, file processing
- Reduces load on primary machines during active work

### Software Stack (All Free/Open-Source)

| Tool | Purpose | Cost |
|------|---------|------|
| Claude Code CLI | Primary AI agent orchestration | $0 (Claude Max subscription) |
| Ollama | Local LLM inference | $0 |
| n8n | Workflow automation | $0 (self-hosted) |
| Syncthing | Cross-machine file sync | $0 |
| Git + Worktrees | Task isolation per agent | $0 |
| Python scripts | Custom automation glue | $0 |
| FFmpeg | Media processing pipeline | $0 |
| Kokoro TTS | Local text-to-speech | $0 |

### Agent Capabilities Deployed

1. **Content Generation Agent** - Writes Instagram posts, product descriptions, email copy
2. **Research Agent** - Scrapes product data, analyzes trends, scores opportunities
3. **Document Processing Agent** - Converts formats, builds PDFs, creates spreadsheets
4. **Communication Agent** - Telegram bot that classifies and routes messages
5. **Media Production Agent** - Generates narration, assembles video reels from scripts
6. **Monitoring Agent** - Tracks system health, disk space, task completion

## Results

### Quantified Output (First 2 Weeks)

| Metric | Before | After |
|--------|--------|-------|
| Products created per week | 0 | 5 digital products ready to sell |
| Content pieces per session | 2-3 manually | 35 reel briefs + 10 Instagram posts in one session |
| Research time per product | 3-4 hours | 15 minutes (automated pipeline) |
| Cross-machine task delegation | Manual copy-paste | Automatic via bridge server |
| Monthly operational cost | $0 | $0 |

### Specific Deliverables Produced by AI Agents

- **35 production-ready reel briefs** with hooks, scripts, and image prompts
- **10 Instagram posts** with captions, hashtags, and posting strategy
- **2 Excel products** (budget template + cash flow dashboard) with formulas and formatting
- **1 full ebook** (242 lessons, 1,041 pages) converted and formatted for sale
- **1 video production pipeline** that creates reels from story scripts automatically
- **1 Telegram bot** handling message classification and idea capture
- **Complete product listing copy** for 4 Gumroad products

### Time Savings

A conservative estimate: tasks that would have taken 80-100 hours of manual work were completed in approximately 6 hours of active supervision. The agents handled the bulk of the execution while the operator focused on strategy and review.

## Key Design Decisions

1. **Local-first architecture.** No cloud dependency means no surprise bills and no downtime from API rate limits.

2. **Specialize each machine.** Instead of overloading one computer, we split workloads by hardware strength. GPU work goes to the GPU machine. Orchestration stays on the fast SSD machine.

3. **Git worktree isolation.** Each agent task runs in its own worktree. No agent can corrupt another's work. Clean rollback if something breaks.

4. **Placeholder fallbacks.** When image generation isn't available, the pipeline uses placeholder images and continues. Nothing blocks on a single component.

5. **File sync over network calls.** Syncthing keeps files synchronized across machines automatically. No custom sync code to maintain.

## What This Means for Your Business

If a college student with consumer hardware can build an AI workforce that produces this output, imagine what the same architecture could do for your business with tasks like:

- **Customer support** - AI handles FAQs, routes complex issues to you
- **Content creation** - Drafts, schedules, and repurposes content across platforms
- **Data processing** - Invoices, reports, inventory updates run automatically
- **Lead follow-up** - Personalized responses drafted and queued for review
- **Product research** - Market trends analyzed and scored without manual searching

The system scales. Add another machine, add another agent. The architecture handles it.

## Want This for Your Business?

We offer the same architecture as a service:

- **Free AI Audit** - 30-minute assessment of what you could automate
- **Starter Agent ($500)** - One agent for one specific task
- **Agent Team ($2,000)** - 3-5 agents working together
- **Full Autonomy ($5,000+)** - Complete autonomous pipeline like ours

Contact: [link to be added when Instagram/landing page is live]
