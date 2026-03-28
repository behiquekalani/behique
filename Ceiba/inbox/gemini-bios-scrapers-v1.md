# BIOS Scraper Specs + Strategy Research (from Gemini)
# Saved: 2026-03-23

## 20 Data Sources for BIOS

### Tier 1 (Core 10)
1. Reddit r/wallstreetbets - /top.json?t=hour
2. Reddit r/cryptocurrency - /top.json?t=hour
3. Reddit r/polymarket - /new.json
4. Reddit r/economics - /top.json?t=day
5. Twitter/X via Nitter RSS - @zerohedge @unusual_whales @financialjuice @KobeissiLetter @WatcherGuru
6. Google Trends - /trends/api/dailytrends
7. ForexFactory - /calendar (BS4 scrape)
8. CoinGecko - /api/v3/coins/markets
9. Fear & Greed Index - api.alternative.me/fng
10. PR Government - fortaleza.pr.gov/blog/feed/

### Tier 2 (High Impact)
11. Hacker News - hacker-news.firebaseio.com/v0/topstories.json
12. YouTube Finance RSS - Real Vision, Bloomberg, Coin Bureau
13. SEC Filings - data.sec.gov/submissions/
14. Polymarket Direct - gamma-api.polymarket.com/markets
15. Binance Open Interest - fapi.binance.com/fapi/v1/openInterest

### Tier 3 (Sentiment)
16. StockTwits - api.stocktwits.com/api/2/streams/symbol/
17. Reddit Comments (deep) - append .json to permalink
18. GDELT News - api.gdeltproject.org/api/v2/doc/doc

### Tier 4 (Macro/Local)
19. FRED Economic Data - api.stlouisfed.org/fred/series/observations
20. El Nuevo Dia RSS - elnuevodia.com/arc/outboundfeeds/rss/

## Conviction Score Architecture (from Gemini)
Master Score (0-100):
- Base Layer (30%): Polymarket probability
- Velocity Layer (30%): Reddit/Twitter mention rate (24h change)
- Sentiment Layer (20%): AI-scored comment depth
- Macro Layer (20%): Economic calendar/news check

## Key Strategic Insights
- Sweet spot: 3-14 day narrative cycle (between Reddit brewing and CNBC coverage)
- Use LLMs as cheap junior analysts (batch 100 comments, get JSON sentiment)
- Extract EXPLICIT trade signals, not just sentiment (buy/sell recommendations)
- Calculate sentiment CHANGE relative to history, not raw scores
- Cross-verify: multiple data classes reduce noise
- Feedback loop: track prediction accuracy, adjust weights over time

## Research-Backed Enhancements
- FinBERT or finance-tuned transformer for better NLP
- Sentiment x volume change score > raw sentiment
- Comment depth (replies, engagement) as quality signal
- Independence factor: 10 tweets from same source = 1.5 signals, not 10
