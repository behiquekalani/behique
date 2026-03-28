---
type: project
status: rebuilding
tools:
  - TOOL_Trends_Scraper
systems:
  - SYS_AI_Cluster
patterns:
  - PAT_Kamikaze_Scraping
decisions:
  - DEC_Proxy_Rotation
tags: [project, scraping, research]
---

# Google Trends Scraper
**Status:** 🔨 Rebuilding (Cobo refactoring with concurrency + batching)
**Priority:** HIGH — feeds entire product pipeline
**First version:** Got banned (no proxy rotation, no rate limiting)

---

## What It Does
Scrapes Google Trends for rising product queries across eBay-relevant categories.
Output: ranked CSV of trending products to research → list on eBay → migrate winners to Shopify.

## Why It Matters
→ [[eBay-Listing-Assistant]] needs products to list
→ [[Shopify-Store]] needs proven winners
Without this, product selection is guesswork. With it, data-driven.

## What Got Fixed (v2)
- Proxy rotation through Webshare 10 proxies
- Random delays 4-9 seconds between requests
- Retry logic with exponential backoff on 429 errors
- Separate pytrends instance per request (fresh session)
- Focuses on rising queries (breakout products)

## Files
- `~/behique/tools/trends_scraper.py` — rebuilt scraper
- `~/Downloads/Webshare 10 proxies.txt` — 10 Webshare proxies (format: ip:port:user:pass)

## How to Run
```bash
python3 ~/behique/tools/trends_scraper.py
```
Output saved to: `~/behique/output/trending_products_YYYY-MM-DD.csv`

## Search Categories (current)
Electronics, Home, Kitchen, Beauty/Health, Kids/Pets + trending general items.
Edit SEARCH_CATEGORIES in the script to customize.

## Proxies
Webshare rotating proxies — 10 available. Username: mmqgymcq
Refresh from Webshare dashboard if they expire.

## Uses Tools
- [[TOOL_Trends_Scraper]] — `~/behique/tools/trends_scraper.py`
- [[SYS_AI_Cluster]] — scoring via Ollama, overnight automation

## Related Projects
- [[eBay-Listing-Assistant]] — uses scraper output for product research
- [[Shopify-Store]] — long-term migration of proven products
- [[01-Projects/MISSIONS]] — Primary Side Quest A

## Key Decisions
- [[DEC_Proxy_Rotation]] — 10 Webshare proxies, rotate aggressively

---

*Next action: Test run. `python3 ~/behique/tools/trends_scraper.py`*
