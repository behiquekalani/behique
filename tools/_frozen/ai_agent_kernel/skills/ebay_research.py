"""
eBay Research Skill — Cobo executor module for eBay sold listing analysis.

Called by the Agent Kernel when a task with skill="ebay_research" is dispatched.
Takes a product query + optional condition, builds eBay search URL,
and returns structured comp data for the pricing engine.

Usage via Kernel:
    dispatcher.add_task(
        skill="skills.ebay_research",
        params={"query": "Funko Pop Vegeta", "condition": "New"},
        priority=TaskPriority.HIGH,
    )

Usage standalone:
    python3 -m skills.ebay_research --query "Hello Kitty Mug" --condition Used
"""

import sys
import os
import json
import statistics
from urllib.parse import quote_plus
from datetime import datetime, timezone


# ============ eBay URL Builder ============
EBAY_BASE = "https://www.ebay.com/sch/i.html"

CONDITION_MAP = {
    "new": "1000",
    "used": "3000",
    "refurbished": "2000",
    "for parts": "7000",
}


def build_sold_url(query: str, condition: str = "") -> str:
    """Build eBay sold listings search URL."""
    encoded = quote_plus(query)
    params = f"_nkw={encoded}&_sop=13&LH_Complete=1&LH_Sold=1"
    cond_code = CONDITION_MAP.get(condition.lower(), "")
    if cond_code:
        params += f"&LH_ItemCondition={cond_code}"
    return f"{EBAY_BASE}?{params}"


def build_active_url(query: str) -> str:
    """Build URL for currently active listings (competition check)."""
    encoded = quote_plus(query)
    return f"{EBAY_BASE}?_nkw={encoded}&_sop=12"


# ============ Comp Data Analysis ============
def analyze_comp_data(sold_prices: list, active_count: int = 0,
                      shipping_costs: list = None) -> dict:
    """
    Analyze sold listing price data and return structured comp analysis.

    Args:
        sold_prices: List of sold prices as floats
        active_count: Number of currently active competing listings
        shipping_costs: List of shipping costs from sold listings

    Returns:
        Dict with pricing analysis, sell-through estimate, and strategy recommendation
    """
    if not sold_prices:
        return {"error": "No sold prices provided", "recommendation": "insufficient_data"}

    prices = sorted(sold_prices)
    avg_ship = statistics.mean(shipping_costs) if shipping_costs else 0.0

    # Price stats
    median = statistics.median(prices)
    mean = statistics.mean(prices)
    stdev = statistics.stdev(prices) if len(prices) > 1 else 0.0
    price_variance = stdev / mean if mean > 0 else 0

    # Sell-through rate estimate (sold in 90 days / total)
    sell_through = None
    if active_count > 0:
        sell_through = round(len(sold_prices) / (len(sold_prices) + active_count), 3)

    # Strategy recommendation
    strategy = "fixed_price"
    if sell_through is not None:
        if sell_through < 0.40 or median < 15:
            strategy = "auction"
        elif price_variance > 0.35:
            strategy = "auction"  # High variance = uncertain market

    return {
        "sample_size": len(prices),
        "avg_price": round(mean, 2),
        "median_price": round(median, 2),
        "min_price": round(min(prices), 2),
        "max_price": round(max(prices), 2),
        "stdev": round(stdev, 2),
        "price_variance": round(price_variance, 3),
        "avg_shipping": round(avg_ship, 2),
        "sell_through_rate": sell_through,
        "active_listings": active_count,
        "recommended_strategy": strategy,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============ Skill Entry Point ============
def run(query: str = "", condition: str = "", sold_prices: str = "",
        active_count: str = "0", **kwargs) -> dict:
    """
    Main skill entry point — called by Cobo's SkillExecutor.

    If sold_prices is provided (comma-separated), runs analysis.
    Otherwise, returns search URLs for manual research.

    Args:
        query: Product search query (e.g. "Funko Pop Vegeta")
        condition: Item condition (New, Used, Refurbished, For Parts)
        sold_prices: Comma-separated sold prices (e.g. "15.99,12.50,18.00")
        active_count: Number of active competing listings
    """
    if not query:
        return {"error": "query parameter is required"}

    result = {
        "query": query,
        "condition": condition,
        "sold_url": build_sold_url(query, condition),
        "active_url": build_active_url(query),
    }

    # If prices are provided, run analysis
    if sold_prices:
        try:
            prices = [float(p.strip()) for p in sold_prices.split(",") if p.strip()]
            analysis = analyze_comp_data(
                sold_prices=prices,
                active_count=int(active_count),
            )
            result["analysis"] = analysis
        except (ValueError, TypeError) as e:
            result["analysis_error"] = str(e)
    else:
        result["note"] = "No sold_prices provided. Search the sold_url and re-run with prices for analysis."

    return result


# ============ CLI ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="eBay Research Skill")
    parser.add_argument("--query", required=True, help="Product search query")
    parser.add_argument("--condition", default="", help="Item condition")
    parser.add_argument("--prices", default="", help="Comma-separated sold prices")
    parser.add_argument("--active", type=int, default=0, help="Active listing count")
    args = parser.parse_args()

    result = run(
        query=args.query,
        condition=args.condition,
        sold_prices=args.prices,
        active_count=str(args.active),
    )
    print(json.dumps(result, indent=2))
