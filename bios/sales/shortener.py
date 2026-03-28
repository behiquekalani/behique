#!/usr/bin/env python3
"""
Self-Hosted Link Shortener

Tracks clicks with timestamp, referrer, user agent, IP hash.
Stores everything in bios/sales/data/short_links.json.

Run:
    uvicorn shortener:app --host 0.0.0.0 --port 8104
    # or
    python3 shortener.py

Endpoints:
    POST /s/create          - Create short link (slug, destination, optional tags)
    GET  /s/{slug}          - Redirect + log click
    GET  /s/{slug}/stats    - Click count, referrer breakdown, daily chart data
    GET  /s/admin           - All links with click counts
"""

import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
DATA_DIR = SALES_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LINKS_FILE = DATA_DIR / "short_links.json"
DASHBOARD_FILE = SALES_DIR / "shortener_dashboard.html"

# ---------------------------------------------------------------------------
# Default links
# ---------------------------------------------------------------------------

DEFAULT_LINKS = {
    "os": {
        "slug": "os",
        "destination": "https://behike.gumroad.com/l/behike-os",
        "tags": ["product", "gumroad"],
        "created_at": "2026-03-25T00:00:00",
        "clicks": []
    },
    "free": {
        "slug": "free",
        "destination": "https://behike.gumroad.com/l/starter",
        "tags": ["lead-magnet", "gumroad", "free"],
        "created_at": "2026-03-25T00:00:00",
        "clicks": []
    },
    "bundle": {
        "slug": "bundle",
        "destination": "https://behike.gumroad.com/l/complete-bundle",
        "tags": ["product", "gumroad", "bundle"],
        "created_at": "2026-03-25T00:00:00",
        "clicks": []
    },
    "ig": {
        "slug": "ig",
        "destination": "https://instagram.com/behikeai",
        "tags": ["social", "instagram"],
        "created_at": "2026-03-25T00:00:00",
        "clicks": []
    },
    "yt": {
        "slug": "yt",
        "destination": "https://youtube.com/@behike",
        "tags": ["social", "youtube"],
        "created_at": "2026-03-25T00:00:00",
        "clicks": []
    },
    "tt": {
        "slug": "tt",
        "destination": "https://tiktok.com/@behikeai",
        "tags": ["social", "tiktok"],
        "created_at": "2026-03-25T00:00:00",
        "clicks": []
    }
}

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def load_links() -> dict:
    """Load links from disk, seeding defaults if file is missing."""
    if LINKS_FILE.exists():
        with open(LINKS_FILE, "r") as f:
            return json.load(f)
    # First run: seed with defaults
    save_links(DEFAULT_LINKS)
    return DEFAULT_LINKS.copy()


def save_links(links: dict):
    """Persist links to disk."""
    with open(LINKS_FILE, "w") as f:
        json.dump(links, f, indent=2, default=str)


def hash_ip(ip: str) -> str:
    """One-way hash an IP for privacy."""
    salt = os.environ.get("SHORTENER_IP_SALT", "behike-shortener-salt-2026")
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Behike Link Shortener", version="1.0.0")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class CreateLinkRequest(BaseModel):
    slug: str
    destination: str
    tags: Optional[list[str]] = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/s/create")
async def create_link(req: CreateLinkRequest):
    """Create a new short link."""
    links = load_links()
    slug = req.slug.strip().lower()

    if not slug:
        raise HTTPException(status_code=400, detail="Slug cannot be empty")
    if slug in ("create", "admin"):
        raise HTTPException(status_code=400, detail="Reserved slug")

    if slug in links:
        raise HTTPException(status_code=409, detail=f"Slug '{slug}' already exists")

    links[slug] = {
        "slug": slug,
        "destination": req.destination,
        "tags": req.tags or [],
        "created_at": datetime.utcnow().isoformat(),
        "clicks": []
    }
    save_links(links)
    return {"status": "created", "short_url": f"/s/{slug}", "destination": req.destination}


@app.get("/s/admin")
async def admin_view():
    """All links with click counts."""
    links = load_links()
    summary = []
    for slug, data in sorted(links.items(), key=lambda x: len(x[1].get("clicks", [])), reverse=True):
        clicks = data.get("clicks", [])
        summary.append({
            "slug": slug,
            "destination": data["destination"],
            "tags": data.get("tags", []),
            "total_clicks": len(clicks),
            "created_at": data.get("created_at", ""),
            "last_click": clicks[-1]["timestamp"] if clicks else None
        })
    return {"links": summary, "total_links": len(summary)}


@app.get("/s/{slug}/stats")
async def link_stats(slug: str):
    """Click count, referrer breakdown, daily chart data for a single link."""
    links = load_links()
    if slug not in links:
        raise HTTPException(status_code=404, detail="Link not found")

    data = links[slug]
    clicks = data.get("clicks", [])

    # Referrer breakdown
    referrers = Counter()
    for c in clicks:
        ref = c.get("referrer") or "direct"
        referrers[ref] += 1

    # Daily counts (last 30 days)
    today = datetime.utcnow().date()
    daily = {}
    for i in range(30):
        day = (today - timedelta(days=i)).isoformat()
        daily[day] = 0
    for c in clicks:
        day = c.get("timestamp", "")[:10]
        if day in daily:
            daily[day] += 1

    # Sort daily chronologically
    daily_sorted = [{"date": k, "clicks": v} for k, v in sorted(daily.items())]

    return {
        "slug": slug,
        "destination": data["destination"],
        "total_clicks": len(clicks),
        "referrer_breakdown": dict(referrers.most_common(20)),
        "daily_clicks": daily_sorted,
        "tags": data.get("tags", []),
        "created_at": data.get("created_at", "")
    }


@app.get("/s/dashboard")
async def serve_dashboard():
    """Serve the HTML dashboard."""
    if DASHBOARD_FILE.exists():
        return HTMLResponse(content=DASHBOARD_FILE.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/s/{slug}")
async def redirect_link(slug: str, request: Request):
    """Redirect to destination and log click."""
    links = load_links()
    if slug not in links:
        raise HTTPException(status_code=404, detail="Link not found")

    # Log click
    client_ip = request.client.host if request.client else "unknown"
    click = {
        "timestamp": datetime.utcnow().isoformat(),
        "referrer": request.headers.get("referer", ""),
        "user_agent": request.headers.get("user-agent", ""),
        "ip_hash": hash_ip(client_ip)
    }
    links[slug].setdefault("clicks", []).append(click)
    save_links(links)

    return RedirectResponse(url=links[slug]["destination"], status_code=302)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/s/health")
async def health():
    links = load_links()
    return {"status": "ok", "links_count": len(links), "port": 8104}


# ---------------------------------------------------------------------------
# Standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    # Seed defaults on first run
    load_links()
    print(f"Link Shortener starting on port 8104")
    print(f"Data file: {LINKS_FILE}")
    print(f"Dashboard: /s/dashboard")
    uvicorn.run(app, host="0.0.0.0", port=8104)
