#!/usr/bin/env python3
"""
Abandoned Cart Recovery System

FastAPI endpoint + CLI for tracking abandoned carts and sending recovery emails.
Stores data in bios/sales/data/abandoned_carts.json.

Run server:
    python3 cart_recovery.py
    # or
    uvicorn cart_recovery:app --host 0.0.0.0 --port 8103

CLI:
    python3 cart_recovery.py --check       # find carts due for recovery email
    python3 cart_recovery.py --send        # send all due recovery emails
    python3 cart_recovery.py --stats       # abandoned cart stats
    python3 cart_recovery.py --recover EMAIL PRODUCT  # mark cart as recovered

Env vars:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS   - email sending
    STORE_BASE_URL                                 - product link base (default: https://behike.co)
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID           - recovery notifications
"""

import argparse
import json
import smtplib
import sys
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
DATA_DIR = SALES_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CARTS_FILE = DATA_DIR / "abandoned_carts.json"

STORE_BASE_URL = os.environ.get("STORE_BASE_URL", "https://behike.co")

# ---------------------------------------------------------------------------
# Recovery sequence config
# ---------------------------------------------------------------------------

RECOVERY_SEQUENCE = [
    {
        "step": 1,
        "delay_hours": 1,
        "subject": "You left something behind",
        "coupon": None,
        "template": (
            "Hey,\n\n"
            "Looks like you were checking out {product_name} but didn't finish.\n\n"
            "No worries. Your cart is still waiting:\n"
            "{product_link}\n\n"
            "If you have any questions, just reply to this email.\n\n"
            "- Behike"
        ),
    },
    {
        "step": 2,
        "delay_hours": 24,
        "subject": "Still thinking about it?",
        "coupon": "COMEBACK10",
        "coupon_discount": 10,
        "template": (
            "Hey,\n\n"
            "Still thinking about {product_name}?\n\n"
            "Here's 10% off to make it easier. Use code COMEBACK10 at checkout:\n"
            "{product_link}\n\n"
            "This code won't last forever.\n\n"
            "- Behike"
        ),
    },
    {
        "step": 3,
        "delay_hours": 72,
        "subject": "Last chance - 20% off {product_name}",
        "coupon": "LASTCHANCE20",
        "coupon_discount": 20,
        "template": (
            "Hey,\n\n"
            "Last nudge on {product_name}.\n\n"
            "Use code LASTCHANCE20 for 20% off. After this, we'll stop bugging you:\n"
            "{product_link}\n\n"
            "- Behike"
        ),
    },
]

# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------


def _load_carts() -> list:
    if CARTS_FILE.exists():
        with open(CARTS_FILE, "r") as f:
            return json.load(f)
    return []


def _save_carts(carts: list) -> None:
    with open(CARTS_FILE, "w") as f:
        json.dump(carts, f, indent=2)


# ---------------------------------------------------------------------------
# Coupon auto-creation
# ---------------------------------------------------------------------------


def _ensure_recovery_coupons():
    """Create COMEBACK10 and LASTCHANCE20 in coupons.py if they don't exist."""
    try:
        from coupons import create_coupon
    except ImportError:
        # Try relative import path
        sys.path.insert(0, str(SALES_DIR))
        from coupons import create_coupon

    create_coupon("COMEBACK10", 10, max_uses=None, expiry_date=None)
    create_coupon("LASTCHANCE20", 20, max_uses=None, expiry_date=None)


# Run once on import
try:
    _ensure_recovery_coupons()
except Exception:
    pass  # coupons.py may not be available in all environments

# ---------------------------------------------------------------------------
# Telegram notification
# ---------------------------------------------------------------------------


