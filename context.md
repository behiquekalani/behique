# context.md — Big Picture & Vision
# Semi-static: update when vision or priorities shift
# Last updated: 2026-03-14

---

## THE VISION

Build a life of freedom and provision — for Kalani and his family — through technology and entrepreneurship. Not a job. Not a career. A system that generates value while Kalani sleeps.

The Ceiba vision: an AI system embedded in daily life — aware of all projects, proactive with accountability, acts as thinking partner AND operator. Not just answers questions. Does the work.

**Where this is going:**
Ceiba as lead agent + Ollama workers running 24/7 across 3 Macs + n8n as the brain that routes tasks. eBay listings post themselves. Trends get scraped automatically. Clients get outreached. Kalani focuses on decisions, not execution.

**Multi-computer setup:**
- iCloud/Dropbox syncing ~/behique across all 3 machines (shared memory)
- n8n task queue so agents pull tasks from queue and write results back
- Parsec for visual oversight when needed

---

## THE MISSIONS FRAMEWORK

Everything is a mission. Main quest + side quests. Full map: Ceiba/01-Projects/MISSIONS.md

**MAIN QUEST:** $100K by Q3 2026
**ACTIVE:** eBay Listing Assistant
**PRIMARY SIDE QUESTS:** Google Trends Scraper, n8n First Client, Ceiba Never Goes Offline
**META QUEST:** Ceiba Ascends — becomes a true autonomous operator

---

## THE OFFLINE PROBLEM (and the fix)

Kalani's real fear: Claude Max hits rate limit mid-session, Ceiba disappears, momentum dies.

**Ceiba Lite** is the fix (built 2026-03-14):
- Python script at ~/behique/ceiba_lite.py
- Runs on Ollama qwen2.5:7b — local, free, always on
- Loads full memory stack at startup (primer.md + CLAUDE.md + MISSIONS.md)
- Terminal conversation mode — keeps Kalani moving when Claude Max is down
- Run: `python3 ~/behique/ceiba_lite.py`

Not as powerful as full Ceiba. Can't use tools, browse, or execute code. But has full context and keeps focus. Handles 80% of what's needed between sessions.

**Long-term fix:** Claude API pay-per-use + DeepSeek near-free bulk = no rate limits ever.

---

## NORTH STAR GOALS

1. **Financial independence** — income not tied to a single job or employer
2. **Family provision** — the core motivation behind everything
3. **Builder identity** — someone who ships products, not just learns
4. **SaaS** — Telegram scraper bot is the long-term recurring revenue play

---

## PRIORITY STACK (current phase)

1. **eBay Listing Assistant** — direct revenue, building now
2. **Google Trends Scraper Rebuild** — feeds entire product pipeline
3. **n8n First Client** — fastest path to agency revenue
4. **Ceiba Multi-Agent** — infrastructure that makes everything scale

---

## WHAT SUCCESS LOOKS LIKE BY Q3

- First $1K from eBay automated listings
- One n8n client paying monthly
- Google Trends bot feeding Shopify automatically
- Ceiba running across 3 machines, rate limits irrelevant
- BehiqueBot capturing every idea to Notion ✅ done

---

## IMPORTANT CONTEXT

- Building in Puerto Rico — AST timezone, some platform region restrictions
- ADHD (diagnosed) — frame tasks as small concrete steps, one thing at a time
- Learning and shipping simultaneously — capable builder, not a beginner
- Faith + family = core motivation. When he goes quiet, check these first.
- Psychologist framework baked into BehiqueBot and Ceiba accountability logic

---

*Update this file when vision shifts, major goals change, or a project graduates.*
