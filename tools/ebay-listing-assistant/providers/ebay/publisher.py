"""
eBay publishing adapter — creates listings via Inventory API.
Takes ListingContent and posts it to eBay.

Uses: Sell Inventory API (create inventory item + offer)
Docs: https://developer.ebay.com/api-docs/sell/inventory/overview.html

Note: Inventory API requires User token (OAuth2 Authorization Code flow),
not just Application token. This means the user must authorize via browser once.
"""

import logging
import uuid

import requests

from core.types import ProductInput, ListingContent, PublishedListing
from providers.ebay.auth import EbayAuth

logger = logging.getLogger(__name__)


class EbayPublisher:
    """
    Stage 3 adapter: publishes listings to eBay.
    Uses Inventory API (create item → create offer → publish offer).
    """

    def __init__(self, auth: EbayAuth):
        self.auth = auth

    def publish(self, product: ProductInput, content: ListingContent) -> PublishedListing:
        """
        Full publish flow:
          1. Create/update inventory item
          2. Create offer
          3. Publish offer → live listing
        """
        sku = self._generate_sku(product.name)

        # Step 1: Create inventory item
        self._create_inventory_item(sku, product, content)

        # Step 2: Create offer
        offer_id = self._create_offer(sku, content)

        # Step 3: Publish offer
        listing_id = self._publish_offer(offer_id)

        listing_url = f"https://www.ebay.com/itm/{listing_id}"
        if self.auth.sandbox:
            listing_url = f"https://sandbox.ebay.com/itm/{listing_id}"

        return PublishedListing(
            platform="ebay",
            listing_id=listing_id,
            listing_url=listing_url,
            title=content.title,
            price=content.suggested_price,
            status="active",
        )

    def _generate_sku(self, name: str) -> str:
        """Generate a unique SKU from product name."""
        slug = name.lower().replace(" ", "-")[:20]
        short_id = uuid.uuid4().hex[:6]
        return f"{slug}-{short_id}"

    def _create_inventory_item(self, sku: str, product: ProductInput, content: ListingContent):
        """Create or update an inventory item."""
        url = f"{self.auth.api_base}/sell/inventory/v1/inventory_item/{sku}"

        condition_map = {
            "New": "NEW",
            "Used": "USED_EXCELLENT",
            "Refurbished": "SELLER_REFURBISHED",
            "For Parts": "FOR_PARTS_OR_NOT_WORKING",
        }

        body = {
            "availability": {
                "shipToLocationAvailability": {
                    "quantity": 1
                }
            },
            "condition": condition_map.get(product.condition, "USED_EXCELLENT"),
            "product": {
                "title": content.title,
                "description": content.description,
                "aspects": {
                    k: [v] for k, v in content.item_specifics.items()
                },
            },
        }

        # Add image if available
        if product.image_url:
            body["product"]["imageUrls"] = [product.image_url]

        headers = self.auth.get_headers()
        headers["Content-Language"] = "en-US"

        logger.info(f"Creating inventory item: {sku}")
        resp = requests.put(url, headers=headers, json=body, timeout=20)
        resp.raise_for_status()
        logger.info(f"Inventory item created: {sku}")

    def _create_offer(self, sku: str, content: ListingContent) -> str:
        """Create an offer for the inventory item."""
        url = f"{self.auth.api_base}/sell/inventory/v1/offer"

        body = {
            "sku": sku,
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "listingDescription": content.description,
            "pricingSummary": {
                "price": {
                    "currency": "USD",
                    "value": str(content.suggested_price),
                }
            },
            "listingPolicies": {
                # These policy IDs come from the seller's eBay account.
                # Must be configured once via eBay Seller Hub.
                "fulfillmentPolicyId": "",  # TODO: set from config
                "paymentPolicyId": "",      # TODO: set from config
                "returnPolicyId": "",       # TODO: set from config
            },
            "categoryId": "",  # TODO: pass from research result
        }

        headers = self.auth.get_headers()
        headers["Content-Language"] = "en-US"

        logger.info(f"Creating offer for SKU: {sku}")
        resp = requests.post(url, headers=headers, json=body, timeout=20)
        resp.raise_for_status()

        offer_id = resp.json().get("offerId")
        logger.info(f"Offer created: {offer_id}")
        return offer_id

    def _publish_offer(self, offer_id: str) -> str:
        """Publish an offer to make it a live listing."""
        url = f"{self.auth.api_base}/sell/inventory/v1/offer/{offer_id}/publish"

        headers = self.auth.get_headers()

        logger.info(f"Publishing offer: {offer_id}")
        resp = requests.post(url, headers=headers, timeout=20)
        resp.raise_for_status()

        listing_id = resp.json().get("listingId")
        logger.info(f"Listing live: {listing_id}")
        return listing_id
