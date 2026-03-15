#!/usr/bin/env python3
"""
trends_scraper.py — Google Trends Product Research Tool
Built for Kalani's eBay/Shopify pipeline

What it does:
- Pulls rising/trending search queries from Google Trends
- Rotates through Webshare proxies to avoid bans
- Filters for product-relevant niches
- Outputs a ranked CSV of trending products to research

Usage:
    python3 ~/behique/tools/trends_scraper.py

Requirements:
    pip3 install pytrends pandas --break-system-packages

Output:
    ~/behique/output/trending_products_YYYY-MM-DD.csv
"""

import os
import time
import random
import json
import csv
from datetime import datetime
from pathlib import Path

try:
    from pytrends.request import TrendReq
    import pandas as pd
except ImportError:
    print("Installing dependencies...")
    os.system("pip3 install pytrends pandas --break-system-packages -q")
    from pytrends.request import TrendReq
    import pandas as pd

# ── CONFIG ─────────────────────────────────────────────────────────────────────

PROXY_FILE = os.path.expanduser("~/Downloads/Webshare 10 proxies.txt")
OUTPUT_DIR = os.path.expanduser("~/behique/output")
TIMEFRAME = "today 1-m"  # Last 30 days
GEO = "US"               # United States market (best for eBay)

# Product categories to search — ranked by eBay/Shopify relevance
SEARCH_CATEGORIES = [
    # Electronics
    "wireless earbuds", "phone stand", "LED strip lights", "portable charger",
    "ring light", "smart watch", "phone case", "laptop stand",
    # Home
    "air purifier", "humidifier", "storage organizer", "desk lamp",
    "shower curtain", "candle holder", "wall art", "throw pillow",
    # Kitchen
    "air fryer accessories", "coffee accessories", "reusable bags", "food container",
    # Beauty/Health
    "face roller", "hair accessories", "resistance bands", "yoga mat",
    # Kids/Pets
    "fidget toys", "dog harness", "cat toys", "baby monitor",
    # Trending general
    "stanley cup accessories", "bookshelf decor", "plant pots", "cable management"
]

# Delay settings — critical for avoiding bans
MIN_DELAY = 4    # seconds between requests
MAX_DELAY = 9    # seconds between requests
RETRY_DELAY = 30 # seconds to wait after a rate limit hit
MAX_RETRIES = 3

# ── PROXY LOADER ───────────────────────────────────────────────────────────────

def load_proxies(proxy_file: str) -> list:
    """Load proxies from Webshare format: ip:port:user:password"""
    proxies = []
    try:
        with open(proxy_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) == 4:
                    ip, port, user, password = parts
                    proxy_url = f"http://{user}:{password}@{ip}:{port}"
                    proxies.append(proxy_url)
        print(f"✓ Loaded {len(proxies)} proxies")
    except FileNotFoundError:
        print(f"⚠ Proxy file not found at {proxy_file}")
        print("  Running without proxies (higher ban risk)")
    return proxies


def get_proxy_config(proxy_url: str) -> dict:
    """Format proxy for pytrends/requests"""
    return {
        "https": proxy_url,
        "http": proxy_url
    }

# ── TRENDS FETCHER ─────────────────────────────────────────────────────────────

def fetch_related_queries(pytrends, keyword: str) -> list:
    """Get rising related queries for a keyword — these are the golden finds."""
    results = []
    try:
        pytrends.build_payload([keyword], timeframe=TIMEFRAME, geo=GEO)
        related = pytrends.related_queries()

        if keyword in related and related[keyword]["rising"] is not None:
            rising_df = related[keyword]["rising"]
            for _, row in rising_df.head(5).iterrows():
                results.append({
                    "query": row["query"],
                    "value": row["value"],  # % increase
                    "type": "rising",
                    "source_keyword": keyword
                })

        if keyword in related and related[keyword]["top"] is not None:
            top_df = related[keyword]["top"]
            for _, row in top_df.head(3).iterrows():
                results.append({
                    "query": row["query"],
                    "value": row["value"],
                    "type": "top",
                    "source_keyword": keyword
                })

    except Exception as e:
        raise e

    return results


