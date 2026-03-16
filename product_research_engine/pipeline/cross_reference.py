"""
Cross-reference pipeline — takes discovered products, looks them up on eBay.
STUB until eBay API keys arrive Monday.
"""

import logging
from core.database import Database
from core.trends_adapter import TrendsAdapter
from core.models import TrendData
from ebay.ebay_cross_reference import EbayCrossReference
from datetime import datetime

logger = logging.getLogger(__name__)


class CrossReferencePipeline:

    def __init__(self, config):
        self.config = config
        self.db = Database(config["database"]["path"])
        self.trends = TrendsAdapter(config)

    def run(self):
        products = self.db.get_all_products()
        logger.info(f"Cross-referencing {len(products)} products...")

        # Step 1: Enrich with Google Trends data (this works now)
        trends_enriched = 0
        for p in products:
            signal = self.trends.get_trend_signal(p["name"])
            trend_data = TrendData(
                product_id=p["id"],
                trend_velocity=signal["trend_velocity"],
                trend_classification=signal["trend_classification"],
                trend_score=signal["trend_score"],
                fetched_at=datetime.utcnow(),
            )
            self.db.upsert_trend_data(trend_data)
            trends_enriched += 1

        logger.info(f"Trends enriched: {trends_enriched} products")

        # Step 2: eBay lookup (stub — will work after Monday)
        try:
            ebay = EbayCrossReference()
            ebay.lookup_batch(products)
        except NotImplementedError:
            logger.info("eBay cross-reference: skipped (API keys pending)")

        return trends_enriched
