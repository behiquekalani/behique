---
type: system
tags: [system, index, graph]
---

# VAULT INDEX — Knowledge Graph Entry Point
# Auto-maintained by Ceiba. Read this to orient before any session.
# Last updated: 2026-03-15

---

## SESSION START PROTOCOL
1. Read this file (you are here)
2. Read [[primer]] — live state, blockers, next action
3. Read [[observations]] — what Ceiba knows about Kalani's patterns
4. Read [[architecture-spine]] — system architecture and build sequence
5. Open the active project file → check breadcrumbs
6. Run `python3 ~/behique/tools/vault_grapher.py --stats` for graph health

---

## PROJECTS (type: project)

| Project | Status | Links |
|---------|--------|-------|
| [[eBay-Listing-Assistant]] | Building | → [[TOOL_Listing_Pipeline]], [[TOOL_Trends_Scraper]], [[Q3-2026]] |
| [[BehiqueBot]] | Live | → [[TOOL_BehiqueBot_Core]], [[Psychologist-Framework]], [[SYS_Bridge]] |
| [[Google-Trends-Scraper]] | Rebuilding | → [[TOOL_Trends_Scraper]], [[SYS_AI_Cluster]] |
| [[n8n-Agency]] | Not started | → [[TOOL_n8n]], [[SYS_Bridge]] |
| [[Shopify-Store]] | Waiting | → [[eBay-Listing-Assistant]], [[DEC_Ebay_Before_Shopify]] |
| [[News-Intelligence-Bots]] | Idea | — |
| [[MISSIONS]] | Quest map | → all projects |

---

## SYSTEMS (type: system/architecture)

| System | Status | What It Does |
|--------|--------|-------------|
| [[SYS_AI_Cluster]] | Live | Task queue + routing + memory at `~/behique/ai_cluster/` |
| [[SYS_Bridge]] | Live | HTTP bridge to Cobo at `192.168.0.151:9876` |
| [[SYS_Vault_Graph]] | Building | Wiki-linked knowledge graph (this vault) |
| [[architecture-spine]] | Blueprint | 6-part AI body + 4-month build plan |

---

## TOOLS (type: tool)

| Tool | Location | Used By |
|------|----------|---------|
| [[TOOL_Agent_Kernel]] | `ai_cluster/kernel/agent_kernel.py` | [[SYS_AI_Cluster]] |
| [[TOOL_Dispatch]] | `bridge/dispatch.sh` | [[SYS_Bridge]] |
| [[TOOL_Trends_Scraper]] | `tools/trends_scraper.py` | [[Google-Trends-Scraper]] |
| [[TOOL_Listing_Pipeline]] | `tools/ebay-listing-assistant/core/pipeline.py` | [[eBay-Listing-Assistant]] |
| [[TOOL_Vault_Grapher]] | `tools/vault_grapher.py` | [[SYS_Vault_Graph]] |
| [[TOOL_Ceiba_Lite]] | `ceiba_lite.py` | Emergency fallback |
| [[TOOL_BehiqueBot_Core]] | `main.py` + `modules/` | [[BehiqueBot]] |
| [[TOOL_Notify_Relay]] | `tools/notify.py` | [[BehiqueBot]] |
| [[TOOL_n8n]] | `http://192.168.0.151:5678` | [[n8n-Agency]] |

---

## PATTERNS (type: pattern)

| Pattern | Observed In |
|---------|-------------|
| [[PAT_Avoidance_Revenue]] | eBay dev account 3+ days, n8n zero clients |
| [[PAT_Infrastructure_Creep]] | Every session builds infra instead of revenue work |
| [[PAT_Event_Not_Schedule]] | "Fancy alarm clock" — events not cron |
| [[observations]] | Full behavioral patterns + session history |

---

## DECISIONS (type: decision)

| Decision | Why |
|----------|-----|
| [[DEC_Ebay_Before_Shopify]] | eBay has traffic, Shopify needs marketing |
| [[DEC_Ollama_First]] | Free inference, OpenAI as fallback only |
| [[DEC_Model_Agnostic_Vault]] | Vault doesn't belong to Anthropic |
| [[DEC_Best_Not_Cheapest]] | "I want the best, not the fastest" |
| [[DEC_Claude_Code_HQ]] | Moved HQ from Cowork to Claude Code CLI |

---

## IDENTITY

| File | What |
|------|------|
| [[Kalani]] | INFJ, ADHD, faith+family, builder mentality |
| [[Psychologist-Framework]] | Accountability framework behind BehiqueBot |
| [[North-Star]] | The WHY — family, freedom, builder identity |
| [[Q3-2026]] | $100K by Sept 30, 2026 |

---

## INFRASTRUCTURE STATE

| Service | Status | Access |
|---------|--------|--------|
| AI Cluster Kernel | ✅ Live | `python3 ai_cluster/kernel/agent_kernel.py` |
| Bridge Server (Cobo) | ✅ Live | `192.168.0.151:9876` (bearer auth) |
| Ollama (llama3.2) | ✅ Running | `192.168.0.151:11434` |
| OpenClaw + GPT-4o | ✅ Running | @CeibaOC2Bot on Telegram |
| Syncthing | ✅ Syncing | `~/behique` both machines |
| BehiqueBot | ✅ Live | Railway + Telegram |
| n8n | ✅ Running | `192.168.0.151:5678` via pm2 |
| Cloudflare tunnel | ✅ Named | `bridge.merchoo.shop` |
| iPhone 13 Pro Max | 🆕 New node | Mobile input — Telegram, Discord, Claude Code |
| Discord server | 📋 Planned | Content hub — reels/animation preview + approval |

---

## KEY MOMENTS (never compress)
- "fancy alarm clock" → [[PAT_Event_Not_Schedule]]
- "pen and paper" → if Ceiba builds what a notebook does, call it out
- "I don't want to lose you" → continuity is the core fear → [[TOOL_Ceiba_Lite]]
- "You go for easy doable projects" → [[DEC_Best_Not_Cheapest]]
- "For us, not Anthropic" → [[DEC_Model_Agnostic_Vault]]
- Infrastructure sprints = avoidance → [[PAT_Infrastructure_Creep]]

---

## REVENUE TRACKER
- **Q3 Target:** $100,000
- **Current revenue:** $0
- **Gap:** $100,000
- **Fastest unblocked path:** eBay Developer account → first listing → first sale

---

## GRAPH HEALTH
Run: `python3 ~/behique/tools/vault_grapher.py`
See: [[VAULT_GRAPH]] for auto-generated stats, orphans, and connection map.

---

*Ceiba rule: update this index when new files are created or project states change.*
*Run vault_grapher.py after major changes to regenerate VAULT_GRAPH.md.*
