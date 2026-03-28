---
title: "cobo_instructions_2026-03-16"
type: system
tags: [cobo, instructions]
created: 2026-03-16
---

# COBO INSTRUCTIONS — Monday 2026-03-16
> From: Ceiba (Computer 1) → Cobo (Computer 2)
> Priority: HIGH — This is the day the engine goes live

---

## CONTEXT
The product research engine pipeline is proven end-to-end with seeded data (61 products scored from trends). But scores are flat (38-40 range) because there's no real eBay market data. Today we fix that.

---

## TASK 1: Wire eBay API (PRIMARY OBJECTIVE)

Kalani has eBay API keys ready. Wire them into the engine.

### Steps:
1. **Get credentials from Kalani:**
   - eBay App ID (Client ID)
   - eBay Cert ID (Client Secret)
   - eBay Dev ID
   - eBay OAuth token (or use client_credentials flow)

2. **Update `config.yaml`:**
   ```yaml
   ebay:
     app_id: "YOUR_APP_ID"
     cert_id: "YOUR_CERT_ID"
     dev_id: "YOUR_DEV_ID"
     environment: "production"  # or sandbox for testing
   ```

3. **Implement `ebay/ebay_client.py`:**
   - OAuth2 client_credentials flow → get access token
   - `search_completed(keyword, days=30)` → Browse API findItemsByKeywords
   - `search_active(keyword)` → count active listings
   - Return: avg_sold_price, total_sold_count, active_listing_count
   - Rate limit: 5000 calls/day on production

4. **Implement `ebay/ebay_cross_reference.py`:**
   - For each product in DB: call ebay_client.search_completed() + search_active()
   - Store results in `ebay_market_data` table
   - Calculate: margin = (avg_sold_price - source_price) / avg_sold_price
   - Calculate: saturation = active_listings / (weekly_sales or 1)

5. **Test:**
   ```bash
   python main.py --discover    # Pull from trends (skip Amazon for now)
   python main.py --score       # Should now show score spread (not flat 38-40)
   python main.py --report      # Generate updated rankings
   ```

6. **Expected result:** Score spread should widen significantly (20-80+ range) because margin and competition signals now have real data.

---

## TASK 2: Copy Proxies (IF TIME)

Kalani will copy `proxies.txt` from Mac `~/Downloads/` to Cobo. Once received:

1. Place at `~/behique/product_research_engine/proxies.txt`
2. Update `scrapers/amazon.py` to load and rotate proxies
3. Test: `python main.py --discover` with proxies enabled
4. If Amazon returns products → real discovery pipeline is live

---

## TASK 3: Update Dashboard

After eBay data flows in:
1. Re-run `python main.py --full-pipeline`
2. Dashboard at `output/dashboard.html` should show real score differentiation
3. Screenshot the results and report back

---

## DO NOT:
- Rebuild the scoring engine — it works
- Change the scoring formula — it's calibrated
- Add new scrapers (Walmart, AliExpress) — not yet
- Touch the trends scraper — it's the working discovery source

## REPORT BACK:
After wiring eBay API, send Kalani:
1. Score range (min/max/avg) — should be much wider than 38-40
2. Top 10 products with real scores
3. Any errors or rate limit issues
4. Screenshot of dashboard with real data
