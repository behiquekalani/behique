#!/usr/bin/env python3
"""
lead_magnet_delivery.py — Webhook handler for lead magnet signups.

FastAPI endpoint on port 8098.
- POST /signup — receives email, pushes subscriber to Beehiiv, logs to leads.json
- GET  /health — health check
- GET  /stats  — lead count and recent signups

Sends Telegram notification on each new signup.

Env vars:
    BEEHIIV_API_KEY            - Beehiiv API key
    BEEHIIV_PUBLICATION_ID     - Beehiiv publication ID
    TELEGRAM_BOT_TOKEN         - Telegram bot token for notifications
    TELEGRAM_CHAT_ID           - Telegram chat ID for notifications

CLI:
    python3 lead_magnet_delivery.py                   # start server on port 8098
    python3 lead_magnet_delivery.py --port 9000        # custom port

Dependencies: pip install fastapi uvicorn requests
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("[lead_magnet] fastapi/uvicorn not installed — run: pip install fastapi uvicorn")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("[lead_magnet] requests not installed — run: pip install requests")
    sys.exit(1)


# ── Config ─────────────────────────────────────────────────────────────────────

BIOS_ROOT = Path(__file__).parent.parent
LEADS_DIR = BIOS_ROOT / "analytics" / "data"
LEADS_FILE = LEADS_DIR / "leads.json"
LOGS_DIR = Path(__file__).parent / "logs"

BEEHIIV_API_KEY = os.environ.get("BEEHIIV_API_KEY", "")
BEEHIIV_PUB_ID = os.environ.get("BEEHIIV_PUBLICATION_ID", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

app = FastAPI(title="Behike Lead Magnet", version="1.0")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_leads():
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE) as f:
        return json.load(f)


def _save_leads(leads):
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)


def _log(event, data):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "leads.log"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "data": data,
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _push_to_beehiiv(email, utm_source="lead_magnet"):
    """Add subscriber to Beehiiv publication."""
    if not BEEHIIV_API_KEY or not BEEHIIV_PUB_ID:
        return {"status": "skipped", "reason": "no_api_key"}

    try:
        url = f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB_ID}/subscriptions"
        headers = {
            "Authorization": f"Bearer {BEEHIIV_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "reactivate_existing": True,
            "send_welcome_email": True,
            "utm_source": utm_source,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return {"status": "ok", "beehiiv": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "reason": str(e)}


def _send_telegram_notification(email, source=""):
    """Notify via Telegram on new signup."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = (
        f"New lead signup\n"
        f"Email: {email}\n"
        f"Source: {source or 'direct'}\n"
        f"Time: {now}"
    )

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=10)
    except requests.RequestException:
        pass  # non-critical, don't break signup flow


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.post("/signup")
async def signup(body: dict):
    """Handle new lead magnet signup."""
    email = body.get("email", "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    source = body.get("source", "lead_magnet")
    name = body.get("name", "")
    now = datetime.now(timezone.utc).isoformat()

    # Check for duplicate
    leads = _load_leads()
    existing_emails = {l["email"] for l in leads}
    if email in existing_emails:
        return JSONResponse({"status": "exists", "message": "Already subscribed"})

    # Record lead
    lead = {
        "email": email,
        "name": name,
        "source": source,
        "signed_up_at": now,
        "beehiiv_synced": False,
    }

    # Push to Beehiiv
    beehiiv_result = _push_to_beehiiv(email, utm_source=source)
    if beehiiv_result.get("status") == "ok":
        lead["beehiiv_synced"] = True

    # Save
    leads.append(lead)
    _save_leads(leads)
    _log("signup", {"email": email, "source": source, "beehiiv": beehiiv_result.get("status")})

    # Telegram notification
    _send_telegram_notification(email, source)

    return JSONResponse({
        "status": "ok",
        "message": "Subscribed successfully",
        "beehiiv": beehiiv_result.get("status", "skipped"),
    })


@app.get("/health")
async def health():
    return {"status": "ok", "service": "behike-leads", "port": 8098}


@app.get("/stats")
async def stats():
    leads = _load_leads()
    recent = leads[-10:] if leads else []
    return {
        "total_leads": len(leads),
        "recent": [{"email": l["email"][:3] + "***", "source": l.get("source", ""), "date": l.get("signed_up_at", "")} for l in recent],
        "beehiiv_synced": sum(1 for l in leads if l.get("beehiiv_synced")),
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    port = 8098
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    print(f"[behike-leads] Starting on port {port}")
    print(f"[behike-leads] Beehiiv sync: {'enabled' if BEEHIIV_API_KEY else 'disabled'}")
    print(f"[behike-leads] Telegram:     {'enabled' if TELEGRAM_BOT_TOKEN else 'disabled'}")
    print()

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
