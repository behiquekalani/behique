#!/usr/bin/env python3
"""
Market Research Tool — Business Blueprint Niche
Tracks Google Trends, Gumroad trending, and identifies market gaps.

Usage:
    python3 market_research.py --full       # Run everything
    python3 market_research.py --trends     # Google Trends only
    python3 market_research.py --gaps       # Gap analysis only

Cron (weekly Monday 9am, after competitor tracker):
    0 9 * * 1 cd /Users/kalani/behique/bios/intelligence && python3 market_research.py --full
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path
from urllib.parse import quote

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

TREND_KEYWORDS = [
    "business blueprint",
    "business template",
    "solopreneur system",
    "notion business template",
    "business in a box",
    "solopreneur toolkit",
]

GUMROAD_TRENDING_CATEGORIES = [
    "business",
    "design",
    "software-development",
]

# Known competitor product types (for gap analysis)
KNOWN_COMPETITOR_PRODUCTS = {
    "mrnotion": [
        "notion business template",
        "business blueprint notion",
        "startup template",
    ],
    "common_gumroad": [
        "business plan template",
        "financial model spreadsheet",
        "pitch deck template",
        "social media planner",
        "content calendar",
        "client onboarding template",
        "invoice template",
        "project management template",
    ],
}

# Product ideas we could fill gaps with
POTENTIAL_PRODUCTS = [
    {"name": "AI-Powered Business Blueprint", "category": "automation", "exists_in_market": False},
    {"name": "Solopreneur Operating System", "category": "system", "exists_in_market": False},
    {"name": "Revenue Tracker + Forecast", "category": "finance", "exists_in_market": False},
    {"name": "Customer Research Toolkit", "category": "research", "exists_in_market": False},
    {"name": "Launch Checklist System", "category": "operations", "exists_in_market": False},
    {"name": "Freelancer-to-Agency Blueprint", "category": "scaling", "exists_in_market": False},
    {"name": "Niche Validation Toolkit", "category": "research", "exists_in_market": False},
    {"name": "Automation Playbook (n8n/Zapier)", "category": "automation", "exists_in_market": False},
    {"name": "Weekly CEO Dashboard", "category": "analytics", "exists_in_market": False},
    {"name": "Side Hustle Starter Pack", "category": "beginner", "exists_in_market": False},
]


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


# ---------------------------------------------------------------------------
# Google Trends (public page scraping, no API)
# ---------------------------------------------------------------------------

def search_google_trends(session: requests.Session, keywords: list[str] = None) -> dict:
    """
    Scrape Google Trends explore page for interest data.
    Uses the public embed/explore URLs — no API key needed.
    """
    if keywords is None:
        keywords = TREND_KEYWORDS

    print("[*] Checking Google Trends...")
    results = {
        "keywords": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "method": "public_page",
    }

    for keyword in keywords:
        print(f"  [*] Checking '{keyword}'...")
        trend_data = _check_trend_keyword(session, keyword)
        results["keywords"][keyword] = trend_data

    # Compare keywords via multi-keyword URL
    if len(keywords) >= 2:
        results["comparison"] = _compare_trends(session, keywords[:5])  # max 5

    return results


def _check_trend_keyword(session: requests.Session, keyword: str) -> dict:
    """Check a single keyword on Google Trends."""
    data = {
        "keyword": keyword,
        "trend": "unknown",
        "related_queries": [],
        "related_topics": [],
    }

    # Google Trends explore page
    url = f"https://trends.google.com/trends/explore?q={quote(keyword)}&geo=US"
    resp = _safe_get(session, url)

    if resp is None:
        data["error"] = "Could not fetch Google Trends page"
        return data

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try to extract trend direction from page content
    page_text = soup.get_text()

    # Look for "Interest over time" data in embedded scripts
    for script in soup.find_all("script"):
        script_text = script.string or ""
        if "comparisonItem" in script_text or "interest" in script_text.lower():
            # Try to extract trend data from embedded JSON
            try:
                # Look for trend values
                nums = re.findall(r'"value"\s*:\s*(\d+)', script_text)
                if nums:
                    values = [int(n) for n in nums[-12:]]  # last 12 data points
                    if values:
                        recent_avg = sum(values[-3:]) / 3
                        older_avg = sum(values[:3]) / 3
                        if older_avg > 0:
                            change = ((recent_avg - older_avg) / older_avg) * 100
                            data["trend"] = "rising" if change > 10 else "declining" if change < -10 else "stable"
                            data["trend_change_pct"] = round(change, 1)
                        data["recent_values"] = values
            except (ValueError, ZeroDivisionError):
                pass

    # Also try the suggestions endpoint for related queries
    suggest_url = f"https://trends.google.com/trends/api/autocomplete/{quote(keyword)}?hl=en-US"
    suggest_resp = _safe_get(session, suggest_url)
    if suggest_resp:
        try:
            # Google prepends ")]}'" to JSON responses
            text = suggest_resp.text
            if text.startswith(")]}'"):
                text = text[5:]
            suggest_data = json.loads(text)
            if "default" in suggest_data and "topics" in suggest_data["default"]:
                for topic in suggest_data["default"]["topics"][:5]:
                    data["related_topics"].append({
                        "title": topic.get("title", ""),
                        "type": topic.get("type", ""),
                    })
        except (json.JSONDecodeError, KeyError):
            pass

    return data


def _compare_trends(session: requests.Session, keywords: list[str]) -> dict:
    """Compare multiple keywords on Google Trends."""
    comparison = {
        "keywords": keywords,
        "relative_interest": {},
    }

    # Build multi-keyword URL
    q_param = ",".join(quote(k) for k in keywords)
    url = f"https://trends.google.com/trends/explore?q={q_param}&geo=US"
    resp = _safe_get(session, url)

    if resp is None:
        comparison["error"] = "Could not fetch comparison page"
        return comparison

    # The actual trend data is loaded via JS, so we note this limitation
    comparison["note"] = (
        "Google Trends data is JS-rendered. For accurate comparison, "
        "use pytrends library or check manually at the URL."
    )
    comparison["manual_url"] = url

    return comparison


# ---------------------------------------------------------------------------
# Gumroad Trending
# ---------------------------------------------------------------------------

def check_gumroad_trending(session: requests.Session, categories: list[str] = None) -> dict:
    """Check trending products on Gumroad discover page."""
    if categories is None:
        categories = GUMROAD_TRENDING_CATEGORIES

    print("[*] Checking Gumroad trending products...")
    results = {
        "scraped_at": datetime.utcnow().isoformat(),
        "categories": {},
    }

    for category in categories:
        print(f"  [*] Category: {category}")
        products = _scrape_gumroad_category(session, category)
        results["categories"][category] = products

    return results


def _scrape_gumroad_category(session: requests.Session, category: str) -> list[dict]:
    """Scrape a Gumroad discover category page."""
    products = []
    url = f"https://gumroad.com/discover?query=&sort=highest_rated&category={category}"
    resp = _safe_get(session, url)

    if resp is None:
        return products

    soup = BeautifulSoup(resp.text, "html.parser")

    # Parse product cards
    cards = soup.find_all("article") or soup.find_all("div", class_=re.compile(r"product"))
    for card in cards[:15]:
        product = {}

        title_el = card.find(["h2", "h3", "h4"])
        if title_el:
            product["title"] = title_el.get_text(strip=True)

        price_text = card.find(string=re.compile(r"\$\d+"))
        if price_text:
            m = re.search(r"\$([\d,.]+)", price_text)
            if m:
                try:
                    product["price"] = float(m.group(1).replace(",", ""))
                except ValueError:
                    pass

        link = card.find("a", href=True)
        if link:
            product["url"] = link["href"]

        # Creator name
        creator = card.find(string=re.compile(r"by\s+"))
        if creator:
            product["creator"] = creator.strip()

        if product.get("title"):
            product["category"] = category
            products.append(product)

    return products


# ---------------------------------------------------------------------------
# Gap Analysis
# ---------------------------------------------------------------------------

def identify_gaps(gumroad_trending: dict, trends_data: dict) -> dict:
    """
    Identify what competitors DON'T sell that we could.
    Cross-reference trending topics with existing products.
    """
    print("[*] Running gap analysis...")

    # Collect all competitor product titles
    competitor_titles = []
    for cat_products in gumroad_trending.get("categories", {}).values():
        for p in cat_products:
            if p.get("title"):
                competitor_titles.append(p["title"].lower())

    # Also add known competitor products
    for comp_products in KNOWN_COMPETITOR_PRODUCTS.values():
        competitor_titles.extend([p.lower() for p in comp_products])

    # Check each potential product against market
    gaps = []
    saturated = []

    for product in POTENTIAL_PRODUCTS:
        name_lower = product["name"].lower()
        keywords = name_lower.split()

        # Check if similar products exist
        match_count = 0
        matching_products = []
        for title in competitor_titles:
            shared_words = sum(1 for kw in keywords if kw in title and len(kw) > 3)
            if shared_words >= 2:
                match_count += 1
                matching_products.append(title)

        product_analysis = {
            "product_idea": product["name"],
            "category": product["category"],
            "similar_in_market": match_count,
            "matching_products": matching_products[:3],
        }

        if match_count == 0:
            product_analysis["opportunity"] = "HIGH — No direct competitors found"
            gaps.append(product_analysis)
        elif match_count <= 2:
            product_analysis["opportunity"] = "MEDIUM — Few competitors, room to differentiate"
            gaps.append(product_analysis)
        else:
            product_analysis["opportunity"] = "LOW — Saturated, needs strong differentiation"
            saturated.append(product_analysis)

    # Check trending keywords for additional gap opportunities
    trending_gaps = []
    for keyword, trend_info in trends_data.get("keywords", {}).items():
        if trend_info.get("trend") == "rising":
            # Is anyone selling products for this rising trend?
            has_product = any(
                keyword.lower() in title for title in competitor_titles
            )
            if not has_product:
                trending_gaps.append({
                    "keyword": keyword,
                    "trend": "rising",
                    "trend_change_pct": trend_info.get("trend_change_pct"),
                    "opportunity": "Rising demand with no matching products in market",
                })

    return {
        "gaps": gaps,
        "saturated": saturated,
        "trending_gaps": trending_gaps,
        "total_gap_opportunities": len(gaps) + len(trending_gaps),
        "analyzed_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def generate_report(
    trends_data: dict,
    gumroad_trending: dict,
    gap_analysis: dict,
) -> dict:
    """Build the full market research report."""
    print("[*] Generating market research report...")

    report = {
        "report_type": "market_research",
        "generated_at": datetime.utcnow().isoformat(),
        "date": date.today().isoformat(),
        "niche": "business blueprint / solopreneur system",

        "google_trends": trends_data,
        "gumroad_trending": gumroad_trending,
        "gap_analysis": gap_analysis,

        "action_items": _generate_action_items(trends_data, gap_analysis),
    }

    # Save
    filename = f"market-research-{date.today().isoformat()}.json"
    filepath = REPORTS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"[+] Report saved to {filepath}")

    return report


def _generate_action_items(trends_data: dict, gap_analysis: dict) -> list[str]:
    """Auto-generate actionable next steps from research data."""
    actions = []

    # High-opportunity gaps
    high_gaps = [g for g in gap_analysis.get("gaps", []) if "HIGH" in g.get("opportunity", "")]
    if high_gaps:
        names = ", ".join(g["product_idea"] for g in high_gaps[:3])
        actions.append(f"PRIORITY: Build products for these uncontested niches: {names}")

    # Rising trends
    rising = [k for k, v in trends_data.get("keywords", {}).items() if v.get("trend") == "rising"]
    if rising:
        actions.append(f"TRENDING UP: Optimize content around: {', '.join(rising)}")

    # Declining trends
    declining = [k for k, v in trends_data.get("keywords", {}).items() if v.get("trend") == "declining"]
    if declining:
        actions.append(f"DECLINING: Reduce focus on: {', '.join(declining)}")

    # Trending gaps
    tgaps = gap_analysis.get("trending_gaps", [])
    if tgaps:
        actions.append(f"EMERGING: {len(tgaps)} rising keywords with no products — first mover advantage available")

    if not actions:
        actions.append("Run with proxy enabled for better data quality, then re-analyze")
        actions.append("Manually check Google Trends for keyword comparison: https://trends.google.com/trends/explore?q=business+blueprint,business+template")

    return actions


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Market Research — Business Blueprint Niche")
    parser.add_argument("--full", action="store_true", help="Run full research")
    parser.add_argument("--trends", action="store_true", help="Google Trends only")
    parser.add_argument("--gumroad", action="store_true", help="Gumroad trending only")
    parser.add_argument("--gaps", action="store_true", help="Gap analysis only (needs cached data)")
    args = parser.parse_args()

    if not any([args.full, args.trends, args.gumroad, args.gaps]):
        parser.print_help()
        sys.exit(1)

    session = _session()

    trends_data = {}
    gumroad_data = {}

    if args.full or args.trends:
        trends_data = search_google_trends(session)

    if args.full or args.gumroad:
        gumroad_data = check_gumroad_trending(session)

    if args.full or args.gaps:
        if not trends_data or not gumroad_data:
            # Load cached
            raw_file = REPORTS_DIR / f"raw-market-{date.today().isoformat()}.json"
            if raw_file.exists():
                with open(raw_file) as f:
                    cached = json.load(f)
                trends_data = trends_data or cached.get("trends", {})
                gumroad_data = gumroad_data or cached.get("gumroad", {})

    # Cache raw data
    if trends_data or gumroad_data:
        raw_file = REPORTS_DIR / f"raw-market-{date.today().isoformat()}.json"
        with open(raw_file, "w") as f:
            json.dump({
                "trends": trends_data,
                "gumroad": gumroad_data,
                "scraped_at": datetime.utcnow().isoformat(),
            }, f, indent=2, default=str)

    # Gap analysis
    gap_analysis = identify_gaps(gumroad_data, trends_data)

    # Generate report
    report = generate_report(trends_data, gumroad_data, gap_analysis)

    # Print summary
    print("\n" + "=" * 60)
    print("  MARKET RESEARCH REPORT")
    print(f"  {date.today().isoformat()}")
    print("=" * 60)

    print(f"\nKeywords tracked: {len(trends_data.get('keywords', {}))}")
    print(f"Gap opportunities found: {gap_analysis['total_gap_opportunities']}")

    print("\nAction items:")
    for i, action in enumerate(report["action_items"], 1):
        print(f"  {i}. {action}")

    if gap_analysis.get("gaps"):
        print("\nTop gaps (no/few competitors):")
        for g in gap_analysis["gaps"][:5]:
            print(f"  - {g['product_idea']}: {g['opportunity']}")
    print()


if __name__ == "__main__":
    main()
