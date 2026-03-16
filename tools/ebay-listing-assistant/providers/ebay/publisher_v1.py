"""
V1 Publisher — Formats listing as copy-paste output for eBay's listing form.

V1: Prints formatted blocks Kalani pastes into eBay.
V2: Publishes via eBay Sell/Inventory API directly.
"""

from datetime import datetime
from core.types import ProductInput, ListingContent, PublishedListing
from core.pricing import PricingRecommendation


class EbayManualPublisher:
    """
    V1 'publisher' — outputs formatted listing for manual eBay posting.
    Implements the publisher interface expected by pipeline.py.
    """

    def __init__(self, pricing: PricingRecommendation = None):
        self.pricing = pricing

    def publish(self, product: ProductInput, content: ListingContent) -> PublishedListing:
        """
        Pipeline adapter interface.
        Formats and prints the listing, returns a draft PublishedListing.
        """
        output = self.format_listing(product, content)
        print(output)

        return PublishedListing(
            platform="ebay",
            listing_id=f"DRAFT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            listing_url="",
            title=content.title,
            price=content.suggested_price,
            status="draft",
            raw_response={"formatted_output": output, "pricing": self.pricing.breakdown if self.pricing else {}},
        )

    def format_listing(self, product: ProductInput, content: ListingContent) -> str:
        """Format the complete listing for copy-paste into eBay."""
        sections = []

        # Header
        sections.append("=" * 60)
        sections.append("  EBAY LISTING — READY TO POST")
        sections.append("=" * 60)

        # Title
        sections.append(f"\n{'─' * 40}")
        sections.append("📋 TITLE (copy this exactly)")
        sections.append(f"{'─' * 40}")
        sections.append(content.title)
        sections.append(f"   [{len(content.title)}/80 characters]")

        # Category
        if content.item_specifics.get("Category"):
            sections.append(f"\n{'─' * 40}")
            sections.append("📁 CATEGORY")
            sections.append(f"{'─' * 40}")
            sections.append(content.item_specifics["Category"])

        # Condition
        sections.append(f"\n{'─' * 40}")
        sections.append("🏷️  CONDITION")
        sections.append(f"{'─' * 40}")
        sections.append(content.suggested_condition)

        # Item Specifics
        sections.append(f"\n{'─' * 40}")
        sections.append("📝 ITEM SPECIFICS (fill each field)")
        sections.append(f"{'─' * 40}")
        for key, val in content.item_specifics.items():
            if key not in ("Category",):
                sections.append(f"  {key}: {val}")

        # Price + Strategy
        sections.append(f"\n{'─' * 40}")
        sections.append("💰 PRICING")
        sections.append(f"{'─' * 40}")
        if self.pricing:
            sections.append(f"  Strategy: {self.pricing.strategy.replace('_', ' ').upper()}")
            if self.pricing.strategy == "fixed_price":
                sections.append(f"  List Price: ${self.pricing.list_price:.2f}")
                sections.append(f"  (includes free shipping)")
            else:
                sections.append(f"  Starting Bid: ${self.pricing.auction_start:.2f}")
                sections.append(f"  Buy It Now: ${self.pricing.list_price:.2f}")

            sections.append(f"\n  --- Cost Breakdown ---")
            for key, val in self.pricing.breakdown.items():
                label = key.replace("_", " ").title()
                sections.append(f"  {label}: {val}")
        else:
            sections.append(f"  Suggested Price: ${content.suggested_price:.2f}")

        # Shipping
        if self.pricing and self.pricing.shipping:
            sections.append(f"\n{'─' * 40}")
            sections.append("📦 SHIPPING")
            sections.append(f"{'─' * 40}")
            sections.append(f"  Service: {self.pricing.shipping.service}")
            sections.append(f"  Cost: ${self.pricing.shipping.cost:.2f} (baked into price)")
            sections.append(f"  Delivery: {self.pricing.shipping.delivery_days} business days")
            sections.append(f"  Ship from: Puerto Rico, US")
            sections.append(f"  Set as: FREE SHIPPING (ranks higher on eBay)")

        # Description
        sections.append(f"\n{'─' * 40}")
        sections.append("📄 DESCRIPTION (paste into Source/HTML mode)")
        sections.append(f"{'─' * 40}")
        sections.append(content.description)

        # Keywords for reference
        if content.keywords:
            sections.append(f"\n{'─' * 40}")
            sections.append("🔍 KEYWORDS (for your reference)")
            sections.append(f"{'─' * 40}")
            sections.append(", ".join(content.keywords))

        # Photos reminder
        sections.append(f"\n{'─' * 40}")
        sections.append("📸 PHOTOS")
        sections.append(f"{'─' * 40}")
        sections.append("  Upload your product photos directly to eBay.")
        sections.append("  Tips: First photo = thumbnail. Use white/clean background.")
        sections.append("  Show all angles + any defects for used items.")
        if product.image_path:
            sections.append(f"  Local file: {product.image_path}")

        sections.append(f"\n{'=' * 60}")
        sections.append("  Copy each section into eBay's listing form.")
        sections.append("  Go to: ebay.com → Sell → List an item")
        sections.append("=" * 60)

        return "\n".join(sections)
