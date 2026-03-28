"""
Behike Product Recommendation Engine
FastAPI server on port 8104
Reads catalog from storefront/products.json

Recommendation logic:
  1. Same category (bought blueprint -> other blueprints)
  2. Upgrade path (bought single -> suggest bundle/premium)
  3. Cross-sell (bought blueprint -> guide in same niche)
  4. Complementary (bought e-commerce -> dropshipping)

CLI:
  python recommender.py --product "behike-os"
  python recommender.py --generate-map
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    app = FastAPI(title="Behike Recommendation Engine", version="1.0.0")
except ImportError:
    app = None  # CLI-only mode, no FastAPI available

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "storefront" / "products.json"
MAP_PATH = Path(__file__).parent / "data" / "recommendation_map.json"


# ---------------------------------------------------------------------------
# Niche tagging -- group products by topic so cross-sell works
# ---------------------------------------------------------------------------

NICHE_KEYWORDS = {
    "ai": ["ai", "claude", "n8n", "automation", "agent", "chatbot", "prompt", "copywriting"],
    "ecommerce": ["ecommerce", "ebay", "amazon", "fba", "dropshipping", "gumroad", "niche-sniper", "overnight"],
    "content": ["content", "writing", "newsletter", "storytelling", "video", "youtube", "short-form", "brand-voice", "vault"],
    "creator-business": ["creator", "personal-brand", "coaching", "course", "faceless", "thought-leadership", "one-person"],
    "revenue": ["revenue", "passive-income", "recurring", "subscription", "monetization", "pricing", "10k", "high-ticket"],
    "marketing": ["email", "linkedin", "twitter", "social-proof", "client-acquisition", "launch"],
    "productivity": ["os", "second-brain", "calendar", "time-freedom", "productivity", "systems", "remote-work"],
    "finance": ["finance", "budget", "cash-flow", "rate-calculator", "adhd-finance"],
    "freelance": ["freelancer", "consulting", "freelance", "rate"],
    "adhd": ["adhd", "study-buddy"],
    "behike": ["behike", "behike-method"],
}

# Category tier for upgrade path logic (low -> high value)
CATEGORY_TIER = {
    "free": 0,
    "template": 1,
    "guide": 2,
    "blueprint": 3,
    "kit": 4,
}


def load_catalog() -> list[dict]:
    with open(CATALOG_PATH) as f:
        return json.load(f)


def get_niches(product: dict) -> set[str]:
    """Tag a product with all matching niches."""
    slug = product["id"].lower()
    title = product["title"].lower()
    desc = product.get("description", "").lower()
    combined = f"{slug} {title} {desc}"

    matches = set()
    for niche, keywords in NICHE_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                matches.add(niche)
                break
    return matches


def score_recommendation(source: dict, candidate: dict, source_niches: set) -> tuple[float, str]:
    """
    Score a candidate product against the source product.
    Returns (score, reason_string). Higher = better recommendation.
    """
    if candidate["id"] == source["id"]:
        return -1, ""

    cand_niches = get_niches(candidate)
    src_cat = source["category"]
    cand_cat = candidate["category"]
    src_tier = CATEGORY_TIER.get(src_cat, 2)
    cand_tier = CATEGORY_TIER.get(cand_cat, 2)
    niche_overlap = source_niches & cand_niches

    score = 0.0
    reasons = []

    # 1. Same category bonus
    if src_cat == cand_cat:
        score += 3.0
        reasons.append("same category")

    # 2. Upgrade path -- candidate is a higher tier
    if cand_tier > src_tier:
        score += 4.0
        reasons.append(f"upgrade from {src_cat} to {cand_cat}")

    # 3. Cross-sell -- different category but same niche
    if src_cat != cand_cat and niche_overlap:
        score += 5.0
        reasons.append(f"cross-sell ({', '.join(sorted(niche_overlap))})")

    # 4. Complementary niche overlap (even same category)
    if niche_overlap:
        score += 2.0 * len(niche_overlap)
        if "cross-sell" not in " ".join(reasons):
            reasons.append(f"related niche: {', '.join(sorted(niche_overlap))}")

    # 5. Price proximity bonus -- don't recommend $200 after a $5 purchase
    price_diff = abs(candidate["price"] - source["price"])
    if price_diff <= 10:
        score += 2.0
    elif price_diff <= 20:
        score += 1.0

    # 6. Slight bonus for higher-priced items (revenue optimization)
    if candidate["price"] > source["price"] and candidate["price"] < source["price"] * 4:
        score += 1.5
        reasons.append("higher value")

    # 7. Penalize free products as recommendations (unless source is also free)
    if candidate["price"] == 0 and source["price"] > 0:
        score -= 5.0

    # Build a clean reason string
    if not reasons:
        reasons = ["popular in our catalog"]

    reason = reasons[0].capitalize()
    if len(reasons) > 1:
        reason = f"{reasons[0].capitalize()}, {reasons[1]}"

    return score, reason


def get_recommendations(product_slug: str, count: int = 3) -> list[dict]:
    """Get top N recommendations for a product slug."""
    catalog = load_catalog()

    source = None
    for p in catalog:
        if p["id"] == product_slug:
            source = p
            break

    if not source:
        return []

    source_niches = get_niches(source)
    scored = []

    for candidate in catalog:
        s, reason = score_recommendation(source, candidate, source_niches)
        if s > 0:
            scored.append((s, reason, candidate))

    scored.sort(key=lambda x: (-x[0], -x[2]["price"]))

    results = []
    for s, reason, prod in scored[:count]:
        results.append({
            "title": prod["title"],
            "price": prod["price"],
            "reason": reason,
            "gumroad_url": prod["gumroad_url"],
            "id": prod["id"],
            "category": prod["category"],
        })

    return results


def generate_full_map() -> dict:
    """Build the full recommendation graph for all products."""
    catalog = load_catalog()
    rec_map = {}

    for product in catalog:
        recs = get_recommendations(product["id"], count=3)
        rec_map[product["id"]] = {
            "title": product["title"],
            "price": product["price"],
            "category": product["category"],
            "recommendations": recs,
        }

    # Save to disk
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MAP_PATH, "w") as f:
        json.dump(rec_map, f, indent=2)

    return rec_map


# ---------------------------------------------------------------------------
# Pre-built recommendation overrides for top products
# These take priority over algorithmic recommendations
# ---------------------------------------------------------------------------

TOP_PRODUCT_OVERRIDES: dict[str, list[str]] = {
    "behike-method": [
        "creators-first-10k-blueprint",
        "zero-to-1k-roadmap",
        "gumroad-starter-kit",
    ],
    "behike-method-v2": [
        "solopreneur-os",
        "ai-automation-blueprint",
        "content-empire-kit",
    ],
    "ai-automation-blueprint": [
        "n8n-solopreneur-guide",
        "ai-agent-installer-kit",
        "ai-employee-guide",
    ],
    "ai-employee-guide": [
        "ai-agent-installer-kit",
        "n8n-automation-pack",
        "ai-automation-blueprint",
    ],
    "ecommerce-playbook": [
        "ebay-dropshipping-guide",
        "niche-sniper-guide",
        "amazon-fba-guide",
    ],
    "ecommerce-playbook-v3": [
        "ebay-dropshipping-guide",
        "overnight-machine",
        "niche-sniper-guide",
    ],
    "ebay-dropshipping-guide": [
        "overnight-machine",
        "niche-sniper-guide",
        "ecommerce-playbook-v3",
    ],
    "solopreneur-os": [
        "solopreneur-systems-bible",
        "solopreneur-second-brain",
        "solopreneurs-time-freedom-blueprint",
    ],
    "creators-first-10k-blueprint": [
        "creators-revenue-blueprint",
        "gumroad-sellers-playbook",
        "digital-product-launch-formula",
    ],
    "content-empire-kit": [
        "content-waterfall",
        "ai-content-machine-kit",
        "the-content-vault",
    ],
    "zero-to-1k-roadmap": [
        "creators-first-10k-blueprint",
        "gumroad-starter-kit",
        "behike-method-v2",
    ],
    "gumroad-starter-kit": [
        "gumroad-sellers-playbook",
        "digital-product-launch-formula",
        "creators-first-10k-blueprint",
    ],
    "youtube-channel-blueprint": [
        "youtube-monetization-blueprint",
        "short-form-video-mastery",
        "faceless-creator-blueprint",
    ],
    "personal-brand-blueprint": [
        "creators-brand-positioning-masterclass",
        "one-person-brand-bible",
        "thought-leadership-playbook",
    ],
}


def get_recommendations_with_overrides(product_slug: str, count: int = 3) -> list[dict]:
    """
    Get recommendations, using manual overrides for top products,
    falling back to algorithmic scoring.
    """
    catalog = load_catalog()
    catalog_by_id = {p["id"]: p for p in catalog}

    if product_slug in TOP_PRODUCT_OVERRIDES:
        override_ids = TOP_PRODUCT_OVERRIDES[product_slug][:count]
        results = []
        for pid in override_ids:
            prod = catalog_by_id.get(pid)
            if prod:
                # Generate a reason based on relationship
                src = catalog_by_id.get(product_slug)
                src_niches = get_niches(src) if src else set()
                _, reason = score_recommendation(src, prod, src_niches)
                if not reason:
                    reason = "Curated recommendation"
                results.append({
                    "title": prod["title"],
                    "price": prod["price"],
                    "reason": reason,
                    "gumroad_url": prod["gumroad_url"],
                    "id": prod["id"],
                    "category": prod["category"],
                })
        return results

    return get_recommendations(product_slug, count)


# ---------------------------------------------------------------------------
# HTML widget generator
# ---------------------------------------------------------------------------

def generate_widget_html(product_slug: str, recs: list[dict]) -> str:
    """Generate an embeddable HTML widget for a thank-you page."""
    if not recs:
        return "<div>No recommendations available.</div>"

    cards = ""
    for r in recs:
        price_str = f"${r['price']}" if r["price"] > 0 else "Free"
        url = r["gumroad_url"] if r["gumroad_url"] != "#" else f"/product/{r['id']}"
        cards += f"""
      <div style="background:#fff;border:1px solid #e0e0e0;border-radius:12px;padding:20px;flex:1;min-width:220px;max-width:320px;">
        <div style="font-size:14px;font-weight:600;margin-bottom:8px;color:#111;">{r['title']}</div>
        <div style="font-size:13px;color:#666;margin-bottom:12px;">{r['reason']}</div>
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <span style="font-size:18px;font-weight:700;color:#111;">{price_str}</span>
          <a href="{url}" target="_blank" rel="noopener"
             style="background:#111;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;">
            Get it
          </a>
        </div>
      </div>"""

    return f"""<!-- Behike Recommendation Widget for: {product_slug} -->
