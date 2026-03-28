#!/usr/bin/env python3
"""
trends_scraper_v2.py -- Google Trends Scraper v2 (Anti-Ban Rebuild)
Copyright 2026 Behike. All rights reserved.

Rebuilt from ~/Desktop/trends_automation.py with proper anti-ban measures:
- Proxy rotation from ~/Downloads/proxies.txt
- User-agent rotation (15 agents)
- Random delays (5-15s between requests)
- Exponential backoff on 429 errors
- No browser required (pytrends only)

Usage:
    python trends_scraper_v2.py
    python trends_scraper_v2.py --category Technology --geo US
    python trends_scraper_v2.py --category Health --timeframe "today 3-m"
    python trends_scraper_v2.py --suggest   # output for ebay-listing-assistant
    python trends_scraper_v2.py --digest     # human-readable markdown digest
    python trends_scraper_v2.py --proxy ~/custom/proxies.txt

Output:
    Ceiba/news/trends.json
    Ceiba/news/trends-digest.md (with --digest)
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from pytrends.request import TrendReq
except ImportError:
    print("ERROR: pytrends not installed. Run: pip install pytrends")
    sys.exit(1)


# ── PATHS ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
NEWS_DIR = BASE_DIR / "Ceiba" / "news"
NEWS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PROXY_FILE = Path.home() / "Downloads" / "proxies.txt"
TRENDS_JSON = NEWS_DIR / "trends.json"
TRENDS_DIGEST = NEWS_DIR / "trends-digest.md"


# ── CATEGORY SEEDS ───────────────────────────────────────────────────
# pytrends category IDs: https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories

CATEGORY_MAP = {
    "Technology":    {"id": 5,   "seeds": ["wireless earbuds", "smart watch", "portable charger", "phone case", "LED lights", "laptop stand", "USB-C hub", "power bank"]},
    "Business":      {"id": 12,  "seeds": ["dropshipping", "side hustle", "passive income", "print on demand", "online arbitrage", "reselling", "wholesale", "ecommerce"]},
    "Health":        {"id": 45,  "seeds": ["supplements", "fitness tracker", "massage gun", "yoga mat", "resistance bands", "protein powder", "posture corrector", "ice roller"]},
    "Home":          {"id": 11,  "seeds": ["air purifier", "humidifier", "desk organizer", "LED mirror", "storage bins", "throw pillow", "wall art", "plant pots"]},
    "Sports":        {"id": 20,  "seeds": ["golf accessories", "pickleball", "running shoes", "gym bag", "water bottle", "sports sunglasses", "compression socks", "jump rope"]},
    "Entertainment": {"id": 3,   "seeds": ["funko pop", "trading cards", "vinyl records", "board games", "collectibles", "action figures", "puzzles", "lego sets"]},
}


# ── USER AGENTS ──────────────────────────────────────────────────────

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
]


# ── EBAY CATEGORY MAPPING ───────────────────────────────────────────

EBAY_CATEGORY_HINTS = {
    "earbuds": "Consumer Electronics > Portable Audio",
    "headphones": "Consumer Electronics > Portable Audio",
    "phone": "Cell Phones & Accessories",
    "watch": "Jewelry & Watches > Watches",
    "smart watch": "Cell Phones & Accessories > Smart Watches",
    "charger": "Cell Phones & Accessories > Chargers",
    "led": "Home & Garden > Lamps, Lighting",
    "light": "Home & Garden > Lamps, Lighting",
    "laptop": "Computers/Tablets & Networking > Laptop Accessories",
    "usb": "Computers/Tablets & Networking > Cables & Adapters",
    "power bank": "Cell Phones & Accessories > Chargers",
    "supplement": "Health & Beauty > Vitamins & Supplements",
    "fitness": "Sporting Goods > Fitness Equipment",
    "massage": "Health & Beauty > Massage",
    "yoga": "Sporting Goods > Yoga & Pilates",
    "resistance": "Sporting Goods > Fitness Equipment",
    "protein": "Health & Beauty > Vitamins & Supplements",
    "posture": "Health & Beauty > Medical Devices",
    "purifier": "Home & Garden > Home Improvement > Heating, Cooling",
    "humidifier": "Home & Garden > Home Improvement > Heating, Cooling",
    "organizer": "Home & Garden > Storage & Organization",
    "mirror": "Home & Garden > Bath > Mirrors",
    "pillow": "Home & Garden > Bedding > Pillows",
    "art": "Home & Garden > Home Decor > Wall Art",
    "plant": "Home & Garden > Yard, Garden > Planters",
    "golf": "Sporting Goods > Golf",
    "pickleball": "Sporting Goods > Tennis & Racquet Sports",
    "shoe": "Clothing, Shoes & Accessories > Shoes",
    "running": "Sporting Goods > Running",
    "bottle": "Sporting Goods > Fitness Equipment",
    "sunglasses": "Clothing, Shoes & Accessories > Sunglasses",
    "funko": "Collectibles > Funko",
    "trading card": "Collectibles > Trading Cards",
    "vinyl": "Music > Records",
    "board game": "Toys & Hobbies > Games",
    "collectible": "Collectibles",
    "action figure": "Toys & Hobbies > Action Figures",
    "puzzle": "Toys & Hobbies > Puzzles",
    "lego": "Toys & Hobbies > Building Toys > LEGO",
    "card": "Collectibles > Trading Cards",
    "game": "Toys & Hobbies > Games",
    "toy": "Toys & Hobbies",
    "bag": "Clothing, Shoes & Accessories > Bags",
    "case": "Cell Phones & Accessories > Cases",
    "cable": "Computers/Tablets & Networking > Cables",
    "speaker": "Consumer Electronics > Portable Audio",
    "mouse": "Computers/Tablets & Networking > Keyboards & Mice",
    "skin care": "Health & Beauty > Skin Care",
    "beauty": "Health & Beauty",
    "kitchen": "Home & Garden > Kitchen",
}


# ── PROXY LOADING ────────────────────────────────────────────────────

def load_proxies(path: Path) -> list:
    """
    Load proxies from file. Supports formats:
    - ip:port
    - user:pass@ip:port
    - ip:port:user:pass (Webshare format)
    """
    proxies = []
    if not path.exists():
        return proxies

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(":")
            if len(parts) == 4:
                # Webshare format: ip:port:user:pass
                ip, port, user, pwd = parts
                proxies.append(f"http://{user}:{pwd}@{ip}:{port}")
            elif len(parts) == 2:
                # Simple format: ip:port
                ip, port = parts
                proxies.append(f"http://{ip}:{port}")
            elif "@" in line:
                # user:pass@ip:port format
                proxies.append(f"http://{line}")
            else:
                # Try as-is
                proxies.append(line if line.startswith("http") else f"http://{line}")

    return proxies


class ProxyRotator:
    """Round-robin proxy rotation with failure tracking."""

    def __init__(self, proxies: list):
        self.proxies = proxies
        self.index = 0
        self.failures = {}  # proxy -> failure count

    def next(self) -> dict | None:
        if not self.proxies:
            return None

        # Skip proxies with 3+ consecutive failures
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.index % len(self.proxies)]
            self.index += 1
            if self.failures.get(proxy, 0) < 3:
                return {"http": proxy, "https": proxy}
            attempts += 1

        # All proxies failed. Reset and try again.
        self.failures.clear()
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return {"http": proxy, "https": proxy}

    def mark_failure(self, proxy_dict: dict):
        if proxy_dict:
            key = proxy_dict.get("http", "")
            self.failures[key] = self.failures.get(key, 0) + 1

    def mark_success(self, proxy_dict: dict):
        if proxy_dict:
            key = proxy_dict.get("http", "")
            self.failures.pop(key, None)

    @property
    def count(self) -> int:
        return len(self.proxies)


# ── TREND FETCHER ────────────────────────────────────────────────────

class TrendFetcher:
    """Fetches Google Trends data with anti-ban measures."""

    def __init__(self, proxy_rotator: ProxyRotator, geo: str = "US", timeframe: str = "today 1-m"):
        self.proxy_rotator = proxy_rotator
        self.geo = geo
        self.timeframe = timeframe
        self.request_count = 0

    def _build_client(self) -> TrendReq:
        """Build a pytrends client with rotated proxy and user-agent."""
        ua = random.choice(USER_AGENTS)
        proxy = self.proxy_rotator.next()

        requests_args = {
            "headers": {"User-Agent": ua},
            "timeout": 30,
        }
        if proxy:
            requests_args["proxies"] = proxy

        client = TrendReq(
            hl="en-US",
            tz=360,
            retries=2,
            backoff_factor=0.5,
            requests_args=requests_args,
        )
        client._current_proxy = proxy  # stash for failure tracking
        return client

    def _delay(self):
        """Random delay between requests (5-15 seconds)."""
        wait = random.uniform(5, 15)
        # Every 5th request, add extra delay to look more human
        if self.request_count > 0 and self.request_count % 5 == 0:
            wait += random.uniform(10, 20)
        time.sleep(wait)

    def fetch_interest_over_time(self, keyword: str, max_retries: int = 4) -> dict | None:
        """Fetch interest over time for a keyword with exponential backoff."""
        for attempt in range(max_retries):
            self._delay()
            self.request_count += 1

            client = self._build_client()
            try:
                client.build_payload([keyword], timeframe=self.timeframe, geo=self.geo)
                df = client.interest_over_time()

                if df.empty:
                    return None

                self.proxy_rotator.mark_success(getattr(client, "_current_proxy", None))

                # Convert to serializable format
                values = df[keyword].tolist()
                dates = [d.strftime("%Y-%m-%d") for d in df.index]

                return {
                    "keyword": keyword,
                    "dates": dates,
                    "values": values,
                    "avg_interest": round(sum(values) / len(values), 2) if values else 0,
                    "peak_interest": max(values) if values else 0,
                    "current_interest": values[-1] if values else 0,
                    "trend_direction": _trend_direction(values),
                }

            except Exception as e:
                err = str(e).lower()
                self.proxy_rotator.mark_failure(getattr(client, "_current_proxy", None))

                if "429" in err or "too many" in err:
                    # Exponential backoff: 30s, 60s, 120s, 240s
                    backoff = (2 ** attempt) * 30
                    print(f"  [429] Rate limited on '{keyword}'. Backing off {backoff}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(backoff)
                    continue
                elif "connect" in err or "proxy" in err or "timeout" in err:
                    print(f"  [CONN] Connection error on '{keyword}'. Rotating proxy (attempt {attempt + 1}/{max_retries})")
                    time.sleep(random.uniform(3, 8))
                    continue
                else:
                    print(f"  [ERR] {keyword}: {e}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(random.uniform(5, 10))

        return None

    def fetch_related_queries(self, keyword: str) -> dict:
        """Fetch related and rising queries for a keyword."""
        self._delay()
        self.request_count += 1

        client = self._build_client()
        result = {"top": [], "rising": []}

        try:
            client.build_payload([keyword], timeframe=self.timeframe, geo=self.geo)
            related = client.related_queries()
            self.proxy_rotator.mark_success(getattr(client, "_current_proxy", None))

            if keyword in related:
                top_df = related[keyword].get("top")
                rising_df = related[keyword].get("rising")

                if top_df is not None and not top_df.empty:
                    result["top"] = top_df.head(10).to_dict("records")

                if rising_df is not None and not rising_df.empty:
                    result["rising"] = rising_df.head(10).to_dict("records")

        except Exception as e:
            self.proxy_rotator.mark_failure(getattr(client, "_current_proxy", None))
            print(f"  [WARN] Related queries failed for '{keyword}': {e}")

        return result


# ── SCORING ──────────────────────────────────────────────────────────

def _trend_direction(values: list) -> str:
    """Determine if a trend is rising, falling, or stable."""
    if len(values) < 4:
        return "unknown"

    recent = values[-4:]
    older = values[:4]
    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older)

    if older_avg == 0:
        return "rising" if recent_avg > 0 else "stable"

    change = (recent_avg - older_avg) / older_avg

    if change > 0.2:
        return "rising"
    elif change < -0.2:
        return "falling"
    return "stable"


def score_trend(interest_data: dict, related: dict) -> dict:
    """
    Score a trend for product potential.

    Factors:
    - Search volume (avg interest, 0-100 from Google)
    - Rising percentage (from rising queries)
    - Recency (how recent the peak is)
    - Related query count (market depth signal)
    """
    scores = {}

    # Volume score (0-40 points): avg interest normalized
    avg = interest_data.get("avg_interest", 0)
    scores["volume"] = min(40, round(avg * 0.4, 1))

    # Rising score (0-30 points): based on rising queries
    rising_queries = related.get("rising", [])
    rising_values = []
    for q in rising_queries:
        val = q.get("value", 0)
        if isinstance(val, str) and "+" in val:
            # "Breakout" or percentage strings
            rising_values.append(5000)
        elif isinstance(val, (int, float)):
            rising_values.append(val)

    if rising_values:
        max_rise = max(rising_values)
        # Cap at 5000% for scoring
        scores["rising"] = min(30, round((min(max_rise, 5000) / 5000) * 30, 1))
    else:
        scores["rising"] = 0

    # Recency score (0-20 points): is the trend peaking now?
    values = interest_data.get("values", [])
    if values:
        peak = max(values)
        peak_idx = values.index(peak)
        recency_ratio = peak_idx / max(len(values) - 1, 1)  # 1.0 = peak at end
        scores["recency"] = round(recency_ratio * 20, 1)
    else:
        scores["recency"] = 0

    # Depth score (0-10 points): related query count signals real market
    top_count = len(related.get("top", []))
    scores["depth"] = min(10, top_count)

    scores["total"] = round(sum(scores.values()), 1)
    return scores


def match_ebay_category(keyword: str) -> str:
    """Match a keyword to the most likely eBay category."""
    keyword_lower = keyword.lower()
    for hint_key, category in EBAY_CATEGORY_HINTS.items():
        if hint_key in keyword_lower:
            return category
    return "General"


# ── MAIN PIPELINE ────────────────────────────────────────────────────

def run_scan(categories: list, geo: str, timeframe: str, proxy_file: Path) -> list:
    """Run the full trend scan pipeline. Returns list of scored trends."""
    proxies = load_proxies(proxy_file)
    rotator = ProxyRotator(proxies)

    print(f"Trends Scraper v2 -- Anti-Ban Rebuild")
    print(f"  Proxies loaded: {rotator.count}")
    print(f"  Categories: {', '.join(categories)}")
    print(f"  Geo: {geo}, Timeframe: {timeframe}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if rotator.count == 0:
        print("  WARNING: No proxies loaded. Requests will use your IP directly.")
        print("  Add proxies to ~/Downloads/proxies.txt to avoid bans.")
        print()

    fetcher = TrendFetcher(rotator, geo=geo, timeframe=timeframe)
    results = []

    for cat_name in categories:
        cat = CATEGORY_MAP.get(cat_name)
        if not cat:
            print(f"  [SKIP] Unknown category: {cat_name}")
            continue

        print(f"--- {cat_name} (category ID: {cat['id']}) ---")

        for seed in cat["seeds"]:
            print(f"  Scanning: {seed}")

            interest = fetcher.fetch_interest_over_time(seed)
            if not interest:
                print(f"    No data. Skipping.")
                continue

            related = fetcher.fetch_related_queries(seed)
            scores = score_trend(interest, related)
            ebay_cat = match_ebay_category(seed)

            entry = {
                "keyword": seed,
                "category": cat_name,
                "geo": geo,
                "timeframe": timeframe,
                "interest": interest,
                "related_queries": related,
                "scores": scores,
                "ebay_category": ebay_cat,
                "scanned_at": datetime.now().isoformat(),
            }

            results.append(entry)
            print(f"    Score: {scores['total']}/100 | Direction: {interest['trend_direction']} | eBay: {ebay_cat}")

    # Sort by total score descending
    results.sort(key=lambda x: x["scores"]["total"], reverse=True)
    return results


def save_json(results: list, path: Path = TRENDS_JSON):
    """Save results to JSON."""
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_trends": len(results),
        "trends": results,
    }

    with open(path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nJSON saved: {path}")


def save_digest(results: list, path: Path = TRENDS_DIGEST):
    """Save human-readable markdown digest."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# Trends Digest",
        f"Generated: {now}",
        f"Total trends scanned: {len(results)}",
        "",
        "## Top Product Opportunities",
        "",
    ]

    for i, t in enumerate(results[:20], 1):
        keyword = t["keyword"]
        score = t["scores"]["total"]
        direction = t["interest"]["trend_direction"]
        ebay_cat = t["ebay_category"]
        avg = t["interest"]["avg_interest"]
        peak = t["interest"]["peak_interest"]

        lines.append(f"### {i}. {keyword}")
        lines.append(f"- **Score:** {score}/100")
        lines.append(f"- **Direction:** {direction}")
        lines.append(f"- **Avg Interest:** {avg} | **Peak:** {peak}")
        lines.append(f"- **eBay Category:** {ebay_cat}")

        # Rising queries
        rising = t.get("related_queries", {}).get("rising", [])
        if rising:
            lines.append(f"- **Rising queries:** {', '.join(q.get('query', '') for q in rising[:5])}")

        lines.append("")

    # Score breakdown legend
    lines.extend([
        "## Scoring Breakdown",
        "- Volume (0-40): Average search interest from Google Trends",
        "- Rising (0-30): Strength of rising related queries",
        "- Recency (0-20): How recently the trend peaked",
        "- Depth (0-10): Number of related queries (market depth)",
        "",
        "---",
        "*Generated by trends_scraper_v2.py. Copyright 2026 Behike.*",
    ])

    with open(path, "w") as f:
        f.write("\n".join(lines))

    print(f"Digest saved: {path}")


