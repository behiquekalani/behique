"""
V2 Publisher — Publishes listings directly via eBay Sell/Inventory API.

V1: Copy-paste formatted output (EbayManualPublisher)
V2: Direct API publishing (this file)

APIs Used:
    - OAuth: POST /identity/v1/oauth2/token (auto-refresh)
    - Inventory: PUT /sell/inventory/v1/inventory_item/{sku}
    - Offer: POST /sell/inventory/v1/offer
    - Publish: POST /sell/inventory/v1/offer/{offerId}/publish
    - Account: GET/POST fulfillment_policy, payment_policy, return_policy

Token Management:
    Loads tokens from ~/.behique_ebay_tokens.json (created by ebay_oauth_token.py).
    Auto-refreshes expired access tokens using the refresh token.
    Never fails due to token expiry — handles it transparently.

Environment Variables Required:
    EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID, EBAY_ENVIRONMENT
    (EBAY_USER_TOKEN is optional — prefers token file)
"""

import os
import json
import uuid
import time
import base64
import random
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from core.types import ProductInput, ListingContent, PublishedListing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token file — same location as ebay_oauth_token.py writes to
TOKEN_FILE = Path.home() / ".behique_ebay_tokens.json"


class EbayAPIError(Exception):
    """Custom exception for eBay API related errors."""
    pass


