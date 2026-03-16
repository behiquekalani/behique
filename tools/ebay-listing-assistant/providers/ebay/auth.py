"""
eBay OAuth2 authentication — Client Credentials flow.
Used by both research and publishing adapters.

Docs: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html
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


class EbayAuth:
    """
    Handles OAuth2 Client Credentials grant for eBay APIs.
    Token is cached and auto-refreshed when expired.
    """

    def __init__(self, app_id=None, cert_id=None, dev_id=None, sandbox=True):
        self.app_id = app_id or os.environ.get("EBAY_APP_ID")
        self.cert_id = cert_id or os.environ.get("EBAY_CERT_ID")
        self.dev_id = dev_id or os.environ.get("EBAY_DEV_ID")
        self.sandbox = sandbox

        self._token = None
        self._token_expiry = 0

        if not self.app_id or not self.cert_id:
            logger.warning("eBay API credentials not set. Set EBAY_APP_ID and EBAY_CERT_ID env vars.")

    @property
    def api_base(self):
        return SANDBOX_API_BASE if self.sandbox else PRODUCTION_API_BASE

    @property
    def auth_url(self):
        return SANDBOX_AUTH_URL if self.sandbox else PRODUCTION_AUTH_URL

    def get_token(self) -> str:
        """Get a valid access token, refreshing if expired."""
        if self._token and time.time() < self._token_expiry:
            return self._token

        return self._authenticate()

    def _authenticate(self) -> str:
        """
        OAuth2 Client Credentials flow.
        POST base64(app_id:cert_id) to token endpoint.
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
        resp.raise_for_status()

        data = resp.json()
        self._token = data["access_token"]
        # Buffer 60 seconds before actual expiry
        self._token_expiry = time.time() + data.get("expires_in", 7200) - 60

        logger.info("eBay auth successful. Token cached.")
        return self._token

    def get_headers(self) -> dict:
        """Return headers dict ready for API calls."""
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }
