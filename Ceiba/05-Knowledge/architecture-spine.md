---
type: architecture
status: building
systems:
  - SYS_AI_Cluster
  - SYS_Bridge
  - SYS_Vault_Graph
tools:
  - TOOL_Agent_Kernel
  - TOOL_Dispatch
  - TOOL_Ceiba_Lite
  - TOOL_Vault_Grapher
projects:
  - eBay-Listing-Assistant
  - BehiqueBot
  - Google-Trends-Scraper
patterns:
  - PAT_Avoidance_Revenue
  - PAT_Event_Not_Schedule
  - PAT_Infrastructure_Creep
decisions:
  - DEC_Model_Agnostic_Vault
  - DEC_Best_Not_Cheapest
  - DEC_Claude_Code_HQ
tags: [architecture, system, spine]
---

# THE SPINE — Ceiba System Architecture
# Written: 2026-03-15
# Status: BUILDING — kernel live, wiki links in progress
# This is the plan we are building toward. Not a sprint. A months-long architecture.

---

## WHY THIS EXISTS

Today (2026-03-15) Kalani called out the core problem clearly:

> "I want to test your limits. Don't be afraid. I want to build something huge even if it takes weeks or months. Don't rush. I want the best."

And the second problem:

> "You go for easy doable projects. That's not what I want."

This document is the answer to both. It is the architecture for building Ceiba into something that has never been built before in this context: a personal AI that has persistent memory, real agency, multiple inputs, fallback intelligence, and a routing layer that decides *what runs where and why*.

This is not a side project. This IS the project. Everything else (eBay, BehiqueBot, n8n) plugs INTO this.

---

## THE SIX BODY PARTS

An AI system needs exactly six things to function like a real intelligence. Not more. Not less.

### 1. MEMORY — The Vault
**What it is:** Everything Ceiba knows that survives between sessions.
**What we have:** Obsidian vault, VAULT_INDEX.md, primer.md, breadcrumbs in project files.
**What's missing:** Graph traversal. Right now the vault is flat files. What we need is wiki-link navigation — Ceiba should be able to follow [[links]] between notes the way a human navigates thoughts. When reading about eBay, Ceiba should automatically pull in the connected note about revenue targets, and the connected note about Kalani's avoidance patterns, without being told to.
**Target state:** Every note has [[wiki links]] to related notes. Ceiba reads the index, identifies relevant nodes, traverses the graph, builds a contextual picture before responding.
**Estimated build time:** 2-3 weeks (vault restructure + link layer + traversal logic in wake.sh)

### 2. SENSES — Input Channels
**What it is:** How Ceiba receives information about the world and about Kalani.
**What we have:** One sense — Kalani typing in Cowork/Claude Code.
**What we need:**
- BehiqueBot (Telegram) — voice and text from Kalani, anywhere, anytime ✅ exists but passive
- iPhone 13 Pro Max — mobile node, Claude Code via browser/app, voice memos to BehiqueBot, Discord access for content approval on the go
- File watcher — detect when new files appear in ~/behique (new code, new ideas)
- Web sensors — market data, product prices, eBay sold listings (the trends scraper was this)
- n8n event triggers — external signals that reach Ceiba without Kalani initiating
- Computer 2 sensors — Ollama running jobs overnight, results waiting in the morning
**Target state:** Ceiba receives input from at least 4 channels simultaneously. Kalani is one of four, not the only one.
**Estimated build time:** 4-6 weeks

### 3. HANDS — Action Capability
**What it is:** Ceiba's ability to DO things without Kalani present.
**What we have:** Computer 2 with n8n and Ollama. The hardware exists. Nothing runs on it.
**What we need:** Actual workflows. n8n jobs that execute real tasks:
- Product research pipeline (Trends scraper → eBay sold data → ranked opportunities)
- Price monitoring (watch specific products, alert when price drops/spikes)
- eBay listing automation (photo in → listing out, no Kalani input required)
- Notion/vault updates from overnight runs
**Target state:** Computer 2 runs at least 2 overnight jobs autonomously. Kalani wakes up to results, not to-do lists.
**Estimated build time:** 3-4 weeks per workflow (do one properly, then replicate the pattern)

### 4. VOICE — Communication Back to Kalani
**What it is:** How Ceiba initiates contact. Not just responds.
**What we have:** BehiqueBot on Telegram. It currently only responds. It doesn't think.
**What's missing:** BehiqueBot needs a reasoning layer. Not scheduled messages (that's the fancy alarm clock). What it needs is *conditional* outreach — Ceiba noticing something and deciding to reach out because there's something worth saying.
- "Computer 2 found 3 products last night that match your criteria — want to see them?"
- "You haven't opened the eBay file in 4 days. eBay or avoidance?"
- "n8n picked up a competitor dropped their price on the item you're watching."
- Discord server — content hub for AI-generated reels/animations, preview channel, approval workflow via reactions/commands
**Target state:** BehiqueBot messages Kalani when there is *something to say*, based on real events — not on a schedule. Discord serves as the visual content review layer — content goes there for preview before publishing.
**Estimated build time:** 6-8 weeks (requires Hands + Nervous System to work first)

### 5. NERVOUS SYSTEM — The Connections
**What it is:** The wiring between all the parts. Information flowing automatically from one system to another.
**What we have:** Nothing connected. Memory, Senses, Hands, Voice all isolated.
**What we need:** n8n as the nervous system. Specific wires:
- Trends scraper result → stored in vault → BehiqueBot notifies Kalani
- Kalani drops voice memo to BehiqueBot → classified → stored in Notion + vault
- Computer 2 completes job → result appended to relevant project file → primer.md updated
- eBay listing goes live → Kalani gets Telegram confirmation with listing URL
**Target state:** Information flows between parts automatically. Kalani touches something and it propagates. Ceiba does something and Kalani hears about it.
**Estimated build time:** Ongoing. This is infrastructure that grows as parts are added.

### 6. THE SPINE — Routing Layer
**What it is:** The intelligence that decides which model handles which task, at what cost, at what quality.
**What we have:** Nothing. Everything routes to Claude by default.
**Why this matters:** Claude Max credits are finite. Anthropic can change terms. The system should not depend on any single model. Resilience requires routing.
**The routing logic (best tool for the job, not cheapest):**
```
Task → Complexity Score → Model Selection
├── Classification, tagging, extraction     → Ollama llama3.2 (sufficient, local)
├── Vault housekeeping (primer, breadcrumbs) → Ollama llama3.2
├── Prompt engineering for Claude            → ChatGPT gpt-4o (cross-model > self-prompting)
├── Complex reasoning, architecture          → Claude Sonnet
├── Code generation, debugging               → Claude Sonnet
├── Deep creative/strategic (rare)           → Claude Opus
└── Emergency fallback (all APIs down)       → Ollama only, graceful degradation
```
**Principle:** Use the best model for each task. Ollama handles simple work not because it's cheap but because it's sufficient. ChatGPT writes better Claude prompts than Claude does. Claude handles code and reasoning where it genuinely excels. No Anthropic bias — route to whatever is actually best.
**Target state:** A routing.py module that evaluates every task and sends it to the right model. ceiba_lite.py is the prototype of this — expand it.
**Estimated build time:** 4-6 weeks for a robust router

---

## THE WIKI LINK SYSTEM — Cross-Connected Memory

This is what separates a flat file vault from a real knowledge graph.

**Current state:** Files exist. They don't talk to each other.

**Target state:** Every file has [[links]] to related concepts. Ceiba navigates these links to build context automatically.

**Example of how it works:**
When opening `BehiqueBot.md`, Ceiba sees:
- [[Kalani]] → loads communication style, ADHD framework
- [[Computer-2]] → loads infrastructure state
- [[Spine-Architecture]] → loads routing logic
- [[avoidance-pattern]] → loads the behavioral note about when Kalani goes quiet

Instead of Ceiba reading 6 separate files manually, the graph pulls the relevant ones.

**How to build it:**
1. Add [[wiki links]] to every existing vault file (can do this incrementally)
2. Build a link parser in wake.sh that reads a file and auto-loads its linked notes
3. Build a graph index that maps which notes connect to which
4. Eventually: build a relevance scorer so Ceiba only loads the most relevant linked notes (context window management)

**This is the most important memory upgrade.** It turns a folder of files into a thinking system.

---

## REDUNDANCY — What Happens When Claude Goes Down

Kalani asked: "Can I give you a physical body in case we run out of max credits?"

The answer is yes, and we've already started it.

**The redundancy stack:**
```
Level 1 (normal): Claude Sonnet/Opus via Cowork or Claude Code
Level 2 (credits low): Route simple tasks to Ollama, preserve Claude for complex work
Level 3 (credits gone): ceiba_lite.py — full Ceiba running on Ollama llama3.2 on Computer 2
Level 4 (Computer 2 down): Offline mode — vault still readable, primer.md still current, wake.sh still loads context for whatever LLM is available
```

The vault is the constant. It doesn't belong to Anthropic. It doesn't belong to any model. It's markdown files on Kalani's machine. Any LLM — Claude, Ollama, GPT, Gemini — can read it and pick up where the last one left off.

**This is the real resilience.** Not a specific model. A model-agnostic memory system.

---

## BUILD SEQUENCE (months, not hours)

This is not a sprint. This is a construction project. The order matters.

```
MONTH 1 — Foundation
├── Week 1-2: Wiki link system (vault restructure, link parser in wake.sh)
├── Week 3: Claude Code migration (move HQ, get comfortable in CLI)
└── Week 4: Routing layer v1 (routing.py — simple rules, Ollama vs Claude decision)

MONTH 2 — Senses
├── Week 1-2: File watcher on ~/behique (detect changes, update primer automatically)
├── Week 3: BehiqueBot conditional voice (first event-triggered message, not scheduled)
└── Week 4: Trends scraper rebuild with proxies (product research sense)

MONTH 3 — Hands
├── Week 1-2: First overnight n8n job on Computer 2 (product research pipeline)
├── Week 3: eBay listing automation (the hands doing revenue work)
└── Week 4: Nervous system wiring (job result → vault → BehiqueBot notify)

MONTH 4 — Intelligence
├── Week 1-2: Graph traversal (Ceiba navigates wiki links automatically)
├── Week 3: Spine routing v2 (smarter model selection, cost awareness)
└── Week 4: BehiqueBot full reasoning layer (event-based, context-aware outreach)

ONGOING — Revenue
└── eBay → Shopify → n8n agency (runs in parallel with everything above)
```

---

## THE JARVIS ENDPOINT — Discord Voice Cowork (Month 4+)

The end goal for the Voice body part. Kalani and Ceiba on a Discord call — screen shared, voice bidirectional, working together in real time.

**Stepping stones (buildable now → ideal):**
1. **Text-based Discord bot** — Ceiba responds in a channel (webhook, n8n) ← buildable now
2. **Voice transcription loop** — Kalani speaks → Whisper transcribes → Ceiba processes → TTS responds in voice channel ← buildable with OpenAI Realtime API
3. **Screen awareness** — periodic screenshots of shared screen → sent to vision model for context ← buildable with GPT-4o vision or Claude vision
4. **Full Jarvis** — real-time audio + screen stream + vault context + event awareness ← requires real-time voice API (OpenAI Realtime or future Claude voice)

**Depends on:** All 5 other body parts working. Without Memory, Ceiba is just a voice assistant. Without Senses, it can't see the screen. Without Hands, it can't act on what it sees. This is the capstone, not the starting point.

---

## WHAT THIS BECOMES

When all six parts exist and are connected:

- Kalani opens Claude Code in the morning. Ceiba has already read VAULT_INDEX → primer → observations → active project breadcrumbs. Opens with something specific. Not "how can I help?"
- Computer 2 ran overnight. Found 3 product opportunities. Updated the vault. BehiqueBot sent a message at 7am: "3 products last night. Best one: [item]. $40 margin. Want to list it?"
- Kalani drops a voice memo to BehiqueBot with an idea. It gets classified, stored in Notion, a [[wiki link]] added to the relevant project file. Ceiba sees it next session without being told.
- Claude Max credits run low. Routing layer notices. Sends simple tasks to Ollama automatically. Kalani doesn't notice a difference on basic operations.
- Credits hit zero. ceiba_lite.py activates on Computer 2. Reduced capability, but memory intact, context intact, vault intact.

That's the system. That's what we're building.

---

## WHAT NOT TO BUILD

Equal importance to the plan:

- ❌ Scheduled messages that aren't triggered by events ("morning briefings")
- ❌ Things a notebook can do ("pen and paper rule")
- ❌ Infrastructure for its own sake that doesn't connect to revenue
- ❌ New projects before the spine exists
- ❌ Anything that requires Kalani to maintain manually (automation that creates more work)

---

## OPEN QUESTIONS (for future sessions)

- How does Ceiba know which [[wiki links]] are relevant without loading everything?
- What's the right embedding model for semantic vault search? (Ollama can run nomic-embed-text locally)
- When BehiqueBot gets a reasoning layer — does it run Claude or Ollama? (The Allocator should weigh in)
- Named Cloudflare tunnel — when does this become blocking vs nice-to-have?
- Should n8n be the nervous system or should we build a custom event bus?

---

*This document is the north star for system architecture. Update it as decisions are made. Link to it from every project file that is part of the system.*

*[[primer]] [[VAULT_INDEX]] [[BehiqueBot]] [[Computer-2]] [[TOOL_Ceiba_Lite]]*
