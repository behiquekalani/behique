#!/usr/bin/env python3
"""
Gumroad Webhook Receiver & Auto-Delivery Server

Receives Gumroad sale pings, logs to analytics, sends Telegram notifications,
and stores raw webhook data for audit.

Run:
    uvicorn webhook_server:app --host 0.0.0.0 --port 8097
    # or
    python3 webhook_server.py

Env vars:
    TELEGRAM_BOT_TOKEN      - Telegram bot token
    TELEGRAM_CHAT_ID        - Telegram chat/group ID
    GUMROAD_WEBHOOK_SECRET  - (optional) shared secret for webhook validation
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
WEBHOOKS_DIR = SALES_DIR / "webhooks"
WEBHOOKS_DIR.mkdir(parents=True, exist_ok=True)

# Analytics tracker lives at bios/analytics/tracker.py
ANALYTICS_DIR = SALES_DIR.parent / "analytics"
sys.path.insert(0, str(ANALYTICS_DIR))

try:
    from tracker import log_sale, daily_report
except ImportError:
    def log_sale(product, price, platform, customer_email=None):
        print(f"[fallback] Sale: {product} ${price} on {platform} ({customer_email})")
        return {"product": product, "price": price}

    def daily_report():
        return {"today_sales_count": 0, "today_revenue": 0}

# Notifier lives in the same directory
from notifier import send_sale_notification

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WEBHOOK_SECRET = os.environ.get("GUMROAD_WEBHOOK_SECRET", "")

# In-memory recent sales buffer (last 50)
recent_sales: list[dict] = []
MAX_RECENT = 50

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Gumroad Webhook Receiver",
    version="1.0.0",
    docs_url="/docs",
)


def _save_raw_webhook(data: dict) -> str:
    """Save raw webhook payload to disk for audit. Returns filename."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    filename = f"raw-{ts}.json"
    filepath = WEBHOOKS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filename


def _validate_webhook(data: dict) -> tuple[bool, str]:
    """Validate that the webhook has required Gumroad fields."""
    required_fields = ["product_name", "price", "email"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/webhook/gumroad")
async def receive_gumroad_webhook(request: Request):
    """
    Receive a Gumroad sale ping.

    Gumroad sends form-encoded data with fields like:
    seller_id, product_id, product_name, price, email,
    sale_timestamp, url_params, etc.

    Gumroad also sends a test ping when you first set up the webhook.
    """
    # Parse body - Gumroad sends form-encoded data
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
    elif "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        data = dict(form)
    else:
        # Try JSON first, fall back to form
        try:
            data = await request.json()
        except Exception:
            form = await request.form()
            data = dict(form)

    # Optional secret validation
    if WEBHOOK_SECRET:
        incoming_secret = data.get("secret", "")
        if incoming_secret != WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    # Save raw webhook for audit
    raw_file = _save_raw_webhook(data)

    # Validate required fields
    valid, error_msg = _validate_webhook(data)
    if not valid:
        # Still save the raw data but return error
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg, "raw_saved": raw_file},
        )

    # Extract sale data
    product_name = data.get("product_name", "Unknown Product")
    # Gumroad sends price in cents as a string like "9700" or as formatted "$97"
    raw_price = data.get("price", "0")
    try:
        # Handle various price formats
        price_str = str(raw_price).replace("$", "").replace(",", "").strip()
        price = float(price_str)
        # If price looks like cents (> 999 and no decimal), convert
        if price > 999 and "." not in price_str:
            price = price / 100.0
    except (ValueError, TypeError):
        price = 0.0

    email = data.get("email", "unknown")
    product_id = data.get("product_id", "")
    seller_id = data.get("seller_id", "")
    sale_timestamp = data.get("sale_timestamp", datetime.now().isoformat())

    # Log to analytics
    try:
        record = log_sale(product_name, price, "gumroad", customer_email=email)
    except Exception as e:
        print(f"[webhook] Failed to log sale to analytics: {e}")
        record = {"product": product_name, "price": price}

    # Send Telegram notification
    try:
        send_sale_notification(product_name, price, email)
    except Exception as e:
        print(f"[webhook] Failed to send Telegram notification: {e}")

    # Add to recent sales buffer
    sale_entry = {
        "product": product_name,
        "product_id": product_id,
        "price": price,
        "email": email,
        "seller_id": seller_id,
        "sale_timestamp": sale_timestamp,
        "received_at": datetime.now().isoformat(),
        "raw_file": raw_file,
    }
    recent_sales.insert(0, sale_entry)
    if len(recent_sales) > MAX_RECENT:
        recent_sales.pop()

    return JSONResponse(
        status_code=200,
        content={"status": "ok", "sale": sale_entry},
    )


@app.get("/webhook/status")
async def health_check():
    """Health check endpoint."""
    webhook_count = len(list(WEBHOOKS_DIR.glob("raw-*.json")))
    return {
        "status": "ok",
        "server": "Gumroad Webhook Receiver",
        "version": "1.0.0",
        "webhook_dir": str(WEBHOOKS_DIR),
        "total_webhooks_received": webhook_count,
        "recent_sales_buffered": len(recent_sales),
        "telegram_configured": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        "webhook_secret_set": bool(WEBHOOK_SECRET),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/webhook/recent")
async def get_recent_sales(limit: int = 10):
    """Return the last N sales from the in-memory buffer."""
    limit = min(limit, MAX_RECENT)
    return {
        "count": len(recent_sales[:limit]),
        "sales": recent_sales[:limit],
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    print("Starting Gumroad Webhook Server on port 8097...")
    print("Docs: http://localhost:8097/docs")
    print("Health: http://localhost:8097/webhook/status")
    uvicorn.run(app, host="0.0.0.0", port=8097)
