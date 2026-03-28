#!/usr/bin/env python3
"""
Competitor Analysis Tool — Business Blueprint Niche
Tracks mrnotion.co (business-blueprints.com) and Gumroad sellers.

Usage:
    python3 competitor_tracker.py --full       # Run full analysis
    python3 competitor_tracker.py --scrape     # Scrape only
    python3 competitor_tracker.py --report     # Generate report from cached data

Cron (weekly Monday 8am):
    0 8 * * 1 cd /Users/kalani/behique/bios/intelligence && python3 competitor_tracker.py --full
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

PROXY_URL = os.environ.get("PROXY_URL")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

COMPETITORS = {
    "mrnotion": {
        "name": "MrNotion / business-blueprints.com",
        "website": "https://business-blueprints.com",
        "instagram": "mrnotion.co",
        "gumroad": None,  # uses own site
    },
}

GUMROAD_SEARCH_TERMS = [
    "business blueprint",
    "business template",
    "solopreneur template",
    "business system notion",
    "startup blueprint",
]

# Our pricing for comparison
OUR_PRICING = {
    "Business Blueprint": 29.00,
    "Starter Pack": 19.00,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    if PROXY_URL:
        s.proxies = {"http": PROXY_URL, "https": PROXY_URL}
    return s


def _safe_get(session: requests.Session, url: str, **kwargs) -> requests.Response | None:
    try:
        r = session.get(url, timeout=15, **kwargs)
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        print(f"  [WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def _extract_number(text: str) -> int | None:
    """Pull first number from text like '12.3K' or '1,234'."""
    if not text:
        return None
    text = text.strip().replace(",", "")
    # Handle K/M suffixes
    m = re.match(r"([\d.]+)\s*([KkMm])?", text)
    if not m:
        return None
    val = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    if suffix == "K":
        val *= 1_000
    elif suffix == "M":
        val *= 1_000_000
    return int(val)


# ---------------------------------------------------------------------------
# Scrapers
# ---------------------------------------------------------------------------

def scrape_mrnotion(session: requests.Session) -> dict:
    """
    Check mrnotion Instagram public profile for follower count
    and latest post engagement. Uses the public page (no API key needed).
    """
    print("[*] Scraping mrnotion Instagram profile...")
    result = {
        "source": "instagram",
        "handle": "mrnotion.co",
        "scraped_at": datetime.utcnow().isoformat(),
        "followers": None,
        "posts_count": None,
        "following": None,
        "bio": None,
        "recent_posts": [],
        "error": None,
    }

    # Instagram public pages are heavily JS-rendered.
    # We try the public page first; if blocked we note it.
    url = "https://www.instagram.com/mrnotion.co/"
    resp = _safe_get(session, url)

    if resp is None:
        result["error"] = "Could not fetch Instagram page (likely blocked without login)"
        # Fallback: try scraping their website instead
        print("  [*] Falling back to business-blueprints.com...")
        website_data = _scrape_competitor_website(session)
        result["website_fallback"] = website_data
        return result

    # Try to extract from meta tags or JSON in page source
    soup = BeautifulSoup(resp.text, "html.parser")

    # Meta description often has follower count
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        content = meta_desc.get("content", "")
        result["bio_meta"] = content
        # Pattern: "1,234 Followers, 567 Following, 89 Posts"
        nums = re.findall(r"([\d,.]+[KkMm]?)\s+(Followers|Following|Posts)", content)
        for val, label in nums:
            n = _extract_number(val)
            if label == "Followers":
                result["followers"] = n
            elif label == "Following":
                result["following"] = n
            elif label == "Posts":
                result["posts_count"] = n

    # Try embedded JSON (shared_data)
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                result["structured_data"] = data
        except (json.JSONDecodeError, TypeError):
            pass

    return result


def _scrape_competitor_website(session: requests.Session) -> dict:
    """Scrape business-blueprints.com for product info and pricing."""
    print("  [*] Scraping business-blueprints.com...")
    data = {
        "url": "https://business-blueprints.com",
        "products": [],
        "error": None,
    }

    resp = _safe_get(session, "https://business-blueprints.com")
    if resp is None:
        data["error"] = "Could not fetch website"
        return data

    soup = BeautifulSoup(resp.text, "html.parser")
    data["title"] = soup.title.string if soup.title else None

    # Look for price elements
    price_els = soup.find_all(string=re.compile(r"\$\d+"))
    prices_found = []
    for el in price_els:
        m = re.findall(r"\$[\d,.]+", el)
        prices_found.extend(m)
    data["prices_found"] = list(set(prices_found))

    # Look for product cards / sections
    for tag in ["h2", "h3", "h4"]:
        headings = soup.find_all(tag)
        for h in headings:
            text = h.get_text(strip=True)
            if any(kw in text.lower() for kw in ["blueprint", "template", "pack", "bundle", "system"]):
                data["products"].append(text)

    # Get all links for deeper analysis
    links = [a.get("href", "") for a in soup.find_all("a", href=True)]
    data["product_links"] = [l for l in links if any(
        kw in l.lower() for kw in ["product", "shop", "buy", "checkout", "gumroad"]
    )]

    return data


def scrape_gumroad_category(session: requests.Session, search_terms: list[str] = None) -> list[dict]:
    """
    Search Gumroad discover page for business blueprint/template products.
    Returns top results with prices and review counts.
    """
    if search_terms is None:
        search_terms = GUMROAD_SEARCH_TERMS

    all_products = []
    seen_urls = set()

    for term in search_terms:
        print(f"[*] Searching Gumroad for '{term}'...")
        url = "https://gumroad.com/discover"
        params = {"query": term}
        resp = _safe_get(session, url, params=params)
        if resp is None:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Gumroad product cards
        cards = soup.find_all("article") or soup.find_all("div", class_=re.compile(r"product"))
        if not cards:
            # Try alternative selectors
            cards = soup.find_all("a", href=re.compile(r"gumroad\.com/l/"))

        for card in cards:
            product = _parse_gumroad_card(card, term)
            if product and product.get("url") not in seen_urls:
                seen_urls.add(product.get("url"))
                all_products.append(product)

        # Also try the search API endpoint
        api_products = _try_gumroad_api_search(session, term)
        for p in api_products:
            if p.get("url") not in seen_urls:
                seen_urls.add(p.get("url"))
                all_products.append(p)

    # Sort by review count (descending), take top 20
    all_products.sort(key=lambda x: x.get("reviews", 0) or 0, reverse=True)
    return all_products[:20]


def _parse_gumroad_card(card, search_term: str) -> dict | None:
    """Parse a Gumroad product card element."""
    product = {"search_term": search_term}

    # Title
    title_el = card.find(["h2", "h3", "h4", "span"])
    if title_el:
        product["title"] = title_el.get_text(strip=True)

    # URL
    link = card.find("a", href=True) if card.name != "a" else card
    if link:
        product["url"] = link.get("href", "")

    # Price
    price_el = card.find(string=re.compile(r"\$\d+"))
    if price_el:
        m = re.search(r"\$([\d,.]+)", price_el)
        if m:
            try:
                product["price"] = float(m.group(1).replace(",", ""))
            except ValueError:
                product["price"] = None

    # Reviews / ratings
    rating_el = card.find(string=re.compile(r"\d+\s*rating|review|\d+\s*\("))
    if rating_el:
        m = re.search(r"(\d+)", rating_el)
        if m:
            product["reviews"] = int(m.group(1))

    # Star rating
    stars_el = card.find(string=re.compile(r"[★⭐]|[\d.]+/5"))
    if stars_el:
        m = re.search(r"([\d.]+)", stars_el)
        if m:
            product["rating"] = float(m.group(1))

    if not product.get("title") and not product.get("url"):
        return None

    return product


def _try_gumroad_api_search(session: requests.Session, query: str) -> list[dict]:
    """Try Gumroad's internal search API for more structured results."""
    products = []
    url = f"https://gumroad.com/discover?query={requests.utils.quote(query)}"

    # Gumroad sometimes has JSON embedded in the page
    resp = _safe_get(session, url, headers={"Accept": "text/html"})
    if resp is None:
        return products

    # Look for JSON data in script tags
    soup = BeautifulSoup(resp.text, "html.parser")
    for script in soup.find_all("script"):
        if script.string and "products" in (script.string or ""):
            try:
                # Try to find JSON objects with product data
                matches = re.findall(r'\{[^{}]*"name"\s*:\s*"[^"]*"[^{}]*"price"\s*:\s*\d+[^{}]*\}', script.string)
                for match in matches:
                    try:
                        data = json.loads(match)
                        products.append({
                            "title": data.get("name"),
                            "price": data.get("price", 0) / 100 if data.get("price") else None,
                            "url": data.get("url", ""),
                            "reviews": data.get("reviews_count", 0),
                            "rating": data.get("average_rating"),
                            "search_term": query,
                            "source": "api",
                        })
                    except (json.JSONDecodeError, TypeError):
                        continue
            except Exception:
                continue

    return products


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_pricing(gumroad_products: list[dict], competitor_website: dict | None = None) -> dict:
    """Compare our pricing against competitors."""
    print("[*] Analyzing pricing...")

    competitor_prices = []
    for p in gumroad_products:
        if p.get("price") is not None and p["price"] > 0:
            competitor_prices.append(p["price"])

    if competitor_website and competitor_website.get("prices_found"):
        for ps in competitor_website["prices_found"]:
            try:
                competitor_prices.append(float(ps.replace("$", "").replace(",", "")))
            except ValueError:
                pass

    analysis = {
        "our_products": OUR_PRICING,
        "competitor_count": len(gumroad_products),
        "competitor_prices": {
            "min": min(competitor_prices) if competitor_prices else None,
            "max": max(competitor_prices) if competitor_prices else None,
            "avg": round(sum(competitor_prices) / len(competitor_prices), 2) if competitor_prices else None,
            "median": sorted(competitor_prices)[len(competitor_prices) // 2] if competitor_prices else None,
            "all": sorted(competitor_prices),
        },
        "price_position": {},
    }

    # Where do we sit in the market?
    for product_name, our_price in OUR_PRICING.items():
        if competitor_prices:
            cheaper = sum(1 for p in competitor_prices if p < our_price)
            pricier = sum(1 for p in competitor_prices if p > our_price)
            same = sum(1 for p in competitor_prices if p == our_price)
            total = len(competitor_prices)
            analysis["price_position"][product_name] = {
                "our_price": our_price,
                "cheaper_competitors": cheaper,
                "pricier_competitors": pricier,
                "same_price": same,
                "percentile": round((cheaper / total) * 100, 1) if total else None,
                "recommendation": _pricing_recommendation(our_price, competitor_prices),
            }

    return analysis


def _pricing_recommendation(our_price: float, competitor_prices: list[float]) -> str:
    """Generate pricing recommendation based on market data."""
    if not competitor_prices:
        return "Insufficient data for recommendation"

    avg = sum(competitor_prices) / len(competitor_prices)
    median = sorted(competitor_prices)[len(competitor_prices) // 2]

    if our_price < avg * 0.7:
        return f"UNDERPRICED — You're at ${our_price}, market avg is ${avg:.2f}. Consider raising price."
    elif our_price > avg * 1.5:
        return f"PREMIUM — You're at ${our_price}, market avg is ${avg:.2f}. Ensure value justifies premium."
    elif our_price < median:
        return f"BELOW MEDIAN — At ${our_price} vs median ${median:.2f}. Room to increase if quality matches."
    else:
        return f"COMPETITIVE — At ${our_price} vs avg ${avg:.2f}. Good positioning."


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def generate_report(
    instagram_data: dict,
    gumroad_data: list[dict],
    pricing_analysis: dict,
) -> dict:
    """Build the full competitive intelligence report."""
    print("[*] Generating report...")

    report = {
        "report_type": "competitor_analysis",
        "generated_at": datetime.utcnow().isoformat(),
        "date": date.today().isoformat(),
        "niche": "business blueprint / business template",

        "competitors": {
            "mrnotion": instagram_data,
            "gumroad_top_sellers": gumroad_data,
        },

        "pricing_analysis": pricing_analysis,

        "top_competitors_by_reviews": [
            {
                "title": p.get("title"),
                "price": p.get("price"),
                "reviews": p.get("reviews"),
                "url": p.get("url"),
            }
            for p in (gumroad_data or [])[:5]
        ],

        "insights": _generate_insights(instagram_data, gumroad_data, pricing_analysis),
    }

    # Save to file
    filename = f"competitor-{date.today().isoformat()}.json"
    filepath = REPORTS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"[+] Report saved to {filepath}")

    return report


def _generate_insights(instagram_data: dict, gumroad_data: list[dict], pricing: dict) -> list[str]:
    """Auto-generate key insights from the data."""
    insights = []

    # Instagram insights
    followers = instagram_data.get("followers")
    if followers:
        if followers > 50_000:
            insights.append(f"MrNotion has {followers:,} followers — strong social proof. Focus on differentiation, not follower count.")
        elif followers > 10_000:
            insights.append(f"MrNotion at {followers:,} followers — established but beatable with better content strategy.")
        else:
            insights.append(f"MrNotion at {followers:,} followers — relatively small. Opportunity to compete on reach.")

    # Pricing insights
    avg_price = pricing.get("competitor_prices", {}).get("avg")
    if avg_price:
        insights.append(f"Market average price is ${avg_price:.2f}")

    # Product count insights
    if gumroad_data:
        free_count = sum(1 for p in gumroad_data if (p.get("price") or 0) == 0)
        if free_count > 5:
            insights.append(f"{free_count} free competitors found — differentiate on depth and quality, not just existence.")

        high_review = [p for p in gumroad_data if (p.get("reviews") or 0) > 50]
        if high_review:
            insights.append(f"{len(high_review)} products have 50+ reviews — study their positioning for what works.")

    if not insights:
        insights.append("Limited data collected — consider running with proxy enabled for better results.")

    return insights


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Competitor Analysis — Business Blueprint Niche")
    parser.add_argument("--full", action="store_true", help="Run full analysis (scrape + report)")
    parser.add_argument("--scrape", action="store_true", help="Scrape only, save raw data")
    parser.add_argument("--report", action="store_true", help="Generate report from latest cached data")
    args = parser.parse_args()

    if not any([args.full, args.scrape, args.report]):
        parser.print_help()
        sys.exit(1)

    session = _session()

    if args.full or args.scrape:
        # Scrape
        instagram_data = scrape_mrnotion(session)
        gumroad_data = scrape_gumroad_category(session)

        # Cache raw data
        raw_file = REPORTS_DIR / f"raw-competitor-{date.today().isoformat()}.json"
        with open(raw_file, "w") as f:
            json.dump({
                "instagram": instagram_data,
                "gumroad": gumroad_data,
                "scraped_at": datetime.utcnow().isoformat(),
            }, f, indent=2, default=str)
        print(f"[+] Raw data cached to {raw_file}")

    if args.full or args.report:
        if not (args.full or args.scrape):
            # Load cached data
            raw_file = REPORTS_DIR / f"raw-competitor-{date.today().isoformat()}.json"
            if not raw_file.exists():
                print("[!] No cached data found for today. Run with --scrape first.", file=sys.stderr)
                sys.exit(1)
            with open(raw_file) as f:
                cached = json.load(f)
            instagram_data = cached["instagram"]
            gumroad_data = cached["gumroad"]

        # Analyze and report
        website_data = instagram_data.get("website_fallback")
        pricing = analyze_pricing(gumroad_data, website_data)
        report = generate_report(instagram_data, gumroad_data, pricing)

        # Print summary to stdout
        print("\n" + "=" * 60)
        print("  COMPETITIVE INTELLIGENCE REPORT")
        print(f"  {date.today().isoformat()}")
        print("=" * 60)
        print(f"\nCompetitors tracked: {len(report['top_competitors_by_reviews'])}")
        print(f"Market avg price: ${pricing['competitor_prices']['avg'] or 'N/A'}")
        print(f"\nInsights:")
        for i, insight in enumerate(report["insights"], 1):
            print(f"  {i}. {insight}")
        print()


if __name__ == "__main__":
    main()
