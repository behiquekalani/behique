"""
eBay OAuth2 client — STUB until API approval (Monday).
Will handle authentication for Browse API.
"""

import logging

logger = logging.getLogger(__name__)


class EbayClient:

    def __init__(self, app_id=None, cert_id=None, dev_id=None):
        self.app_id = app_id
        self.cert_id = cert_id
        self.dev_id = dev_id
        self.token = None

    def authenticate(self):
        """
        OAuth2 Client Credentials flow for eBay Browse API.
        POST to https://api.ebay.com/identity/v1/oauth2/token
        with base64(app_id:cert_id)
        """
        logger.info("eBay authentication: STUB -- awaiting API approval")
        raise NotImplementedError("eBay API keys pending -- expected Monday 2026-03-16")

    def get_headers(self):
        if not self.token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
