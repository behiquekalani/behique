#!/usr/bin/env python3
"""
Coupon / Discount Code System

FastAPI server + CLI for managing discount codes.
Stores all data in bios/sales/data/coupons.json.

Run server:
    python3 coupons.py
    # or
    uvicorn coupons:app --host 0.0.0.0 --port 8102

CLI:
    python3 coupons.py --list
    python3 coupons.py --validate LAUNCH20
    python3 coupons.py --stats
    python3 coupons.py --create CODE --discount 25 --max-uses 100 --expiry 2026-05-01
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
DATA_DIR = SALES_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
COUPONS_FILE = DATA_DIR / "coupons.json"

# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------


def _load_coupons() -> dict:
    """Load coupons from disk."""
    if COUPONS_FILE.exists():
        with open(COUPONS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_coupons(coupons: dict) -> None:
    """Persist coupons to disk."""
    with open(COUPONS_FILE, "w") as f:
        json.dump(coupons, f, indent=2)


def _seed_defaults() -> None:
    """Pre-create default coupons if file doesn't exist yet."""
    if COUPONS_FILE.exists():
        return

    now = datetime.now().isoformat()
    defaults = {
        "LAUNCH20": {
            "code": "LAUNCH20",
            "discount_percent": 20,
            "max_uses": 100,
            "uses": 0,
            "expiry_date": "2026-04-30",
            "products": None,
            "created_at": now,
            "redemptions": [],
        },
        "FIRST10": {
            "code": "FIRST10",
            "discount_percent": 10,
            "max_uses": None,
            "uses": 0,
            "expiry_date": None,
            "products": None,
            "created_at": now,
            "redemptions": [],
        },
        "BUNDLE30": {
            "code": "BUNDLE30",
            "discount_percent": 30,
            "max_uses": 50,
            "uses": 0,
            "expiry_date": "2026-04-15",
            "products": ["bundle"],
            "created_at": now,
            "redemptions": [],
        },
        "FRIEND50": {
            "code": "FRIEND50",
            "discount_percent": 50,
            "max_uses": 5,
            "uses": 0,
            "expiry_date": None,
            "products": None,
            "created_at": now,
            "redemptions": [],
        },
        "FREE100": {
            "code": "FREE100",
            "discount_percent": 100,
            "max_uses": 20,
            "uses": 0,
            "expiry_date": None,
            "products": ["starter-blueprint"],
            "created_at": now,
            "redemptions": [],
        },
    }
    _save_coupons(defaults)


# Seed on import
_seed_defaults()

# ---------------------------------------------------------------------------
# Core logic (no FastAPI dependency)
# ---------------------------------------------------------------------------


def validate_coupon(code: str, product: Optional[str] = None) -> dict:
    """
    Check if a coupon is valid. Returns dict with 'valid' bool and details.
    """
    coupons = _load_coupons()
    upper = code.upper()

    if upper not in coupons:
        return {"valid": False, "reason": "Coupon not found"}

    coupon = coupons[upper]

    # Check expiry
    if coupon.get("expiry_date"):
        expiry = datetime.strptime(coupon["expiry_date"], "%Y-%m-%d")
        if datetime.now() > expiry:
            return {"valid": False, "reason": "Coupon expired", "expired_on": coupon["expiry_date"]}

    # Check max uses
    if coupon.get("max_uses") is not None and coupon["uses"] >= coupon["max_uses"]:
        return {"valid": False, "reason": "Coupon usage limit reached", "max_uses": coupon["max_uses"]}

    # Check product filter
    if coupon.get("products") and product:
        if product.lower() not in [p.lower() for p in coupon["products"]]:
            return {
                "valid": False,
                "reason": f"Coupon not valid for product '{product}'",
                "valid_products": coupon["products"],
            }

    return {
        "valid": True,
        "code": upper,
        "discount_percent": coupon["discount_percent"],
        "uses_remaining": (coupon["max_uses"] - coupon["uses"]) if coupon.get("max_uses") else "unlimited",
        "expiry_date": coupon.get("expiry_date"),
        "products": coupon.get("products"),
    }


