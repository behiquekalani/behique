#!/usr/bin/env python3
"""
Email Capture Server for Behike.
FastAPI server that collects newsletter subscribers.
Port 8082. Stores to Ceiba/email-list/subscribers.json.

Usage:
    uvicorn tools.email_capture:app --port 8082
    # or
    python tools/email_capture.py

Copyright 2026 Behike.
"""

import json
import os
import re
import csv
import io
import time
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, field_validator

# -- Config --

BASE_DIR = Path(__file__).resolve().parent.parent
SUBSCRIBERS_FILE = BASE_DIR / "Ceiba" / "email-list" / "subscribers.json"
SENT_LOG_FILE = BASE_DIR / "Ceiba" / "email-list" / "sent_log.json"

# Rate limiting: 5 signups per IP per hour
RATE_LIMIT = 5
RATE_WINDOW = 3600  # seconds

# Basic auth for admin endpoints (set via env or defaults)
ADMIN_USER = os.getenv("EMAIL_ADMIN_USER", "behike")
ADMIN_PASS = os.getenv("EMAIL_ADMIN_PASS", "behike2026")

# CORS allowed origins
ALLOWED_ORIGINS = [
    "http://localhost:*",
    "http://127.0.0.1:*",
    "https://behike.com",
    "https://www.behike.com",
    "https://store.behike.com",
    "https://behikeai.com",
    "https://www.behikeai.com",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5500",
    "*",
]

# -- App --

app = FastAPI(title="Behike Email Capture", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

# In-memory rate limiter
rate_tracker: dict[str, list[float]] = defaultdict(list)


# -- Helpers --

def load_subscribers() -> list[dict]:
    """Load subscribers from JSON file."""
    if not SUBSCRIBERS_FILE.exists():
        return []
    try:
        data = json.loads(SUBSCRIBERS_FILE.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_subscribers(subscribers: list[dict]):
    """Save subscribers to JSON file."""
    SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUBSCRIBERS_FILE.write_text(json.dumps(subscribers, indent=2, default=str))


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def check_rate_limit(ip: str) -> bool:
    """Returns True if request is within rate limit."""
    now = time.time()
    # Clean old entries
    rate_tracker[ip] = [t for t in rate_tracker[ip] if now - t < RATE_WINDOW]
    if len(rate_tracker[ip]) >= RATE_LIMIT:
        return False
    rate_tracker[ip].append(now)
    return True


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """Verify basic auth for admin endpoints."""
    correct_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_pass = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return True


# -- Models --

class SubscribeRequest(BaseModel):
    email: str
    source: str = "unknown"

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v):
        v = v.strip().lower()
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v


class SubscribeResponse(BaseModel):
    success: bool
    message: str
    subscriber_count: int


# -- Routes --

@app.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(data: SubscribeRequest, request: Request):
    """Subscribe a new email address."""
    ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many signups. Try again in an hour."
        )

    subscribers = load_subscribers()
    existing_emails = {s["email"] for s in subscribers}

    if data.email in existing_emails:
        return SubscribeResponse(
            success=True,
            message="You're already subscribed.",
            subscriber_count=len(subscribers)
        )

    new_subscriber = {
        "email": data.email,
        "source": data.source,
        "subscribed_at": datetime.utcnow().isoformat(),
        "ip": ip,
        "active": True,
    }
    subscribers.append(new_subscriber)
    save_subscribers(subscribers)

    return SubscribeResponse(
        success=True,
        message="Welcome to Behike. You're in.",
        subscriber_count=len(subscribers)
    )


@app.get("/unsubscribe")
async def unsubscribe(email: str):
    """Unsubscribe an email address."""
    email = email.strip().lower()
    subscribers = load_subscribers()
    found = False

    for sub in subscribers:
        if sub["email"] == email:
            sub["active"] = False
            sub["unsubscribed_at"] = datetime.utcnow().isoformat()
            found = True
            break

    if found:
        save_subscribers(subscribers)
        return {"success": True, "message": "You've been unsubscribed. Sorry to see you go."}
    else:
        return {"success": False, "message": "Email not found."}


@app.get("/subscriber-count")
async def subscriber_count():
    """Public endpoint. Returns active subscriber count for social proof."""
    subscribers = load_subscribers()
    active = [s for s in subscribers if s.get("active", True)]
    return {"count": len(active)}


@app.get("/stats")
async def stats(authorized: bool = Depends(verify_admin)):
    """Admin endpoint. Returns subscriber stats and growth rate."""
    subscribers = load_subscribers()
    active = [s for s in subscribers if s.get("active", True)]
    inactive = [s for s in subscribers if not s.get("active", True)]

    # Growth rate: signups in last 7 days vs previous 7 days
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    this_week = 0
    last_week = 0
    for s in active:
        try:
            dt = datetime.fromisoformat(s["subscribed_at"])
            if dt >= week_ago:
                this_week += 1
            elif dt >= two_weeks_ago:
                last_week += 1
        except (KeyError, ValueError):
            pass

    growth_rate = 0.0
    if last_week > 0:
        growth_rate = ((this_week - last_week) / last_week) * 100

    # Source breakdown
    sources: dict[str, int] = defaultdict(int)
    for s in active:
        sources[s.get("source", "unknown")] += 1

    return {
        "total": len(subscribers),
        "active": len(active),
        "unsubscribed": len(inactive),
        "this_week": this_week,
        "last_week": last_week,
        "growth_rate_pct": round(growth_rate, 1),
        "sources": dict(sources),
    }


@app.get("/export")
async def export_csv(authorized: bool = Depends(verify_admin)):
    """Admin endpoint. Export subscribers as CSV download."""
    subscribers = load_subscribers()
    active = [s for s in subscribers if s.get("active", True)]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["email", "source", "subscribed_at"])
    writer.writeheader()
    for s in active:
        writer.writerow({
            "email": s["email"],
            "source": s.get("source", ""),
            "subscribed_at": s.get("subscribed_at", ""),
        })

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=behike-subscribers-{datetime.utcnow().strftime('%Y-%m-%d')}.csv"}
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "email-capture"}


# -- Run --

if __name__ == "__main__":
    import uvicorn
    print("Starting Behike Email Capture on port 8082...")
    uvicorn.run(app, host="0.0.0.0", port=8082)
