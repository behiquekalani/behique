"""
eBay publishing adapter — creates listings via Inventory API.
Takes ListingContent and posts it to eBay.

Uses: Sell Inventory API (create inventory item + offer + publish)
Docs: https://developer.ebay.com/api-docs/sell/inventory/overview.html

Flow:
  1. PUT /sell/inventory/v1/inventory_item/{sku} — create/update inventory item
  2. POST /sell/inventory/v1/offer — create offer with pricing + policies
  3. POST /sell/inventory/v1/offer/{offerId}/publish — make listing live

Note: Inventory API requires User token (OAuth2 Authorization Code flow),
not just Application token. Set EBAY_USER_TOKEN env var.
"""

import logging
import os
import uuid

import requests

from core.types import ProductInput, ListingContent, PublishedListing
from providers.ebay.auth import EbayAuth

logger = logging.getLogger(__name__)


class EbayApiError(Exception):
    """Raised when an eBay API call fails with details."""

    def __init__(self, stage, status_code, response_body):
        self.stage = stage
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(
            f"eBay API error in {stage}: HTTP {status_code} — {response_body}"
        )


class EbayPublisher:
    """
    Stage 3 adapter: publishes listings to eBay.
    Uses Inventory API (create item -> create offer -> publish offer).

    Shipping defaults: Puerto Rico (00901), free shipping,
    USPS First Class (<16oz) or Priority Mail (>16oz).

    Return policy: 30 days, buyer pays return shipping.
    """

    # Shipping defaults — Puerto Rico
    DEFAULT_SHIP_FROM = {
        "city": "San Juan",
        "stateOrProvince": "PR",
        "postalCode": "00901",
        "country": "US",
    }

    # eBay condition enum mapping
    CONDITION_MAP = {
        "New": "NEW",
        "Like New": "LIKE_NEW",
        "Used": "USED_EXCELLENT",
        "Good": "USED_GOOD",
        "Acceptable": "USED_ACCEPTABLE",
        "Refurbished": "SELLER_REFURBISHED",
        "For Parts": "FOR_PARTS_OR_NOT_WORKING",
    }

    def __init__(self, auth: EbayAuth):
        self.auth = auth
        # Policy IDs from eBay Seller Hub — set via env vars or pass directly
        self.fulfillment_policy_id = os.environ.get("EBAY_FULFILLMENT_POLICY_ID", "")
        self.payment_policy_id = os.environ.get("EBAY_PAYMENT_POLICY_ID", "")
        self.return_policy_id = os.environ.get("EBAY_RETURN_POLICY_ID", "")

    def publish(self, product: ProductInput, content: ListingContent) -> PublishedListing:
        """
        Full publish flow:
          1. Create/update inventory item
          2. Create offer
          3. Publish offer -> live listing

        Args:
            product: ProductInput with name, condition, images, notes
            content: ListingContent with title, description, item_specifics, price

        Returns:
            PublishedListing with listing_id, listing_url, status, title, price
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

    def authenticate(self):
        """
        Verify authentication works before publishing.
        Tests both app token and user token availability.
        """
        self.auth.get_user_token()
        logger.info("eBay authentication verified.")

    def _generate_sku(self, name: str) -> str:
        """Generate a unique SKU from product name."""
        slug = name.lower().replace(" ", "-")[:20]
        short_id = uuid.uuid4().hex[:6]
        return f"{slug}-{short_id}"

    def _api_call(self, method, url, stage, **kwargs):
        """
        Wrapper for all eBay API calls.
        Logs request/response, raises EbayApiError with details on failure.
        """
        headers = self.auth.get_seller_headers()
        kwargs.setdefault("headers", headers)
        kwargs.setdefault("timeout", 20)

        logger.info(f"[{stage}] {method.upper()} {url}")

        try:
            resp = requests.request(method, url, **kwargs)
        except requests.RequestException as e:
            logger.error(f"[{stage}] Network error: {e}")
            raise EbayApiError(stage, 0, str(e))

        if not resp.ok:
            body = resp.text
            logger.error(f"[{stage}] HTTP {resp.status_code}: {body}")
            raise EbayApiError(stage, resp.status_code, body)

        logger.info(f"[{stage}] Success: HTTP {resp.status_code}")
        return resp

    def _create_inventory_item(self, sku: str, product: ProductInput, content: ListingContent):
        """
        Create or update an inventory item.

        Endpoint: PUT /sell/inventory/v1/inventory_item/{sku}
        Docs: https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/createOrReplaceInventoryItem

        This creates the product record in eBay's inventory system.
        It does NOT create a listing — that requires an offer + publish.
        """
        url = f"{self.auth.api_base}/sell/inventory/v1/inventory_item/{sku}"

        condition = self.CONDITION_MAP.get(product.condition, "USED_EXCELLENT")

        body = {
            "availability": {
                "shipToLocationAvailability": {
                    "quantity": 1
                }
            },
            "condition": condition,
            "product": {
                "title": content.title,
                "description": content.description,
                "aspects": {
                    k: [v] if isinstance(v, str) else v
                    for k, v in content.item_specifics.items()
                },
            },
        }

        # Add image if available
        if product.image_url:
            body["product"]["imageUrls"] = [product.image_url]

        logger.info(f"Creating inventory item: {sku}")
        self._api_call("put", url, "create_inventory_item", json=body)
        logger.info(f"Inventory item created: {sku}")

    def _create_offer(self, sku: str, content: ListingContent) -> str:
        """
        Create an offer for the inventory item.

        Endpoint: POST /sell/inventory/v1/offer
        Docs: https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods/createOffer

        An offer connects an inventory item to a marketplace with pricing,
        policies, and category. The offer must be published to become a live listing.
        """
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
                "fulfillmentPolicyId": self.fulfillment_policy_id,
                "paymentPolicyId": self.payment_policy_id,
                "returnPolicyId": self.return_policy_id,
            },
        }

        # Category from research result (passed via item_specifics or content)
        category_id = content.item_specifics.get("_category_id", "")
        if category_id:
            body["categoryId"] = str(category_id)

        logger.info(f"Creating offer for SKU: {sku}")
        resp = self._api_call("post", url, "create_offer", json=body)

        offer_id = resp.json().get("offerId")
        logger.info(f"Offer created: {offer_id}")
        return offer_id

    def _publish_offer(self, offer_id: str) -> str:
        """
        Publish an offer to make it a live listing on eBay.

        Endpoint: POST /sell/inventory/v1/offer/{offerId}/publish
        Docs: https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods/publishOffer

        After this call succeeds, the listing is live and visible to buyers.
        Returns the eBay listing ID which can be used to construct the listing URL.
        """
        url = f"{self.auth.api_base}/sell/inventory/v1/offer/{offer_id}/publish"

        logger.info(f"Publishing offer: {offer_id}")
        resp = self._api_call("post", url, "publish_offer")

        listing_id = resp.json().get("listingId")
        logger.info(f"Listing live: {listing_id}")
        return listing_id


def test_sandbox():
    """
    Test the full publish flow against eBay sandbox.

    Prerequisites:
      - EBAY_APP_ID set to sandbox app ID
      - EBAY_CERT_ID set to sandbox cert ID
      - EBAY_USER_TOKEN set to sandbox user token
      - EBAY_ENVIRONMENT=sandbox (or omit, sandbox is default)

    This creates a test inventory item, offer, and publishes it.
    """
    logging.basicConfig(level=logging.INFO, format="%(name)s — %(message)s")

    auth = EbayAuth(sandbox=True)
    publisher = EbayPublisher(auth)

    # Verify auth first
    publisher.authenticate()
    print("Auth OK")

    # Test product
    product = ProductInput(
        name="Test Funko Pop Spider-Man",
        condition="New",
        image_url="https://i.ebayimg.com/images/g/test/s-l1600.jpg",
    )

    content = ListingContent(
        title="Funko Pop Spider-Man #123 - New In Box - Marvel",
        description="<p>Brand new Funko Pop Spider-Man figure. Mint condition, never opened.</p>",
        item_specifics={
            "Brand": "Funko",
            "Character": "Spider-Man",
            "Type": "Pop! Vinyl",
        },
        suggested_price=24.99,
        suggested_condition="New",
    )

    print(f"Publishing test listing: {content.title}")
    result = publisher.publish(product, content)

    print(f"\nListing published!")
    print(f"  ID:     {result.listing_id}")
    print(f"  URL:    {result.listing_url}")
    print(f"  Title:  {result.title}")
    print(f"  Price:  ${result.price}")
    print(f"  Status: {result.status}")

    return result


if __name__ == "__main__":
    test_sandbox()
