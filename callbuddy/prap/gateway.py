"""
PRAP Gateway
Puerto Rico Agentic Protocol - FastAPI gateway that receives agent requests,
validates identity, checks scope, and routes to the appropriate handler.

If an agency has an MCP endpoint configured, route there.
Otherwise, trigger Shadow Protocol (CallBuddy voice fallback).

Run: uvicorn callbuddy.prap.gateway:app --port 8095
"""

import os
import json
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional

from callbuddy.prap.identity_signer import verify_passport
from callbuddy.prap.pr_mapping import translate_intent, get_ivr_path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
AUDIT_LOG_PATH = Path(__file__).parent / "audit_log.json"

# Agencies with MCP endpoints (add real endpoints as they become available).
# If an agency is listed here, requests route to MCP instead of Shadow Protocol.
MCP_ENDPOINTS = {
    # "CESCO": "http://localhost:9001/mcp",  # example - uncomment when live
}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="PRAP Gateway",
    description="Puerto Rico Agentic Protocol - Agent request gateway",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class PrapIdentity(BaseModel):
    passport_token: str
    did: Optional[str] = None


class PrapIntent(BaseModel):
    domain: str
    action: str
    params: Optional[dict] = None


class PrapConstraints(BaseModel):
    max_wait_seconds: int = 300
    preferred_language: str = "es"
    fallback_allowed: bool = True
    require_confirmation: bool = True


class PrapRequest(BaseModel):
    protocol_version: str = "1.0"
    transaction_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    identity: PrapIdentity
    intent: PrapIntent
    constraints: Optional[PrapConstraints] = PrapConstraints()


# ---------------------------------------------------------------------------
# Audit log helpers
# ---------------------------------------------------------------------------
def _load_audit_log() -> list:
    """Load existing audit log from disk."""
    if AUDIT_LOG_PATH.exists():
        try:
            with open(AUDIT_LOG_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_audit_log(log: list):
    """Persist audit log to disk."""
    with open(AUDIT_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2, default=str)


def _append_audit(entry: dict):
    """Add an entry to the audit log and save."""
    log = _load_audit_log()
    log.append(entry)
    _save_audit_log(log)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.post("/agent/v1/request")
async def handle_request(req: PrapRequest):
    """
    Main PRAP endpoint. Receives a request from an agent, validates
    the JWT passport, checks scope against PR_GOV_MAPPING, and routes
    to either an MCP endpoint or Shadow Protocol (CallBuddy).
    """
    # 1. Validate the JWT passport
    try:
        decoded = verify_passport(req.identity.passport_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Passport verification failed: {str(e)}")

    # 2. Check that the scope in the token matches the requested action
    token_scope = decoded.get("scope", "")
    if token_scope != req.intent.action:
        raise HTTPException(
            status_code=403,
            detail=f"Scope mismatch: token scope '{token_scope}' does not match action '{req.intent.action}'",
        )

    # 3. Look up the action in PR government mapping
    mapping = translate_intent(req.intent.action)
    if not mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action: '{req.intent.action}'. Check pr_mapping.py for valid actions.",
        )

    # 4. Determine routing: MCP endpoint or Shadow Protocol
    agency = mapping["agency"]
    route_method = "mcp" if agency in MCP_ENDPOINTS else "shadow_protocol"

    # 5. Build the response
    transaction_id = req.transaction_id or str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    result = {
        "transaction_id": transaction_id,
        "status": "accepted",
        "route": route_method,
        "agency": agency,
        "action": req.intent.action,
        "es_term": mapping["es_term"],
        "timestamp": timestamp,
    }

    # Add routing details based on method
    if route_method == "mcp":
        result["mcp_endpoint"] = MCP_ENDPOINTS[agency]
        result["message"] = f"Request routed to {agency} MCP endpoint."
    else:
        # Shadow Protocol: CallBuddy voice fallback
        result["phone_number"] = mapping["phone_number"]
        result["ivr_path"] = mapping["ivr_path"]
        result["required_docs"] = mapping["required_docs"]
        result["message"] = (
            f"No MCP endpoint for {agency}. "
            f"Shadow Protocol activated - CallBuddy will call {mapping['phone_number']} "
            f"and navigate IVR with DTMF: {mapping['ivr_path']}"
        )

    # 6. Log to audit trail
    audit_entry = {
        "transaction_id": transaction_id,
        "timestamp": timestamp,
        "user": decoded.get("sub", "unknown"),
        "agency": agency,
        "action": req.intent.action,
        "route": route_method,
        "status": "accepted",
        "token_jti": decoded.get("jti", ""),
    }
    _append_audit(audit_entry)

    return result


@app.get("/agent/v1/status/{transaction_id}")
async def check_status(transaction_id: str):
    """
    Check the status of a PRAP transaction by its ID.
    Looks up the transaction in the audit log.
    """
    log = _load_audit_log()

    # Find the transaction
    matches = [entry for entry in log if entry.get("transaction_id") == transaction_id]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")

    # Return the most recent entry for this transaction
    latest = matches[-1]
    return {
        "transaction_id": transaction_id,
        "status": latest.get("status", "unknown"),
        "agency": latest.get("agency", ""),
        "action": latest.get("action", ""),
        "route": latest.get("route", ""),
        "timestamp": latest.get("timestamp", ""),
    }


@app.get("/agent/v1/audit")
async def view_audit():
    """
    View the last 50 transactions in the audit log.
    """
    log = _load_audit_log()
    # Return last 50 entries, newest first
    return {
        "total": len(log),
        "showing": min(len(log), 50),
        "entries": log[-50:][::-1],
    }


# ---------------------------------------------------------------------------
# Run directly for development
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting PRAP Gateway on port 8095...")
    uvicorn.run(app, host="0.0.0.0", port=8095)
