"""
Scoring pipeline — loads features, scores products, stores results.
Can re-score without re-scraping.
"""

import logging
from datetime import datetime
from core.database import Database
from core.scoring_engine import ScoringEngine
from core.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


# Default market data for products without eBay data yet
DEFAULT_MARKET = {
    "avg_price": 0,
    "units_sold_90d": 0,
    "active_listings": 0,
    "sell_through": 0.5,
    "last_sale_days": 30,
}

DEFAULT_TREND = {
    "trend_velocity": 0.5,
    "trend_classification": "stable",
    "trend_score": 0.5,
}


class ScoringPipeline:

    def __init__(self, config):
        self.config = config
        self.db = Database(config["database"]["path"])
        self.engine = ScoringEngine(config)
        self.features = FeatureEngineer(config)

    def run(self):
        products = self.db.get_all_products()
        logger.info(f"Scoring {len(products)} products...")

        scored = 0
        for p in products:
            # Get latest market data (or defaults if eBay not connected yet)
            market = self.db.get_latest_ebay_data(p["id"]) or DEFAULT_MARKET
            trend = self.db.get_latest_trend_data(p["id"]) or DEFAULT_TREND

            # Compute features
            feat = self.features.compute(p, market, trend)
            self.db.save_features(p["id"], feat)

            # Score
            scored_product = self.engine.score(p["id"], feat, market, trend)
            self.db.save_score(scored_product)
            scored += 1

        logger.info(f"Scoring complete. {scored} products scored.")
        return scored
