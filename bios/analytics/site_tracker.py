#!/usr/bin/env python3
"""
Behike Site Analytics Tracker
Self-hosted, privacy-first page view analytics for behike.co and behike.store.
Replaces Google Analytics. Zero external deps beyond fastapi/uvicorn.

Usage:
    uvicorn site_tracker:app --host 0.0.0.0 --port 8099
    # or
    python3 site_tracker.py
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Behike Analytics", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
PAGEVIEWS_FILE = DATA_DIR / "pageviews.json"
# Daily salt rotation for IP hashing -- extra privacy
SALT = f"behike-{datetime.utcnow().strftime('%Y-%m-%d')}"


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(f"{SALT}:{ip}".encode()).hexdigest()[:16]


def _load_pageviews() -> list[dict]:
    if not PAGEVIEWS_FILE.exists():
        return []
    try:
        with open(PAGEVIEWS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_pageviews(data: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PAGEVIEWS_FILE, "w") as f:
        json.dump(data, f)


# ---------- tracking JS snippet ----------

TRACKING_JS = """
(function(){
  var d={url:location.href,ref:document.referrer,ua:navigator.userAgent,ts:Date.now()};
  var x=new XMLHttpRequest();
  x.open("POST","%BASE%/api/pageview",true);
  x.setRequestHeader("Content-Type","application/json");
  x.send(JSON.stringify(d));
})();
""".strip()


@app.get("/track.js")
async def serve_tracking_js(request: Request):
    # Detect the base URL from the request so the snippet works on any host
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
    base = f"{scheme}://{host}"
    js = TRACKING_JS.replace("%BASE%", base)
    return Response(content=js, media_type="application/javascript")


# ---------- record pageview ----------

@app.post("/api/pageview")
async def record_pageview(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "bad json"}, status_code=400)

    ip = request.headers.get("x-forwarded-for", request.client.host or "unknown")
    ip = ip.split(",")[0].strip()

    entry = {
        "url": str(body.get("url", ""))[:2048],
        "referrer": str(body.get("ref", ""))[:2048],
        "user_agent": str(body.get("ua", ""))[:512],
        "ip_hash": _hash_ip(ip),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    views = _load_pageviews()
    views.append(entry)
    _save_pageviews(views)

    return JSONResponse({"ok": True})


# ---------- stats ----------

def _today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")


def _week_ago():
    return (datetime.utcnow() - timedelta(days=7)).isoformat()


def _month_ago():
    return (datetime.utcnow() - timedelta(days=30)).isoformat()


@app.get("/api/stats")
async def get_stats():
    views = _load_pageviews()
    today = _today_str()

    today_views = [v for v in views if v["timestamp"][:10] == today]
    week_views = [v for v in views if v["timestamp"] >= _week_ago()]
    month_views = [v for v in views if v["timestamp"] >= _month_ago()]

    # top pages
    page_counts: dict[str, int] = {}
    for v in views:
        url = v.get("url", "unknown")
        page_counts[url] = page_counts.get(url, 0) + 1
    top_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    # top referrers
    ref_counts: dict[str, int] = {}
    for v in views:
        ref = v.get("referrer", "").strip()
        if not ref:
            ref = "(direct)"
        ref_counts[ref] = ref_counts.get(ref, 0) + 1
    top_referrers = sorted(ref_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # unique visitors today (by hashed IP)
    unique_today = len(set(v["ip_hash"] for v in today_views))
    unique_week = len(set(v["ip_hash"] for v in week_views))
    unique_month = len(set(v["ip_hash"] for v in month_views))

    return JSONResponse({
        "today": {
            "views": len(today_views),
            "unique": unique_today,
        },
        "week": {
            "views": len(week_views),
            "unique": unique_week,
        },
        "month": {
            "views": len(month_views),
            "unique": unique_month,
        },
        "total_views": len(views),
        "top_pages": [{"url": u, "count": c} for u, c in top_pages],
        "top_referrers": [{"referrer": r, "count": c} for r, c in top_referrers],
    })


@app.get("/api/stats/daily")
async def get_daily_stats():
    views = _load_pageviews()
    cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    daily: dict[str, dict] = {}
    for v in views:
        day = v["timestamp"][:10]
        if day < cutoff:
            continue
        if day not in daily:
            daily[day] = {"views": 0, "unique_ips": set()}
        daily[day]["views"] += 1
        daily[day]["unique_ips"].add(v["ip_hash"])

    # Build sorted list for last 30 days
    result = []
    for i in range(30, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        entry = daily.get(d, {"views": 0, "unique_ips": set()})
        result.append({
            "date": d,
            "views": entry["views"],
            "unique": len(entry["unique_ips"]),
        })

    return JSONResponse(result)


# ---------- serve dashboard ----------

DASHBOARD_PATH = Path(__file__).parent / "site_dashboard.html"


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    if DASHBOARD_PATH.exists():
        return HTMLResponse(DASHBOARD_PATH.read_text())
    return HTMLResponse("<h1>Dashboard not found</h1>")


# ---------- run directly ----------

if __name__ == "__main__":
    import uvicorn
    print("Behike Analytics running on http://0.0.0.0:8099")
    uvicorn.run(app, host="0.0.0.0", port=8099)
