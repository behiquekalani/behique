"""
eBay Pricing Engine — Recommends listing price and selling strategy.

Takes comp data from research + seller costs → outputs price, strategy, and full breakdown.
Never prices below breakeven. Accounts for eBay fees, shipping from PR, and desired margin.
"""

from dataclasses import dataclass, field
from typing import Optional
from core.types import ResearchResult
from core.shipping import estimate_shipping, ShippingEstimate


# eBay fee structure (2026)
# Final Value Fee: ~12.35% for most categories
# Payment processing: ~0.90%
# Total blended rate: ~13.25%
EBAY_FEE_RATE = 0.1325


@dataclass
class PricingRecommendation:
    list_price: float
    min_acceptable: float      # breakeven price
    strategy: str              # "fixed_price" or "auction"
    auction_start: float       # starting bid (only if auction)
    profit_estimate: float
    fee_estimate: float
    shipping: ShippingEstimate
    breakdown: dict = field(default_factory=dict)


def recommend_price(
    research: ResearchResult,
    item_cost: float,
    weight_oz: float,
    desired_margin_pct: float = 0.20,
    shipping_zone: int = 5,
    free_shipping: bool = True,
    fragile: bool = False,
) -> PricingRecommendation:
    """
    Calculate optimal listing price based on comp data and costs.

    Args:
        research: Sold listing research data
        item_cost: What the seller paid for the item
        weight_oz: Package weight in ounces
        desired_margin_pct: Target profit margin (0.20 = 20%)
        shipping_zone: USPS zone from PR (default 5)
        free_shipping: If True, bake shipping into price (eBay ranks free shipping higher)
        fragile: If True, adds padding weight to shipping estimate
    """
    # 1. Calculate shipping
    shipping = estimate_shipping(weight_oz, zone=shipping_zone, fragile=fragile)

    # 2. Calculate breakeven
    # breakeven × (1 - fee_rate) = item_cost + shipping_cost
    # breakeven = (item_cost + shipping_cost) / (1 - fee_rate)
    total_cost = item_cost + (shipping.cost if free_shipping else 0)
    breakeven = total_cost / (1 - EBAY_FEE_RATE)

    # 3. Calculate target price with margin
    target_with_margin = breakeven * (1 + desired_margin_pct)

    # 4. Compare against market
    market_price = research.median_sold_price if research.median_sold_price > 0 else research.avg_sold_price

    # 5. Choose listing price — never below breakeven, aim for market rate
    list_price = max(target_with_margin, market_price * 0.95)  # Slightly under market to sell faster
    list_price = max(list_price, breakeven * 1.05)  # Always at least 5% above breakeven

    # 6. Determine strategy
    strategy = _decide_strategy(research, market_price)

    # 7. Calculate auction start (if applicable)
    auction_start = round(breakeven * 1.10, 2) if strategy == "auction" else 0.0

    # 8. Calculate estimates
    fee_estimate = round(list_price * EBAY_FEE_RATE, 2)
    shipping_cost_to_seller = shipping.cost if free_shipping else 0
    profit_estimate = round(list_price - fee_estimate - item_cost - shipping_cost_to_seller, 2)

    # Round the final price to look clean
    list_price = _round_price(list_price)

    return PricingRecommendation(
        list_price=list_price,
        min_acceptable=round(breakeven, 2),
        strategy=strategy,
        auction_start=auction_start,
        profit_estimate=profit_estimate,
        fee_estimate=fee_estimate,
        shipping=shipping,
        breakdown={
            "item_cost": item_cost,
            "shipping_cost": shipping.cost,
            "shipping_service": shipping.service,
            "shipping_baked_in": free_shipping,
            "ebay_fee_rate": EBAY_FEE_RATE,
            "ebay_fee_amount": fee_estimate,
            "breakeven": round(breakeven, 2),
            "market_median": research.median_sold_price,
            "market_avg": research.avg_sold_price,
            "market_range": f"${research.min_sold_price:.2f} - ${research.max_sold_price:.2f}",
            "desired_margin": f"{desired_margin_pct * 100:.0f}%",
            "estimated_profit": profit_estimate,
            "sell_through_rate": research.sell_through_rate,
        },
    )


def _decide_strategy(research: ResearchResult, market_price: float) -> str:
    """
    Fixed price vs auction decision.

    Rules:
    - High sell-through (>60%) + decent price (>$20) → fixed price (demand is there)
    - Low sell-through (<40%) or cheap items (<$15) → auction (create competition)
    - High price variance → auction (market is uncertain)
    """
    sell_through = research.sell_through_rate or 0.5  # Default 50% if unknown

    # Price variance check
    price_range = research.max_sold_price - research.min_sold_price
    variance_ratio = price_range / market_price if market_price > 0 else 0

    if sell_through > 0.60 and market_price > 20:
        return "fixed_price"
    elif sell_through < 0.40 or market_price < 15:
        return "auction"
    elif variance_ratio > 0.80:
        return "auction"  # Market is uncertain
    else:
        return "fixed_price"  # Default to fixed for medium confidence


def _round_price(price: float) -> float:
    """Round price to look natural — .99 or .95 endings."""
    if price < 10:
        return round(price, 2)
    elif price < 50:
        # Round to nearest .99
        return float(int(price)) + 0.99
    else:
        # Round to nearest .95
        base = round(price / 5) * 5
        return base - 0.05
