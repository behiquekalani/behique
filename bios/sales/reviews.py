#!/usr/bin/env python3
"""
Review/Testimonial Collection System

FastAPI server for collecting, moderating, and displaying customer reviews.
Sends Telegram notifications on new submissions.

Run:
    uvicorn reviews:app --host 0.0.0.0 --port 8103
    # or
    python3 reviews.py

Env vars:
    TELEGRAM_BOT_TOKEN  - Bot token from @BotFather
    TELEGRAM_CHAT_ID    - Your chat/group ID
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
DATA_DIR = SALES_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REVIEWS_FILE = DATA_DIR / "reviews.json"
PRODUCTS_FILE = Path(__file__).resolve().parent.parent.parent / "storefront" / "products.json"

# Import notifier from same directory
sys.path.insert(0, str(SALES_DIR))
try:
    from notifier import send_custom
except ImportError:
    def send_custom(msg: str) -> bool:
        print(f"[reviews] No notifier. Message:\n{msg}")
        return False

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def _load_reviews() -> list[dict]:
    if not REVIEWS_FILE.exists():
        return []
    try:
        return json.loads(REVIEWS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_reviews(reviews: list[dict]) -> None:
    REVIEWS_FILE.write_text(
        json.dumps(reviews, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_products() -> list[dict]:
    if not PRODUCTS_FILE.exists():
        return []
    try:
        return json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ReviewSubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    product: str = Field(..., min_length=1, max_length=200, description="Product slug or title")
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=10, max_length=2000)
    email: Optional[str] = Field(None, max_length=200)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Behike Reviews", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/review/submit")
async def submit_review(review: ReviewSubmission):
    """Customer submits a review. Starts as pending moderation."""
    reviews = _load_reviews()

    entry = {
        "id": str(uuid.uuid4())[:8],
        "name": review.name,
        "product": review.product,
        "rating": review.rating,
        "text": review.text,
        "email": review.email,
        "status": "pending",
        "submitted_at": datetime.utcnow().isoformat(),
    }

    reviews.append(entry)
    _save_reviews(reviews)

    # Telegram notification
    stars = "★" * review.rating + "☆" * (5 - review.rating)
    msg = (
        f"<b>NEW REVIEW</b>\n"
        f"Product: {review.product}\n"
        f"Rating: {stars}\n"
        f"By: {review.name}\n"
        f'"{review.text[:200]}"'
    )
    send_custom(msg)

    return {"ok": True, "id": entry["id"], "message": "Review submitted for moderation."}


@app.get("/review/product/{product_slug}")
async def get_product_reviews(product_slug: str):
    """Returns all approved reviews for a product."""
    reviews = _load_reviews()
    approved = [
        r for r in reviews
        if r["product"] == product_slug and r["status"] == "approved"
    ]
    # Sort newest first
    approved.sort(key=lambda r: r.get("submitted_at", ""), reverse=True)

    avg_rating = 0.0
    if approved:
        avg_rating = round(sum(r["rating"] for r in approved) / len(approved), 1)

    return {
        "product": product_slug,
        "count": len(approved),
        "average_rating": avg_rating,
        "reviews": approved,
    }


@app.get("/review/pending")
async def get_pending_reviews():
    """Admin view: all unmoderated reviews."""
    reviews = _load_reviews()
    pending = [r for r in reviews if r["status"] == "pending"]
    pending.sort(key=lambda r: r.get("submitted_at", ""), reverse=True)
    return {"count": len(pending), "reviews": pending}


@app.post("/review/approve/{review_id}")
async def approve_review(review_id: str):
    """Approve a pending review."""
    reviews = _load_reviews()
    for r in reviews:
        if r["id"] == review_id:
            if r["status"] == "approved":
                return {"ok": True, "message": "Already approved."}
            r["status"] = "approved"
            r["moderated_at"] = datetime.utcnow().isoformat()
            _save_reviews(reviews)
            return {"ok": True, "message": f"Review {review_id} approved."}
    raise HTTPException(status_code=404, detail="Review not found.")


@app.post("/review/reject/{review_id}")
async def reject_review(review_id: str):
    """Reject a pending review."""
    reviews = _load_reviews()
    for r in reviews:
        if r["id"] == review_id:
            if r["status"] == "rejected":
                return {"ok": True, "message": "Already rejected."}
            r["status"] = "rejected"
            r["moderated_at"] = datetime.utcnow().isoformat()
            _save_reviews(reviews)
            return {"ok": True, "message": f"Review {review_id} rejected."}
    raise HTTPException(status_code=404, detail="Review not found.")


@app.get("/review/widget/{product_slug}", response_class=HTMLResponse)
async def review_widget(product_slug: str):
    """Embeddable HTML widget showing approved reviews with star ratings."""
    reviews = _load_reviews()
    approved = [
        r for r in reviews
        if r["product"] == product_slug and r["status"] == "approved"
    ]
    approved.sort(key=lambda r: r.get("submitted_at", ""), reverse=True)

    avg_rating = 0.0
    if approved:
        avg_rating = round(sum(r["rating"] for r in approved) / len(approved), 1)

    review_cards = ""
    for r in approved:
        stars = "★" * r["rating"] + "☆" * (5 - r["rating"])
        date_str = r.get("submitted_at", "")[:10]
        review_cards += f"""
        <div class="review-card">
            <div class="review-stars">{stars}</div>
            <p class="review-text">"{r['text']}"</p>
            <div class="review-meta">- {r['name']} | {date_str}</div>
        </div>
        """

    if not approved:
        review_cards = '<p class="no-reviews">No reviews yet. Be the first!</p>'

    summary_stars = "★" * round(avg_rating) + "☆" * (5 - round(avg_rating)) if approved else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: transparent; color: #e0e0e0; }}
    .widget {{ max-width: 600px; margin: 0 auto; }}
    .widget-header {{ margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #333; }}
    .widget-header .stars {{ font-size: 20px; color: #d4a017; }}
    .widget-header .summary {{ font-size: 14px; color: #999; margin-top: 4px; }}
    .review-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
    .review-stars {{ color: #d4a017; font-size: 16px; margin-bottom: 8px; }}
    .review-text {{ font-size: 14px; line-height: 1.5; color: #ccc; margin-bottom: 8px; font-style: italic; }}
    .review-meta {{ font-size: 12px; color: #888; }}
    .no-reviews {{ color: #666; font-style: italic; text-align: center; padding: 24px; }}
</style>
</head>
<body>
<div class="widget">
    <div class="widget-header">
        <div class="stars">{summary_stars}</div>
        <div class="summary">{avg_rating} out of 5 - {len(approved)} review{'s' if len(approved) != 1 else ''}</div>
    </div>
    {review_cards}
</div>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/review/products")
async def list_products():
    """Returns product list for the review form dropdown."""
    products = _load_products()
    return [{"id": p["id"], "title": p["title"]} for p in products]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8103)
