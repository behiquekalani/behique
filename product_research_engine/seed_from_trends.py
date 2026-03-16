"""
Seed the product research engine DB from the trends scraper output.
Bridges the gap while Amazon/Google Shopping scrapers are blocked.
"""

import json
import sys
import os
import yaml
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.models import Product, TrendData
from core.product_normalizer import ProductNormalizer


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


def seed(trends_json_path):
    config = load_config()
    db = Database(config["database"]["path"])
    normalizer = ProductNormalizer(config)

    with open(trends_json_path) as f:
        data = json.load(f)

    products = data.get("products", [])
    print(f"Loading {len(products)} products from trends output...")

    stored = 0
    for p in products:
        name = p["query"]
        normalized = normalizer.normalize(name)

        product = Product(
            name=name,
            normalized_name=normalized,
            category=p.get("category", "uncategorized"),
            source="google_trends",
            source_price=0,
            source_url="",
            rank=None,
            discovered_at=datetime.utcnow(),
        )
        db.upsert_product(product)

        # Also store trend data directly
        row = db.conn.execute(
            "SELECT id FROM products WHERE normalized_name = ? AND source = ?",
            (normalized, "google_trends")
        ).fetchone()

        if row:
            trend = TrendData(
                product_id=row[0],
                trend_velocity=p.get("trend_velocity", 0.5),
                trend_classification=p.get("trend_classification", "stable"),
                trend_score=p.get("score", 0.5),
                fetched_at=datetime.utcnow(),
            )
            db.upsert_trend_data(trend)

        stored += 1

    print(f"Seeded {stored} products + trend data into engine DB.")
    return stored


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "../output/trending_products_2026-03-15.json"
    seed(path)