def fetch_interest_score(pytrends, keyword: str) -> int:
    """Get overall interest score for a keyword (0-100)"""
    try:
        pytrends.build_payload([keyword], timeframe=TIMEFRAME, geo=GEO)
        interest = pytrends.interest_over_time()
        if not interest.empty and keyword in interest.columns:
            return int(interest[keyword].mean())
    except:
        pass
    return 0

# ── MAIN SCRAPER ───────────────────────────────────────────────────────────────

def run_scraper():
    proxies = load_proxies(PROXY_FILE)
    proxy_index = 0

    all_results = []
    failed = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"\n🔍 Google Trends Product Research")
    print(f"📅 {timestamp} | Market: {GEO} | Window: {TIMEFRAME}")
    print(f"📦 Scanning {len(SEARCH_CATEGORIES)} product categories\n")
    print("─" * 50)

    for i, keyword in enumerate(SEARCH_CATEGORIES):
        # Rotate proxy
        if proxies:
            proxy_url = proxies[proxy_index % len(proxies)]
            proxy_index += 1
            proxies_dict = get_proxy_config(proxy_url)
        else:
            proxies_dict = {}

        # Init pytrends with proxy
        pytrends = TrendReq(
            hl="en-US",
            tz=300,  # AST (Puerto Rico)
            proxies=list(proxies_dict.values()) if proxies_dict else [],
            retries=2,
            backoff_factor=0.5,
            timeout=(10, 25)
        )

        for attempt in range(MAX_RETRIES):
            try:
                print(f"[{i+1}/{len(SEARCH_CATEGORIES)}] {keyword}...", end=" ", flush=True)

                results = fetch_related_queries(pytrends, keyword)
                interest = fetch_interest_score(pytrends, keyword)

                for r in results:
                    r["category_keyword"] = keyword
                    r["interest_score"] = interest
                    r["scraped_at"] = timestamp
                    all_results.append(r)

                print(f"✓ {len(results)} queries found (interest: {interest})")
                break

            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "rate" in err_str or "too many" in err_str:
                    print(f"\n  ⚠ Rate limited. Waiting {RETRY_DELAY}s + switching proxy...")
                    time.sleep(RETRY_DELAY)
                    proxy_index += 2  # Skip ahead in proxy list
                elif attempt < MAX_RETRIES - 1:
                    print(f"\n  ↺ Retry {attempt+1}/{MAX_RETRIES}...")
                    time.sleep(MIN_DELAY * 2)
                else:
                    print(f"\n  ✗ Failed: {str(e)[:60]}")
                    failed.append(keyword)

        # Random delay between requests — critical
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)

    # ── OUTPUT ─────────────────────────────────────────────────────────────────

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"trending_products_{date_str}.csv")

    if all_results:
        # Sort by: rising first, then by value score
        all_results.sort(key=lambda x: (0 if x["type"] == "rising" else 1, -x["value"]))

        # Write CSV
        fieldnames = ["query", "value", "type", "source_keyword", "interest_score",
                      "category_keyword", "scraped_at"]
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)

        print(f"\n{'─' * 50}")
        print(f"✅ Done. {len(all_results)} results saved.")
        print(f"📄 Output: {output_path}")

        # Print top 15 rising products
        rising = [r for r in all_results if r["type"] == "rising"][:15]
        if rising:
            print(f"\n🔥 TOP RISING PRODUCTS TO RESEARCH ON EBAY:")
            print(f"{'─' * 50}")
            for r in rising:
                print(f"  {r['query']:<40} +{r['value']}% ↑")
        print()

    if failed:
        print(f"\n⚠ {len(failed)} keywords failed: {', '.join(failed)}")

    return output_path if all_results else None


# ── ENTRY POINT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*50)
    print("CEIBA — Google Trends Scraper")
    print("Feeding the eBay/Shopify product pipeline")
    print("="*50)
    run_scraper()