def redeem_coupon(code: str, product: Optional[str] = None, order_total: float = 0.0) -> dict:
    """
    Redeem a coupon. Increments usage, returns discount amount.
    """
    check = validate_coupon(code, product)
    if not check["valid"]:
        return check

    coupons = _load_coupons()
    upper = code.upper()
    coupon = coupons[upper]

    discount_amount = round(order_total * (coupon["discount_percent"] / 100.0), 2)

    coupon["uses"] += 1
    coupon["redemptions"].append({
        "redeemed_at": datetime.now().isoformat(),
        "product": product,
        "order_total": order_total,
        "discount_applied": discount_amount,
    })

    _save_coupons(coupons)

    return {
        "redeemed": True,
        "code": upper,
        "discount_percent": coupon["discount_percent"],
        "discount_amount": discount_amount,
        "final_price": round(order_total - discount_amount, 2),
        "uses_remaining": (coupon["max_uses"] - coupon["uses"]) if coupon.get("max_uses") else "unlimited",
    }


def create_coupon(code: str, discount_percent: float, max_uses: Optional[int] = None,
                  expiry_date: Optional[str] = None, products: Optional[list] = None) -> dict:
    """Create a new coupon. Returns the coupon dict or error."""
    coupons = _load_coupons()
    upper = code.upper()

    if upper in coupons:
        return {"error": f"Coupon '{upper}' already exists"}

    if expiry_date:
        try:
            datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "expiry_date must be YYYY-MM-DD format"}

    if not (0 < discount_percent <= 100):
        return {"error": "discount_percent must be between 1 and 100"}

    coupon = {
        "code": upper,
        "discount_percent": discount_percent,
        "max_uses": max_uses,
        "uses": 0,
        "expiry_date": expiry_date,
        "products": products,
        "created_at": datetime.now().isoformat(),
        "redemptions": [],
    }

    coupons[upper] = coupon
    _save_coupons(coupons)
    return {"status": "created", "coupon": coupon}


# ---------------------------------------------------------------------------
# FastAPI app (lazy-loaded, only when imported by uvicorn or --serve)
# ---------------------------------------------------------------------------


def _build_app():
    """Build and return the FastAPI app. Deferred so CLI works without fastapi."""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    _app = FastAPI(
        title="Coupon & Discount Code System",
        version="1.0.0",
        docs_url="/docs",
    )

    class CouponCreateModel(BaseModel):
        code: str
        discount_percent: float
        max_uses: Optional[int] = None
        expiry_date: Optional[str] = None
        products: Optional[list[str]] = None

    class RedeemRequest(BaseModel):
        product: Optional[str] = None
        order_total: float = 0.0

    @_app.post("/coupon/create")
    async def api_create_coupon(data: CouponCreateModel):
        """Create a new coupon code."""
        result = create_coupon(
            data.code, data.discount_percent,
            data.max_uses, data.expiry_date, data.products,
        )
        if "error" in result:
            status = 409 if "already exists" in result["error"] else 400
            raise HTTPException(status_code=status, detail=result["error"])
        return result

    @_app.get("/coupon/validate/{code}")
    async def api_validate_coupon(code: str, product: Optional[str] = None):
        """Check if a coupon code is valid."""
        return validate_coupon(code, product)

    @_app.post("/coupon/redeem/{code}")
    async def api_redeem_coupon(code: str, data: RedeemRequest):
        """Redeem a coupon. Marks a use, returns discount amount."""
        result = redeem_coupon(code, data.product, data.order_total)
        if not result.get("redeemed") and not result.get("valid", True):
            raise HTTPException(status_code=400, detail=result.get("reason", "Redemption failed"))
        return result

    @_app.get("/coupon/list")
    async def api_list_coupons():
        """List all coupons with usage stats."""
        coupons = _load_coupons()
        summary = []
        for code, c in coupons.items():
            is_expired = False
            if c.get("expiry_date"):
                is_expired = datetime.now() > datetime.strptime(c["expiry_date"], "%Y-%m-%d")
            maxed_out = False
            if c.get("max_uses") is not None:
                maxed_out = c["uses"] >= c["max_uses"]
            summary.append({
                "code": code,
                "discount_percent": c["discount_percent"],
                "uses": c["uses"],
                "max_uses": c.get("max_uses"),
                "expiry_date": c.get("expiry_date"),
                "products": c.get("products"),
                "active": not is_expired and not maxed_out,
                "created_at": c.get("created_at"),
            })
        return {"count": len(summary), "coupons": summary}

    return _app


