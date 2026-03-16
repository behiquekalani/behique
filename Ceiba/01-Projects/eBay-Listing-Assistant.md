---
type: project
status: building
priority: critical
tools:
  - TOOL_Listing_Pipeline
  - TOOL_Trends_Scraper
systems:
  - SYS_AI_Cluster
  - SYS_Bridge
patterns:
  - PAT_Avoidance_Revenue
decisions:
  - DEC_Ebay_Before_Shopify
tags: [project, ecommerce, revenue]
---

# eBay Listing Assistant
**Status:** 🔨 Building → V1 LIVE, V2 built
**Priority:** CRITICAL — direct revenue
**Started:** 2026-03-14

---

## What It Does
Takes a product name + photo → researches sold prices on eBay → generates complete listing → publishes automatically. Zero manual work.

## Why It Matters
→ [[02-Goals/Q3-2026]] — fastest path to first eBay revenue
Every listing done manually is an hour wasted. This runs in seconds.

## Current State (2026-03-16)
- [x] eBay Developer account created (developer.ebay.com)
- [x] Production API keys obtained (`~/.behique_ebay_keys`, chmod 600)
- [x] Sandbox API keys obtained (`~/.behique_ebay_keys_sandbox`, chmod 600)
- [x] Marketplace deletion exemption granted
- [x] V1 listing pipeline — full 9-module system
- [x] V2 API publisher built (auto-refresh, rate limiting, draft preview)
- [x] OAuth token script built (`ebay_oauth_token.py`)
- [x] Quick lister built (`quick_list.py` — skip research, direct listing)
- [x] Funko Pop Goodfellas listing generated + saved to `listings/`
- [ ] **POST THE FUNKO POPS ON EBAY** — Kalani needs to paste into form
- [ ] Run OAuth consent flow to activate V2 API
- [ ] First eBay sale

## Build Plan (updated)
1. ~~eBay Developer account → sandbox keys~~ ✅ DONE
2. ~~Research module: search eBay sold listings~~ ✅ DONE
3. ~~AI module: generate title, description, item specifics~~ ✅ DONE
4. ~~Input flow: product + condition + quantity + shipping~~ ✅ DONE
5. ~~V2 Publisher via eBay Inventory API~~ ✅ BUILT (needs OAuth token)
6. Telegram confirmation when listing goes live — NEXT
7. First sale → iterate

## File Map
```
tools/ebay-listing-assistant/
├── run.py                          # V1 CLI entry point (research-based)
├── quick_list.py                   # Quick lister (skip research, direct)
├── listings/                       # Saved generated listings (.txt + .json)
├── core/
│   ├── types.py                    # Shared data models (ProductInput, ListingContent, etc.)
│   ├── types_v1.py                 # V1 extended input types
│   ├── pipeline.py                 # 3-stage orchestrator
│   ├── pricing.py                  # Pricing engine (fees, shipping, margin calc)
│   └── shipping.py                 # USPS rates from Puerto Rico
├── ai/
│   └── content_generator.py        # SEO title, HTML description, item specifics
├── providers/ebay/
│   ├── research.py                 # eBay sold listing research
│   ├── publisher_v1.py             # Manual copy-paste publisher
│   ├── publisher_v2.py             # API auto-publisher (OAuth, rate limit, draft preview)
│   └── ebay_oauth_token.py         # Standalone OAuth helper
└── media/
    └── image_handler.py            # Image validation
```

## Credentials
- Production keys: `~/.behique_ebay_keys` (App ID, Dev ID, Cert ID)
- Sandbox keys: `~/.behique_ebay_keys_sandbox`
- OAuth tokens: `~/.behique_ebay_tokens.json` (NOT YET — needs consent flow)

## Uses Tools
- [[TOOL_Listing_Pipeline]] — `~/behique/tools/ebay-listing-assistant/core/pipeline.py`
- [[TOOL_Trends_Scraper]] — feeds product ideas into this tool
- [[SYS_AI_Cluster]] — GPT-4o generates listing content via kernel

## Key Decisions
- [[DEC_Ebay_Before_Shopify]] — eBay winners migrate to Shopify, not the other way

## Related Projects
- [[Google-Trends-Scraper]] — product research pipeline
- [[Shopify-Store]] — eBay winners migrate here
- [[01-Projects/MISSIONS]] — Active Quest #1

## Patterns Observed
- [[PAT_Avoidance_Revenue]] — eBay dev account was "next action" for 3+ days before finally getting done 2026-03-16

---

## 🧭 CEIBA BREADCRUMBS
*Ceiba leaves notes here for future sessions. Read before touching this project.*

- **2026-03-14:** Skeleton built — `types.py` + `pipeline.py`. Nothing wired up.
- **2026-03-15:** eBay API keys still not obtained. Pure avoidance pattern.
- **2026-03-16 (session 1):** MASSIVE progress. Got Production + Sandbox API keys. Built V2 publisher with OAuth auto-refresh, rate limiting, exponential backoff, draft preview. Built OAuth token script. Built quest dashboard. Funko Pop listing generated.
- **2026-03-16 (session 2):** Built `quick_list.py` — skip-research direct lister. Generated Funko Pop Goodfellas listing (3 sets × $27.99, $11.22 profit per unit = $33.66 total). Saved to `listings/` folder. Hello Kitty cups skipped (too many variants, needs specifics from Kalani).
- **Revenue is still $0.** The Funko Pop listing is ready. Kalani just needs to paste it into eBay's form.

*Next action: Kalani pastes the Funko Pop listing into eBay. Then run `python3 ebay_oauth_token.py` to activate V2 API publisher.*