def format_for_quick_list(results: list) -> list:
    """
    Format top trends as product suggestions for ebay-listing-assistant/quick_list.py.

    Output: list of dicts with fields quick_list.py expects.
    Each entry includes the CLI command to run.
    """
    suggestions = []

    for t in results[:10]:
        keyword = t["keyword"]
        score = t["scores"]["total"]
        direction = t["interest"]["trend_direction"]
        ebay_cat = t["ebay_category"]
        rising = t.get("related_queries", {}).get("rising", [])

        # Build product name from keyword + top rising query
        product_name = keyword.title()
        if rising:
            top_rising = rising[0].get("query", "")
            if top_rising and top_rising.lower() != keyword.lower():
                product_name = top_rising.title()

        suggestion = {
            "product_name": product_name,
            "trend_keyword": keyword,
            "trend_score": score,
            "trend_direction": direction,
            "ebay_category": ebay_cat,
            "rising_queries": [q.get("query", "") for q in rising[:5]],
            "quick_list_cmd": f'python quick_list.py "{product_name}" --price 19.99 --condition New --weight 8',
        }
        suggestions.append(suggestion)

    return suggestions


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Google Trends Scraper v2 -- Anti-Ban Rebuild. Copyright 2026 Behike.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--category", "-c",
        nargs="+",
        default=list(CATEGORY_MAP.keys()),
        choices=list(CATEGORY_MAP.keys()),
        help="Categories to scan (default: all)",
    )
    parser.add_argument(
        "--geo", "-g",
        default="US",
        help="Geographic region (default: US)",
    )
    parser.add_argument(
        "--timeframe", "-t",
        default="today 1-m",
        help='Timeframe (default: "today 1-m"). Options: "today 1-m", "today 3-m", "today 12-m"',
    )
    parser.add_argument(
        "--proxy", "-p",
        type=Path,
        default=DEFAULT_PROXY_FILE,
        help=f"Path to proxy file (default: {DEFAULT_PROXY_FILE})",
    )
    parser.add_argument(
        "--digest", "-d",
        action="store_true",
        help="Generate human-readable markdown digest",
    )
    parser.add_argument(
        "--suggest", "-s",
        action="store_true",
        help="Output product suggestions formatted for ebay-listing-assistant/quick_list.py",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Custom output path for JSON (default: Ceiba/news/trends.json)",
    )

    args = parser.parse_args()

    # Run the scan
    results = run_scan(
        categories=args.category,
        geo=args.geo,
        timeframe=args.timeframe,
        proxy_file=args.proxy,
    )

    if not results:
        print("\nNo trend data collected. Check your proxies and try again.")
        sys.exit(1)

    # Save JSON
    json_path = args.output or TRENDS_JSON
    save_json(results, json_path)

    # Save digest if requested
    if args.digest:
        save_digest(results)

    # Output suggestions if requested
    if args.suggest:
        suggestions = format_for_quick_list(results)
        print("\n" + "=" * 60)
        print("PRODUCT SUGGESTIONS FOR EBAY LISTING ASSISTANT")
        print("=" * 60)
        for i, s in enumerate(suggestions, 1):
            print(f"\n{i}. {s['product_name']}")
            print(f"   Trend: {s['trend_keyword']} (score: {s['trend_score']}, {s['trend_direction']})")
            print(f"   eBay: {s['ebay_category']}")
            if s["rising_queries"]:
                print(f"   Rising: {', '.join(s['rising_queries'])}")
            print(f"   CMD: {s['quick_list_cmd']}")

        # Also save suggestions JSON
        suggest_path = NEWS_DIR / "trend-suggestions.json"
        with open(suggest_path, "w") as f:
            json.dump(suggestions, f, indent=2)
        print(f"\nSuggestions saved: {suggest_path}")

    # Summary
    print(f"\nScan complete. {len(results)} trends scored.")
    if results:
        top = results[0]
        print(f"Top trend: {top['keyword']} (score: {top['scores']['total']}/100, {top['interest']['trend_direction']})")


if __name__ == "__main__":
    main()
