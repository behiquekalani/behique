#!/usr/bin/env python3
"""
Quick Lister — Skip research, go straight to listing.

You already know what you're selling and what price. This skips the
research loop and generates a ready-to-paste eBay listing instantly.

Usage:
    python quick_list.py "Funko Pop Goodfellas 3-Pack" --price 27.99 --condition New --weight 12 --qty 3
    python quick_list.py "Hello Kitty Coffee Cup" --price 14.99 --condition New --weight 16 --fragile
    python quick_list.py "Nintendo Switch Joy-Con" --price 39.99 --condition Used --weight 8 --cost 15

Output is saved to listings/ folder AND printed to console.
"""

import argparse
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.types import ProductInput, ResearchResult, ListingContent
from core.shipping import estimate_shipping
from core.pricing import PricingRecommendation, EBAY_FEE_RATE, _round_price


# ── eBay SEO title generator ──────────────────────────────────────

FILLER_WORDS = {"the", "a", "an", "for", "with", "and", "of", "in", "on", "to", "is", "it"}

def generate_title(name: str, condition: str, brand: str = "", extra_keywords: list = None) -> str:
    """Generate eBay-optimized title (max 80 chars)."""
    parts = []

    # Brand first if provided and not already in name
    if brand and brand.lower() not in name.lower():
        parts.append(brand)

    # Product name words
    for word in name.split():
        if word.lower() not in FILLER_WORDS:
            parts.append(word)

    # Condition for non-new items
    if condition in ("Used", "Refurbished"):
        parts.append(condition)

    # Extra keywords if room (skip duplicates)
    existing_lower = {p.lower() for p in parts}
    if extra_keywords:
        for kw in extra_keywords:
            if kw.lower() not in existing_lower:
                parts.append(kw)
                existing_lower.add(kw.lower())

    title = " ".join(parts)

    # Trim to 80 chars keeping whole words
    while len(title) > 80 and " " in title:
        title = title.rsplit(" ", 1)[0]

    return title


# ── HTML description generator ────────────────────────────────────

def generate_description(
    name: str,
    condition: str,
    brand: str = "",
    specifics: dict = None,
    shipping_service: str = "USPS First Class",
    delivery_days: str = "3-5",
    notes: str = "",
) -> str:
    """Generate clean mobile-friendly HTML description."""
    specifics = specifics or {}

    condition_text = {
        "New": "Brand new, unused, in original packaging (if applicable).",
        "Used": "Pre-owned item in good condition. See photos for actual condition.",
        "Refurbished": "Professionally refurbished to working condition.",
        "For Parts": "Sold as-is for parts or repair. May not be fully functional.",
    }.get(condition, "See photos for condition details.")

    spec_html = ""
    if specifics:
        spec_html = "<h3 style='color:#333;'>Details</h3>\n<ul style='line-height:1.8;'>\n"
        for k, v in specifics.items():
            spec_html += f"  <li><strong>{k}:</strong> {v}</li>\n"
        spec_html += "</ul>\n"

    notes_html = f"<h3 style='color:#333;'>Notes</h3>\n<p>{notes}</p>\n" if notes else ""

    return f"""<div style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:10px;">

<h2 style="color:#333;margin-bottom:5px;">{name}</h2>
{f'<p style="color:#666;font-size:14px;">by {brand}</p>' if brand else ''}

<hr style="border:1px solid #eee;">

<h3 style="color:#333;">Condition</h3>
<p>{condition_text}</p>

{spec_html}
{notes_html}

<hr style="border:1px solid #eee;">

<h3 style="color:#333;">Shipping</h3>
<p>Ships from Puerto Rico via {shipping_service}. Estimated delivery: {delivery_days} business days. FREE SHIPPING included.</p>

<p style="color:#888;font-size:12px;margin-top:20px;">
Thank you for looking! Message with any questions before purchasing.
</p>

</div>"""


# ── Pricing calculator ────────────────────────────────────────────

