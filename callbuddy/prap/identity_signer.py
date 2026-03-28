"""
PRAP Identity Signer
Puerto Rico Agentic Protocol - JWT-based agent passport system.

Generates and verifies short-lived JWT tokens that authenticate
an AI agent's identity and scope when interacting with PR government agencies.
"""

import os
import jwt
import time
import uuid
import argparse
from datetime import datetime, timezone


# Default secret key: pulled from env or fallback for local dev.
# In production, PRAP_SECRET_KEY must be set as an environment variable.
DEFAULT_SECRET = os.environ.get("PRAP_SECRET_KEY", "dev_secret_key")

# Token lifetime: 5 minutes (300 seconds)
TOKEN_EXPIRY_SECONDS = 300


def create_agent_passport(
    user_id: str,
    target_agency: str,
    scope: str,
    secret_key: str = None,
) -> str:
    """
    Generate a signed JWT passport for an agent acting on behalf of a user.

    Args:
        user_id: The user identifier (e.g. phone number, citizen ID).
        target_agency: The PR government agency being contacted (e.g. CESCO, HACIENDA).
        scope: The action being requested (e.g. renew_marbete, pay_fine).
        secret_key: Optional override for the signing key.

    Returns:
        Encoded JWT string.
    """
    key = secret_key or DEFAULT_SECRET
    now = time.time()

    payload = {
        # Issuer: the BIOS framework that spawned this agent
        "iss": "BIOS_FRAMEWORK_PR",
        # Subject: the user's agent identity
        "sub": f"agent:{user_id}",
        # Audience: which agency this passport is valid for
        "aud": target_agency,
        # Scope: what the agent is authorized to do
        "scope": scope,
        # Issued at
        "iat": int(now),
        # Expiration: 5 minutes from now
        "exp": int(now + TOKEN_EXPIRY_SECONDS),
        # Unique transaction reference
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(payload, key, algorithm="HS256")
    return token


def verify_passport(token: str, secret_key: str = None) -> dict:
    """
    Verify and decode a PRAP agent passport.

    Args:
        token: The JWT string to verify.
        secret_key: Optional override for the verification key.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.ExpiredSignatureError: Token has expired.
        jwt.InvalidTokenError: Token is malformed or signature is invalid.
    """
    key = secret_key or DEFAULT_SECRET

    # Decode without audience validation since the audience varies per agency
    decoded = jwt.decode(
        token,
        key,
        algorithms=["HS256"],
        options={"verify_aud": False},
    )
    return decoded


# ---------------------------------------------------------------------------
# CLI mode: quick passport generation for testing
# Usage: python3 identity_signer.py --user 787123 --agency CESCO --scope renew_marbete
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PRAP Identity Signer - Generate agent passports")
    parser.add_argument("--user", required=True, help="User ID (e.g. phone number)")
    parser.add_argument("--agency", required=True, help="Target agency (e.g. CESCO, HACIENDA)")
    parser.add_argument("--scope", required=True, help="Action scope (e.g. renew_marbete)")
    parser.add_argument("--secret", default=None, help="Override secret key (default: env or dev key)")
    args = parser.parse_args()

    token = create_agent_passport(args.user, args.agency, args.scope, args.secret)
    print(f"\n--- PRAP Agent Passport ---")
    print(f"Token: {token}\n")

    # Verify it immediately to show the payload
    decoded = verify_passport(token, args.secret)
    print(f"Decoded payload:")
    for k, v in decoded.items():
        label = k
        if k == "iat":
            v = f"{v} ({datetime.fromtimestamp(v, tz=timezone.utc).isoformat()})"
        elif k == "exp":
            v = f"{v} ({datetime.fromtimestamp(v, tz=timezone.utc).isoformat()})"
        print(f"  {label}: {v}")
