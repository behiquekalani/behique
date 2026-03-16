"""
eBay OAuth2 authentication — Client Credentials + User Token support.
Used by both research and publishing adapters.

Client Credentials flow: for public API calls (Browse API, search).
User Token: for seller-context calls (Inventory API, publishing).

Docs: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html
Docs: https://developer.ebay.com/api-docs/static/oauth-authorization-code-grant.html
"""

import base64
import logging
import os
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

SANDBOX_AUTH_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
PRODUCTION_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"

SANDBOX_API_BASE = "https://api.sandbox.ebay.com"
PRODUCTION_API_BASE = "https://api.ebay.com"

# Scopes needed for Inventory API (selling)
SELL_SCOPES = (
    "https://api.ebay.com/oauth/api_scope "
    "https://api.ebay.com/oauth/api_scope/sell.inventory "
    "https://api.ebay.com/oauth/api_scope/sell.account "
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
)


class EbayAuth:
    """
    Handles OAuth2 authentication for eBay APIs.

    Two token modes:
    1. Client Credentials (app token) — for Browse API, public searches.
    2. User Token — for Inventory API, publishing. Requires EBAY_USER_TOKEN env var.
       This token comes from the Authorization Code flow (browser-based, one-time).
    """

    def __init__(self, app_id=None, cert_id=None, dev_id=None, sandbox=True):
        self.app_id = app_id or os.environ.get("EBAY_APP_ID")
        self.cert_id = cert_id or os.environ.get("EBAY_CERT_ID")
        self.dev_id = dev_id or os.environ.get("EBAY_DEV_ID")
        self.sandbox = sandbox

        # User token for seller-context API calls (Inventory API)
        env_key = "EBAY_ENVIRONMENT"
        env_val = os.environ.get(env_key, "sandbox").lower()
        if env_val == "production":
            self.sandbox = False

        self.user_token = os.environ.get("EBAY_USER_TOKEN")

        self._app_token = None
        self._app_token_expiry = 0

        if not self.app_id or not self.cert_id:
            logger.warning("eBay API credentials not set. Set EBAY_APP_ID and EBAY_CERT_ID env vars.")

    @property
    def api_base(self):
        return SANDBOX_API_BASE if self.sandbox else PRODUCTION_API_BASE

    @property
    def auth_url(self):
        return SANDBOX_AUTH_URL if self.sandbox else PRODUCTION_AUTH_URL

    def get_app_token(self) -> str:
        """Get a valid application token (Client Credentials), refreshing if expired."""
        if self._app_token and time.time() < self._app_token_expiry:
            return self._app_token

        return self._authenticate_client_credentials()

    def get_user_token(self) -> str:
        """
        Get user token for seller-context calls.
        For now this reads from EBAY_USER_TOKEN env var.
        Future: implement refresh token flow.
        """
        if not self.user_token:
            raise RuntimeError(
                "eBay user token not configured. "
                "Set EBAY_USER_TOKEN environment variable. "
                "Get it from: https://developer.ebay.com/my/keys (User Tokens tab)"
            )
        return self.user_token

    def get_token(self) -> str:
        """
        Get the best available token.
        Prefers user token (needed for Inventory API), falls back to app token.
        """
        if self.user_token:
            return self.user_token
        return self.get_app_token()

    def _authenticate_client_credentials(self) -> str:
        """
        OAuth2 Client Credentials flow.
        POST base64(app_id:cert_id) to token endpoint.
        Returns an application-level access token.
        """
        if not self.app_id or not self.cert_id:
            raise RuntimeError(
                "eBay API keys not configured. "
                "Set EBAY_APP_ID and EBAY_CERT_ID environment variables, "
                "or pass them to EbayAuth()."
            )

        credentials = base64.b64encode(
            f"{self.app_id}:{self.cert_id}".encode()
        ).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}",
        }

        body = urlencode({
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        })

        logger.info(f"Authenticating with eBay ({'sandbox' if self.sandbox else 'production'})...")

        resp = requests.post(self.auth_url, headers=headers, data=body, timeout=15)

        if not resp.ok:
            logger.error(f"eBay auth failed: {resp.status_code} — {resp.text}")
            resp.raise_for_status()

        data = resp.json()
        self._app_token = data["access_token"]
        # Buffer 60 seconds before actual expiry
        self._app_token_expiry = time.time() + data.get("expires_in", 7200) - 60

        logger.info("eBay auth successful. App token cached.")
        return self._app_token

    def get_headers(self) -> dict:
        """Return headers dict ready for API calls."""
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }

    def get_seller_headers(self) -> dict:
        """Return headers with user token specifically for seller API calls."""
        return {
            "Authorization": f"Bearer {self.get_user_token()}",
            "Content-Type": "application/json",
            "Content-Language": "en-US",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }
