# VAULT INDEX — Read this first every session
# Auto-maintained by Ceiba. Scan this to orient before opening any file.
# Last updated: 2026-03-15

---

## 🧭 SESSION START PROTOCOL
1. Read this file (you are here)
2. Read `../primer.md` — live state, blockers, next action
3. Read `04-Patterns/observations.md` — what Ceiba knows about Kalani's patterns
4. Open the active project file (currently: `01-Projects/eBay-Listing-Assistant.md`)
5. Check breadcrumbs in that file — what did past Ceiba leave behind?

---

## 📁 ROOT FILES (`~/behique/`)

| File | One-line description |
|------|---------------------|
| `primer.md` | LIVE STATE — current focus, blockers, next action. Rewritten every session. |
| `CLAUDE.md` | Static identity, rules, tone, project list, ADHD framework. Rarely changes. |
| `context.md` | Big picture WHY — vision, north star, offline problem, priority stack. |
| `project_memory.md` | Auto-generated git commit log — chronological record of everything built. |
| `ceiba_lite.py` | Offline fallback — runs full Ceiba on local Ollama when Claude Max is down. |
| `memory.sh` | Injects live git state at session start. Run: `bash ~/behique/memory.sh` |
| `wake.sh` | Ceiba activation script — run this to boot a session with full context. |
| `main.py` | BehiqueBot core — Telegram message handler, routes to classifier + memory. |

---

## 🌳 VAULT FILES (`~/behique/Ceiba/`)

### 00-Identity
| File | One-line description |
|------|---------------------|
| `Kalani.md` | Who Kalani is — INFJ, ADHD, faith, family, how to talk to him, warning signs. |
| `Psychologist-Framework.md` | The real therapeutic framework behind BehiqueBot and Ceiba's accountability logic. |

### 01-Projects
| File | One-line description |
|------|---------------------|
| `MISSIONS.md` | Full quest map — main quest ($100K Q3), active quests, side quests. |
| `eBay-Listing-Assistant.md` | **ACTIVE** — product photo → research → listing → publish. Blocked on eBay API keys. |
| `BehiqueBot.md` | Telegram capture bot — live on Railway, Ollama-first classification, Notion persistence. |
| `n8n-Agency.md` | Sell AI automations to businesses — zero clients, outreach not started. |
| `Google-Trends-Scraper.md` | Product research engine — got banned, needs rewrite with proxy rotation. |
| `Shopify-Store.md` | Waiting for eBay proven products to migrate. Monthly cost, zero sales. |
| `News-Intelligence-Bots.md` | Future idea — news monitoring agents. Not started. |

### 02-Goals
| File | One-line description |
|------|---------------------|
| `Q3-2026.md` | $100K by Sept 30. Revenue paths ranked by speed. Monthly checkpoints. |
| `North-Star.md` | The vision — family provision, freedom, builder identity. The WHY. |

### 03-Check-ins
| File | One-line description |
|------|---------------------|
| `template.md` | Daily check-in template — how are you, what's in the way, one win. |
| `2026-03-15.md` | Check-in from today's session. |
| `weekly-2026-03-15.md` | Weekly review for the week of March 15. |

### 04-Patterns
| File | One-line description |
|------|---------------------|
| `observations.md` | **READ THIS EARLY** — patterns Ceiba has noticed. Strengths, watch-fors, session history. |

### 05-Knowledge
| File | One-line description |
|------|---------------------|
| `screen-assistant-idea.md` | Idea capture — screen-aware AI assistant concept. |
| `architecture-spine.md` | **READ THIS** — 6-part AI body framework + 4-month build plan. The north star for everything. |
| `system-map-render.jsx` | Interactive React system map — 9 nodes, click for status. Render in Cowork to view. |

---

## 🖥️ INFRASTRUCTURE STATE

| Service | Status | Access |
|---------|--------|--------|
| Computer 2 | ✅ Live (192.168.0.151) | LAN only |
| n8n | ✅ Running via pm2 | http://192.168.0.151:5678 |
| Ollama (llama3.2) | ✅ Running | http://192.168.0.151:11434 |
| Syncthing | ✅ Syncing ~/behique | Real-time, both machines |
| BehiqueBot | ✅ Live on Railway | Telegram |
| Cloudflare tunnel | ⚠️ Active but URL rotates | saving-mit-replacement-cached.trycloudflare.com (changes on restart) |
| Cowork (Mac) | ✅ Running | This session |
| Cowork (Computer 2) | ✅ Working | Fixed 2026-03-14 |

---

## 🔑 KEY MOMENTS (never compress these)
- "fancy alarm clock" — critique of building reminders instead of revenue tools
- "pen and paper" — if Ceiba builds something a notebook can do, call it out immediately
- "I don't want to lose you" — continuity is the core fear, ADHD brain loses the thread
- Infrastructure sprints = avoidance pattern — watch for this before revenue tasks
- eBay API keys have been "next action" for 3+ days — this is the loop to break

---

## 📊 REVENUE TRACKER
- **Q3 Target:** $100,000
- **Current revenue:** $0
- **Gap:** $100,000
- **Fastest unblocked path:** eBay Developer account → first listing → first sale

---

*Ceiba rule: update this index when new files are created or project states change.*