# Module-level app for uvicorn import (uvicorn coupons:app)
# Uses lazy property pattern so fastapi is only imported when accessed
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


def cli_list():
    """Print all coupons."""
    coupons = _load_coupons()
    if not coupons:
        print("No coupons found.")
        return

    print(f"\n{'CODE':<12} {'DISC':>5} {'USES':>8} {'MAX':>6} {'EXPIRES':<12} {'PRODUCTS':<20} {'STATUS'}")
    print("-" * 80)

    for code, c in coupons.items():
        is_expired = False
        if c.get("expiry_date"):
            is_expired = datetime.now() > datetime.strptime(c["expiry_date"], "%Y-%m-%d")
        maxed_out = False
        if c.get("max_uses") is not None:
            maxed_out = c["uses"] >= c["max_uses"]

        status = "ACTIVE" if (not is_expired and not maxed_out) else "INACTIVE"
        max_str = str(c["max_uses"]) if c.get("max_uses") is not None else "inf"
        exp_str = c.get("expiry_date") or "never"
        prod_str = ", ".join(c["products"]) if c.get("products") else "all"

        print(f"{code:<12} {c['discount_percent']:>4}% {c['uses']:>8} {max_str:>6} {exp_str:<12} {prod_str:<20} {status}")

    print()


def cli_validate(code: str):
    """Validate a single coupon."""
    result = validate_coupon(code)
    if result["valid"]:
        print(f"  VALID: {result['code']} - {result['discount_percent']}% off")
        print(f"  Uses remaining: {result['uses_remaining']}")
        print(f"  Expires: {result.get('expiry_date') or 'never'}")
        print(f"  Products: {result.get('products') or 'all'}")
    else:
        print(f"  INVALID: {result['reason']}")


def cli_stats():
    """Print redemption stats."""
    coupons = _load_coupons()
    total_redemptions = 0
    total_discount_given = 0.0

    print(f"\n{'CODE':<12} {'REDEMPTIONS':>12} {'TOTAL DISCOUNT':>15}")
    print("-" * 45)

    for code, c in coupons.items():
        r_count = len(c.get("redemptions", []))
        r_discount = sum(r.get("discount_applied", 0) for r in c.get("redemptions", []))
        total_redemptions += r_count
        total_discount_given += r_discount
        print(f"{code:<12} {r_count:>12} ${r_discount:>13.2f}")

    print("-" * 45)
    print(f"{'TOTAL':<12} {total_redemptions:>12} ${total_discount_given:>13.2f}")
    print()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coupon & Discount Code System")
    parser.add_argument("--list", action="store_true", help="List all coupons")
    parser.add_argument("--validate", type=str, metavar="CODE", help="Validate a coupon code")
    parser.add_argument("--stats", action="store_true", help="Show redemption stats")
    parser.add_argument("--create", type=str, metavar="CODE", help="Create a new coupon")
    parser.add_argument("--discount", type=float, help="Discount percentage (used with --create)")
    parser.add_argument("--max-uses", type=int, default=None, help="Max uses (used with --create)")
    parser.add_argument("--expiry", type=str, default=None, help="Expiry date YYYY-MM-DD (used with --create)")
    parser.add_argument("--products", type=str, nargs="*", default=None, help="Product filter (used with --create)")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI server on port 8102")

    args = parser.parse_args()

    if args.list:
        cli_list()
    elif args.validate:
        cli_validate(args.validate)
    elif args.stats:
        cli_stats()
    elif args.create:
        if not args.discount:
            print("  ERROR: --discount is required with --create")
            sys.exit(1)
        result = create_coupon(args.create, args.discount, args.max_uses, args.expiry, args.products)
        if "error" in result:
            print(f"  ERROR: {result['error']}")
            sys.exit(1)
        c = result["coupon"]
        print(f"  Created: {c['code']} - {c['discount_percent']}% off, max_uses={c['max_uses'] or 'unlimited'}, expires={c['expiry_date'] or 'never'}")
    elif args.serve or len(sys.argv) == 1:
        import uvicorn
        real_app = _build_app()
        print("Starting Coupon Server on port 8102...")
        print("Docs: http://localhost:8102/docs")
        print(f"Data: {COUPONS_FILE}")
        uvicorn.run(real_app, host="0.0.0.0", port=8102)
    else:
        parser.print_help()
