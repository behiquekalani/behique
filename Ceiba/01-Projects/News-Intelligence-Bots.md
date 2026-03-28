---
title: "News-Intelligence-Bots"
type: project
tags: [news, intelligence, bots]
created: 2026-03-16
---

# News Intelligence Bots

Status: Idea — not started
Priority: Medium (build after Ceiba core is stable)

---

## Bot 1 — Market News Alert Bot

### Concept
Monitor ForexFactory and similar sources for high-impact economic events.
Alert in real-time so Kalani can act before the market processes the information.

### Use Cases (beyond trading)
- eBay/reselling pricing opportunities around economic shifts
- Content creation timed to market events
- n8n client alerts for e-commerce businesses
- Crypto positioning awareness

### Data Sources
- ForexFactory (economic calendar)
- Investing.com
- Bloomberg RSS
- CoinDesk (crypto angle)

### Stack Ideas
- n8n for scheduling and alerts
- Telegram for delivery
- Simple classifier to filter high vs low impact

---

## Bot 2 — AI Intelligence Bot

### Concept
Scan AI news sources and filter for things that are ACTIONABLE for Kalani's stack.
Not "new model dropped" — but "this changes how you should build X."

### The Gap
Most AI news is written for investors or researchers. Nobody is doing this well
for solo builders. First-mover advantage here is real.

### Filter Criteria
- Does this affect Python / LangGraph / Claude API?
- Does this create a new revenue opportunity?
- Does this make something Kalani is building obsolete?
- Is this a new tool that could replace something in the stack?

### Data Sources
- Anthropic blog / changelog
- OpenAI blog
- Hugging Face
- X/Twitter (selected builders)
- TLDR AI newsletter
- The Rundown AI

### Stack Ideas
- n8n for scraping and scheduling
- Claude for filtering and summarizing
- Telegram for daily digest delivery
- Obsidian for logging what was implemented

---

## Combined Vision
Both bots eventually feed into Ceiba.
Market awareness + tech awareness = Kalani is never blindsided and never behind.

---

*Logged: 2026-03-14. Revisit when Ceiba core is stable.*
