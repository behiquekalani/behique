#!/usr/bin/env python3
"""
trends_scraper.py — Google Trends Product Research v2
Refactored for Kalani's eBay/Shopify pipeline

Changes from v1:
- Concurrent workers (ThreadPoolExecutor, 5 workers)
- Query batching (5 keywords per payload)
- Multi-timeframe analysis (7d, 1m, 3m) with trend classification
- Problem-based seed expansion (--seed mode)
- SQLite caching (24h TTL)
- New scoring formula (velocity + volume + viability + specificity)
- --geo and --timeframe CLI flags

Usage:
    python trends_scraper.py                          # Full run
    python trends_scraper.py --quick                  # Top 20 keywords
    python trends_scraper.py --category electronics   # Single category
    python trends_scraper.py --seed "air fryer"       # Seed expansion mode
    python trends_scraper.py --geo US --timeframe "today 3-m"

Output:
    ~/behique/output/trending_products_YYYY-MM-DD.csv
    ~/behique/output/trending_products_YYYY-MM-DD.json
    ~/behique/output/top_picks_YYYY-MM-DD.txt
    ~/behique/output/seed_keywords.json  (seed mode only)
"""

import os
import sys
import time
import random
import json
import csv
import sqlite3
import logging
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from pytrends.request import TrendReq
    import pandas as pd
    import numpy as np
except ImportError:
    print("Installing dependencies...")
    os.system("pip install pytrends pandas numpy --break-system-packages -q")
    from pytrends.request import TrendReq
    import pandas as pd
    import numpy as np

# ── CONFIG ─────────────────────────────────────────────────────────────────────

PROXY_FILE = os.path.expanduser("~/Downloads/Webshare 10 proxies.txt")
OUTPUT_DIR = os.path.expanduser("~/behique/output")
CACHE_DIR = os.path.expanduser("~/behique/cache")
DEFAULT_GEO = "US"
MAX_WORKERS = 5
BATCH_SIZE = 5  # Google Trends allows 5 keywords per payload

# Delay settings
MIN_DELAY = 5
MAX_DELAY = 12
RETRY_BASE_DELAY = 15
MAX_RETRIES = 4
COOLDOWN_AFTER_BLOCK = 60

# Timeframes for multi-timeframe analysis
TIMEFRAMES = ["now 7-d", "today 1-m", "today 3-m"]

# Seed patterns for problem-based expansion
SEED_PATTERNS = [
    "fix {}",
    "replacement {}",
    "best {} for",
    "how to clean {}",
    "{} accessories",
    "{} parts",
]

# ── PRODUCT CATEGORIES ─────────────────────────────────────────────────────────

CATEGORIES = {
    "electronics": [
        "wireless earbuds", "phone stand", "LED strip lights", "portable charger",
        "ring light", "smart watch", "phone case", "laptop stand", "webcam",
        "bluetooth speaker", "USB hub", "wireless mouse", "screen protector",
        "power bank", "cable organizer",
    ],
    "home": [
        "air purifier", "humidifier", "storage organizer", "desk lamp",
        "shower curtain", "candle holder", "wall art", "throw pillow",
        "bookshelf decor", "plant pots", "cable management", "drawer organizer",
        "aromatherapy diffuser", "LED mirror", "floating shelf",
    ],
    "kitchen": [
        "air fryer accessories", "coffee accessories", "reusable bags",
        "food container", "water bottle", "lunch box", "kitchen gadgets",
        "silicone baking", "spice organizer", "knife set",
    ],
    "beauty_health": [
        "face roller", "hair accessories", "skincare tools", "makeup organizer",
        "LED face mask", "hair dryer brush", "nail art kit", "teeth whitening",
        "scalp massager", "gua sha",
    ],
    "fitness": [
        "resistance bands", "yoga mat", "jump rope", "foam roller",
        "fitness tracker", "gym bag", "massage gun", "pull up bar",
        "adjustable dumbbells", "workout gloves",
    ],
    "kids_pets": [
        "fidget toys", "dog harness", "cat toys", "baby monitor",
        "kids tablet case", "pet camera", "dog bed", "pet grooming",
        "baby carrier", "educational toys",
    ],
    "fashion": [
        "crossbody bag", "sunglasses", "minimalist wallet", "tote bag",
        "baseball cap", "sneaker cleaning", "belt bag", "watch band",
        "jewelry organizer", "scarf",
    ],
    "seasonal_viral": [
        "stanley cup accessories", "viral tiktok product", "trending gadget 2026",
        "summer outdoor", "beach accessories", "camping gear", "graduation gift",
        "back to school supplies", "halloween costume", "christmas gift ideas",
    ],
}