def calculate_pricing(price: float, cost: float, weight_oz: float, fragile: bool = False) -> dict:
    """Calculate fees, shipping, and profit at the given price."""
    shipping = estimate_shipping(weight_oz, fragile=fragile)
    fees = round(price * EBAY_FEE_RATE, 2)
    profit = round(price - fees - cost - shipping.cost, 2)
    margin_pct = round((profit / price) * 100, 1) if price > 0 else 0

    return {
        "list_price": price,
        "ebay_fees": fees,
        "shipping_cost": shipping.cost,
        "shipping_service": shipping.service,
        "delivery_days": shipping.delivery_days,
        "item_cost": cost,
        "profit": profit,
        "margin": f"{margin_pct}%",
        "breakeven": round((cost + shipping.cost) / (1 - EBAY_FEE_RATE), 2),
    }


# ── Listing formatter ─────────────────────────────────────────────

def format_listing(
    title: str,
    price: float,
    condition: str,
    description: str,
    specifics: dict,
    keywords: list,
    pricing: dict,
    quantity: int = 1,
) -> str:
    """Format the complete listing for copy-paste into eBay."""
    lines = []

    lines.append("=" * 60)
    lines.append("  EBAY LISTING — READY TO POST")
    lines.append("=" * 60)

    lines.append(f"\n{'─' * 40}")
    lines.append("TITLE (copy this exactly)")
    lines.append(f"{'─' * 40}")
    lines.append(title)
    lines.append(f"   [{len(title)}/80 characters]")

    lines.append(f"\n{'─' * 40}")
    lines.append("CONDITION")
    lines.append(f"{'─' * 40}")
    lines.append(condition)

    if specifics:
        lines.append(f"\n{'─' * 40}")
        lines.append("ITEM SPECIFICS")
        lines.append(f"{'─' * 40}")
        for k, v in specifics.items():
            lines.append(f"  {k}: {v}")

    lines.append(f"\n{'─' * 40}")
    lines.append("PRICING")
    lines.append(f"{'─' * 40}")
    lines.append(f"  List Price: ${price:.2f}")
    lines.append(f"  Quantity: {quantity}")
    lines.append(f"  Strategy: Fixed Price + Free Shipping")
    lines.append(f"\n  --- Cost Breakdown ---")
    lines.append(f"  Item Cost:      ${pricing['item_cost']:.2f}")
    lines.append(f"  eBay Fees:      ${pricing['ebay_fees']:.2f} ({EBAY_FEE_RATE*100:.1f}%)")
    lines.append(f"  Shipping:       ${pricing['shipping_cost']:.2f} ({pricing['shipping_service']})")
    lines.append(f"  Breakeven:      ${pricing['breakeven']:.2f}")
    lines.append(f"  PROFIT:         ${pricing['profit']:.2f} per unit ({pricing['margin']})")
    if quantity > 1:
        lines.append(f"  TOTAL PROFIT:   ${pricing['profit'] * quantity:.2f} (×{quantity})")

    lines.append(f"\n{'─' * 40}")
    lines.append("SHIPPING")
    lines.append(f"{'─' * 40}")
    lines.append(f"  Service: {pricing['shipping_service']}")
    lines.append(f"  Cost: ${pricing['shipping_cost']:.2f} (baked into price)")
    lines.append(f"  Delivery: {pricing['delivery_days']} business days")
    lines.append(f"  Ship from: Puerto Rico, US")
    lines.append(f"  Set as: FREE SHIPPING")

    lines.append(f"\n{'─' * 40}")
    lines.append("DESCRIPTION (paste into Source/HTML mode)")
    lines.append(f"{'─' * 40}")
    lines.append(description)

    if keywords:
        lines.append(f"\n{'─' * 40}")
        lines.append("KEYWORDS (reference)")
        lines.append(f"{'─' * 40}")
        lines.append(", ".join(keywords))

    lines.append(f"\n{'─' * 40}")
    lines.append("PHOTOS")
    lines.append(f"{'─' * 40}")
    lines.append("  Upload product photos directly to eBay.")
    lines.append("  First photo = thumbnail. White/clean background.")
    lines.append("  Show all angles + defects for used items.")

    lines.append(f"\n{'=' * 60}")
    lines.append("  Go to: ebay.com > Sell > List an item")
    lines.append("  Copy each section into the form.")
    lines.append("=" * 60)

    return "\n".join(lines)


# ── Save to file ──────────────────────────────────────────────────

