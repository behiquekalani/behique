#!/usr/bin/env python3
"""
eBay Listing Agent V1 — CLI Entry Point

Usage:
    python run.py "Hello Kitty Strawberry Coffee Mug" --condition New --weight 12 --cost 3.00
    python run.py "Funko Pop Naruto" --condition Used --weight 8 --cost 5.00 --margin 0.30

V1: Generates formatted listing for manual eBay posting.
V2: Will publish directly via eBay API.
"""

import argparse
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.types import ProductInput, ResearchResult
from core.types_v1 import V1ProductInput
from core.pipeline import ListingPipeline
from core.pricing import recommend_price
from providers.ebay.research import EbayWebResearch
from ai.content_generator import EbayContentGenerator
from providers.ebay.publisher_v1 import EbayManualPublisher
from media.image_handler import ImageHandler


def run_interactive(v1_input: V1ProductInput, research_data: dict = None):
    """
    Run the full listing pipeline interactively.

    If research_data is None, prints the search URL and waits for data.
    If research_data is provided, runs the full pipeline.
    """
    product = v1_input.product
    researcher = EbayWebResearch()

    # Step 1: Research
    if research_data is None:
        # Print search URLs for Ceiba to look up
        sold_url = researcher.build_search_url(product, sold_only=True)
        active_url = researcher.build_active_url(product)
        print(f"\n🔍 RESEARCH STEP — Search these URLs:")
        print(f"\n  Sold listings:   {sold_url}")
        print(f"  Active listings: {active_url}")
        print(f"\nGather: sold prices, top titles, item specifics, category ID/name")
        print(f"Then call run_with_research() with the data.\n")
        return {"status": "needs_research", "sold_url": sold_url, "active_url": active_url}

    # Step 2: Parse research
    research = researcher.parse_comp_data(**research_data)

    # Step 3: Pricing
    pricing = recommend_price(
        research=research,
        item_cost=v1_input.item_cost,
        weight_oz=v1_input.weight_oz,
        fragile=v1_input.fragile,
    )

    # Step 4: Generate content
    generator = EbayContentGenerator()
    content = generator.generate(
        product=product,
        research=research,
        pricing=pricing,
        item_cost=v1_input.item_cost,
        weight_oz=v1_input.weight_oz,
        fragile=v1_input.fragile,
    )

    # Step 5: Format output
    publisher = EbayManualPublisher(pricing=pricing)
    result = publisher.publish(product, content)

    # Step 6: Image validation (if images provided)
    if product.image_path:
        handler = ImageHandler()
        validation = handler.validate(product.image_path)
        print(f"\n{handler.summary([validation])}")

    return {
        "status": "ready",
        "listing": result,
        "research": research,
        "pricing": pricing,
        "content": content,
    }


def main():
    parser = argparse.ArgumentParser(description="eBay Listing Agent V1")
    parser.add_argument("name", help="Product name (e.g., 'Hello Kitty Strawberry Coffee Mug')")
    parser.add_argument("--condition", default="Used", choices=["New", "Used", "Refurbished", "For Parts"])
    parser.add_argument("--weight", type=float, default=12.0, help="Weight in ounces")
    parser.add_argument("--cost", type=float, default=0.0, help="What you paid for the item")
    parser.add_argument("--margin", type=float, default=0.20, help="Desired profit margin (0.20 = 20%%)")
    parser.add_argument("--quantity", type=int, default=1, help="Number of items")
    parser.add_argument("--fragile", action="store_true", help="Item is fragile (adds padding weight)")
    parser.add_argument("--image", type=str, help="Path to product image")
    parser.add_argument("--notes", type=str, help="Extra notes for the listing")

    args = parser.parse_args()

    v1_input = V1ProductInput.from_quick_input(
        name=args.name,
        condition=args.condition,
        weight_oz=args.weight,
        item_cost=args.cost,
        quantity=args.quantity,
        fragile=args.fragile,
        image_paths=[args.image] if args.image else None,
        notes=args.notes,
    )
    v1_input.desired_margin = args.margin

    result = run_interactive(v1_input)

    if result["status"] == "needs_research":
        print("=" * 60)
        print("  Waiting for research data.")
        print("  In Claude Code, Ceiba will search the URLs above")
        print("  and feed the data back into run_interactive().")
        print("=" * 60)


if __name__ == "__main__":
    main()