ALL_KEYWORDS = []
for cat_keywords in CATEGORIES.values():
    ALL_KEYWORDS.extend(cat_keywords)

# ── LOGGING ────────────────────────────────────────────────────────────────────

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

log_path = os.path.join(OUTPUT_DIR, f"scraper_log_{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("trends")

# ── SQLITE CACHE ───────────────────────────────────────────────────────────────


class TrendsCache:
    """SQLite cache for Google Trends data. 24h TTL per (keyword, timeframe, geo)."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(CACHE_DIR, "trends_cache.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trends_cache (
                    keyword TEXT,
                    timeframe TEXT,
                    geo TEXT,
                    fetched_at INTEGER,
                    data TEXT,
                    PRIMARY KEY(keyword, timeframe, geo)
                )
            """)

    def get(self, keyword, timeframe, geo):
        """Return cached data if fresh (< 24h), else None."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT data, fetched_at FROM trends_cache WHERE keyword=? AND timeframe=? AND geo=?",
                (keyword, timeframe, geo),
            ).fetchone()
            if row:
                data_str, fetched_at = row
                age_hours = (time.time() - fetched_at) / 3600
                if age_hours < 24:
                    return json.loads(data_str)
        return None

    def set(self, keyword, timeframe, geo, data):
        """Store data in cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO trends_cache (keyword, timeframe, geo, fetched_at, data)
                   VALUES (?, ?, ?, ?, ?)""",
                (keyword, timeframe, geo, int(time.time()), json.dumps(data)),
            )


# ── PROXY MANAGEMENT ──────────────────────────────────────────────────────────


class ProxyPool:
    """Rotating proxy pool with failure tracking."""

    def __init__(self, proxy_file):
        self.proxies = []
        self.failures = {}
        self._load(proxy_file)
        self.index = 0

    def _load(self, path):
        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(":")
                    if len(parts) == 4:
                        ip, port, user, password = parts
                        url = f"http://{user}:{password}@{ip}:{port}"
                        self.proxies.append(url)
                        self.failures[url] = 0
            log.info(f"Loaded {len(self.proxies)} proxies")
        except FileNotFoundError:
            log.warning(f"Proxy file not found: {path}")
            log.warning("Running without proxies (higher ban risk)")

    def next(self):
        if not self.proxies:
            return None
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.index % len(self.proxies)]
            self.index += 1
            if self.failures.get(proxy, 0) < 3:
                return proxy
            attempts += 1
        log.warning("All proxies degraded. Resetting failure counts.")
        for p in self.proxies:
            self.failures[p] = 0
        return self.proxies[self.index % len(self.proxies)]

    def report_failure(self, proxy):
        if proxy:
            self.failures[proxy] = self.failures.get(proxy, 0) + 1

    def report_success(self, proxy):
        if proxy:
            self.failures[proxy] = 0

    @property
    def active_count(self):
        return sum(1 for p in self.proxies if self.failures.get(p, 0) < 3)


# ── TRENDS FETCHER ─────────────────────────────────────────────────────────────


def create_pytrends(proxy_url=None):
    """Create a new pytrends session with optional proxy."""
    kwargs = {
        "hl": "en-US",
        "tz": 240,  # AST (Puerto Rico)
        "timeout": (10, 30),
    }
    if proxy_url:
        kwargs["proxies"] = [proxy_url]
    # Note: retries/backoff_factor removed — causes method_whitelist error
    # with newer urllib3. Retries handled in worker_fetch_keyword instead.
    return TrendReq(**kwargs)


def chunk_keywords(keywords, size=BATCH_SIZE):
    """Split keywords into batches of `size`."""
    for i in range(0, len(keywords), size):
        yield keywords[i:i + size]


def fetch_interest_multi_timeframe(pytrends, keyword, geo, cache):
    """Fetch interest over time for multiple timeframes. Returns dict of timeframe -> mean value."""
    results = {}
    for tf in TIMEFRAMES:
        # Check cache first
        cached = cache.get(keyword, tf, geo)
        if cached is not None:
            results[tf] = cached
            continue

        try:
            pytrends.build_payload([keyword], timeframe=tf, geo=geo)
            interest = pytrends.interest_over_time()
            if not interest.empty and keyword in interest.columns:
                values = interest[keyword].tolist()
                data = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "values": values,
                }
                results[tf] = data
                cache.set(keyword, tf, geo, data)
            else:
                results[tf] = {"mean": 0, "std": 0, "values": []}
                cache.set(keyword, tf, geo, results[tf])
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            log.debug(f"Interest fetch failed for {keyword} ({tf}): {e}")
            results[tf] = {"mean": 0, "std": 0, "values": []}

    return results


def classify_trend(timeframe_data):
    """
    Classify trend type based on multi-timeframe data.
    Returns: spike, emerging, seasonal, or stable
    """
    d7 = timeframe_data.get("now 7-d", {})
    m1 = timeframe_data.get("today 1-m", {})
    m3 = timeframe_data.get("today 3-m", {})

    d7_mean = d7.get("mean", 0)
    m1_mean = m1.get("mean", 0)
    m3_mean = m3.get("mean", 0)
    m3_std = m3.get("std", 0)
    m3_values = m3.get("values", [])

    # Spike: 7d mean is 2x+ the 1m mean
    if m1_mean > 0 and d7_mean > 2 * m1_mean:
        return "spike"

    # Emerging: positive slope in 3m data
    if len(m3_values) >= 10:
        first_half = np.mean(m3_values[:len(m3_values) // 2])
        second_half = np.mean(m3_values[len(m3_values) // 2:])
        if second_half > first_half * 1.2:
            return "emerging"

    # Seasonal: high variance but recurring peaks
    if m3_mean > 0 and m3_std / m3_mean > 0.5:
        return "seasonal"

    return "stable"


def fetch_related_queries(pytrends, keyword, geo):
    """Get rising + top related queries for a keyword."""
    results = []
    pytrends.build_payload([keyword], timeframe="today 1-m", geo=geo)
    related = pytrends.related_queries()

    if keyword in related and related[keyword]["rising"] is not None:
        rising_df = related[keyword]["rising"]
        for _, row in rising_df.head(8).iterrows():
            results.append({
                "query": row["query"],
                "trend_value": int(row["value"]),
                "trend_type": "rising",
                "source_keyword": keyword,
            })

    if keyword in related and related[keyword]["top"] is not None:
        top_df = related[keyword]["top"]
        for _, row in top_df.head(5).iterrows():
            results.append({
                "query": row["query"],
                "trend_value": int(row["value"]),
                "trend_type": "top",
                "source_keyword": keyword,
            })

    return results


# ── SCORING v2 ─────────────────────────────────────────────────────────────────

VIABILITY_KEYWORDS = [
    "replacement", "parts", "cleaner", "kit", "filter",
    "accessories", "case", "cover", "charger", "organizer",
    "set", "bundle", "premium", "pro", "upgraded", "custom",
    "holder", "mount", "stand", "bracket", "adapter",
]

LOW_VALUE_SIGNALS = [
    "free", "cheap", "diy", "how to", "tutorial", "review", "vs",
    "meaning", "definition", "reddit", "wiki",
]


def compute_trend_velocity(timeframe_data):
    """Ratio of recent vs older trend values. >1 means accelerating."""
    m3 = timeframe_data.get("today 3-m", {})
    values = m3.get("values", [])
    if len(values) < 20:
        m1 = timeframe_data.get("today 1-m", {})
        values = m1.get("values", [])
    if len(values) < 4:
        return 0.5
    mid = len(values) // 2
    prev_avg = np.mean(values[:mid]) if np.mean(values[:mid]) > 0 else 1
    recent_avg = np.mean(values[mid:])
    return float(recent_avg / prev_avg)


def compute_search_volume(timeframe_data):
    """Proxy for search volume: mean of 3-month interest."""
    m3 = timeframe_data.get("today 3-m", {})
    return m3.get("mean", 0)


def compute_specificity(query):
    """More words = more niche = higher specificity."""
    words = len(query.split())
    if words >= 4:
        return 1.0
    elif words == 3:
        return 0.8
    elif words == 2:
        return 0.5
    else:
        return 0.2


def compute_product_viability(query):
    """Heuristic: does the query look like a buyable product?"""
    q = query.lower()
    score = 0.3  # baseline

    for signal in VIABILITY_KEYWORDS:
        if signal in q:
            score += 0.15

    for signal in LOW_VALUE_SIGNALS:
        if signal in q:
            score -= 0.2

    # Numbers and colors suggest specificity
    if any(c.isdigit() for c in q):
        score += 0.1
    if any(color in q for color in ["black", "white", "pink", "blue", "red", "green"]):
        score += 0.05

    return max(0.0, min(1.0, score))


def normalize(value, min_val, max_val):
    """Normalize to 0-1 range."""
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def score_results(all_results):
    """
    Apply new scoring formula to all results.
    score = velocity * 0.35 + volume * 0.25 + viability * 0.25 + specificity * 0.15
    """
    if not all_results:
        return all_results

    # Collect raw values for normalization
    velocities = [r.get("_velocity", 0.5) for r in all_results]
    volumes = [r.get("_volume", 0) for r in all_results]

    vel_min, vel_max = min(velocities), max(velocities)
    vol_min, vol_max = min(volumes), max(volumes)

    for r in all_results:
        vel_norm = normalize(r.get("_velocity", 0.5), vel_min, vel_max)
        vol_norm = normalize(r.get("_volume", 0), vol_min, vol_max)
        viability = r.get("product_viability", 0.3)
        specificity = r.get("specificity", 0.5)

        r["search_volume"] = round(r.get("_volume", 0), 2)
        r["trend_velocity"] = round(r.get("_velocity", 0.5), 3)
        r["score"] = round(
            vel_norm * 0.35 +
            vol_norm * 0.25 +
            viability * 0.25 +
            specificity * 0.15,
            4,
        )

        # Clean up internal fields
        r.pop("_velocity", None)
        r.pop("_volume", None)

    return all_results


# ── WORKER ─────────────────────────────────────────────────────────────────────


def worker_fetch_keyword(keyword, pool, geo, cache):
    """
    Worker function: fetch all data for one keyword.
    Each worker creates its own TrendReq session.
    Returns list of result dicts.
    """
    proxy_url = pool.next()
    pytrends = create_pytrends(proxy_url)
    results = []

    for attempt in range(MAX_RETRIES):
        try:
            # 1. Related queries
            related = fetch_related_queries(pytrends, keyword, geo)
            time.sleep(random.uniform(2, 4))

            # 2. Multi-timeframe interest
            tf_data = fetch_interest_multi_timeframe(pytrends, keyword, geo, cache)

            # 3. Classify trend
            trend_class = classify_trend(tf_data)

            # 4. Compute raw metrics
            velocity = compute_trend_velocity(tf_data)
            volume = compute_search_volume(tf_data)

            # Find category
            category = "other"
            for cat, kws in CATEGORIES.items():
                if keyword in kws:
                    category = cat
                    break

            for r in related:
                r["category"] = category
                r["trend_classification"] = trend_class
                r["specificity"] = compute_specificity(r["query"])
                r["product_viability"] = compute_product_viability(r["query"])
                r["_velocity"] = velocity
                r["_volume"] = volume
                r["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                results.append(r)

            pool.report_success(proxy_url)
            log.info(f"  OK {keyword} -- {len(related)} queries, trend: {trend_class}")
            return results

        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate" in err_str or "too many" in err_str:
                pool.report_failure(proxy_url)
                wait = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 10)
                log.warning(f"  Rate limited on {keyword}. Backoff {wait:.0f}s (attempt {attempt + 1})")
                time.sleep(wait)
                proxy_url = pool.next()
                pytrends = create_pytrends(proxy_url)
            elif attempt < MAX_RETRIES - 1:
                log.warning(f"  Error on {keyword}: {str(e)[:60]} — retry {attempt + 1}")
                time.sleep(MIN_DELAY * 2)
            else:
                log.error(f"  Failed {keyword} after {MAX_RETRIES} attempts: {str(e)[:80]}")

    return results


# ── SEED EXPANSION ─────────────────────────────────────────────────────────────


def run_seed_mode(seed_keyword, pool, geo, cache):
    """
    Problem-based seed expansion.
    Takes a keyword, generates pattern queries, runs related_queries,
    outputs discovered keywords to seed_keywords.json.
    """
    log.info(f"Seed expansion mode: '{seed_keyword}'")
    log.info(f"Generating {len(SEED_PATTERNS)} pattern queries...")

    pattern_queries = [p.format(seed_keyword) for p in SEED_PATTERNS]
    all_discovered = []

    for pq in pattern_queries:
        proxy_url = pool.next()
        pytrends = create_pytrends(proxy_url)

        try:
            log.info(f"  Querying: {pq}")
            related = fetch_related_queries(pytrends, pq, geo)

            for r in related:
                r["seed_pattern"] = pq
                r["original_seed"] = seed_keyword
                r["specificity"] = compute_specificity(r["query"])
                r["product_viability"] = compute_product_viability(r["query"])
                all_discovered.append(r)

            pool.report_success(proxy_url)
            log.info(f"    → {len(related)} related queries found")
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

        except Exception as e:
            log.warning(f"    Failed: {str(e)[:60]}")
            pool.report_failure(proxy_url)
            time.sleep(RETRY_BASE_DELAY)

    # Deduplicate by query
    seen = set()
    unique = []
    for r in all_discovered:
        if r["query"].lower() not in seen:
            seen.add(r["query"].lower())
            unique.append(r)

    # Sort by viability
    unique.sort(key=lambda x: -x["product_viability"])

    # Output
    output_path = os.path.join(OUTPUT_DIR, "seed_keywords.json")
    with open(output_path, "w") as f:
        json.dump({
            "seed": seed_keyword,
            "patterns_used": pattern_queries,
            "total_discovered": len(unique),
            "keywords": unique,
        }, f, indent=2)

    log.info(f"\nSeed expansion complete.")
    log.info(f"Discovered {len(unique)} unique keywords from '{seed_keyword}'")
    log.info(f"Output: {output_path}")

    if unique:
        log.info(f"\nTop 10 discovered keywords:")
        for i, r in enumerate(unique[:10], 1):
            log.info(f"  {i}. {r['query']:<40} viability: {r['product_viability']:.2f}")

    return output_path


# ── MAIN SCRAPER ───────────────────────────────────────────────────────────────


def run_scraper(keywords=None, quick=False, geo=DEFAULT_GEO):
    pool = ProxyPool(PROXY_FILE)
    cache = TrendsCache()

    if keywords is None:
        keywords = ALL_KEYWORDS
    if quick:
        keywords = keywords[:20]

    all_results = []
    failed = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_str = datetime.now().strftime("%Y-%m-%d")

    log.info(f"Google Trends Product Research v2")
    log.info(f"Date: {timestamp} | Market: {geo} | Timeframes: {TIMEFRAMES}")
    log.info(f"Scanning {len(keywords)} keywords across {len(CATEGORIES)} categories")
    log.info(f"Workers: {MAX_WORKERS} | Batch size: {BATCH_SIZE}")
    log.info(f"Active proxies: {pool.active_count}/{len(pool.proxies)}")
    log.info("-" * 50)

    # Process keywords with thread pool
    completed = 0
    total = len(keywords)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_kw = {
            executor.submit(worker_fetch_keyword, kw, pool, geo, cache): kw
            for kw in keywords
        }

        for future in as_completed(future_to_kw):
            kw = future_to_kw[future]
            completed += 1
            try:
                results = future.result()
                if results:
                    all_results.extend(results)
                else:
                    failed.append(kw)
                log.info(f"[{completed}/{total}] {kw} done")
            except Exception as e:
                log.error(f"[{completed}/{total}] {kw} error: {e}")
                failed.append(kw)

            # Small delay between completions to avoid proxy flooding
            time.sleep(random.uniform(1, 3))

    # ── SCORING ────────────────────────────────────────────────────────────────

    if not all_results:
        log.warning("No results collected. Check proxies and rate limits.")
        return None

    all_results = score_results(all_results)
    all_results.sort(key=lambda x: -x["score"])

    # ── OUTPUT ─────────────────────────────────────────────────────────────────

    # CSV
    csv_path = os.path.join(OUTPUT_DIR, f"trending_products_{date_str}.csv")
    fieldnames = [
        "query", "score", "trend_velocity", "search_volume",
        "product_viability", "specificity", "trend_classification",
        "trend_value", "trend_type", "source_keyword", "category", "scraped_at",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_results)

    # JSON
    json_path = os.path.join(OUTPUT_DIR, f"trending_products_{date_str}.json")
    with open(json_path, "w") as f:
        json.dump({
            "scraped_at": timestamp,
            "geo": geo,
            "timeframes": TIMEFRAMES,
            "total_results": len(all_results),
            "failed_keywords": failed,
            "products": all_results,
        }, f, indent=2)

    # Human-readable top picks
    picks_path = os.path.join(OUTPUT_DIR, f"top_picks_{date_str}.txt")
    top_picks = [r for r in all_results if r["score"] >= 0.5][:25]
    with open(picks_path, "w") as f:
        f.write(f"TOP PRODUCT PICKS — {date_str}\n")
        f.write(f"Scanned {len(keywords)} keywords, found {len(all_results)} trending queries\n")
        f.write(f"Geo: {geo} | Timeframes: {', '.join(TIMEFRAMES)}\n")
        f.write("=" * 70 + "\n\n")
        for i, r in enumerate(top_picks, 1):
            f.write(
                f"{i:2}. {r['query']:<40} score:{r['score']:.3f} "
                f"vel:{r['trend_velocity']:.2f} [{r['trend_classification']}] "
                f"[{r['category']}]\n"
            )
        if failed:
            f.write(f"\nFailed keywords ({len(failed)}): {', '.join(failed)}\n")

    # Summary
    log.info("=" * 50)
    log.info(f"Done. {len(all_results)} results collected.")
    log.info(f"CSV:  {csv_path}")
    log.info(f"JSON: {json_path}")
    log.info(f"Picks: {picks_path}")

    if top_picks:
        log.info(f"\nTOP 10 PRODUCTS:")
        log.info("-" * 60)
        for r in top_picks[:10]:
            log.info(
                f"  {r['query']:<38} score:{r['score']:.3f} "
                f"vel:{r['trend_velocity']:.2f} [{r['trend_classification']}]"
            )

    if failed:
        log.warning(f"\n{len(failed)} keywords failed: {', '.join(failed[:10])}")

    log.info(f"\nActive proxies remaining: {pool.active_count}/{len(pool.proxies)}")

    return csv_path


# ── CLI ────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Trends Product Research v2")
    parser.add_argument("--quick", action="store_true", help="Top 20 keywords only")
    parser.add_argument("--category", type=str, help="Single category to scan")
    parser.add_argument("--seed", type=str, help="Seed keyword for expansion mode")
    parser.add_argument("--geo", type=str, default=DEFAULT_GEO, help="Geography (default: US)")
    parser.add_argument("--timeframe", type=str, help="Override default timeframe")
    args = parser.parse_args()

    # Override timeframes if specified
    if args.timeframe:
        TIMEFRAMES = [args.timeframe]
        log.info(f"Timeframe override: {args.timeframe}")

    if args.seed:
        pool = ProxyPool(PROXY_FILE)
        cache = TrendsCache()
        run_seed_mode(args.seed, pool, args.geo, cache)
    elif args.category:
        if args.category in CATEGORIES:
            log.info(f"Running single category: {args.category}")
            run_scraper(keywords=CATEGORIES[args.category], geo=args.geo)
        else:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)
    elif args.quick:
        run_scraper(quick=True, geo=args.geo)
    else:
        run_scraper(geo=args.geo)
