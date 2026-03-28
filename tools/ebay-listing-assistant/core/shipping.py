"""
USPS Shipping Calculator — Puerto Rico to Continental US
Hardcoded rate tables for V1. V2 can hit USPS Web Tools API for live rates.

Puerto Rico is a US territory — uses domestic USPS rates.
Default zone 5 covers most of CONUS from PR (zones 4-6 typical).
"""

from dataclasses import dataclass


@dataclass
class ShippingEstimate:
    service: str           # "USPS First Class" or "USPS Priority Mail"
    cost: float
    delivery_days: str     # "3-5" etc.
    weight_oz: float
    zone: int


# USPS First Class Package (up to 15.999 oz) — 2026 rates, zone-based
# Simplified: using zone 5 as default from PR
FIRST_CLASS_RATES = {
    # weight_oz_max: cost
    4: 4.63,
    8: 5.13,
    12: 5.73,
    15.999: 6.33,
}

# USPS Priority Mail — 2026 rates, zone 5 from PR
# Flat rate options are zone-independent
PRIORITY_MAIL_RATES = {
    "flat_rate_envelope": 9.85,
    "flat_rate_small_box": 10.40,
    "flat_rate_medium_box": 17.10,
    "flat_rate_large_box": 22.45,
    # Weight-based (zone 5 estimates)
    "1lb": 9.50,
    "2lb": 11.20,
    "3lb": 13.45,
    "5lb": 17.80,
    "10lb": 25.50,
    "20lb": 38.00,
}

# eBay shipping discount (typically ~20% off retail USPS via eBay labels)
EBAY_SHIPPING_DISCOUNT = 0.80  # Pay 80% of retail


def estimate_shipping(
    weight_oz: float,
    zone: int = 5,
    use_ebay_labels: bool = True,
    fragile: bool = False,
) -> ShippingEstimate:
    """
    Estimate USPS shipping cost from Puerto Rico.

    Args:
        weight_oz: Package weight in ounces
        zone: USPS zone (default 5 for PR → CONUS)
        use_ebay_labels: Apply eBay shipping discount (~20% off)
        fragile: Add padding weight estimate (+4oz)

    Returns:
        ShippingEstimate with service, cost, delivery window
    """
    if fragile:
        weight_oz += 4  # Extra padding weight

    discount = EBAY_SHIPPING_DISCOUNT if use_ebay_labels else 1.0

    if weight_oz < 16:
        # First Class Package
        cost = _first_class_cost(weight_oz)
        return ShippingEstimate(
            service="USPS First Class Package",
            cost=round(cost * discount, 2),
            delivery_days="3-5",
            weight_oz=weight_oz,
            zone=zone,
        )
    else:
        # Priority Mail
        cost = _priority_mail_cost(weight_oz)
        return ShippingEstimate(
            service="USPS Priority Mail",
            cost=round(cost * discount, 2),
            delivery_days="2-4",
            weight_oz=weight_oz,
            zone=zone,
        )


def estimate_flat_rate(box_type: str = "small_box") -> ShippingEstimate:
    """Use Priority Mail Flat Rate — price doesn't change by weight or zone."""
    key = f"flat_rate_{box_type}"
    cost = PRIORITY_MAIL_RATES.get(key, PRIORITY_MAIL_RATES["flat_rate_small_box"])
    return ShippingEstimate(
        service=f"USPS Priority Mail Flat Rate ({box_type.replace('_', ' ').title()})",
        cost=round(cost * EBAY_SHIPPING_DISCOUNT, 2),
        delivery_days="1-3",
        weight_oz=0,  # Doesn't matter for flat rate
        zone=0,
    )


def _first_class_cost(weight_oz: float) -> float:
    """Look up First Class rate by weight bracket."""
    for max_oz, rate in sorted(FIRST_CLASS_RATES.items()):
        if weight_oz <= max_oz:
            return rate
    # Shouldn't reach here if caller checks weight < 16
    return FIRST_CLASS_RATES[15.999]


def _priority_mail_cost(weight_oz: float) -> float:
    """Estimate Priority Mail cost by weight."""
    weight_lb = weight_oz / 16
    if weight_lb <= 1:
        return PRIORITY_MAIL_RATES["1lb"]
    elif weight_lb <= 2:
        return PRIORITY_MAIL_RATES["2lb"]
    elif weight_lb <= 3:
        return PRIORITY_MAIL_RATES["3lb"]
    elif weight_lb <= 5:
        return PRIORITY_MAIL_RATES["5lb"]
    elif weight_lb <= 10:
        return PRIORITY_MAIL_RATES["10lb"]
    elif weight_lb <= 20:
        return PRIORITY_MAIL_RATES["20lb"]
    else:
        # Over 20lb — rough extrapolation
        return PRIORITY_MAIL_RATES["20lb"] + (weight_lb - 20) * 1.50
