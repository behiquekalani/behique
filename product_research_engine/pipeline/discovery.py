"""
Discovery pipeline — runs source scrapers, normalizes products, stores to DB.
"""

import logging
from datetime import datetime
from core.database import Database
from core.models import Product
from core.product_normalizer import ProductNormalizer
from scrapers.amazon_best_sellers import AmazonBestSellersScraper

logger = logging.getLogger(__name__)

# Map of available scrapers
SCRAPER_MAP = {
    "amazon": AmazonBestSellersScraper,
    # "walmart": WalmartTrendingScraper,  # stub
    # "target": TargetTrendingScraper,    # stub
    # "homedepot": HomeDepotBestSellersScraper, # stub
    # "costco": CostcoPopularScraper,     # stub
}


class DiscoveryPipeline:

    def __init__(self, config):
        self.config = config
        self.db = Database(config["database"]["path"])
        self.normalizer = ProductNormalizer(config)

    def run(self, sources=None, category=None):
        active_sources = sources or list(SCRAPER_MAP.keys())
        total = 0

        for source_name in active_sources:
            if source_name not in SCRAPER_MAP:
                logger.warning(f"Unknown source: {source_name}")
                continue

            scraper_class = SCRAPER_MAP[source_name]
            scraper = scraper_class(self.config)

            logger.info(f"Running discovery: {source_name}")
            try:
                raw_products = scraper.scrape()
            except NotImplementedError:
                logger.info(f"Skipping {source_name} (not implemented)")
                continue
            except Exception as e:
                logger.error(f"Scraper {source_name} failed: {e}")
                continue

            stored = 0
            for p in raw_products:
                normalized = self.normalizer.normalize(p["name"])

                # Filter by category if specified
                if category and p.get("category", "") != category:
                    continue

                product = Product(
                    name=p["name"],
                    normalized_name=normalized,
                    category=p.get("category", "uncategorized"),
                    source=p.get("source", source_name),
                    source_price=p.get("price", 0),
                    source_url=p.get("url", ""),
                    rank=p.get("rank"),
                    discovered_at=datetime.utcnow(),
                )

                self.db.upsert_product(product)
                stored += 1

            logger.info(f"  {source_name}: {len(raw_products)} found, {stored} stored")
            total += stored

        logger.info(f"Discovery complete. {total} products in database.")
        return total
