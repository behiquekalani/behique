"""
A/B Testing System for Behike Sales Pages
FastAPI server on port 8100

Endpoints:
  GET  /ab/variant  - returns A or B (50/50, sticky by cookie)
  POST /ab/convert  - logs conversion event
  GET  /ab/results  - conversion rates + chi-squared significance
"""

import json
import os
import time
import uuid
import math
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Behike A/B Testing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "ab_tests.json"
DASHBOARD_FILE = Path(__file__).parent / "ab_dashboard.html"


def load_data() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"visitors": {}, "conversions": []}


def save_data(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def chi_squared_p(a_views: int, a_conv: int, b_views: int, b_conv: int) -> float:
    """Chi-squared test for independence. Returns p-value approximation."""
    total = a_views + b_views
    total_conv = a_conv + b_conv
    total_no_conv = total - total_conv

    if total == 0 or total_conv == 0 or total_no_conv == 0:
        return 1.0
    if a_views == 0 or b_views == 0:
        return 1.0

    # Expected values
    e_a_conv = a_views * total_conv / total
    e_a_no = a_views * total_no_conv / total
    e_b_conv = b_views * total_conv / total
    e_b_no = b_views * total_no_conv / total

    if any(e == 0 for e in [e_a_conv, e_a_no, e_b_conv, e_b_no]):
        return 1.0

    # Chi-squared statistic
    chi2 = (
        (a_conv - e_a_conv) ** 2 / e_a_conv
        + ((a_views - a_conv) - e_a_no) ** 2 / e_a_no
        + (b_conv - e_b_conv) ** 2 / e_b_conv
        + ((b_views - b_conv) - e_b_no) ** 2 / e_b_no
    )

    # Approximate p-value for 1 df using survival function approximation
    # Wilson-Hilferty approximation for chi-squared CDF
    if chi2 <= 0:
        return 1.0
    # For 1 degree of freedom, p = 2 * (1 - Phi(sqrt(chi2)))
    # Using error function approximation
    z = math.sqrt(chi2)
    # Abramowitz and Stegun approximation for complementary normal CDF
    t = 1.0 / (1.0 + 0.2316419 * z)
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p = d * math.exp(-z * z / 2.0) * (
        t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
    )
    return 2 * p  # two-tailed


@app.get("/ab/variant")
async def get_variant(request: Request, response: Response, test: str = "default", product: str = ""):
    data = load_data()
    visitor_id = request.cookies.get("ab_visitor_id")

    if visitor_id and visitor_id in data["visitors"]:
        visitor = data["visitors"][visitor_id]
        # Check if this visitor already has a variant for this test
        if test in visitor.get("tests", {}):
            variant = visitor["tests"][test]
            response.set_cookie("ab_visitor_id", visitor_id, max_age=60 * 60 * 24 * 90)
            return {"variant": variant, "visitor_id": visitor_id, "test": test}

    if not visitor_id:
        visitor_id = str(uuid.uuid4())

    if visitor_id not in data["visitors"]:
        data["visitors"][visitor_id] = {"tests": {}, "created": time.time()}

    # 50/50 split based on UUID hash
    variant = "A" if hash(visitor_id + test) % 2 == 0 else "B"
    data["visitors"][visitor_id]["tests"][test] = variant
    save_data(data)

    response.set_cookie("ab_visitor_id", visitor_id, max_age=60 * 60 * 24 * 90)
    return {"variant": variant, "visitor_id": visitor_id, "test": test}


@app.post("/ab/convert")
async def log_conversion(request: Request):
    body = await request.json()
    variant = body.get("variant", "")
    product = body.get("product", "unknown")
    test = body.get("test", "default")
    visitor_id = request.cookies.get("ab_visitor_id", body.get("visitor_id", ""))

    if not variant:
        return JSONResponse({"error": "variant is required"}, status_code=400)

    data = load_data()
    data["conversions"].append({
        "variant": variant,
        "product": product,
        "test": test,
        "visitor_id": visitor_id,
        "timestamp": time.time(),
        "ts_readable": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_data(data)
    return {"status": "ok", "conversion_logged": True}


@app.get("/ab/results")
async def get_results(test: str = ""):
    data = load_data()

    # Group by test
    tests = {}
    for vid, visitor in data["visitors"].items():
        for t, variant in visitor.get("tests", {}).items():
            if test and t != test:
                continue
            if t not in tests:
                tests[t] = {"A": {"views": 0, "conversions": 0}, "B": {"views": 0, "conversions": 0}}
            tests[t][variant]["views"] += 1

    for conv in data["conversions"]:
        t = conv.get("test", "default")
        v = conv.get("variant", "")
        if test and t != test:
            continue
        if t in tests and v in tests[t]:
            tests[t][v]["conversions"] += 1

    results = {}
    for t, variants in tests.items():
        a = variants["A"]
        b = variants["B"]
        a_rate = (a["conversions"] / a["views"] * 100) if a["views"] > 0 else 0
        b_rate = (b["conversions"] / b["views"] * 100) if b["views"] > 0 else 0

        p_value = chi_squared_p(a["views"], a["conversions"], b["views"], b["conversions"])
        confidence = (1 - p_value) * 100

        if confidence >= 95:
            significance = "significant"
        elif confidence >= 80:
            significance = "trending"
        else:
            significance = "insufficient"

        winner = None
        if significance == "significant":
            winner = "A" if a_rate > b_rate else "B" if b_rate > a_rate else "tie"

        results[t] = {
            "A": {"views": a["views"], "conversions": a["conversions"], "rate": round(a_rate, 2)},
            "B": {"views": b["views"], "conversions": b["conversions"], "rate": round(b_rate, 2)},
            "p_value": round(p_value, 4),
            "confidence": round(confidence, 1),
            "significance": significance,
            "winner": winner,
        }

    return {"tests": results, "total_visitors": len(data["visitors"]), "total_conversions": len(data["conversions"])}


@app.get("/ab/dashboard")
async def dashboard():
    if DASHBOARD_FILE.exists():
        return HTMLResponse(DASHBOARD_FILE.read_text())
    return HTMLResponse("<h1>Dashboard not found</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
