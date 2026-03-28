"""
Behike Affiliate/Referral Tracking System
FastAPI server on port 8101
Stores data in bios/sales/data/affiliates.json
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Behike Affiliate Tracker", version="1.0.0")

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "affiliates.json"
STORE_URL = "https://behike.co/store"


# --- Models ---

class AffiliateCreate(BaseModel):
    name: str
    email: str
    commission_pct: float = 20.0


class SaleLog(BaseModel):
    product: str
    amount: float
    affiliate_code: str


# --- Persistence ---

def _load_data() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"affiliates": {}, "clicks": [], "sales": []}


def _save_data(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _generate_code(name: str, email: str) -> str:
    raw = f"{name.lower().strip()}{email.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


# --- Routes ---

@app.post("/affiliate/create")
def create_affiliate(body: AffiliateCreate):
    data = _load_data()
    code = _generate_code(body.name, body.email)

    if code in data["affiliates"]:
        raise HTTPException(status_code=409, detail=f"Affiliate already exists with code: {code}")

    data["affiliates"][code] = {
        "name": body.name,
        "email": body.email,
        "commission_pct": body.commission_pct,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
    }
    _save_data(data)

    return {
        "status": "created",
        "affiliate_code": code,
        "referral_link": f"http://localhost:8101/r/{code}",
        "commission_pct": body.commission_pct,
    }


@app.get("/r/{affiliate_code}")
def referral_redirect(affiliate_code: str):
    data = _load_data()

    if affiliate_code not in data["affiliates"]:
        raise HTTPException(status_code=404, detail="Unknown affiliate code")

    data["clicks"].append({
        "affiliate_code": affiliate_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_data(data)

    return RedirectResponse(url=f"{STORE_URL}?ref={affiliate_code}", status_code=302)


@app.post("/affiliate/sale")
def log_sale(body: SaleLog):
    data = _load_data()

    if body.affiliate_code not in data["affiliates"]:
        raise HTTPException(status_code=404, detail="Unknown affiliate code")

    aff = data["affiliates"][body.affiliate_code]
    commission = round(body.amount * (aff["commission_pct"] / 100), 2)

    data["sales"].append({
        "affiliate_code": body.affiliate_code,
        "product": body.product,
        "amount": body.amount,
        "commission": commission,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_data(data)

    return {
        "status": "sale_logged",
        "affiliate_code": body.affiliate_code,
        "product": body.product,
        "amount": body.amount,
        "commission": commission,
    }


@app.get("/affiliate/dashboard/{code}")
def affiliate_dashboard(code: str):
    data = _load_data()

    if code not in data["affiliates"]:
        raise HTTPException(status_code=404, detail="Unknown affiliate code")

    aff = data["affiliates"][code]
    clicks = [c for c in data["clicks"] if c["affiliate_code"] == code]
    sales = [s for s in data["sales"] if s["affiliate_code"] == code]
    total_earnings = round(sum(s["commission"] for s in sales), 2)
    total_revenue = round(sum(s["amount"] for s in sales), 2)
    conversion_rate = round((len(sales) / len(clicks) * 100), 2) if clicks else 0.0

    return {
        "affiliate": {
            "name": aff["name"],
            "email": aff["email"],
            "code": code,
            "commission_pct": aff["commission_pct"],
            "created_at": aff["created_at"],
            "active": aff["active"],
        },
        "stats": {
            "total_clicks": len(clicks),
            "total_sales": len(sales),
            "total_revenue": total_revenue,
            "total_earnings": total_earnings,
            "conversion_rate_pct": conversion_rate,
        },
        "click_history": clicks[-20:],
        "sale_history": sales[-20:],
    }


@app.get("/affiliate/admin")
def admin_dashboard():
    data = _load_data()
    affiliates_out = []

    for code, aff in data["affiliates"].items():
        clicks = [c for c in data["clicks"] if c["affiliate_code"] == code]
        sales = [s for s in data["sales"] if s["affiliate_code"] == code]
        total_earnings = round(sum(s["commission"] for s in sales), 2)
        total_revenue = round(sum(s["amount"] for s in sales), 2)
        conversion = round((len(sales) / len(clicks) * 100), 2) if clicks else 0.0

        affiliates_out.append({
            "code": code,
            "name": aff["name"],
            "email": aff["email"],
            "commission_pct": aff["commission_pct"],
            "active": aff["active"],
            "clicks": len(clicks),
            "sales": len(sales),
            "revenue": total_revenue,
            "earnings_owed": total_earnings,
            "conversion_rate_pct": conversion,
        })

    grand_clicks = len(data["clicks"])
    grand_sales = len(data["sales"])
    grand_revenue = round(sum(s["amount"] for s in data["sales"]), 2)
    grand_commission = round(sum(s["commission"] for s in data["sales"]), 2)

    return {
        "totals": {
            "affiliates": len(data["affiliates"]),
            "clicks": grand_clicks,
            "sales": grand_sales,
            "revenue": grand_revenue,
            "commission_owed": grand_commission,
        },
        "affiliates": affiliates_out,
    }


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    html_path = Path(__file__).parent / "affiliate_dashboard.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)
