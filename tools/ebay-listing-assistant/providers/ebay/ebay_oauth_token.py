"""
Standalone eBay OAuth helper.

Run once to generate a user token and refresh token.

Steps:
    1. Generate consent URL
    2. Login to eBay and approve access
    3. Paste authorization code
    4. Script exchanges code for tokens
    5. Tokens saved to ~/.behique_ebay_tokens.json

Supports refresh tokens so you don't need to repeat OAuth flow.

Usage:
    export EBAY_APP_ID=KalaniGo-AppID-PRD-...
    export EBAY_CERT_ID=PRD-...
    export EBAY_REDIRECT_URI=https://localhost
    export EBAY_ENVIRONMENT=sandbox  (or production)

    python ebay_oauth_token.py
"""

import os
import base64
import json
import requests
from pathlib import Path
from urllib.parse import urlencode


# Store tokens securely in home directory, not in repo
TOKEN_FILE = Path.home() / ".behique_ebay_tokens.json"


class EbayOAuthHelper:

    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.redirect_uri = os.getenv("EBAY_REDIRECT_URI", "https://localhost")
        self.environment = os.getenv("EBAY_ENVIRONMENT", "sandbox")

        if self.environment == "production":
            self.base_identity = "https://api.ebay.com/identity/v1/oauth2/token"
            self.auth_url = "https://auth.ebay.com/oauth2/authorize"
        else:
            self.base_identity = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            self.auth_url = "https://auth.sandbox.ebay.com/oauth2/authorize"

        self.scopes = [
            "https://api.ebay.com/oauth/api_scope",
            "https://api.ebay.com/oauth/api_scope/sell.inventory",
            "https://api.ebay.com/oauth/api_scope/sell.account",
            "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
        ]

    # ---------------------------------------------------------
    # CONSENT URL
    # ---------------------------------------------------------

    def generate_consent_url(self) -> str:
        """Generate the eBay OAuth consent URL for user authorization."""
        params = {
            "client_id": self.app_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
        }
        return f"{self.auth_url}?{urlencode(params)}"

    # ---------------------------------------------------------
    # TOKEN EXCHANGE
    # ---------------------------------------------------------

    def exchange_code(self, code: str) -> dict:
        """Exchange authorization code for access + refresh tokens."""
        credentials = f"{self.app_id}:{self.cert_id}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded}",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(self.base_identity, headers=headers, data=data)
        if not response.ok:
            raise Exception(f"OAuth exchange failed ({response.status_code}): {response.text}")

        tokens = response.json()
        self.save_tokens(tokens)
        return tokens

    # ---------------------------------------------------------
    # REFRESH TOKEN
    # ---------------------------------------------------------

    def refresh_access_token(self, refresh_token: str = None) -> dict:
        """
        Use refresh token to get a new access token.

        Access tokens expire every ~2 hours.
        Refresh tokens last ~18 months.
        """
        if refresh_token is None:
            saved = self.load_tokens()
            if saved and "refresh_token" in saved:
                refresh_token = saved["refresh_token"]
            else:
                raise Exception("No refresh token available. Run full OAuth flow first.")

        credentials = f"{self.app_id}:{self.cert_id}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded}",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": " ".join(self.scopes),
        }

        response = requests.post(self.base_identity, headers=headers, data=data)
        if not response.ok:
            raise Exception(f"Token refresh failed ({response.status_code}): {response.text}")

        tokens = response.json()
        # Preserve the refresh token (eBay doesn't always return it on refresh)
        if "refresh_token" not in tokens:
            tokens["refresh_token"] = refresh_token
        self.save_tokens(tokens)
        return tokens

    # ---------------------------------------------------------
    # TOKEN STORAGE
    # ---------------------------------------------------------

    def save_tokens(self, tokens: dict):
        """Save tokens to secure file in home directory."""
        TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
        TOKEN_FILE.chmod(0o600)
        print(f"\nTokens saved to {TOKEN_FILE}")

    def load_tokens(self) -> dict | None:
        """Load previously saved tokens."""
        if not TOKEN_FILE.exists():
            return None
        return json.loads(TOKEN_FILE.read_text())

    def get_valid_token(self) -> str:
        """
        Get a valid access token — refreshes automatically if needed.

        Use this in EbayAPIPublisher instead of reading EBAY_USER_TOKEN directly.
        """
        saved = self.load_tokens()
        if not saved:
            raise Exception("No tokens found. Run: python ebay_oauth_token.py")

        # Try the saved access token first
        # If it fails, the publisher's _request() will catch 401 and call refresh
        return saved.get("access_token", "")


# ---------------------------------------------------------
# MAIN FLOW
# ---------------------------------------------------------

def main():
    oauth = EbayOAuthHelper()

    if not oauth.app_id or not oauth.cert_id:
        print("ERROR: Set EBAY_APP_ID and EBAY_CERT_ID environment variables first.")
        print("\nQuick setup:")
        print("  export EBAY_APP_ID=KalaniGo-AppID-SBX-...")
        print("  export EBAY_CERT_ID=SBX-...")
        print("  export EBAY_ENVIRONMENT=sandbox")
        return

    # Check if we already have tokens and just need a refresh
    existing = oauth.load_tokens()
    if existing and "refresh_token" in existing:
        print("Found existing tokens. Refreshing access token...")
        try:
            tokens = oauth.refresh_access_token()
            print("\n✅ Access token refreshed!")
            print(f"\nEBAY_USER_TOKEN={tokens['access_token'][:50]}...")
            return
        except Exception as e:
            print(f"Refresh failed: {e}")
            print("Running full OAuth flow...\n")

    print("=" * 50)
    print("  eBay OAuth Setup — One-Time Authorization")
    print("=" * 50)

    print(f"\nEnvironment: {oauth.environment.upper()}")
    print(f"Redirect URI: {oauth.redirect_uri}")

    print("\nSTEP 1 — Open this URL in your browser:\n")
    print(oauth.generate_consent_url())

    print("\nSTEP 2 — Login to eBay and approve access.")
    print("You'll be redirected to your redirect URI.")
    print("Copy the 'code' parameter from the URL bar.")
    print("\nExample: https://localhost/?code=v%5E1.1%23...")
    print("Copy everything after 'code=' (URL decode if needed)\n")

    code = input("Paste authorization code here:\n> ").strip()

    if not code:
        print("No code provided. Aborting.")
        return

    tokens = oauth.exchange_code(code)

    print("\n✅ Authorization complete!")
    print(f"\nAccess Token (first 50 chars): {tokens['access_token'][:50]}...")
    print(f"Refresh Token saved for future use.")
    print(f"\nTo use in publisher:")
    print(f"  export EBAY_USER_TOKEN={tokens['access_token'][:30]}...")
    print(f"\nOr let the publisher load from {TOKEN_FILE} automatically.")


if __name__ == "__main__":
    main()
