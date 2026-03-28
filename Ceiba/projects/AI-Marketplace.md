---
type: project
status: done-v1
tags: [ai-marketplace, proof-of-concept, revisitable, claw-empire-fork]
created: 2026-03-19
completed: 2026-03-19
location: ~/ai-marketplace
url: http://localhost:8800
---

# AI Marketplace — Behique Command

## Status: DONE (v1 proof of concept)

Tags: `ai-marketplace` `proof-of-concept` `revisitable`

Built in one session. Functional proof of concept — can be revisited and improved later.

---

## What It Is

An interactive AI marketplace built on top of Claw-Empire (open source, Apache 2.0). Instead of an office with employees, it's a marketplace with AI vendor NPCs that sell products and chat with visitors.

Walk around a pixel-art market, click a vendor, ask them about their products. They respond with AI-powered, product-aware answers.

---

## What Was Built

### Phase 1: Data Layer
- Products table in SQLite (CRUD API)
- 20 products across 10 vendors
- Frontend API client
- Puerto Rican marketplace theme (Dona Maria, Sazon, Terreno, Reliquia, etc.)

### Phase 2: Visual Layer
- Market stall counters replacing office desks
- Stall awnings, product displays, vendor signs
- Warm earthy color palette (sandy browns, greens, warm reds)
- Plaza entrance with fountain
- 5 marketplace zones: Fresh Produce, Electronics, Artisan Crafts, Food Court, Vintage & Collectibles

### Phase 3: Interaction Layer
- Vendor chat with product-aware system prompts
- ProductSidebar showing vendor's catalog
- Quick action buttons ("Show products", "What's on sale?", "Recommend something")
- Click product → auto-fills chat input
- OpenAI API connected for AI responses

### Phase 4: Infrastructure
- Ruflo Bridge — visual effects for agent events (spawns, tasks, learning)
- RufloPanel sidebar (lightning bolt button, bottom-right)
- Ceiba CLI — `ceiba wake/bridge/task/tasks` for Mac↔Cobo communication
- Cobo task queue — persistent, survives reboots (pm2)

---

## Tech Stack

- **Frontend:** React 19 + PixiJS (pixel art) + Tailwind CSS
- **Backend:** Express + SQLite + WebSocket
- **AI:** OpenAI API (GPT-4o) via vendor system prompts
- **Orchestration:** Ruflo (99 agents, self-learning, swarms)
- **Network:** Mac (Ceiba) ↔ Cobo (bridge) ↔ Comp3 (worker)

---

## How to Run

```bash
cd ~/ai-marketplace && pnpm dev
# Open http://localhost:8800
```

---

## What Would Make v2 Better

- [ ] Real product images instead of placeholders
- [ ] Payment integration (Stripe)
- [ ] User accounts / cart system
- [ ] More vendor personalities and sales styles
- [ ] Auction / bidding system (from Dermatify concept)
- [ ] "Free fall" pricing (prices drop until someone buys)
- [ ] VR/3D version (long-term vision)
- [ ] Connect to real inventory (eBay/Shopify products)
- [ ] Mobile-responsive marketplace view
- [ ] Multi-language vendor responses (Spanish/English)

---

## Origin

Idea came from Kalani's Dermatify skincare store concept (2025) — a virtual store where you walk aisles, inspect products, talk to AI sales assistants. Combined with Claw-Empire's open-source pixel-art office simulator to create a general-purpose AI marketplace platform.

---

*This project is tagged `revisitable` — it works as a proof of concept. Come back when there's a real use case (actual products to sell, a customer base, or a pitch to investors).*
