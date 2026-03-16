---
name: trends-scraper
description: >
  Google Trends product research pipeline v2. Concurrent scraping with proxy rotation,
  SQLite caching, multi-timeframe analysis, and revenue scoring. Trigger when Kalani asks
  about trending products, product research, "what should I sell", niche hunting, or wants
  to run the scraper. Also trigger on "find products", "trends", "what's selling", "run
  the scraper", or "overnight scan".
---

## What This Does

Scrapes Google Trends for rising search queries across 80+ keywords in 8 categories,
scores them for eBay/Shopify resale potential, and classifies trend type (spike, emerging,
seasonal, stable). Output feeds the eBay listing pipeline.

## The Script

Located at `~/behique/tools/trends_scraper.py` — runs on both Computer 1 (Mac) and Computer 2 (Cobo/Windows).

Python 3.12 installed on Cobo as of 2026-03-15.

Run it:
```bash
# Full scan (80+ keywords, all categories)
python3 ~/behique/tools/trends_scraper.py

# Quick scan (20 keywords)
python3 ~/behique/tools/trends_scraper.py --quick

# Single category
python3 ~/behique/tools/trends_scraper.py --category electronics

# Seed-based expansion (find related products)
python3 ~/behique/tools/trends_scraper.py --seed "air fryer"

# Custom geo/timeframe
python3 ~/behique/tools/trends_scraper.py --geo US --timeframe today 3-m
```

Output: `~/behique/output/` — CSV, JSON, and `top_picks.txt` (human-readable)

## v2 Upgrades (2026-03-15)

| Feature | Details |
|---------|---------|
| Concurrent workers | 5 threads, ~27s for 10 keywords vs serial |
| Query batching | 5 keywords per Google Trends payload |
| Multi-timeframe | 7d, 1m, 3m — classifies spike/emerging/seasonal/stable |
| Seed expansion | `--seed "air fryer"` finds related product niches |
| SQLite caching | 24h TTL, avoids redundant API calls |
| Scoring formula | velocity x 0.35 + volume x 0.25 + viability x 0.25 + specificity x 0.15 |
| Trend classification | Spike, emerging, seasonal, stable based on velocity |
| Normalized metrics | All scores 0-1 range |

## 8 Keyword Categories

electronics, home, kitchen, beauty_health, fitness, kids_pets, fashion, seasonal_viral

## Known Issues

- pytrends 4.9.2 has urllib3 compatibility issue — fixed in script by skipping retry params
- Google rate limits aggressively. Proxy rotation helps but isn't bulletproof
- Proxies at `~/Downloads/Webshare 10 proxies.txt`

## Overnight Automation (planned)

Target: LaunchAgent on Mac or Task Scheduler on Cobo for 3 AM runs.
Results land in `~/behique/output/`, synced via Syncthing.
BehiqueBot notification when scan completes (not yet wired).

## What to Do With Results

1. Review `top_picks.txt` — sorted by score, shows trend type and velocity
2. Emerging trends with velocity >1.5x are real product signals
3. Cross-reference with eBay sold listings (manual until API keys arrive)
4. Products with high trend + available supply = list on eBay
5. Winners from eBay graduate to Shopify

## Dependencies

```
pip install pytrends pandas numpy
```