class EbayAPIPublisher:
    """
    V2 publisher — creates eBay listings via Sell/Inventory API.

    Matches the same interface as EbayManualPublisher so it plugs
    directly into the existing pipeline:

        publisher = EbayAPIPublisher()
        publisher.authenticate()
        result = publisher.publish(product, content)

    Auto-discovers or creates seller policies (fulfillment, payment, return)
    on first use. Ships from Puerto Rico (00901), free shipping baked into price.
    """

    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.dev_id = os.getenv("EBAY_DEV_ID")
        self.environment = os.getenv("EBAY_ENVIRONMENT", "sandbox")

        if self.environment == "production":
            self.base_url = "https://api.ebay.com"
            self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            self.listing_base = "https://www.ebay.com/itm"
        else:
            self.base_url = "https://api.sandbox.ebay.com"
            self.auth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            self.listing_base = "https://www.sandbox.ebay.com/itm"

        self.marketplace_id = "EBAY_US"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        # Token state — populated by _load_tokens()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_in: int = 7200
        self.obtained_at: float = 0

        # Policy IDs — populated by _ensure_policies()
        self.fulfillment_policy_id: Optional[str] = None
        self.payment_policy_id: Optional[str] = None
        self.return_policy_id: Optional[str] = None

        self.scopes = (
            "https://api.ebay.com/oauth/api_scope "
            "https://api.ebay.com/oauth/api_scope/sell.inventory "
            "https://api.ebay.com/oauth/api_scope/sell.account "
            "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
        )

        # Rate limiting — safe default ~2 req/sec
        self.max_retries = 5
        self.base_delay = 1.5
        self.min_request_interval = 0.5
        self._last_request_time: float = 0

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------

    def authenticate(self):
        """
        Set up authenticated session with auto-refresh token management.

        Token loading priority:
        1. Token file (~/.behique_ebay_tokens.json) — preferred, supports refresh
        2. EBAY_USER_TOKEN env var — fallback, no refresh capability

        If the token is expired, it's refreshed automatically before proceeding.
        """
        self._load_tokens()

        if not self.access_token:
            raise EbayAPIError(
                "No eBay tokens found. Run: python ebay_oauth_token.py\n"
                "Or set EBAY_USER_TOKEN environment variable."
            )

        # Refresh if expired
        if self._token_expired():
            self._refresh_access_token()

        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        logger.info(f"Authenticated with eBay API ({self.environment})")
        self._ensure_policies()

    # ---------------------------------------------------------
    # TOKEN MANAGEMENT (auto-refresh middleware)
    # ---------------------------------------------------------

    def _load_tokens(self):
        """
        Load tokens from file or environment variable.

        Token file is preferred because it includes refresh_token and
        obtained_at timestamp for automatic refresh.
        """
        # Try token file first
        if TOKEN_FILE.exists():
            try:
                data = json.loads(TOKEN_FILE.read_text())
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.expires_in = data.get("expires_in", 7200)
                self.obtained_at = data.get("obtained_at", 0)
                logger.info(f"Loaded tokens from {TOKEN_FILE}")
                return
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Token file corrupt: {e}")

        # Fallback to env var (no refresh capability)
        env_token = os.getenv("EBAY_USER_TOKEN")
        if env_token:
            self.access_token = env_token
            self.obtained_at = time.time()
            logger.info("Using EBAY_USER_TOKEN env var (no auto-refresh)")

    def _token_expired(self) -> bool:
        """Check if access token is expired (with 60s safety buffer)."""
        if not self.obtained_at:
            return False  # Can't determine — assume valid
        expires_at = self.obtained_at + self.expires_in - 60
        return time.time() >= expires_at

    def _refresh_access_token(self):
        """
        Refresh the access token using the stored refresh token.

        Refresh tokens last ~18 months. Access tokens expire every ~2 hours.
        This method is called automatically — no manual intervention needed.
        """
        if not self.refresh_token:
            raise EbayAPIError(
                "Access token expired and no refresh token available. "
                "Run: python ebay_oauth_token.py"
            )

        logger.info("Refreshing eBay access token...")

        credentials = f"{self.app_id}:{self.cert_id}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded}",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": self.scopes,
        }

        response = requests.post(self.auth_url, headers=headers, data=data)
        if not response.ok:
            raise EbayAPIError(
                f"Token refresh failed ({response.status_code}): {response.text[:300]}"
            )

        tokens = response.json()

        # Preserve refresh token (eBay doesn't always return it on refresh)
        tokens["refresh_token"] = tokens.get("refresh_token", self.refresh_token)
        tokens["obtained_at"] = time.time()

        # Update instance state
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self.expires_in = tokens.get("expires_in", 7200)
        self.obtained_at = tokens["obtained_at"]

        # Update session header
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

        # Persist to disk
        TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
        TOKEN_FILE.chmod(0o600)
        logger.info("Access token refreshed and saved")

    # ---------------------------------------------------------
    # HTTP HELPER
    # ---------------------------------------------------------

    def _throttle(self):
        """Enforce minimum interval between API requests (~2 req/sec)."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """
        Make an authenticated request to the eBay API.

        Includes:
        1. Pre-flight token expiry check + auto-refresh
        2. Rate limiting (~2 req/sec throttle)
        3. Auto-retry on 401 (token expired mid-request)
        4. Auto-retry on 429 (rate limit) with exponential backoff + jitter
        5. Auto-retry on 5xx (transient eBay errors) with exponential backoff
        """
        # Pre-flight token check
        if self._token_expired():
            self._refresh_access_token()

        url = f"{self.base_url}{path}"
        attempt = 0

        while attempt <= self.max_retries:
            self._throttle()
            response = self.session.request(method, url, **kwargs)
            status = response.status_code
            logger.info(f"{method} {url} → {status}")

            # Success
            if 200 <= status < 300:
                if response.text:
                    return response.json()
                return {}

            # Token expired mid-request
            if status == 401:
                logger.warning("Got 401 — refreshing token and retrying...")
                self._refresh_access_token()
                attempt += 1
                continue

            # Rate limited
            if status == 429:
                delay = self.base_delay * (2 ** attempt) + random.uniform(0.1, 0.5)
                logger.warning(f"Rate limit hit (429). Retry in {delay:.1f}s")
                time.sleep(delay)
                attempt += 1
                continue

            # Transient eBay server errors
            if status >= 500:
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"eBay server error {status}. Retry in {delay:.1f}s")
                time.sleep(delay)
                attempt += 1
                continue

            # Permanent error — don't retry
            error_detail = response.text[:500] if response.text else "No detail"
            raise EbayAPIError(
                f"eBay API error {status} on {method} {path}: {error_detail}"
            )

        raise EbayAPIError(f"Max retries ({self.max_retries}) exceeded on {method} {path}")

    # ---------------------------------------------------------
    # POLICY MANAGEMENT (auto-discover or create)
    # ---------------------------------------------------------

    def _ensure_policies(self):
        """Ensure seller policies exist. Creates defaults if none found."""
        self.fulfillment_policy_id = self._get_or_create_fulfillment_policy()
        self.payment_policy_id = self._get_or_create_payment_policy()
        self.return_policy_id = self._get_or_create_return_policy()
        logger.info(
            f"Policies ready: fulfillment={self.fulfillment_policy_id}, "
            f"payment={self.payment_policy_id}, return={self.return_policy_id}"
        )

    def _get_or_create_fulfillment_policy(self) -> str:
        """Free shipping via USPS from Puerto Rico."""
        data = self._request(
            "GET",
            f"/sell/account/v1/fulfillment_policy?marketplace_id={self.marketplace_id}"
        )
        policies = data.get("fulfillmentPolicies", [])
        if policies:
            return policies[0]["fulfillmentPolicyId"]

        payload = {
            "name": "Merchoo Free Shipping",
            "marketplaceId": self.marketplace_id,
            "categoryTypes": [{"name": "ALL_EXCLUDING_MOTORS_VEHICLES"}],
            "handlingTime": {"value": 1, "unit": "DAY"},
            "shippingOptions": [{
                "optionType": "DOMESTIC",
                "costType": "FLAT_RATE",
                "shippingServices": [{
                    "shippingCarrierCode": "USPS",
                    "shippingServiceCode": "USPSFirstClass",
                    "shippingCost": {"value": "0", "currency": "USD"},
                    "sortOrder": 1,
                    "freeShipping": True,
                }]
            }],
            "shipToLocations": {
                "regionIncluded": [{"regionName": "US"}]
            },
        }
        result = self._request("POST", "/sell/account/v1/fulfillment_policy", json=payload)
        return result["fulfillmentPolicyId"]

    def _get_or_create_payment_policy(self) -> str:
        """eBay managed payments (default for all sellers since 2023)."""
        data = self._request(
            "GET",
            f"/sell/account/v1/payment_policy?marketplace_id={self.marketplace_id}"
        )
        policies = data.get("paymentPolicies", [])
        if policies:
            return policies[0]["paymentPolicyId"]

        payload = {
            "name": "Merchoo Payments",
            "marketplaceId": self.marketplace_id,
            "categoryTypes": [{"name": "ALL_EXCLUDING_MOTORS_VEHICLES"}],
            "paymentMethods": [{"paymentMethodType": "EBAY_PAYMENTS"}],
        }
        result = self._request("POST", "/sell/account/v1/payment_policy", json=payload)
        return result["paymentPolicyId"]

    def _get_or_create_return_policy(self) -> str:
        """30-day returns, buyer pays return shipping."""
        data = self._request(
            "GET",
            f"/sell/account/v1/return_policy?marketplace_id={self.marketplace_id}"
        )
        policies = data.get("returnPolicies", [])
        if policies:
            return policies[0]["returnPolicyId"]

        payload = {
            "name": "Merchoo Returns",
            "marketplaceId": self.marketplace_id,
            "categoryTypes": [{"name": "ALL_EXCLUDING_MOTORS_VEHICLES"}],
            "returnsAccepted": True,
            "returnPeriod": {"value": 30, "unit": "DAY"},
            "returnShippingCostPayer": "BUYER",
        }
        result = self._request("POST", "/sell/account/v1/return_policy", json=payload)
        return result["returnPolicyId"]

    # ---------------------------------------------------------
    # INVENTORY ITEM
    # ---------------------------------------------------------

    def create_inventory_item(self, sku: str, product: ProductInput, content: ListingContent) -> str:
        """
        Create or replace an inventory item on eBay.

        Endpoint: PUT /sell/inventory/v1/inventory_item/{sku}
        """
        # Build aspects dict — eBay wants {"Brand": ["BrandName"]}
        aspects = {}
        for key, val in content.item_specifics.items():
            if key != "Category":
                aspects[key] = [val] if isinstance(val, str) else val

        payload = {
            "product": {
                "title": content.title,
                "description": content.description,
                "aspects": aspects,
                "imageUrls": product.image_urls if hasattr(product, "image_urls") else [],
            },
            "condition": self._map_condition(content.suggested_condition),
            "availability": {
                "shipToLocationAvailability": {
                    "quantity": product.quantity if hasattr(product, "quantity") else 1
                }
            },
        }

        self._request("PUT", f"/sell/inventory/v1/inventory_item/{sku}", json=payload)
        logger.info(f"Inventory item created: {sku}")
        return sku

    # ---------------------------------------------------------
    # OFFER
    # ---------------------------------------------------------

    def create_offer(self, sku: str, content: ListingContent, category_id: str = None) -> str:
        """
        Create an offer for an inventory item.

        Endpoint: POST /sell/inventory/v1/offer
        """
        payload = {
            "sku": sku,
            "marketplaceId": self.marketplace_id,
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "pricingSummary": {
                "price": {
                    "value": str(content.suggested_price),
                    "currency": "USD",
                }
            },
            "listingPolicies": {
                "fulfillmentPolicyId": self.fulfillment_policy_id,
                "paymentPolicyId": self.payment_policy_id,
                "returnPolicyId": self.return_policy_id,
            },
        }

        if category_id:
            payload["categoryId"] = category_id

        result = self._request("POST", "/sell/inventory/v1/offer", json=payload)
        offer_id = result["offerId"]
        logger.info(f"Offer created: {offer_id}")
        return offer_id

    # ---------------------------------------------------------
    # PUBLISH
    # ---------------------------------------------------------

    def publish_offer(self, offer_id: str) -> str:
        """
        Publish an offer to make the listing live on eBay.

        Endpoint: POST /sell/inventory/v1/offer/{offerId}/publish
        """
        result = self._request("POST", f"/sell/inventory/v1/offer/{offer_id}/publish")
        listing_id = result.get("listingId", "")
        logger.info(f"Listing published: {listing_id}")
        return listing_id

    # ---------------------------------------------------------
    # FULL PIPELINE (matches EbayManualPublisher interface)
    # ---------------------------------------------------------

    def publish(self, product: ProductInput, content: ListingContent) -> PublishedListing:
        """
        Full pipeline: inventory item → offer → publish → return result.

        Compatible with EbayManualPublisher.publish() signature so it
        drops directly into the existing ListingPipeline.
        """
        sku = f"MERCHOO-{uuid.uuid4().hex[:8].upper()}"

        # Get category ID from item specifics if available
        category_id = content.item_specifics.get("Category ID")

        # Step 1: Create inventory item
        self.create_inventory_item(sku, product, content)

        # Step 2: Create offer
        offer_id = self.create_offer(sku, content, category_id)

        # Step 3: Publish
        listing_id = self.publish_offer(offer_id)
        listing_url = f"{self.listing_base}/{listing_id}" if listing_id else ""

        return PublishedListing(
            platform="ebay",
            listing_id=listing_id or f"DRAFT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            listing_url=listing_url,
            title=content.title,
            price=content.suggested_price,
            status="published" if listing_id else "failed",
            raw_response={
                "sku": sku,
                "offer_id": offer_id,
                "listing_id": listing_id,
                "environment": self.environment,
            },
        )

    # ---------------------------------------------------------
    # DRAFT PREVIEW (QA before publishing)
    # ---------------------------------------------------------

    def create_draft_preview(self, product: ProductInput, content: ListingContent) -> str:
        """
        Create a draft listing for preview without publishing live.

        Creates inventory item + draft offer, returns preview URL.
        Draft offers are NOT visible to buyers.
        You can update the draft and publish later with publish_offer().

        Returns: preview URL string
        """
        sku = f"MERCHOO-DRAFT-{uuid.uuid4().hex[:8].upper()}"
        category_id = content.item_specifics.get("Category ID")

        # Create inventory item
        self.create_inventory_item(sku, product, content)

        # Create offer in DRAFT status
        payload = {
            "sku": sku,
            "marketplaceId": self.marketplace_id,
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "pricingSummary": {
                "price": {
                    "value": str(content.suggested_price),
                    "currency": "USD",
                }
            },
            "listingPolicies": {
                "fulfillmentPolicyId": self.fulfillment_policy_id,
                "paymentPolicyId": self.payment_policy_id,
                "returnPolicyId": self.return_policy_id,
            },
        }
        if category_id:
            payload["categoryId"] = category_id

        result = self._request("POST", "/sell/inventory/v1/offer", json=payload)
        offer_id = result["offerId"]

        if self.environment == "production":
            preview_url = f"https://www.ebay.com/sh/lst/{offer_id}"
        else:
            preview_url = f"https://www.sandbox.ebay.com/sh/lst/{offer_id}"

        logger.info(f"Draft preview created: {preview_url}")
        return preview_url

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _map_condition(condition_str: str) -> str:
        """Map human condition strings to eBay condition enums."""
        mapping = {
            "New": "NEW",
            "Used": "USED_EXCELLENT",
            "Refurbished": "SELLER_REFURBISHED",
            "For Parts": "FOR_PARTS_OR_NOT_WORKING",
        }
        return mapping.get(condition_str, "USED_EXCELLENT")


# ---------------------------------------------------------
# SANDBOX TEST
# ---------------------------------------------------------

def test_sandbox():
    """
    End-to-end sandbox test. Creates a test listing.

    Before running:
        export EBAY_APP_ID=KalaniGo-AppID-SBX-...
        export EBAY_CERT_ID=SBX-...
        export EBAY_DEV_ID=deefbea6-...
        export EBAY_ENVIRONMENT=sandbox
        export EBAY_USER_TOKEN=v^1.1#i^1#...  (get from developer.ebay.com)
    """
    publisher = EbayAPIPublisher()
    publisher.authenticate()

    # Create test product using our pipeline types
    product = ProductInput(
        name="Test API Listing — Sandbox",
        condition="New",
        category="Test",
    )

    content = ListingContent(
        title="Test API Listing Sandbox Verification",
        description="<p>Sandbox test listing created via eBay Sell API.</p>",
        suggested_price=9.99,
        suggested_condition="New",
        item_specifics={"Brand": "Test"},
        keywords=["test", "sandbox"],
    )

    result = publisher.publish(product, content)
    print(f"\n✅ Listing created!")
    print(f"   ID:  {result.listing_id}")
    print(f"   URL: {result.listing_url}")
    print(f"   Status: {result.status}")


if __name__ == "__main__":
    test_sandbox()
