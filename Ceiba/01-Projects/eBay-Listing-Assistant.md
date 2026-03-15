# eBay Listing Assistant
**Status:** 🔨 Building
**Priority:** CRITICAL — direct revenue
**Started:** 2026-03-14

---

## What It Does
Takes a product name + photo → researches sold prices on eBay → generates complete listing → publishes automatically. Zero manual work.

## Why It Matters
→ [[02-Goals/Q3-2026]] — fastest path to first eBay revenue
Every listing done manually is an hour wasted. This runs in seconds.

## Current Blockers
- [ ] eBay Developer account (developer.ebay.com) — NOT SET UP
- [ ] Sandbox API keys (App ID, Cert ID, Dev ID, User token)

## Build Plan
1. eBay Developer account → sandbox keys
2. Research module: search eBay sold listings → get price range
3. AI module: generate title, description, item specifics, category
4. Input flow: product name + image → ask condition + quantity + shipping
5. Publish via eBay Trading API or Inventory API
6. Telegram confirmation sent when listing goes live

## Related
→ [[Google-Trends-Scraper]] — feeds product ideas into this tool
→ [[Shopify-Store]] — eBay winners migrate here automatically
→ [[01-Projects/MISSIONS]] — Active Quest #1

---

---

## 🧭 CEIBA BREADCRUMBS
*Ceiba leaves notes here for future sessions. Read before touching this project.*

- **2026-03-14:** Skeleton built — `types.py` (data models) + `pipeline.py` (3-stage orchestrator). Both at `~/behique/tools/ebay-listing-assistant/core/`. Nothing wired up yet. All adapters missing.
- **2026-03-15:** eBay API keys still not obtained. This has been "next action" for 3+ days. No technical blocker — pure avoidance. Name it directly.
- **Pattern note:** Every session ends without doing developer.ebay.com. Open the tab NOW, not at the end of the session.

*Next action: developer.ebay.com → create account → get App ID, Cert ID, Dev ID, OAuth token → paste into session*