<div id="behike-recs" style="max-width:960px;margin:32px auto;font-family:-apple-system,system-ui,sans-serif;">
  <h3 style="font-size:20px;font-weight:700;margin-bottom:16px;color:#111;">You might also like</h3>
  <div style="display:flex;gap:16px;flex-wrap:wrap;">
    {cards}
  </div>
</div>"""


# ---------------------------------------------------------------------------
# FastAPI endpoints (only registered when FastAPI is available)
# ---------------------------------------------------------------------------

if app is not None:

    @app.get("/recommend/{product_slug}")
    async def recommend(product_slug: str, count: int = 3):
        """Get product recommendations as JSON."""
        catalog = load_catalog()
        known_ids = {p["id"] for p in catalog}

        if product_slug not in known_ids:
            raise HTTPException(status_code=404, detail=f"Product '{product_slug}' not found in catalog")

        recs = get_recommendations_with_overrides(product_slug, count)
        return JSONResponse({
            "product": product_slug,
            "recommendations": recs,
        })

    @app.get("/recommend/{product_slug}/widget", response_class=HTMLResponse)
    async def recommend_widget(product_slug: str, count: int = 3):
        """Get an embeddable HTML recommendation widget."""
        catalog = load_catalog()
        known_ids = {p["id"] for p in catalog}

        if product_slug not in known_ids:
            raise HTTPException(status_code=404, detail=f"Product '{product_slug}' not found")

        recs = get_recommendations_with_overrides(product_slug, count)
        html = generate_widget_html(product_slug, recs)
        return HTMLResponse(html)

    @app.get("/recommendation-map")
    async def full_map():
        """Return the full recommendation graph."""
        if MAP_PATH.exists():
            with open(MAP_PATH) as f:
                return JSONResponse(json.load(f))
        rec_map = generate_full_map()
        return JSONResponse(rec_map)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli():
    parser = argparse.ArgumentParser(description="Behike Product Recommendation Engine")
    parser.add_argument("--product", type=str, help="Show recommendations for a product slug")
    parser.add_argument("--generate-map", action="store_true", help="Build full recommendation graph")
    parser.add_argument("--count", type=int, default=3, help="Number of recommendations (default: 3)")
    parser.add_argument("--widget", action="store_true", help="Output HTML widget instead of JSON")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI server on port 8104")
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        print("Starting recommendation engine on http://localhost:8104")
        uvicorn.run(app, host="0.0.0.0", port=8104)
        return

    if args.generate_map:
        rec_map = generate_full_map()
        print(f"Generated recommendation map for {len(rec_map)} products")
        print(f"Saved to {MAP_PATH}")

        # Show summary
        total_recs = sum(len(v["recommendations"]) for v in rec_map.values())
        print(f"Total recommendation edges: {total_recs}")
        return

    if args.product:
        recs = get_recommendations_with_overrides(args.product, args.count)
        if not recs:
            print(f"No product found with slug: {args.product}")
            sys.exit(1)

        if args.widget:
            print(generate_widget_html(args.product, recs))
        else:
            print(f"\nRecommendations for: {args.product}")
            print("-" * 50)
            for i, r in enumerate(recs, 1):
                price_str = f"${r['price']}" if r["price"] > 0 else "Free"
                print(f"  {i}. {r['title']} ({price_str})")
                print(f"     Reason: {r['reason']}")
                print(f"     URL: {r['gumroad_url']}")
                print()
        return

    parser.print_help()


if __name__ == "__main__":
    cli()