def save_listing(name: str, output: str, pricing: dict, args_dict: dict):
    """Save listing to listings/ folder as .txt + .json metadata."""
    listings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "listings")
    os.makedirs(listings_dir, exist_ok=True)

    slug = name.lower().replace(" ", "_")[:40]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{slug}_{timestamp}"

    # Save formatted listing
    txt_path = os.path.join(listings_dir, f"{base}.txt")
    with open(txt_path, "w") as f:
        f.write(output)

    # Save metadata as JSON
    meta = {
        "product": name,
        "generated_at": datetime.now().isoformat(),
        "pricing": pricing,
        "args": args_dict,
    }
    json_path = os.path.join(listings_dir, f"{base}.json")
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2)

    return txt_path, json_path


# ── Main ──────────────────────────────────────────────────────────

def quick_list(
    name: str,
    price: float,
    condition: str = "New",
    weight_oz: float = 12.0,
    cost: float = 0.0,
    quantity: int = 1,
    fragile: bool = False,
    brand: str = "",
    category: str = "",
    keywords: list = None,
    specifics: dict = None,
    notes: str = "",
) -> str:
    """Generate a complete listing and return formatted output."""

    # Title
    title = generate_title(name, condition, brand=brand, extra_keywords=keywords)

    # Pricing
    pricing = calculate_pricing(price, cost, weight_oz, fragile=fragile)

    # Specifics
    item_specifics = specifics or {}
    if brand:
        item_specifics.setdefault("Brand", brand)
    if category:
        item_specifics.setdefault("Category", category)
    item_specifics.setdefault("Condition", condition)

    # Keywords
    kw = set()
    for word in name.lower().split():
        if len(word) > 2 and word not in FILLER_WORDS:
            kw.add(word)
    if keywords:
        kw.update(k.lower() for k in keywords)
    if brand:
        kw.add(brand.lower())

    # Description
    description = generate_description(
        name=name,
        condition=condition,
        brand=brand,
        specifics=item_specifics,
        shipping_service=pricing["shipping_service"],
        delivery_days=pricing["delivery_days"],
        notes=notes,
    )

    # Format
    output = format_listing(
        title=title,
        price=price,
        condition=condition,
        description=description,
        specifics=item_specifics,
        keywords=sorted(kw),
        pricing=pricing,
        quantity=quantity,
    )

    return output, pricing


def main():
    parser = argparse.ArgumentParser(
        description="Quick eBay Lister — skip research, generate listing instantly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_list.py "Funko Pop Goodfellas 3-Pack" --price 27.99 --condition New --qty 3
  python quick_list.py "Hello Kitty Coffee Cup" --price 14.99 --fragile --brand "Sanrio"
  python quick_list.py "PS5 Controller" --price 45.00 --condition Used --cost 20 --weight 16
        """,
    )
    parser.add_argument("name", help="Product name")
    parser.add_argument("--price", type=float, required=True, help="Listing price (USD)")
    parser.add_argument("--condition", default="New", choices=["New", "Used", "Refurbished", "For Parts"])
    parser.add_argument("--weight", type=float, default=12.0, help="Weight in ounces (default: 12)")
    parser.add_argument("--cost", type=float, default=0.0, help="What you paid for it (default: 0)")
    parser.add_argument("--qty", type=int, default=1, help="Quantity (default: 1)")
    parser.add_argument("--fragile", action="store_true", help="Item is fragile")
    parser.add_argument("--brand", type=str, default="", help="Brand name")
    parser.add_argument("--category", type=str, default="", help="eBay category")
    parser.add_argument("--keywords", type=str, default="", help="Extra keywords (comma-separated)")
    parser.add_argument("--notes", type=str, default="", help="Extra notes for description")
    parser.add_argument("--no-save", action="store_true", help="Don't save to file")

    args = parser.parse_args()

    extra_kw = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else None
    specifics = {}
    if args.brand:
        specifics["Brand"] = args.brand
    if args.category:
        specifics["Category"] = args.category

    output, pricing = quick_list(
        name=args.name,
        price=args.price,
        condition=args.condition,
        weight_oz=args.weight,
        cost=args.cost,
        quantity=args.qty,
        fragile=args.fragile,
        brand=args.brand,
        category=args.category,
        keywords=extra_kw,
        specifics=specifics,
        notes=args.notes,
    )

    print(output)

    if not args.no_save:
        txt_path, json_path = save_listing(
            name=args.name,
            output=output,
            pricing=pricing,
            args_dict=vars(args),
        )
        print(f"\n✅ Saved to: {txt_path}")
        print(f"   Meta:     {json_path}")


if __name__ == "__main__":
    main()