def _notify_recovery(email: str, product_slug: str):
    """Send Telegram notification when a cart is recovered."""
    try:
        sys.path.insert(0, str(SALES_DIR))
        from notifier import send_custom
        send_custom(
            f"<b>CART RECOVERED</b>\n"
            f"Product: {product_slug}\n"
            f"Email: {email}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    except Exception as e:
        print(f"[cart_recovery] Telegram notification failed: {e}")


# ---------------------------------------------------------------------------
# Email sending
# ---------------------------------------------------------------------------


def _send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email via SMTP. Returns True on success."""
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not smtp_host or not smtp_user:
        print(f"[cart_recovery] No SMTP config. Would send to {to_email}:")
        print(f"  Subject: {subject}")
        print(f"  Body: {body[:200]}...")
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[cart_recovery] Email send failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def abandon_cart(email: str, product_slug: str, timestamp: Optional[str] = None) -> dict:
    """Record an abandoned cart."""
    carts = _load_carts()

    # Check if this email+product already has an active abandoned cart
    for cart in carts:
        if (cart["email"] == email
                and cart["product_slug"] == product_slug
                and cart["status"] == "abandoned"):
            return {"status": "exists", "id": cart["id"]}

    cart_id = f"cart_{len(carts) + 1:04d}"
    ts = timestamp or datetime.now().isoformat()

    cart = {
        "id": cart_id,
        "email": email,
        "product_slug": product_slug,
        "abandoned_at": ts,
        "status": "abandoned",  # abandoned | recovering | recovered | expired
        "emails_sent": [],
        "recovered_at": None,
    }

    carts.append(cart)
    _save_carts(carts)
    return {"status": "created", "id": cart_id}


def check_due_emails() -> list:
    """Find carts that are due for the next recovery email."""
    carts = _load_carts()
    now = datetime.now()
    due = []

    for cart in carts:
        if cart["status"] not in ("abandoned", "recovering"):
            continue

        abandoned_at = datetime.fromisoformat(cart["abandoned_at"])
        steps_sent = len(cart["emails_sent"])

        if steps_sent >= len(RECOVERY_SEQUENCE):
            continue

        next_step = RECOVERY_SEQUENCE[steps_sent]
        send_after = abandoned_at + timedelta(hours=next_step["delay_hours"])

        if now >= send_after:
            due.append({
                "cart": cart,
                "step": next_step,
                "due_since": send_after.isoformat(),
            })

    return due


def send_due_emails() -> dict:
    """Send all recovery emails that are due. Returns summary."""
    due = check_due_emails()
    sent = 0
    failed = 0

    carts = _load_carts()

    for item in due:
        cart = item["cart"]
        step = item["step"]

        product_name = cart["product_slug"].replace("-", " ").title()
        product_link = f"{STORE_BASE_URL}/products/{cart['product_slug']}"

        subject = step["subject"].format(product_name=product_name)
        body = step["template"].format(
            product_name=product_name,
            product_link=product_link,
        )

        success = _send_email(cart["email"], subject, body)

        # Update cart in the master list
        for c in carts:
            if c["id"] == cart["id"]:
                c["emails_sent"].append({
                    "step": step["step"],
                    "sent_at": datetime.now().isoformat(),
                    "success": success,
                    "coupon": step.get("coupon"),
                })
                c["status"] = "recovering"
                break

        if success:
            sent += 1
        else:
            failed += 1

    _save_carts(carts)
    return {"due": len(due), "sent": sent, "failed": failed}


def mark_recovered(email: str, product_slug: str) -> dict:
    """Mark a cart as recovered (sale came in for that email+product)."""
    carts = _load_carts()
    recovered = False

    for cart in carts:
        if (cart["email"] == email
                and cart["product_slug"] == product_slug
                and cart["status"] in ("abandoned", "recovering")):
            cart["status"] = "recovered"
            cart["recovered_at"] = datetime.now().isoformat()
            recovered = True
            break

    if recovered:
        _save_carts(carts)
        _notify_recovery(email, product_slug)
        return {"status": "recovered", "email": email, "product": product_slug}

    return {"status": "not_found", "email": email, "product": product_slug}


def get_stats() -> dict:
    """Return abandoned cart stats."""
    carts = _load_carts()

    total = len(carts)
    abandoned = sum(1 for c in carts if c["status"] == "abandoned")
    recovering = sum(1 for c in carts if c["status"] == "recovering")
    recovered = sum(1 for c in carts if c["status"] == "recovered")
    expired = sum(1 for c in carts if c["status"] == "expired")

    emails_sent = sum(len(c["emails_sent"]) for c in carts)
    recovery_rate = (recovered / total * 100) if total > 0 else 0

    # Per-step stats
    step_stats = {}
    for step in RECOVERY_SEQUENCE:
        step_num = step["step"]
        sent_count = sum(
            1 for c in carts
            for e in c["emails_sent"]
            if e["step"] == step_num
        )
        step_stats[f"step_{step_num}"] = {
            "subject": step["subject"],
            "delay_hours": step["delay_hours"],
            "sent": sent_count,
        }

    return {
        "total_carts": total,
        "abandoned": abandoned,
        "recovering": recovering,
        "recovered": recovered,
        "expired": expired,
        "emails_sent": emails_sent,
        "recovery_rate": f"{recovery_rate:.1f}%",
        "steps": step_stats,
    }


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------


def _build_app():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    _app = FastAPI(
        title="Abandoned Cart Recovery",
        version="1.0.0",
        docs_url="/docs",
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class AbandonRequest(BaseModel):
        email: str
        product_slug: str
        timestamp: Optional[str] = None

    class RecoverRequest(BaseModel):
        email: str
        product_slug: str

    @_app.post("/cart/abandon")
    async def api_abandon_cart(data: AbandonRequest):
        """Record an abandoned cart."""
        return abandon_cart(data.email, data.product_slug, data.timestamp)

    @_app.post("/cart/recover")
    async def api_recover_cart(data: RecoverRequest):
        """Mark a cart as recovered (sale completed)."""
        return mark_recovered(data.email, data.product_slug)

    @_app.get("/cart/check")
    async def api_check_due():
        """Check which carts are due for a recovery email."""
        due = check_due_emails()
        return {
            "due_count": len(due),
            "carts": [
                {
                    "id": d["cart"]["id"],
                    "email": d["cart"]["email"],
                    "product": d["cart"]["product_slug"],
                    "step": d["step"]["step"],
                    "due_since": d["due_since"],
                }
                for d in due
            ],
        }

    @_app.post("/cart/send")
    async def api_send_due():
        """Send all due recovery emails."""
        return send_due_emails()

    @_app.get("/cart/stats")
    async def api_stats():
        """Get abandoned cart stats."""
        return get_stats()

    return _app


# Lazy app for uvicorn import
class _LazyApp:
    _instance = None

    def __getattr__(self, name):
        if _LazyApp._instance is None:
            _LazyApp._instance = _build_app()
        return getattr(_LazyApp._instance, name)

    def __call__(self, *args, **kwargs):
        if _LazyApp._instance is None:
            _LazyApp._instance = _build_app()
        return _LazyApp._instance(*args, **kwargs)


app = _LazyApp()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cli_check():
    """Print carts due for recovery email."""
    due = check_due_emails()
    if not due:
        print("No carts due for recovery email right now.")
        return

    print(f"\n{len(due)} cart(s) due for recovery email:\n")
    print(f"  {'ID':<12} {'EMAIL':<30} {'PRODUCT':<20} {'STEP':>4} {'DUE SINCE'}")
    print("  " + "-" * 85)

    for d in due:
        cart = d["cart"]
        step = d["step"]
        print(f"  {cart['id']:<12} {cart['email']:<30} {cart['product_slug']:<20} {step['step']:>4} {d['due_since']}")
    print()


def cli_send():
    """Send all due recovery emails."""
    result = send_due_emails()
    print(f"\nRecovery emails: {result['due']} due, {result['sent']} sent, {result['failed']} failed\n")


def cli_stats():
    """Print abandoned cart stats."""
    stats = get_stats()

    print(f"\n--- Abandoned Cart Stats ---")
    print(f"  Total carts:    {stats['total_carts']}")
    print(f"  Abandoned:      {stats['abandoned']}")
    print(f"  Recovering:     {stats['recovering']}")
    print(f"  Recovered:      {stats['recovered']}")
    print(f"  Expired:        {stats['expired']}")
    print(f"  Emails sent:    {stats['emails_sent']}")
    print(f"  Recovery rate:  {stats['recovery_rate']}")

    print(f"\n  Recovery Sequence:")
    for key, s in stats["steps"].items():
        print(f"    Step {key[-1]}: {s['subject'][:40]:<40} ({s['delay_hours']}h delay, {s['sent']} sent)")
    print()


def cli_recover(email: str, product: str):
    """Manually mark a cart as recovered."""
    result = mark_recovered(email, product)
    if result["status"] == "recovered":
        print(f"  Marked as recovered: {email} / {product}")
    else:
        print(f"  No active abandoned cart found for {email} / {product}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abandoned Cart Recovery System")
    parser.add_argument("--check", action="store_true", help="Find carts due for recovery email")
    parser.add_argument("--send", action="store_true", help="Send all due recovery emails")
    parser.add_argument("--stats", action="store_true", help="Show abandoned cart stats")
    parser.add_argument("--recover", nargs=2, metavar=("EMAIL", "PRODUCT"), help="Mark cart as recovered")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI server on port 8103")

    args = parser.parse_args()

    if args.check:
        cli_check()
    elif args.send:
        cli_send()
    elif args.stats:
        cli_stats()
    elif args.recover:
        cli_recover(args.recover[0], args.recover[1])
    elif args.serve or len(sys.argv) == 1:
        import uvicorn
        real_app = _build_app()
        print("Starting Cart Recovery Server on port 8103...")
        print("Docs: http://localhost:8103/docs")
        print(f"Data: {CARTS_FILE}")
        uvicorn.run(real_app, host="0.0.0.0", port=8103)
    else:
        parser.print_help()
